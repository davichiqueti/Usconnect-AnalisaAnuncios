import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import os
import sys
import re
import argparse


def requestAdsBySeller(seller_name, sort, offset, limit, filter):
    # Function to scrape data from the website by a seller name
    url = f"https://api.mercadolibre.com/sites/MLB/search?"
    params = {
        'nickname': seller_name,
        'sort': sort,
        'offset': offset,
        'limit': limit,
    }
    # Adding filters ID to the query
    if filter and 'internacional' in filter: params['shipping_origin'] = 10215069
    

    if filter and 'best_sellers' in filter: params['power_seller'] = 'yes'

    response = requests.get(url, params=params)

    if response.status_code == 200: return response.json()['results']
    
    else:

        print("\nAPI ERROR:", response.status_code)
        print("Erro ao extrair os anúncios:", response.text)



def requestAdsByProduct(search_query, sort, offset, limit, filter):
    #Function to scrape data from the website by a item name
    url = f"https://api.mercadolibre.com/sites/MLB/search?"
    params = {
        'q' : search_query,
        'sort': sort,
        'offset': offset,
        'limit': limit,
    }
    #Adding filters ID in the query
    if filter and'internacional' in filter: params['shipping_origin'] = 10215069
    

    if filter and 'best_sellers' in filter: params['power_seller'] = 'yes'

    response = requests.get(url, params=params)

    if response.status_code == 200: return response.json()['results']
    
    else:

        print("\nAPI ERROR:", response.status_code)
        print("Erro ao extrair os anúncios:", response.text)



def requestTotalItems(search_query, is_seller_search=True, filter = None):
    # Function to scrape the total quantity of ads
    params ={}
    params['limit'] = 1

    if is_seller_search:
        # Scrapes total quantity by seller name
        url = f"https://api.mercadolibre.com/sites/MLB/search?"
        params = {'nickname': search_query}

    else:
        # Scrapes total quantity by item name
        url = f"https://api.mercadolibre.com/sites/MLB/search?"
        params = {'q' : search_query}


    if filter and'internacional' in filter:
        # Add filter ID in the query
        params['shipping_origin'] = 10215069
    
    if filter and 'best_sellers' in filter:
        # Add filter ID in the query
        params['power_seller'] = 'yes'


    response = requests.get(url, params=params)
    data = response.json()

    return data['paging']['total']


def getVisits(ad_id):
    
    url = f'https://api.mercadolibre.com/visits/items?ids={ad_id}'

    try:

        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200: return data[ad_id]

        elif response.status_code == 429: return getVisits(ad_id)

        else:

            print("\nAPI ERROR:", response.status_code)
            print("Erro ao extrair as visitas:", response.text)

    except requests.exceptions.ConnectTimeout as e: print("\nErro de tempo limite de conexão:", e)

    except requests.exceptions.RequestException as e: print("\nErro de requisição:", e)



def pagingLoop(search_query, sort, is_seller_search=True, filter = None):
    # Calls the right extraction function by the search type and loops it until extracts all data
    offset = 0
    limit = 50
    analysisDate = datetime.now().date().strftime("%d/%m/%Y")
    adsDataList = []
    total_items = requestTotalItems(search_query, is_seller_search=True, filter = filter) if is_seller_search else requestTotalItems(search_query, is_seller_search=False, filter = filter)
    pbar = tqdm(total=total_items, desc='Extraindo Dados') # Create a progress bar using tqdm library

    while True:
        # Ternary operator to call the right function to get data
        data = requestAdsBySeller(search_query, sort, offset, limit, filter) if is_seller_search else requestAdsByProduct(search_query, sort, offset, limit, filter)

        if not data or len(adsDataList) == total_items:
            
            pbar.close()
            break

        for item in data:
            
            creation_date = convertDate(item['stop_time'])
            days_active = calculateDateDifference(creation_date)
            sales = item['sold_quantity']
            sales_per_day = sales / days_active if days_active != 0 else 0
            visits = getVisits(item['id'])
            ad = {
                'ID' : item['id'],
                'Título' : item['title'],
                'Preço' : item['price'],
                'Tipo' : 'Premium' if item['listing_type_id'] == 'gold_pro' else 'Clássico',
                'Vendas' : sales,
                'Visitas' : visits,
                'Conversão' : sales / visits if item['sold_quantity'] != 0 else 0,
                'Data de Criação' : creation_date,
                'QTD Dias Ativo' : days_active,
                'Vendas/Dias' : sales_per_day,
                'Envio' : 'Normal' if item['shipping']['logistic_type'] != 'fulfillment' else 'Normal',
                'Vendedor' : item["seller"]["nickname"] if not is_seller_search else None,
                'Origem' : item['address']['state_id'] if not is_seller_search else None,
                'Link': item['permalink'],
                'Data da Análise' : analysisDate
            }
            adsDataList.append(ad)
            pbar.update(1)

        offset += limit

    return adsDataList


