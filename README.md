# Usconnect-AnalisaAnuncios

Sistema projetado para extrair informações do Mercado Livre atraves de sua API oficial. A busca pode ser feita pelo nome do produto ou do vendedor. Os dados são tratados e transferidos para uma tabela do Excel.

Projeto exigido pelo E-commerce em que atuo. Logo, foi meu primeiro projeto profissional. É muito gratificante poder aplicar meus conhecimentos na resolução de problemas da minha equipe!


## Objetivo:

Automatizar o processo da coleta de dados do Mercado Livre para Gerar Insights e estratégias de marketing com informações coletadas. Permitindo as seguintes análises:

* Avaliar rentabilidade de novos produtos.
* Encontrar os melhores métodos utilizados para anunciar um produto.
* Analisar anúncios de um concorrente.
* Visão geral sobre o rendimento de anúncios em nossas contas no MarketPlace.
   
## Tecnologias Utilizadas:

* Estruturação e execução de *Requisições HTTP* utilizando *Requests*
* Tratamento de dados com *Pandas*
* Passagem de parâmetros por linha de comando utilizando *argparse*

## Exemplo de saída:

![Exemplo.png](https://github.com/davichiqueti/Usconnect-AnalisaAnuncios/blob/main/Exemplo.png)
> apenas 5 itens para visualização
   
## Como Usar:

1. Baixar interpretador [Python](https://www.python.org/downloads/)

2. Instalar Bibliotecas especificadas em [requirement.txt](https://github.com/davichiqueti/Usconnect-AnalisaAnuncios/blob/main/requirements.txt)

3. Fazer o dowload do código python no diretório de destino das tabelas

4. Abrir o prompt de comando e rodar comando ```cd C:\"CaminhoDoDiretório"**```

5. Rodar comando ```python usco-AnalisaAnuncios-v1.1.py -v "nome do vendedor"```
   > Mais informações sobre os parametros com -h ou --help

## Observação:

Há um limite de 1000 anúncios para a forma atual que a API está sendo consumida.
Conforme as intruções passadas para mim a quantidade atual já permite muitas análises e não é interessante investir tempo para quebrar esse limite.

O código está atualmente sendo revisado. Quero implementar orientação a objetos utilizando classe para melhor organização, também percebi a repetição desnecessária pela falta de uma função única para realizar as requisições.

## Referências:

[Documentação Bibliteca Requests](https://requests.readthedocs.io/en/latest/)

[Documentação Mercado Livre API](https://developers.mercadolivre.com.br/pt_br/api-docs-pt-br)

