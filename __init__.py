"""
Integration between Zendesk and Trello. The main purpose here is to automatize
the workflow between the platforms.
"""
from flask import Flask, request
from zenpy import Zenpy

from ..TrelloApi.trelloapi import Trello
from .config import settings
from .utils.trello import (
    handle_card_creation,
    handle_card_update,
    initialize_webhook,
)

app = Flask(__name__)

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
    print("##### CARD CREATION #####")
    response = request.get_json()
    ticket_id, title, description, id_labels = handle_card_creation(response)
    ticket = zenpy_client.tickets(id=ticket_id)
    custom_fields = ticket.custom_fields

    custom_field = list(
        filter(
            lambda field: field["id"]
            == int(settings.TRELLO_CARD_CUSTOM_FIELD),
            ticket.custom_fields,
        )
    )[0]
    custom_field_index = custom_fields.index(custom_field)

    card_id, response_status_code = card_list.create_card(
        title, description, id_labels
    )

    ticket.custom_fields[custom_field_index]["value"] = card_id
    zenpy_client.tickets.update(ticket)

    print(
        f"Novo Ticket criado no Zendesk!\n"
        f"- id: {card_id}\n- Título: {title}\n"
        f"- Código HTTP: {response_status_code}"
    )

    return card_id, response_status_code


@app.route("/update_ticket", methods=["POST"])
def update_ticket():
    """A Zendesk Ticket has been updated"""
    print("##### CARD UPDATE #####")
    response = request.get_json()
    ticket_id = response.get("id", None)
    ticket = zenpy_client.tickets(id=ticket_id)
    ticket_id = handle_card_update(response, ticket)

    print(f"Ticket atualizado no Zendesk!\n- ID do Ticket: {ticket_id}")
    return ticket_id, 200


@app.route("/board_webhook", methods=["POST"])
def board_webhook():
    """An update has been made on the board"""
    print("##### BOARD WEBHOOK TEST #####")
    response = request.get_json()
    print(response)
    return response["model"]["id"], 200
