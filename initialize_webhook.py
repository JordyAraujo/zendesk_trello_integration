import httpx
from flask_loguru import logger

from config import settings


def initialize_webhook():
    url = f"https://api.trello.com/1/tokens/{settings.TRELLO_TOKEN}/webhooks"
    try:
        headers = {"Accept": "application/json"}
        param = {"key": settings.TRELLO_KEY, "token": settings.TRELLO_TOKEN}
        rsp = httpx.get(url, headers=headers, params={**param})
        rsp.raise_for_status()
        webhooks = rsp.json()
    except httpx.HTTPStatusError as exc:
        webhooks = None
        logger.error(exc)

    if webhooks:
        for webhook in webhooks:
            if webhook["idModel"] == settings.BOARD_ID:
                if not is_webhook_updated(webhook):
                    delete_webhook(webhook["id"])
                break

    create_webhook()


def delete_webhook(webhook_id):
    delete_webhook_url = (
        f"https://api.trello.com/1/tokens/"
        f"{settings.TRELLO_TOKEN}/webhooks/{webhook_id}"
    )
    try:
        param = {"key": settings.TRELLO_KEY, "token": settings.TRELLO_TOKEN}

        rsp = httpx.delete(delete_webhook_url, params={**param})
        rsp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(exc)


def is_webhook_updated(webhook):
    return webhook["callbackURL"] == f"{settings.BASE_URL}/board_webhook"


def create_webhook():
    import requests
    import json

    url = f"https://api.trello.com/1/tokens/{settings.TRELLO_TOKEN}/webhooks"

    headers = {"Accept": "application/json"}

    query = {
        "callbackURL": f"{settings.BASE_URL}/board_webhook",
        "idModel": settings.BOARD_ID,
        "key": settings.TRELLO_KEY,
        "token": settings.TRELLO_TOKEN,
    }

    response = requests.request("POST", url, headers=headers, params=query)

    return_json = json.dumps(
            json.loads(response.text),
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
        )

    logger.info(
        f"Webhook created successfully:\n {return_json}"
    )


initialize_webhook()
