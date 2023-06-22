import gui
import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def requestAds(seller_name, limit, offset):

    url = f"https://api.mercadolibre.com/sites/MLB/search?"

    params = {
        'nickname': seller_name,
        'sort': 'price_asc',
        'offset': offset,
        'limit': limit
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        print("Erro na chamada da API:", response.status_code)
        print("Mensagem de erro:", response.text)
        return []


def pagingLoop(seller_name):

    offset = 0
    limit = 50
    analysisDate = datetime.now().date().strftime("%d/%m/%Y")
    adList = []

    while True:

        data = requestAds(seller_name, limit, offset)
        if data == []: break
        for item in data:

            ad = {}
            ad['ID'] = item['id']
            ad['Título'] = item['title']
            ad['Preço'] = float(item['price'])
            if  item['listing_type_id'] == 'gold_pro': ad['Tipo'] = 'Premium'
            else: ad['Tipo'] = 'Clássico'
            ad['Vendas'] = item['sold_quantity']
            ad['Data de Criação'] = convertDate(item['stop_time'])
            ad['QTD Dias Ativo'] = calculateDateDifference(ad['Data de Criação'])
            ad['Vendas/Dias'] = ad['Vendas'] / ad['QTD Dias Ativo']
            ad['Link'] = item['permalink']
            ad['Data da Análise'] = analysisDate
            
            adList.append(ad)

        offset += limit

    return adList


def save_dicts_as_excel(dict_list, column_names, filename):

    df = pd.DataFrame(dict_list)
    df.to_excel(filename, index=False)


def convertDate(date):

    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    corrected_date = date_obj - relativedelta(years=20) + timedelta(days=5)
    formated_date = corrected_date.strftime("%d/%m/%Y")

    return formated_date



def calculateDateDifference(date):

    current_date = datetime.now().date()
    date_obj = datetime.strptime(date, "%d/%m/%Y").date()
    difference = (current_date - date_obj).days
    return difference


def main():

    seller_name = gui.getNickName()
    seller_data = pagingLoop(seller_name)
    filename = f'Anuncios-{seller_name}.xlsx'
    column_names = ['ID', 'Título', 'Preço', 'Tipo', 'Vendas', 'Data de Criação', 'QTD Dias Ativo', 'Vendas/Dias', 'Link', 'Data da Análise']
    if seller_name != None:
        
        save_dicts_as_excel(seller_data, column_names, filename)
        gui.savedPopup(filename)

if __name__ == '__main__':
    main()