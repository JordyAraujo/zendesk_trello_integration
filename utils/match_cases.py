from ..config import settings


def tag_by_priority(priority):
    match priority:
        case "Baixa":
            return settings.LABEL_ID_GREEN_DARK
        case "Normal":
            return settings.LABEL_ID_YELLOW_DARK
        case "Alta":
            return settings.LABEL_ID_ORANGE_DARK
        case "Urgente":
            return settings.LABEL_ID_RED_DARK
        case _:
            return None


def priority_by_tag_id(tag_id):
    match tag_id:
        case settings.LABEL_ID_GREEN_DARK:
            return "low"
        case settings.LABEL_ID_YELLOW_DARK:
            return "normal"
        case settings.LABEL_ID_ORANGE_DARK:
            return "high"
        case settings.LABEL_ID_RED_DARK:
            return "urgent"
        case _:
            return None


def tag_by_brand(brand):
    match brand:
        case "CDA Distribuidora":
            return settings.LABEL_ID_BLUE_DARK
        case "Docelandia":
            return settings.LABEL_ID_SKY_DARK
        case _:
            return None


def tag_by_category(category):
    match category:
        case "bi":
            return settings.LABEL_ID_PINK_DARK
        case "consinco":
            return settings.LABEL_ID_PURPLE_DARK
        case "pdv_ti":
            return settings.LABEL_ID_LIME_DARK
        case _:
            return None


def tag_by_department(department):
    match department:
        case "diretoria":
            return settings.LABEL_ID_BLACK_DARK
        case "docelandia":
            return settings.LABEL_ID_SKY_DARK
        case _:
            return None


def department_title(department):
    ret = None
    match department:
        case "administrativo":
            ret = "Administrativo"
        case "almoxarifado":
            ret = "Almoxarifado"
        case "caixa_pagador":
            ret = "Caixa Pagador"
        case "comercial":
            ret = "Comercial"
        case "contabilidade":
            ret = "Contabilidade"
        case "controladoria":
            ret = "Controladoria"
        case "credito_e_cobrança":
            ret = "Crédito e Cobrança"
        case "departamento_pessoal":
            ret = "Departamento Pessoal"
        case "diretoria":
            ret = "Diretoria"
        case "docelandia":
            ret = "Docelândia"
        case "faturamento":
            ret = "Faturamento"
        case "financeiro":
            ret = "Financeiro"
        case "logistica":
            ret = "Logística"
        case "portaria":
            ret = "Portaria"
        case "recepção":
            ret = "Recepção"
        case "recursos_humanos":
            ret = "Recursos Humanos"
        case "suporte_de_vendas":
            ret = "Suporte de Vendas"
        case "televendas":
            ret = "Televendas"
        case "tesouraria":
            ret = "Tesouraria"
        case "ti":
            ret = "TI"
        case "vendas_cda":
            ret = "Vendas"
        case _:
            ret = None
    return ret


def list_by_status(status):
    match status:
        case "Novo":
            return settings.NEW_CARDS_LIST_ID
        case "Aberto":
            return settings.NEW_CARDS_LIST_ID
        case "Pendente":
            return settings.PENDING_LIST_ID
        case "Em espera":
            return settings.HOLD_LIST_ID
        case "Resolvido":
            return settings.SOLVED_LIST_ID
        case _:
            return None


def status_by_list_id(list_id):
    match list_id:
        case settings.NEW_CARDS_LIST_ID:
            return "new"
        case settings.NEW_CARDS_LIST_ID:
            return "open"
        case settings.PENDING_LIST_ID:
            return "pending"
        case settings.HOLD_LIST_ID:
            return "hold"
        case settings.SOLVED_LIST_ID:
            return "solved"
        case _:
            return None
