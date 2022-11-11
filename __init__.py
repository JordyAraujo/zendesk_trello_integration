"""
Integration between Zendesk and Trello. The main purpose here is to automatize
the workflow between the platforms.
"""
from flask import Flask, request
from flask_loguru import Logger, logger
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, Comment
import httpx

from trello_api_wrapper import Trello
from .config import settings
from .utils.match_cases import status_by_list_id, priority_by_tag_id
from .utils.trello import (
    create_description,
    filter_custom_field,
    handle_card_creation,
    handle_card_update
)

app = Flask(__name__)

app_logger = Logger()

app_logger.init_app(app, {"LOG_PATH": ".", "LOG_NAME": "loguru_logger.json"})

trello = Trello(settings.TRELLO_KEY, settings.TRELLO_TOKEN)

card_list = trello.card_list(settings.NEW_CARDS_LIST_ID)

credentials = {
    "email": settings.ZENDESK_EMAIL,
    "token": settings.ZENDESK_TOKEN,
    "subdomain": settings.ZENDESK_SUBDOMAIN,
}

zenpy_client = Zenpy(**credentials)


@app.route("/new_ticket", methods=["POST"])
def new_ticket():
    """A new Zendesk Ticket has been created"""
    response = request.get_json()
    tags = response["tags"].split(" ")
    ticket_id = response.get("id", None)
    ticket = zenpy_client.tickets(id=ticket_id)
    return_id = ticket_id
    response_status_code = 304
    if "zendesk" in tags:
        title, description, id_labels = handle_card_creation(response)
        custom_fields = ticket.custom_fields

        card_id_custom_field = filter_custom_field(
            ticket, settings.TRELLO_CARD_ID_CUSTOM_FIELD
        )

        card_id_custom_field_index = custom_fields.index(card_id_custom_field)

        card_id, response_status_code = card_list.create_card(
            title, description, id_labels
        )

        return_id = card_id

        ticket.custom_fields[card_id_custom_field_index]["value"] = card_id
        zenpy_client.tickets.update(ticket)

        logger.info(
            f"Cartão criado baseado em ticket novo no Zendesk!\n"
            f"- id: {card_id}\n- Título: {title}\n"
            f"- Código HTTP: {response_status_code}"
        )
    elif "trello" not in tags:
        # As the tickets created on Trello always have the trello tag,
        # this one should have come from zendesk
        if "zendesk" not in tags:
            ticket.tags.extend(["zendesk"])
        zenpy_client.tickets.update(ticket)
        response_status_code = 200

    return return_id, response_status_code


@app.route("/update_ticket", methods=["POST"])
def update_ticket(rsp=None):
    """A Zendesk Ticket has been updated"""
    response = rsp if rsp else request.get_json()
    ticket_id = response.get("id", None)
    ticket = zenpy_client.tickets(id=ticket_id)
    ticket_id = handle_card_update(response, ticket)

    logger.info(
        "Cartão editado baseado em ticket atualizado no Zendesk!\n"
        f"- ID do Ticket: {ticket_id}"
    )
    return ticket_id, 200


