"""
Integration between Zendesk and Trello. The main purpose here is to automatize
the workflow between the platforms.
"""
import requests
from flask import Flask, request

from config import settings
# from utils import dicts

app = Flask(__name__)

@app.route("/new_ticket", methods=["POST"])
def new_ticket():
    """A new Zendesk Ticket has been created"""
    response = request.get_json()
    create_card(
        response["ticket"]["title"],
        response["ticket"]["description"],
        response["ticket"]["url"]
    )
    return "ok", 200


def create_card(title, description, url):
    """Create a new Trello card"""
    params = {
        "name": title,
        "desc": f"{url}\n\n{description}",
        "pos": "top",
        "idList": settings.LISTS_IDS[0],
        "key": settings.TRELLO_KEY,
        "token": settings.TRELLO_TOKEN,
    }
    requests.request("POST", settings.CREATE_CARD, params=params)
    return "ok", 200
