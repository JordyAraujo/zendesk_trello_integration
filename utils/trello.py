from .match_cases import tag_by_priority, tag_by_brand, tag_by_category, tag_by_department, department_title

def handle_card(response):
    label_ids = []

    ticket_id = response.get("id", "-")

    priority = response.get("priority", "Ticket sem prioridade")
    label_ids.append(tag_by_priority(priority))

    brand = response.get("brand", "CDA Distribuidora")
    label_ids.append(tag_by_brand(brand))

    category = response.get("category", "suporte_outros")
    label_ids.append(tag_by_category(category))

    department = response.get("department", "ti")
    label_ids.append(tag_by_department(department))

    url = response.get("url", "cdanatal.zendesk.com/agent/dashboard")
    subdescription = response.get("description", "Ticket sem descrição")
    ticket_type = response.get("ticket_type", "Tarefa")
    creator = response.get("user", "Usuário")
    tags = response.get("tags", "ti").replace(" ", ", ")

    description = create_description(url, subdescription, ticket_type, creator, department, tags)

    subject = response.get("title", "Ticket do Zendesk")
    title = "#" + ticket_id + " - " + subject

    return title, description, label_ids

def create_description(url, subdescription, ticket_type, creator, department, tags):
    # Index variables
    date_beginning = subdescription.find(",") + 1
    date_end = find_nth_substring(subdescription, "\n\n", 2)
    department = department_title(department)

    # String variables
    insert_by = (
        " criado por: "
        if ticket_type in ("Incidente", "Problema")
        else " criada por: "
    )

    return (
        f"{url}\n\n{ticket_type}{insert_by}{creator} do setor {department}, em "
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
