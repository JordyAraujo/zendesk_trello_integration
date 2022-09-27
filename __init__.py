"""
Integration between Zendesk and Trello. The main purpose here is to automatize
the workflow between the platforms.
"""
import requests
from ..TrelloApi.trelloapi import Trello
from flask import Flask, request
from .utils.trello import handle_card

from .config import settings

app = Flask(__name__)

trello = Trello(settings.TRELLO_KEY, settings.TRELLO_TOKEN)
list = trello.card_list('62c991d6b4fec53835cd8d62')

@app.route("/new_ticket", methods=["POST"])
def new_ticket():
    """A new Zendesk Ticket has been created"""
    response = request.get_json()
    title, description, label_ids = handle_card(response)
    card_id, response_status_code = list.create_card(
        title,
        description,
        label_ids
    )
    print(f'Novo Ticket criado no Zendesk!\nid: {card_id} - Título: {title} - Código HTTP: {response_status_code}')
    return card_id, response_status_code
