import httpx

from ..config import settings
from .match_cases import (
    department_title,
    list_by_status,
    tag_by_brand,
    tag_by_category,
    tag_by_department,
    tag_by_priority,
)


def handle_card_creation(response):
    id_labels = []

    ticket_id = response.get("id", None)

    priority = response.get("priority", "Ticket sem prioridade")
    priority_tag = tag_by_priority(priority)
    if priority_tag:
        id_labels.append(priority_tag)

    brand = response.get("brand", "CDA Distribuidora")
    brand_tag = tag_by_brand(brand)
    if brand_tag:
        id_labels.append(brand_tag)

    category = response.get("category", "suporte_outros")
    category_tag = tag_by_category(category)
    if category_tag:
        id_labels.append(category_tag)

    department = response.get("department", "ti")
    department_tag = tag_by_department(department)
    if department_tag:
        id_labels.append(department_tag)

    url = response.get("url", "cdanatal.zendesk.com/agent/dashboard")
    subdescription = response.get("description", "Ticket sem descrição")
    ticket_type = response.get("ticket_type", "Tarefa")
    collaborator = response.get("user", "Usuário")
    tags = response.get("tags", "ti").replace(" ", ", ")

    description = create_description(
        url, subdescription, ticket_type, collaborator, department, tags
    )

    subject = response.get("title", "Ticket do Zendesk")
    title = "#" + ticket_id + " - " + subject

    return ticket_id, title, description, id_labels


def handle_card_update(response, ticket):
    id_labels = []

    custom_fields = ticket.custom_fields

    card_id_custom_field = filter_custom_field(
        ticket, settings.TRELLO_CARD_ID_CUSTOM_FIELD
    )
    card_id_custom_field_index = custom_fields.index(card_id_custom_field)

    card_id = ticket.custom_fields[card_id_custom_field_index]["value"]

    ticket_id = response.get("id", "-")

    status = response.get("status", "Aberto")
    id_list = list_by_status(status)

    last_zendesk_comment = response.get("last_comment", "Aberto")
    comments_url = f"https://api.trello.com/1/cards/{card_id}/actions"

    agent = response.get("agent", "Agente")

    try:
        headers = {"Accept": "application/json"}
        param = {
            "key": settings.TRELLO_KEY,
            "token": settings.TRELLO_TOKEN,
            "filter": "commentCard",
        }
        rsp = httpx.get(comments_url, headers=headers, params={**param})
        rsp.raise_for_status()
        comments = rsp.json()
    except httpx.HTTPStatusError as exc:
        comments = None
        print(exc)

    if not comments:
        last_trello_comment = None
    else:
        last_trello_comment = comments[0]["data"]["text"]

    if f"{last_zendesk_comment} - __{agent}__" != last_trello_comment:
        create_comment_url = (
            f"https://api.trello.com/1/cards/{card_id}/actions/comments"
        )
        try:
            headers = {"Accept": "application/json"}
            param = {
                "key": settings.TRELLO_KEY,
                "token": settings.TRELLO_TOKEN,
                "text": f"{last_zendesk_comment} - __{agent}__",
            }
            rsp = httpx.post(
                create_comment_url, headers=headers, params={**param}
            )
            rsp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            print(exc)

    priority = response.get("priority", "Ticket sem prioridade")
    priority_tag = tag_by_priority(priority)
    if priority_tag:
        id_labels.append(priority_tag)

    brand = response.get("brand", "CDA Distribuidora")
    brand_tag = tag_by_brand(brand)
    if brand_tag:
        id_labels.append(brand_tag)

    category = response.get("category", "suporte_outros")
    category_tag = tag_by_category(category)
    if category_tag:
        id_labels.append(category_tag)

    department = response.get("department", "ti")
    department_tag = tag_by_department(department)
    if department_tag:
        id_labels.append(department_tag)

    url = response.get("url", "cdanatal.zendesk.com/agent/dashboard")
    subdescription = response.get("description", "Ticket sem descrição")
    ticket_type = response.get("ticket_type", "Tarefa")

    tags = response.get("tags", "ti").replace(" ", ", ")

    description = create_description(
        url, subdescription, ticket_type, agent, department, tags
    )

    category = response.get("status", "status")

    update_url = f"https://api.trello.com/1/cards/{card_id}"
    id_labels_str = ",".join(id_labels)

    try:
        headers = {"Accept": "application/json"}
        param = {
            "key": settings.TRELLO_KEY,
            "token": settings.TRELLO_TOKEN,
            "desc": description,
            "pos": "top",
            "idLabels": id_labels_str,
            "idList": id_list,
        }
        rsp = httpx.put(update_url, headers=headers, params={**param})
        rsp.raise_for_status()
        update_data = rsp.json()
        response = {
            "status": rsp.status_code,
            "url": update_url,
            "data": update_data,
        }
    except httpx.HTTPStatusError as exc:
        print(
            f"status: {exc.response.status_code},"
            f"url: {update_url},"
            f"data: {exc}"
        )
        response = {
            "status": exc.response.status_code,
            "url": update_url,
            "data": [],
        }

    return ticket_id


def create_description(
    url, subdescription, ticket_type, collaborator, department, tags
):
    # Index variables
    date_beginning = subdescription.find(",") + 1
    date_end = find_nth_substring(subdescription, "\n\n", 2)
    department = department_title(department)

    insert_by = (
        " criado por "
        if ticket_type in ("Incidente", "Problema")
        else " criada por "
    )

    return (
        f"{url}\n\n{ticket_type}{insert_by}{collaborator} do setor "
        f"{department}, em {subdescription[date_beginning:date_end]}\n\n"
        f"---\n\n{subdescription[date_end+2:]}\n\nTags: "
        f"{tags}"
    )


def find_nth_substring(string, substring, occurrence):
    """Find the index for the nth ocurrence of a substring on a string"""
    if occurrence == 1:
        index = string.find(substring)
    else:
        index = string.find(
            substring,
            find_nth_substring(string, substring, occurrence - 1) + 1,
        )
    return index


def webhook_exists_for_board():
    exists = False
    url = f"https://api.trello.com/1/tokens/{settings.TRELLO_TOKEN}/webhooks"
    try:
        headers = {"Accept": "application/json"}
        param = {"key": settings.TRELLO_KEY, "token": settings.TRELLO_TOKEN}
        rsp = httpx.get(url, headers=headers, params={**param})
        rsp.raise_for_status()
        webhooks = rsp.json()
    except httpx.HTTPStatusError as exc:
        webhooks = None
        print(exc)

    if webhooks:
        for webhook in webhooks:
            if webhook["idModel"] == settings.BOARD_ID:
                exists = True
                break

    return exists


def initialize_webhook():
    if not webhook_exists_for_board():
        create_webhook_url = "https://api.trello.com/1/webhooks"
        try:
            headers = {"Accept": "application/json"}
            param = {
                "callbackURL": f"{settings.BASE_URL}/board_webhook",
                "idModel": settings.BOARD_ID,
                "key": settings.TRELLO_KEY,
                "token": settings.TRELLO_TOKEN,
            }
            rsp = httpx.post(
                create_webhook_url, headers=headers, params={**param}
            )
            rsp.raise_for_status()
            print(
                f"Webhook do Trello criado sucesso!!\n"
                f"- ID do Webhook: {rsp.json()['id']}"
            )
        except httpx.HTTPStatusError as exc:
            print(exc)


def filter_custom_field(ticket, custom_field):
    return list(
        filter(
            lambda field: field["id"] == int(custom_field),
            ticket.custom_fields,
        )
    )[0]
