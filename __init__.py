"""
Integration between Zendesk and Trello. The main purpose here is to automatize
the workflow between the platforms.
"""
from flask import Flask, request
from flask_loguru import Logger, logger
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, Comment

from ..TrelloApi.trelloapi import Trello
from .config import settings
from .utils.match_cases import status_by_list_id, priority_by_tag_id
from .utils.trello import (
    filter_custom_field,
    handle_card_creation,
    handle_card_update,
    initialize_webhook
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

initialize_webhook()


@app.route("/new_ticket", methods=["POST"])
def new_ticket():
    """A new Zendesk Ticket has been created"""
    response = request.get_json()
    ticket_id, title, description, id_labels = handle_card_creation(response)
    ticket = zenpy_client.tickets(id=ticket_id)
    custom_fields = ticket.custom_fields
    return_id = ticket_id

    created_at_custom_field = filter_custom_field(
        ticket, settings.CREATED_AT_CUSTOM_FIELD
    )

    card_id_custom_field = filter_custom_field(
        ticket, settings.TRELLO_CARD_ID_CUSTOM_FIELD
    )

    if created_at_custom_field["value"] == "zendesk":

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
    else:
        created_at_custom_field_index = custom_fields.index(
            created_at_custom_field
        )
        ticket.custom_fields[created_at_custom_field_index]["value"] = "trello"
        zenpy_client.tickets.update(ticket)
        response_status_code = 200

    return return_id, response_status_code


@app.route("/update_ticket", methods=["POST"])
def update_ticket():
    """A Zendesk Ticket has been updated"""
    response = request.get_json()
    ticket_id = response.get("id", None)
    ticket = zenpy_client.tickets(id=ticket_id)
    ticket_id = handle_card_update(response, ticket)

    logger.info(
        "Cartão editado baseado em ticket atualizado no Zendesk!\n"
        f"- ID do Ticket: {ticket_id}"
    )
    return ticket_id, 200


@app.route("/board_webhook", methods=["POST"])
def board_webhook():
    """An update has been made on the board"""

    response = request.get_json()

    if "type" in response["action"].keys():
        action_type = response["action"]["type"]
    else:
        action_type = None


    # When a card is created
    if action_type and action_type == "createCard":
        # Se o título do cartão não começa com #, significa que foi
        # criado diretamente no Trello, então deve ser criado no zendesk
        if not response["action"]["data"]["card"]["name"][0] == "#":
            card_id = response["action"]["data"]["card"]["id"]
            custom_fields = [
                {"id": settings.TRELLO_CARD_ID_CUSTOM_FIELD, "value": card_id},
                {"id": settings.TI_AGENT_CUSTOM_FIELD, "value": "jordy"},
                {"id": settings.CREATED_AT_CUSTOM_FIELD, "value": "trello"},
            ]

            subject = response["action"]["data"]["card"]["name"]

            list_id = response["action"]["data"]["list"]["id"]
            status = status_by_list_id(list_id)

            ticket = Ticket(
                subject=subject,
                description="Criado pelo Trello",
                status=status,
                custom_fields=custom_fields,
            )

            zenpy_client.tickets.create(ticket)
    else:
        card_name = response["action"]["data"]["card"]["name"]
        ticket_id = card_name.split('#')[1].split(' - ')[0]
        ticket = zenpy_client.tickets(id=ticket_id)
        # When a comment is added
        if action_type and action_type == "commentCard":
            new_comment = response["action"]["data"]["text"]
            if not bool(new_comment.split('\n')[0] == '----------------------------------------------'):
                comments = []
                for comment in zenpy_client.tickets.comments(ticket=ticket_id):
                    comments.append(comment)
                if not ' - __' in new_comment:
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

    return response, 200
