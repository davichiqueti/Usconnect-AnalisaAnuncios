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
    # Requisição para extrair os dados a partir do nome de um vendedor
    url = f"https://api.mercadolibre.com/sites/MLB/search?"
    params = {
        'nickname': seller_name,
        'sort': sort,
        'offset': offset,
        'limit': limit,
    }

    if filter and ('internacional' in filter):
        # Adiciona o filtro de venda internacional pelo ID
        params['shipping_origin'] = 10215069
    
    if filter and ('best_sellers' in filter): 
        # Adiciona o filtro de melhores vendedores
        params['power_seller'] = 'yes'


    try: 
        # Tentativa de realizar a requisição
        response = requests.get(url, params=params)
        data = response.json()

        return data['results']
    
    except requests.exceptions.ConnectTimeout as e: 

        print("\nErro de tempo limite de conexão:", e)

    except requests.exceptions.RequestException as e: 
        
        print("\nErro de requisição:", e)




def requestAdsByProduct(search_query, sort, offset, limit, filter):
    # Requisição para extrair os dados a partir do nome de um produto
    url = f"https://api.mercadolibre.com/sites/MLB/search?"
    params = {
        'q' : search_query,
        'sort': sort,
        'offset': offset,
        'limit': limit,
    }

    if filter and ('internacional' in filter):
        # Adiciona o filtro de venda internacional pelo ID
        params['shipping_origin'] = 10215069
    
    if filter and ('best_sellers' in filter): 
        # Adiciona o filtro de melhores vendedores
        params['power_seller'] = 'yes'


    try: 
        # Tentativa de realizar a requisição
        response = requests.get(url, params=params)
        data = response.json()

        return data['results']
    
    except requests.exceptions.ConnectTimeout as e: 

        print("\nErro de tempo limite de conexão:", e)

    except requests.exceptions.RequestException as e: 
        
        print("\nErro de requisição:", e)



def requestTotalItems(search_query, is_seller_search=True, filter = None):
    # Função para extrair a quantidade total de anúncios
    params = {}
    params['limit'] = 1

    if is_seller_search:
        # Extrai a quantidade de anúncios do vendedor
        url = f"https://api.mercadolibre.com/sites/MLB/search?"
        params = {'nickname': search_query}

    else:
        # Extrai a quantidade de anúncios do produto
        url = f"https://api.mercadolibre.com/sites/MLB/search?"
        params = {'q' : search_query}


    if filter and ('internacional' in filter):
        # Aciona o filtro de venda internacional pelo ID
        params['shipping_origin'] = 10215069
    

    if filter and ('best_sellers' in filter):
        # Aciona o filtro de melhores vendedores
        params['power_seller'] = 'yes'


    try: 
        # Tentativa de realizar a requisição
        response = requests.get(url, params=params)
        data = response.json()

        return data['paging']['total']
    
    except requests.exceptions.ConnectTimeout as e: 

        print("\nErro de tempo limite de conexão:", e)

    except requests.exceptions.RequestException as e: 
        
        print("\nErro de requisição:", e)



def getVisits(ad_id):
    # Request para extrair o número de visitas de um anúncio
    url = f'https://api.mercadolibre.com/visits/items?ids={ad_id}'
    response = requests.get(url)
    data = response.json()
        
    if response.status_code == 200: return data[ad_id]

    elif response.status_code == 429: return getVisits(ad_id) # Recursividade para forçar resposta da API

    else:

        print("\nAPI ERROR:", response.status_code)
        print("Erro ao extrair as visitas:", response.text)



def pagingLoop(search_query, sort, is_seller_search=True, filter = None):
    # Looping realizar a paginação considerando um limite de 50 anúncios por requisição
    offset = 0 # Ponto Inicial
    limit = 50
    analysisDate = datetime.now().date().strftime("%d/%m/%Y")
    adsDataList = []
    # Operador ternário para associar a variavel "total_items" ao retorno da função correta
    total_items = requestTotalItems(search_query, is_seller_search=True, filter = filter) if is_seller_search else requestTotalItems(search_query, is_seller_search=False, filter = filter)
    pbar = tqdm(total=total_items, desc='Extraindo Dados') # Cria uma barra de progresso

    while True:
        # Operador ternário para associar a variavel "data" ao retorno da função correta
        data = requestAdsBySeller(search_query, sort, offset, limit, filter) if is_seller_search else requestAdsByProduct(search_query, sort, offset, limit, filter)

        if not data or len(adsDataList) == total_items:
            # Finaliza o loop caso não haja dados ou se foram extraídos todos os dados
            break

        for item in data:
            # Tratando dados de cada anúncio da resposta
            creation_date = convertDate(item['stop_time']) # Conversão da data de criação
            days_active = calculateDateDifference(creation_date)# Calcula a quantidade de dias desde a criação do anúncio
            sales = item['sold_quantity']
            sales_per_day = sales / days_active if days_active != 0 else 0 # Operador ternário para evitar divisões por 0
            visits = getVisits(item['id']) # Chamada isolada para receber o número de visitas
            # Associação dos dados do anúncio em um dicionario
            ad = {
                'ID' : item['id'],
                'Título' : item['title'],
                'Preço' : item['price'],
                'Tipo' : 'Premium' if item['listing_type_id'] == 'gold_pro' else 'Clássico', # Tratamento de dados
                'Vendas' : sales,
                'Visitas' : visits,
                'Conversão' : sales / visits if item['sold_quantity'] != 0 else 0, # Operador ternário para evitar divisões por 0
                'Data de Criação' : creation_date,
                'QTD Dias Ativo' : days_active,
                'Vendas/Dias' : sales_per_day,
                'Envio' : 'Normal' if item['shipping']['logistic_type'] != 'fulfillment' else 'Normal', # Tratamento de dados
                'Link': item['permalink'],
                'Data da Análise' : analysisDate
            }

            if not is_seller_search: 
                
                ad['Vendedor']  = item["seller"]["nickname"]
                ad['Origem']    = item['address']['state_id']
            
            adsDataList.append(ad) # Adiciona os dicionários na lista de dados
            pbar.update(1) # Atualiza a barra de progresso

        offset += limit # Faz com que a proxima extração iniciei no final do limite atual

    return adsDataList


