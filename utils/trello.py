import httpx

from .match_cases import tag_by_priority, tag_by_brand, tag_by_category, tag_by_department, department_title, list_by_status
from ..config import settings

def handle_card_creation(response):
    id_labels = []

    ticket_id = response.get("id", None)

    priority = response.get("priority", "Ticket sem prioridade")
    id_labels.append(tag_by_priority(priority))

    brand = response.get("brand", "CDA Distribuidora")
    id_labels.append(tag_by_brand(brand))

    category = response.get("category", "suporte_outros")
    id_labels.append(tag_by_category(category))

    department = response.get("department", "ti")
    id_labels.append(tag_by_department(department))

    url = response.get("url", "cdanatal.zendesk.com/agent/dashboard")
    subdescription = response.get("description", "Ticket sem descrição")
    ticket_type = response.get("ticket_type", "Tarefa")
    collaborator = response.get("user", "Usuário")
    tags = response.get("tags", "ti").replace(" ", ", ")

    description = create_description(url, subdescription, ticket_type, collaborator, department, tags)

    subject = response.get("title", "Ticket do Zendesk")
    title = "#" + ticket_id + " - " + subject

    return ticket_id, title, description, id_labels


def handle_card_update(response, ticket):
    id_labels = []

    custom_fields = ticket.custom_fields

    custom_field = list(filter(lambda field: field["id"] == int(settings.TRELLO_CARD_CUSTOM_FIELD), ticket.custom_fields))[0]
    custom_field_index = custom_fields.index(custom_field)

    card_id = ticket.custom_fields[custom_field_index]["value"]

    ticket_id = response.get("id", "-")

    status = response.get("status", "Aberto")
    id_list = list_by_status(status)

    last_zendesk_comment = response.get("last_comment", "Aberto")
    comments_url = f"https://api.trello.com/1/cards/{card_id}/actions"

    try:
        headers = {"Accept": "application/json"}
        param = {
            "key": settings.TRELLO_KEY,
            "token": settings.TRELLO_TOKEN,
            "filter": "commentCard"
        }
        rsp = httpx.get(comments_url, headers=headers, params={**param})
        rsp.raise_for_status()
        comments = rsp.json()
    except httpx.HTTPStatusError as exc:
        comments = {}

    last_trello_comment = comments[-1]["data"]["text"]
    last_trello_comment_author = comments[-1]["memberCreator"]["fullName"]

    if last_zendesk_comment != f'----------------------------------------------\n\n{last_trello_comment}':
        create_comment_url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
        try:
            headers = {"Accept": "application/json"}
            param = {
                "key": settings.TRELLO_KEY,
                "token": settings.TRELLO_TOKEN,
                "text": last_zendesk_comment
            }
            rsp = httpx.post(create_comment_url, headers=headers, params={**param})
            rsp.raise_for_status()
            new_comment = rsp.json()
        except httpx.HTTPStatusError as exc:
            new_comment = {}

    priority = response.get("priority", "Ticket sem prioridade")
    id_labels.append(tag_by_priority(priority))

    brand = response.get("brand", "CDA Distribuidora")
    id_labels.append(tag_by_brand(brand))

    category = response.get("category", "suporte_outros")
    id_labels.append(tag_by_category(category))

    department = response.get("department", "ti")
    id_labels.append(tag_by_department(department))

    url = response.get("url", "cdanatal.zendesk.com/agent/dashboard")
    subdescription = response.get("description", "Ticket sem descrição")
    ticket_type = response.get("ticket_type", "Tarefa")
    collaborator = response.get("user", "Usuário")
    tags = response.get("tags", "ti").replace(" ", ", ")

    description = create_description(url, subdescription, ticket_type, collaborator, department, tags)

    subject = response.get("title", "Ticket do Zendesk")
    title = "#" + ticket_id + " - " + subject

    category = response.get("status", "status")

    update_url = f"https://api.trello.com/1/cards/{card_id}"

    try:
        headers = {"Accept": "application/json"}
        param = {
            "key": settings.TRELLO_KEY,
            "token": settings.TRELLO_TOKEN,
            "name": title,
            "desc": description,
            "pos": "top",
            "idLabels": id_labels,
            "idList": id_list
        }
        response = httpx.put(update_url, headers=headers, params={**param})
        response.raise_for_status()
        response = {
            "status": response.status_code,
            "url": update_url,
            "data": response.json(),
        }
    except httpx.HTTPStatusError as exc:
        response = {"status": exc.response.status_code, "url": update_url, "data": []}

    return ticket_id # title, description, id_labels


def create_description(url, subdescription, ticket_type, collaborator, department, tags):
    # Index variables
    date_beginning = subdescription.find(",") + 1
    date_end = find_nth_substring(subdescription, "\n\n", 2)
    department = department_title(department)

    return (
        f"{url}\n\n{ticket_type} colaborador(a): {collaborator} do setor {department}, em "
        f"{subdescription[date_beginning:date_end]}\n\n---\n\n"
        f"{subdescription[date_end+2:]}\n\nTags: "
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
