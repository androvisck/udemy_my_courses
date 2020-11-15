"""
  Este scrip trata-se de um estudo prático sobre Web Scrapping.
  Ele faz a varredura dos "meus cursos" na plataforma Udemy e coleta alguns dados.
  São eles: título do curso, avaliação, duração e o endereço.
  E, por fim, estrai todas as informações em um arquivo CSV.
"""

### Importando as bibliotecas ###

import requests # Requests HTTP Library
import json # JavaScript Object Notatio used as a lightweight data interchange format
import csv # CSV parsing and writing
import random # Random variable generators
import time # This module provides various functions to manipulate time values.
import re # This module provides regular expression matching operations similar to those found in Perl.
from bs4 import BeautifulSoup
import pandas as pd


headers = { # configuração dos navegadores necessária para acessar a página "meus cursos"
    "Authorization": "COLE AQUI A SUA CHAVE AUTORIZAÇÃO", # chave privada de acesso à API da Udemy
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
}

lista_urls = []
counter = 1
while(1):
  params = (('ordering', '-last_accessed'),
            ('page', str(counter)),
            ('page_size', '100')
            ) # parâmetros de filtragem  dos cursos

  resposta = requests.get('https://www.udemy.com/api-2.0/users/me/subscribed-courses/', headers=headers, params=params) # Realiza o acesso à API
  json_data = json.loads(resposta.text) # carrega todo o resultado em um json

  if "results" in json_data:
      for data in json_data['results']:
        if "/draft/" in data['url']: # guarda as URLs dos cursos
          continue
        lista_urls.append("https://www.udemy.com"+data['url'][0:-6]) # lista dos cursos adquiridos
  counter+=1  
  if not "results" in json_data:
   break
print("Total de cursos adquiridos: ", len(lista_urls)) # quantidade de cursos obtidos

### Coletando os dados ###

count = 0
dados = []
for endereco in lista_urls:
  endereco = endereco.replace("learn/", '') # retira o trecho "learn/" das urls
  soneca = random.randint(1, 50)/100
  time.sleep(soneca) # tempo de espera
  r = requests.get(endereco) # faz a requisição do HTML da página do curso
  #soup = BeautifulSoup(r.text, 'html.parser')
  soup = BeautifulSoup(r.text.encode("utf-8"), 'html.parser') # organiza o códigoo HTML e converte para a codificação utf8
  titulo = soup.title.text[0:-8] # obtendo o título do curso
  titulo = titulo.replace('"', '') # tratamento do texto do título
  titulo = titulo.replace("'", '')
  titulo = titulo.replace(",", '')
  if titulo == "Online Courses - Anytime, Anywhere":
    titulo = "Curso Privado"
    author=""
    duracao=""
    avaliacao=""
    dados.append((titulo, avaliacao, duracao, endereco)) # estruturação da lista
    continue
  try:
    duracao = soup.find_all('span', attrs={'class':'curriculum--content-length--1XzLS'}) # busca o exato campo <span> que contem o campo horas
    stats = [(i.contents[0], i.contents[1].text) for i in duracao]
    stats = stats[0]
    stats = stats[1]
    stats = stats.replace("\xa0", ' ') # retira possíveis trechos no dado
    stats = stats.replace(" total length", '')
    duracao = stats.replace("Duração total: ", '')
    temp = duracao.split()
    try:
      temp[1].count('m') or temp[1].count('min') 
      temp0 = [int(s) for s in re.findall(r'-?\d+\.?\d*', temp[0])]
      temp1 = [int(s) for s in re.findall(r'-?\d+\.?\d*', temp[1])]
      duracao = temp0[0] + temp1[0]/60
      duracao = round(duracao,2)
    except:
      temp[0].count('h') 
      temp0 = [int(s) for s in re.findall(r'-?\d+\.?\d*', temp[0])]
      duracao = float(temp0[0])
  except:
    try:
      duracao = soup.find('span', attrs={'data-purpose':'video-content-length'}).contents[0] # busca o exato campo <span> que contem o campo horas
      duracao = str(duracao)
      duracao = duracao.replace(" duracao on-demand video", '')
      temp=duracao.split()
      try:
        temp[1].count('m') or temp[1].count('min') 
        temp0 = [int(s) for s in re.findall(r'-?\d+\.?\d*', temp[0])]
        temp1 = [int(s) for s in re.findall(r'-?\d+\.?\d*', temp[1])]
        duracao = temp0[0] + temp1[0]/60
        duracao = round(duracao,2)
      except:
        temp[0].count('h') 
        temp0 = [int(s) for s in re.findall(r'-?\d+\.?\d*', temp[0])]
        duracao = float(temp0[0])
    except:
      duracao = temp[0] 
  try:
    avaliacao = soup.find('div', attrs={'class':'rate-count'}).contents[1].find('span').contents[0] # busca o exato campo <div> que contem o campo avaliacao
    avaliacao = avaliacao.replace(",", ".")
  except:
    avaliacao = soup.find('span', attrs={'data-purpose':'rating-number'}).contents[0] # busca o exato campo <span> que contem o campo avaliacao
    avaliacao = avaliacao.replace(",", ".") 
  dados.append((titulo, avaliacao, duracao, endereco)) # carrega os datos nas suas respectivas colunas
  titulo = ""
  duracao=""
  avaliacao=""
  r=""
  count = count + 1
  print("Restantes = ", (len(lista_urls) - count)) # cursos que ainda faltam ser coletados

### Salvando o arquivo CSV ###

df = pd.DataFrame(dados, columns=['titulo', 'avaliacao', 'duracao (h)', 'endereco'])
df['avaliacao'] = pd.to_numeric(df['avaliacao'])
df.to_csv('meus_cursos.csv', index=False, encoding='utf-8')