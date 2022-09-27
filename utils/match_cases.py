from ..config import settings

def tag_by_priority(priority):
    match priority:
        case 'Baixa':
            return settings.LABEL_ID_GREEN_DARK
        case 'Normal':
            return settings.LABEL_ID_YELLOW_DARK
        case 'Alta':
            return settings.LABEL_ID_ORANGE_DARK
        case 'Urgente':
            return settings.LABEL_ID_RED_DARK
        case _:
            return None

def tag_by_brand(brand):
    match brand:
        case 'CDA Distribuidora':
            return settings.LABEL_ID_BLUE_DARK
        case 'Docelandia':
            return settings.LABEL_ID_SKY_DARK
        case _:
            return None

def tag_by_category(category):
    match category:
        case 'pdv_ti':
            return settings.LABEL_ID_LIME_DARK
        case 'bi':
            return settings.LABEL_ID_PINK_DARK
        case _:
            return None

def tag_by_department(department):
    match department:
        case 'diretoria':
            return settings.LABEL_ID_BLACK_DARK
        case 'docelandia':
            return settings.LABEL_ID_SKY_DARK
        case _:
            return None

def department_title(department):
    match department:
        case 'administrativo':
            return 'Administrativo'
        case 'almoxarifado':
            return 'Almoxarifado'
        case 'caixa_pagador':
            return 'Caixa Pagador'
        case 'comercial':
            return 'Comercial'
        case 'contabilidade':
            return 'Contabilidade'
        case 'controladoria':
            return 'Controladoria'
        case 'credito_e_cobrança':
            return 'Crédito e Cobrança'
        case 'departamento_pessoal':
            return 'Departamento Pessoal'
        case 'diretoria':
            return 'Diretoria'
        case 'docelandia':
            return 'Docelândia'
        case 'faturamento':
            return 'Faturamento'
        case 'financeiro':
            return 'Financeiro'
        case 'logistica':
            return 'Logística'
        case 'portaria':
            return 'Portaria'
        case 'recepção':
            return 'Recepção'
        case 'recursos_humanos':
            return 'Recursos Humanos'
        case 'suporte_de_vendas':
            return 'Suporte de Vendas'
        case 'televendas':
            return 'Televendas'
        case 'tesouraria':
            return 'Tesouraria'
        case 'ti':
            return 'TI'
        case 'vendas_cda':
            return 'Vendas'
        case _:
            return None
