import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from tqdm import tqdm
import os

def requestAds(seller_name, offset, limit):

    url = f"https://api.mercadolibre.com/sites/MLB/search?"

    params = {

        'nickname': seller_name,
        'sort': 'price_desc',
        'offset': offset,
        'limit': limit,

    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        
        data = response.json()
        return data['results']
    
    else:

        print("\nErro na chamada da API:", response.status_code)
        print("Mensagem de erro:", response.text)
        return []



def requestTotalItems(seller_name):

    url = f"https://api.mercadolibre.com/sites/MLB/search?"

    params = {
        'nickname': seller_name,
        'limit': 1
    }

    response = requests.get(url, params=params)

        
    data = response.json()
    return data['paging']['total']


def pagingLoop(seller_name):

    offset = 0
    limit = 50
    analysisDate = datetime.now().date().strftime("%d/%m/%Y")
    adsDataList = []

    total_items = requestTotalItems(seller_name)
    pbar = tqdm(total=total_items, desc='Extraindo Dados')

    while True:

        data = requestAds(seller_name, offset, limit)
        if data == [] or len(adsDataList) == total_items: break

        for item in data:

            if item not in adsDataList:
            
                ad = {}
                ad['ID'] = item['id']
                ad['Título'] = item['title']
                ad['Preço'] = item['price']

                if  item['listing_type_id'] == 'gold_pro': ad['Tipo'] = 'Premium'
                else: ad['Tipo'] = 'Clássico'

                ad['Vendas'] = item['sold_quantity']
                ad['Data de Criação'] = convertDate(item['stop_time'])
                ad['QTD Dias Ativo'] = calculateDateDifference(ad['Data de Criação'])

                if ad['QTD Dias Ativo'] != 0: ad['Vendas/Dias'] = ad['Vendas'] / ad['QTD Dias Ativo']
                else: ad['Vendas/Dias'] = ad['Vendas']

                ad['Link'] = item['permalink']
                ad['Data da Análise'] = analysisDate
                
                adsDataList.append(ad)
                pbar.update(1)

        offset += limit

    return adsDataList


def save_dicts_as_excel(dict_list, filename):

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


def clear():

    if os.name == 'nt':  # Windows
        os.system('cls')

    else: os.system('clear')


def main():

    clear()
    seller_name = input('Digite o nome do vendedor: ').upper()
    seller_data = pagingLoop(seller_name)

    if seller_data != []:

        filename = f'Anúncios - {seller_name}.xlsx'
        save_dicts_as_excel(seller_data, filename)
        print(f'\nDados salvos em {filename}\n')

    else: print('\nERRO: Dados não encontrados, verifique o nome do vendedor e a conexão')

    time.sleep(3)
    main()


if __name__ == '__main__':

    main()
