import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import os
import sys
import re
import argparse


class AnalysisAds():

    def __init__(self, is_seller_search, search_query, search_sort, search_filter):
        self.is_seller_search = is_seller_search
        self.search_query = search_query
        self.sort = search_sort
        self.search_filter = search_filter


    def getAdsData(self):
        def requestDataFromAPI(offset = 0, limit = 50):
            search_query_key = 'nickname' if self.is_seller_search else 'q'  # Definindo a chave correta do parametro de pesquisa

            url = f"https://api.mercadolibre.com/sites/MLB/search?"
            params = {
                search_query_key: self.search_query,
                'sort': self.sort,
                'offset': offset,
                'limit': limit,
            }

            if self.search_filter:
                if 'internacional' in self.search_filter:
                    params['shipping_origin'] = 10215069    # Adiciona o filtro de venda internacional pelo ID
                elif 'best_sellers' in self.search_filter: 
                    params['power_seller'] = 'yes'          # Adiciona o filtro de melhores vendedores

            try: 
                response = requests.get(url, params=params)
                data = response.json()
                return data
            except requests.exceptions.ConnectTimeout as e: 
                print("\nErro de tempo limite de conexão:", e)
            except requests.exceptions.RequestException as e:
                print("\nErro de requisição:", e)

        def requestAdVisitsFromAPI(ad_id):
            url = f'https://api.mercadolibre.com/visits/items?ids={ad_id}'
            params = {
                'Authorization': f'Bearer 9vUx388fBOXxkNOftqR8gPVcwBnz2pi9'
            }
            response = requests.get(url, params=params)
            data = response.json()
                
            if response.status_code == 200:
                return data[ad_id]
            elif response.status_code == 429: 
                requestAdVisitsFromAPI(ad_id) # Recursividade para forçar resposta da API
            else:
                print("\nAPI ERROR:", response.status_code)
                print("Erro ao extrair as visitas:", response.text)

        # Looping realizar a paginação considerando um limite de 50 anúncios por requisição
        offset = 0
        limit = 50
        analysis_date = datetime.now().date().strftime("%d/%m/%Y")
        ads_data_list = []

        total_items = requestDataFromAPI(limit = 1) 
        total_items = total_items['paging']['total']
        pbar = tqdm(total=total_items, desc='Extraindo Dados') # Cria uma barra de progresso

        while True:
            data = requestDataFromAPI(offset=offset)
            data = data['results']

            if not data or len(ads_data_list) == total_items:
                break

            for item in data:   # Tratando dados de cada anúncio da resposta
                creation_date = convertDate(item['stop_time']) 
                days_active = calculateDateDifference(creation_date)
                sales = item['sold_quantity']
                sales_per_day = sales / days_active if days_active != 0 else 0 # Operador ternário para evitar divisões por 0
                ad_id = item['id']
                visits = requestAdVisitsFromAPI(ad_id)
                
                ad = {
                    'ID' : ad_id,
                    'Título' : item['title'],
                    'Preço' : item['price'],
                    'Tipo' : 'Premium' if item['listing_type_id'] == 'gold_pro' else 'Clássico',
                    'Vendas' : sales,
                    'Visitas' : visits,
                    'Conversão' : (sales / visits) if (item['sold_quantity'] != 0 and visits) else 0, # Operador ternário para evitar divisões por 0
                    'Data de Criação' : creation_date,
                    'QTD Dias Ativo' : days_active,
                    'Vendas/Dias' : sales_per_day,
                    'Envio' : 'Normal' if item['shipping']['logistic_type'] != 'fulfillment' else 'Normal',
                    'Link': item['permalink'],
                    'Data da Análise' : analysis_date
                }

                if not self.is_seller_search: 
                    ad['Vendedor']  = item["seller"]["nickname"]
                    ad['Origem']    = item['address']['state_id']
                
                ads_data_list.append(ad) # Adiciona os dicionários na lista de dados
                pbar.update(1) # Atualiza a barra de progresso

            offset += limit # Faz com que a proxima extração iniciei no final do limite atual

        return ads_data_list



def convertDate(date):
    # Tratamento da "stop_date" para encontrar a data de criação
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

    
def saveDataAsExcel(adsDataList, output_filename):
    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, "Dados Extraídos")

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        
    full_filename = os.path.join(target_directory, f"{output_filename}.xlsx")

    if os.path.exists(full_filename):
        i = 2

        while os.path.exists(f"{output_filename}.xlsx"):
            match = re.search(r'\((\d+)\)', output_filename)

            if match: 
                new_number = str(i)
                output_filename = re.sub(r'\(\d+\)', f'({new_number})', output_filename)
            else: 
                output_filename = f'{output_filename} ({i})'

        i += 1
        print(f"\nO arquivo '{output_filename}' já existe. O nome será alterado para '{output_filename}'")

    df = pd.DataFrame(adsDataList) # Transforma a lista com os dicionários em um DataFrame Pandas
    df.to_excel(full_filename, index=True, columns=df.columns) # Salva os dados em um arquivo Excel

    print(f"\nDados salvos em 'Dados Extraídos\{output_filename}.xlsx'\n")


def clearPrompt():
    if os.name == 'nt':
        os.system('cls') # Comando Windows
    else: 
        os.system('clear') # Comando Mac e Linux


def main(args):
    clearPrompt()
    
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
    search_sort = args.ordenacao
    search_filter = args.filtro

    if seller_name:
        is_seller_search = True
        search_query = seller_name
    elif item_name:
        is_seller_search = False
        search_query = seller_name
        
    else:
        print("""
                Você deve especificar o nome do vendedor (-v USCONNECT) ou do item (-i "Iphone 7")
            
                Comando -h ou --help para mais informações
        """)
        return

    output_filename = args.nome_arquivo if args.nome_arquivo else f"Anuncios - {search_query}"

    analysis = AnalysisAds(
        is_seller_search = is_seller_search,
        search_query = search_query,
        search_sort = search_sort,
        search_filter = search_filter
    )
    adsDataList = analysis.getAdsData()
    
    if adsDataList: 
        saveDataAsExcel(adsDataList, output_filename)
    else:
        print("Nenhum dado foi encontrado. Verifique o nome do vendedor ou item")


if __name__ == '__main__':
    main(sys.argv[1:])