@app.route("/board_webhook", methods=["POST", "GET"])
def board_webhook():
    """An update has been made on the board"""
    if request.method == 'POST':
        response = request.get_json()

        if "type" in response["action"].keys():
            action_type = response["action"]["type"]
        else:
            action_type = None

        # When a card is created
        if action_type and action_type == "createCard":
            card_id = response["action"]["data"]["card"]["id"]
            # Get the labels on the card newly created
            labels_url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
            try:
                headers = {"Accept": "application/json"}
                param = {
                    "key": settings.TRELLO_KEY,
                    "token": settings.TRELLO_TOKEN,
                }
                rsp = httpx.get(
                    labels_url, headers=headers, params={**param}
                )
                rsp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                logger.error(exc)
            labels = rsp.json()

            # Check if it was created initially on trello or zendesk
            # If there are no labels,
            # the card has been created manually on trello
            if not labels:
                card_id = response["action"]["data"]["card"]["id"]
                custom_fields = [
                    {"id": settings.TRELLO_CARD_ID_CUSTOM_FIELD, "value": card_id},
                    {"id": settings.TI_AGENT_CUSTOM_FIELD, "value": "-"},
                    {"id": settings.CREATED_AT_CUSTOM_FIELD, "value": "trello"},
                    {"id": settings.PRIORITY_CUSTOM_FIELD, "value": "normal"}
                ]

                subject = response["action"]["data"]["card"]["name"]

                list_id = response["action"]["data"]["list"]["id"]
                status = status_by_list_id(list_id)

                ticket = Ticket(
                    subject=subject,
                    description="Criado no Trello",
                    tags=["trello"],
                    status=status,
                    priority="normal",
                    custom_fields=custom_fields
                )

                new_ticket = zenpy_client.tickets.create(ticket)
                ticket_id = new_ticket.ticket.id
                title = "#" + str(ticket_id) + " - " + subject

                ticket_url = f"https://cdanatal.zendesk.com/agent/tickets/{ticket_id}"
                subdescription = "Trello"
                ticket_type = "Tarefa"
                collaborator = "Trello"
                department = "ti"
                tags = "trello"

                description = create_description(
                    ticket_url, subdescription, ticket_type, collaborator, department, tags
                )

                url = f"https://api.trello.com/1/cards/{card_id}"
                try:
                    headers = {
                        "Accept": "application/json"
                    }
                    param = {
                        "key": settings.TRELLO_KEY,
                        "token": settings.TRELLO_TOKEN
                    }
                    data = {
                        "name": title,
                        "desc": description,
                        "pos": "top"
                    }
                    rsp = httpx.put(
                        url, headers=headers, params={**param}, data={**data}
                    )
                    rsp.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    logger.error(exc)

                url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
                try:
                    param = {
                        "key": settings.TRELLO_KEY,
                        "token": settings.TRELLO_TOKEN,
                        "value": settings.LABEL_ID_LIME_DARK
                    }

                    rsp = httpx.post(
                        url, headers=headers, params={**param}
                    )
                    rsp.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    logger.error(exc)

            logger.info(response)
            card = {}
            card["tags"] = tags if tags else "zendesk"
            card["card_id"] = card_id
            card["id"] = ticket_id
            card["title"] = subject
            card["status"] = status
            card["priority"] = "Normal"
            card["url"] = ticket_url
            card["description"] = description
            card["ticket_type"] = ticket_type
            card["user"] = "Trello"
            card["agent"] = "Trello"
            update_ticket(card)
        else:
            card_name = response["action"]["data"]["card"]["name"]
            ticket_id = card_name.split("#")[1].split(" - ")[0]
            ticket = zenpy_client.tickets(id=int(ticket_id))
            # When a comment is added
            if action_type and action_type == "commentCard":
                new_comment = response["action"]["data"]["text"]
                if not bool(new_comment.split("\n")[0] == "----------------------------------------------"):
                    comments = []
                    for comment in zenpy_client.tickets.comments(ticket=ticket_id):
                        comments.append(comment)
                    if not " - __" in new_comment:
                        ticket.comment = Comment(body=new_comment, public=True)
                        zenpy_client.tickets.update(ticket)
            # When a card is updated
            elif action_type and action_type == "updateCard":
                # When a tag is added or removed
                if "idLabels" in response["action"]["data"]["old"]:
                    old_labels_list = response["action"]["data"]["old"]["idLabels"]
                    new_labels_list = response["action"]["data"]["card"]["idLabels"]
                    removed_label_id = set(old_labels_list).difference(set(new_labels_list))
                    for label in removed_label_id:
                        removed_label_id = label
                    added_label_id = set(new_labels_list).difference(set(old_labels_list))
                    for label in added_label_id:
                        added_label_id = label
                    # When a tag is added
                    if added_label_id:
                        # If the added label is priority related
                        if added_label_id in (
                            settings.LABEL_ID_GREEN_DARK,
                            settings.LABEL_ID_YELLOW_DARK,
                            settings.LABEL_ID_ORANGE_DARK,
                            settings.LABEL_ID_RED_DARK
                        ):
                            priority_custom_field = filter_custom_field(
                                ticket, settings.PRIORITY_CUSTOM_FIELD
                            )
                            custom_fields = ticket.custom_fields
                            priority_custom_field_index = custom_fields.index(priority_custom_field)
                            priority = priority_by_tag_id(added_label_id)

                            ticket.custom_fields[priority_custom_field_index]["value"] = priority
                            zenpy_client.tickets.update(ticket)
    else:
        response = 'board_webhook'

    return response, 200
