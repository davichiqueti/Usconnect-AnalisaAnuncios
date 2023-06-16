import csv
import requests


def exportar_anuncios(access_token, seller_id):
    url = f"https://api.mercadolibre.com/users/{seller_id}/items/search"

    params = {
        "access_token": access_token,
        "status": "active",
        "limit": 50
    }

    anuncios = []

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        anuncios += data["results"]
        total = data["paging"]["total"]

        while len(anuncios) < total:
            params["offset"] = len(anuncios)
            response = requests.get(url, params=params)
            data = response.json()
            anuncios += data["results"]

        return anuncios
    else:
        print("Erro na chamada da API:", response.status_code)
        print("Mensagem de erro:", data["message"])  # Nova linha adicionada
        return None



def salvar_dados_csv(dados_anuncios, nome_vendedor):
    nome_arquivo = f"ANÚNCIOS_{nome_vendedor}.csv"

    with open(nome_arquivo, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for anuncio in dados_anuncios:
            anuncio_id = anuncio["id"]
            link = anuncio["permalink"]
            titulo = anuncio["title"]
            valor = anuncio["price"]
            data_criacao = anuncio["date_created"]
            quantidade_vendas = anuncio["sold_quantity"]
            quantidade_visitas = anuncio["visits"]
            taxa_conversao = anuncio["conversion_rate"]

            if not verificar_anuncio_existente(anuncio_id, nome_arquivo):
                writer.writerow([anuncio_id, link, titulo, valor, data_criacao, quantidade_vendas, quantidade_visitas, taxa_conversao])


def verificar_anuncio_existente(anuncio_id, nome_arquivo):
    try:
        with open(nome_arquivo, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == anuncio_id:
                    return True
        return False
    except FileNotFoundError:
        return False


access_token = 8094781068110689
seller_id = input('Informe o ID do vendedor: ')

dados_anuncios = exportar_anuncios(access_token, seller_id)

if dados_anuncios:
    nome_vendedor = "NOME_DO_VENDEDOR"
    salvar_dados_csv(dados_anuncios, nome_vendedor)
    print("Dados dos anúncios salvos com sucesso!")