def saveDictsAsExcel(dict_list, filename):
    # Salva os dados em uma tabela Excel na pasta "Dados Extraídos"
    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, "Dados Extraídos")

    if not os.path.exists(target_directory): 
        
        os.makedirs(target_directory)
    
    full_filename = os.path.join(target_directory, f"{filename}.xlsx")

    if os.path.exists(full_filename): # Tratamento para arquivos já existentes

        i = 2

        while os.path.exists(f"{filename}.xlsx"):

            match = re.search(r'\((\d+)\)', filename)

            if match: 

                new_number = str(i)
                filename = re.sub(r'\(\d+\)', f'({new_number})', filename)

            else: 
                
                filename = f'{filename} ({i})'

        i += 1
        print(f"\nO arquivo '{filename}' já existe. O nome será alterado para '{filename}'")

    df = pd.DataFrame(dict_list) # Transforma a lista com os dicionários em um DataFrame Pandas
    df.to_excel(full_filename, index=True, columns=df.columns) # Salva os dados em um arquivo Excel

    print(f"\nDados salvos em 'Dados Extraídos\{filename}.xlsx'\n")


def convertDate(date):
    # Tratamento da "stop_date" para acessar a data de criação(Informação que não é disponibilizada pela API)
    date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    corrected_date = date_obj - relativedelta(years=20) + timedelta(days=5)
    formatted_date = corrected_date.strftime("%d/%m/%Y")

    return formatted_date


def calculateDateDifference(date):
    # Calcular os dias em que o anúncio está ativo
    current_date = datetime.now().date()
    date_obj = datetime.strptime(date, "%d/%m/%Y").date()
    difference = (current_date - date_obj).days

    return difference


def clear():
    # Limpar o prompt
    if os.name == 'nt':
        
        os.system('cls') # Comando Windows

    else: 
        
        os.system('clear') # Comando Mac e Linux



def main(args):

    clear()
    # Definição dos argumentos
    parser = argparse.ArgumentParser(description='USconnect Analisa Anuncios - Este programa permite analisar anúncios por vendedor ou item.')
    parser.add_argument('-v', '--vendedor')
    parser.add_argument('-i', '--item')
    parser.add_argument('-o', '--ordenacao', choices=['price_asc', 'price_desc', 'relevance'], default='price_desc',)
    parser.add_argument('-n', '--nome_arquivo')
    parser.add_argument('-f', '--filtro', nargs='*', metavar=('filter_1', 'filter_2'), choices=['power_seller', 'internacional'])
    parser.usage = "USconnect Analisa Anuncios - modo de uso: [-v [Vendedor] ou -i [Item]] -o [Ordenação] -n [Nome do Arquivo] -f [Filtro]"
    args = parser.parse_args(args)
    # Associação das variáveis seller_name, item_name, sort e output_filename com base nos argumentos fornecidos.
    seller_name = args.vendedor
    item_name = args.item
    sort = args.ordenacao
    output_filename = args.nome_arquivo
    filter = args.filtro

    if seller_name: # Chamada da função de extração na pesquisa por vendedor
        
        adsDataList = pagingLoop(seller_name, sort, is_seller_search=True, filter = filter)

    elif item_name: # Chamada da função de extração na pesquisa por item
        
        adsDataList = pagingLoop(item_name, sort, is_seller_search=False, filter = filter)

    else: # Tratando casos em que nenhum item ou produto é especificado

        print("""
                Você deve especificar o nome do vendedor (-v USCONNECT) ou do item (-i "Iphone 7")
            
                Comando -h ou --help para mais informações
        """)

        return


    if not output_filename: 
        # Defininindo o nome do arquivo conforme o tipo de pesquisa com operador ternário
        output_filename = f"Anuncios - {seller_name}" if seller_name else f"Anuncios - {item_name}"


    if adsDataList: 
        
        saveDictsAsExcel(adsDataList, output_filename) # Salvar os dados em Excel

    else:
        
        print("Nenhum dado foi encontrado. Verifique o nome do vendedor ou item") # Resposta para conjuntos vazios


if __name__ == '__main__':

    main(sys.argv[1:])