def saveDictsAsExcel(dict_list, filename):

    if os.path.exists(f"{filename}.xlsx"):

        i = 2

        while os.path.exists(f"{filename}.xlsx"):

            match = re.search(r'\((\d+)\)', filename)

            if match: 

                new_number = str(i)
                filename = re.sub(r'\(\d+\)', f'({new_number})', filename)

            else: filename = f'{filename} ({i})'

            i += 1
    
            print(f"\nO arquivo '{filename}' já existe. O nome será alterado para '{filename}'")
            
    df = pd.DataFrame(dict_list)
    df.to_excel(f"{filename}.xlsx", index=False)

    return f"\nDados salvos em '{filename}.xlsx'\n"


def convertDate(date):

    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    corrected_date = date_obj - relativedelta(years=20) + timedelta(days=5)
    formatted_date = corrected_date.strftime("%d/%m/%Y")

    return formatted_date


def calculateDateDifference(date):

    current_date = datetime.now().date()
    date_obj = datetime.strptime(date, "%d/%m/%Y").date()
    difference = (current_date - date_obj).days

    return difference


def clear():
    
    if os.name == 'nt': os.system('cls') #Windows

    else: os.system('clear')



def main(args):

    clear()

    parser = argparse.ArgumentParser(description='USconnect Analisa Anuncios - Este programa permite analisar anúncios por vendedor ou item.')

    parser.add_argument('-v', '--vendedor')
    parser.add_argument('-i', '--item')
    parser.add_argument('-o', '--ordenacao', choices=['price_asc', 'price_desc', 'relevance'], default='price_desc',)
    parser.add_argument('-n', '--nome_arquivo')
    parser.add_argument('-f', '--filtro', nargs='*', metavar=('filter_1', 'filter_2'), choices=['power_seller', 'internacional'])

    parser.usage = "USconnect Analisa Anuncios - modo de uso: [-v [Vendedor] ou -i [Item]] -o [Ordenação] -n [Nome do Arquivo] -f [Filtro]"
    args = parser.parse_args(args)

    # Aqui definimos as variáveis seller_name, item_name, sort e output_filename com base nos argumentos fornecidos
    seller_name = args.vendedor
    item_name = args.item
    sort = args.ordenacao
    output_filename = args.nome_arquivo
    filter = args.filtro

    if seller_name:
        adsDataList = pagingLoop(seller_name, sort, is_seller_search=True, filter = filter)

    elif item_name:
        adsDataList = pagingLoop(item_name, sort, is_seller_search=False, filter = filter)

    else: 
        print("""
Você deve especificar o nome do vendedor (-v USCONNECT) ou do item (-i "Iphone 7")
            
Comando -h ou --help para mais informações
        """)
        return

    if not output_filename:

        if seller_name:
            output_filename = f"Anuncios - {seller_name} - {sort}"
        elif item_name:
            output_filename = f"Anuncios - {item_name} - {sort}"


    if adsDataList: 
        saveDictsAsExcel(adsDataList, output_filename)

    else:
        print("Nenhum dado foi encontrado. Verifique o nome do vendedor ou item")


if __name__ == '__main__':

    main(sys.argv[1:])