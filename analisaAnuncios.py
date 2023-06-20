import requests
import csv


accessToken = 8094781068110689


def getAds(acessToken):

    #sellerID = input('Digite o ID do vendedor: ')
    sellerID = 703985802

    url = f"https://api.mercadolibre.com/sites/MLB/search"

    headers = {
        "Authorization": f"Bearer {accessToken}"
    }

    params = {
        "seller_id": sellerID
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # Processar os dados recebidos
        with open('PrintedData.txt', 'w') as file:

            file.write(str(data['results']))
            print(data['seller']['nickname'])
            print('Dados salvos no arquivo txt')

    else:

        print("Erro na chamada da API:", response.status_code)
        print("Mensagem de erro:", response.text)



def main():

    getAds(accessToken)


if __name__ == '__main__':

    main()