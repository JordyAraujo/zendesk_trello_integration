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
            return "62c991d6b4fec53835cd8d62"
        case "Aberto":
            return "62c991d6b4fec53835cd8d62"
        case "Pendente":
            return "62ed2c7f187ade7138779186"
        case "Em espera":
            return "62ed2c846ab25f5f84a20ae9"
        case "Resolvido":
            return "62ed2ce97ac1e65ed9a9d114"
        case _:
            return None


def status_by_list_id(list_id):
    match list_id:
        case "62c991d6b4fec53835cd8d62":
            return "Novo"
        case "62c991d6b4fec53835cd8d62":
            return "Aberto"
        case "62ed2c7f187ade7138779186":
            return "Pendente"
        case "62ed2c846ab25f5f84a20ae9":
            return "Em espera"
        case "62ed2ce97ac1e65ed9a9d114":
            return "Resolvido"
        case _:
            return None
