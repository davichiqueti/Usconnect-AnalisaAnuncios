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

    url = f"https://api.mercadolibre.com/sites/MLB/search?"

    params = {
        'nickname': seller_name,
        'sort': sort,
        'offset': offset,
        'limit': limit,
    }

    if filter and'internacional' in filter:
        params['shipping_origin'] = 10215069
    
    if filter and 'best_sellers' in filter:
        params['power_seller'] = 'yes'

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:

        print("\nErro na chamada da API:", response.status_code)
        print("Mensagem de erro:", response.text)
        return []


def requestAdsByProduct(search_query, sort, offset, limit, filter):

    url = f"https://api.mercadolibre.com/sites/MLB/search?"

    params = {
        'q' : search_query,
        'sort': sort,
        'offset': offset,
        'limit': limit,
    }

    if filter and'internacional' in filter:
        params['shipping_origin'] = 10215069
    
    if filter and 'best_sellers' in filter:
        params['power_seller'] = 'yes'

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['results']
    
    else:
        print("\nErro na chamada da API:", response.status_code)
        print("Mensagem de erro:", response.text)


def requestTotalItems(search_query, is_seller_search=True, filter = None):

    if is_seller_search:
        url = f"https://api.mercadolibre.com/sites/MLB/search?"
        params = {'nickname': search_query}

    else:
        url = f"https://api.mercadolibre.com/sites/MLB/search?"
        params = {'q' : search_query}

    params['limit'] = 1

    if filter and'internacional' in filter:
        params['shipping_origin'] = 10215069
    
    if filter and 'best_sellers' in filter:
        params['power_seller'] = 'yes'

    response = requests.get(url, params=params)

    data = response.json()

    return data['paging']['total']


def pagingLoop(search_query, sort, is_seller_search=True, filter = None):

    offset = 0
    limit = 50
    analysisDate = datetime.now().date().strftime("%d/%m/%Y")
    adsDataList = []

    if is_seller_search:
        total_items = requestTotalItems(search_query, is_seller_search=True, filter = filter)
        
    else:
        total_items = requestTotalItems(search_query, is_seller_search=False, filter = filter)

    pbar = tqdm(total=total_items, desc='Extraindo Dados')

    while True:

        if is_seller_search:
            data = requestAdsBySeller(search_query, sort, offset, limit, filter)

        else:
            data = requestAdsByProduct(search_query, sort, offset, limit, filter)

        if not data or len(adsDataList) == total_items:
            
            pbar.close()
            break

        for item in data:
            if item not in adsDataList:

                ad = {}
                ad['ID'] = item['id']
                ad['Título'] = item['title']
                ad['Preço'] = item['price']

                if item['listing_type_id'] == 'gold_pro':
                    ad['Tipo'] = 'Premium'

                else:
                    ad['Tipo'] = 'Clássico'

                ad['Vendas'] = item['sold_quantity']
                ad['Data de Criação'] = convertDate(item['stop_time'])
                ad['QTD Dias Ativo'] = calculateDateDifference(ad['Data de Criação'])

                if ad['QTD Dias Ativo'] != 0:
                    ad['Vendas/Dias'] = ad['Vendas'] / ad['QTD Dias Ativo']
    
                else:
                    ad['Vendas/Dias'] = 0

                ad['Envio'] = item['shipping']['logistic_type'].replace('xd_drop_off', 'normal').replace('drop_off', 'normal')

                if not is_seller_search:
                    ad['Vendedor'] = item["seller"]["nickname"]
                    ad['Origem'] = item['address']['state_id']

                ad['Link'] = item['permalink']
                ad['Data da Análise'] = analysisDate

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
                old_number = match.group(1)
                new_number = str(i)
                filename = re.sub(r'\(\d+\)', f'({new_number})', filename)
            else:
                filename = f'{filename} ({i})'
            i += 1
    
            print(f"\nO arquivo '{filename}' já existe. O nome será alterado para '{filename}'")
            
    df = pd.DataFrame(dict_list)
    df.to_excel(f"{filename}.xlsx", index=False)
    print(f"\nDados salvos em '{filename}.xlsx'\n")


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
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:
        os.system('clear')


def exibir_mensagem_de_ajuda():
    # Mensagem de ajuda
    print("""
Opções disponíveis:

  -v <nome do vendedor>   : Especifica que a pesquisa será pelo nome do vendedor e recebe o nome.

  -i <nome do item>       : Especifica que a pesquisa será pelo nome do item e recebe o nome do item.

  -o <ordenação>          : Especifica o método de ordenação dos resultados: price_asc, price_desc, relevance.
                            O padrão é price_desc.

  -n <nome do arquivo>    : Especifica o nome do arquivo .xlsx. O padrão é "Anuncios - <nome do vendedor/item> - <metodo de ordenação>".

  -h                      : Exibe esta mensagem de ajuda.

  
Argumentos que contém espaço devem ser passados com aspas

Exemplos de uso:

  usco-AnalisaAnuncios -i "Iphone 7"
  usco-AnalisaAnuncios -v João -o price_asc
  usco-AnalisaAnuncios -i Celular -n "Meus Anúncios" -o relevance
  """)


def main(args):

    clear()

    parser = argparse.ArgumentParser(description='Usconnect Analisa Anuncios')

    parser.add_argument('-v', '--vendedor', help='Especifica o nome do vendedor')
    parser.add_argument('-i', '--item', help='Especifica o nome do item')
    parser.add_argument('-o', '--ordenação', choices=['price_asc', 'price_desc', 'relevance'], default='price_desc',
                        help='Especifica a ordenação dos resultados')
    parser.add_argument('-n', '--nome_arquivo', help='Especifica o nome do arquivo')
    parser.add_argument('-f', '--filtro', nargs='*', metavar=('filter_1', 'filter_2'), choices=['power_seller', 'internacional'], help='Especifica um filtro para a pesquisa')


    args = parser.parse_args(args)

    # Aqui definimos as variáveis seller_name, item_name, sort e output_filename com base nos argumentos fornecidos
    seller_name = args.vendedor
    item_name = args.item
    sort = args.ordenação
    output_filename = args.nome_arquivo
    filter = args.filtro
    
    if '-h' in args or '--help' in args:
        exibir_mensagem_de_ajuda()
        return

    if seller_name:
        adsDataList = pagingLoop(seller_name, sort, is_seller_search=True, filter = filter)

    elif item_name:
        adsDataList = pagingLoop(item_name, sort, is_seller_search=False, filter = filter)

    else: 
        print("""
Você deve especificar o nome do vendedor (-v USCONNECT) ou do item (-i "Iphone 7")
            
Comando usco-AnalisaAnuncios -h para mais informações
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
