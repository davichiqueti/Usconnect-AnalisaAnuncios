import requests
import json
import pandas as pd
import openpyxl



def requestAds(seller_id, limit, offset):

    url = f"https://api.mercadolibre.com/sites/MLB/search?"

    params = {

        'seller_id': seller_id,
        'offset': offset,
        'limit': limit

    }
    
    response = requests.get(url, params=params)

    if response.status_code == 200:

        data = response.json()
        # Organiza os dados em formato JSON para visualização
        json_data = json.dumps(data['results'], indent=4)
        with open('dados.txt', 'w') as file: file.write(json_data)

    else:

        print("Erro na chamada da API:", response.status_code)
        print("Mensagem de erro:", response.text)

    return data['results']



def save_lists_as_excel(lists, filename):

    # Verifica se todas as listas têm o mesmo tamanho
    list_size = len(lists[0])
    if not all(len(lst) == list_size for lst in lists):
        raise ValueError("As listas não têm o mesmo tamanho.")

    # Cria um dicionário com os dados das listas
    data = {f"Column{i+1}": lst for i, lst in enumerate(lists)}

    # Cria um DataFrame a partir do dicionário
    df = pd.DataFrame(data)

    # Salva o DataFrame em um arquivo Excel
    df.to_excel(filename, index=False)



def pagingLoop():

    seller_id = 703985802
    offset = 0
    limit = 50
    
    idList = []
    titleList = []
    priceList = []


    for i in range(3):
    #while True:

        data = requestAds(seller_id, limit, offset)
        if data == []: break

        # Loops para extração dos dados
        for item in data:

            idList.append(item['id'])
            titleList.append(item['title'])
            priceList.append(item['price'])



        offset += limit


    return idList, titleList, priceList


def main():

    save_lists_as_excel(pagingLoop(), 'tabela_teste.xlsx')


if __name__ == '__main__':

    main()
