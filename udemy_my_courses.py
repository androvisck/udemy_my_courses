import requests
import pandas as pd
import os

# Use variáveis de ambiente para segurança
TOKEN = os.getenv("UDEMY_API_TOKEN")

def fetch_subscribed_courses():
    all_courses = []
    url = 'https://www.udemy.com/api-2.0/users/me/subscribed-courses/'
    headers = {"Authorization": TOKEN}
    params = {'page_size': 100}

    while url:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Aqui você extrai os dados diretamente do JSON
        for course in data.get('results', []):
            all_courses.append({
                'titulo': course.get('title'),
                'url': f"https://www.udemy.com{course.get('url')}",
                # Verifique se estes campos existem na resposta da API
                'avaliacao': course.get('avg_rating'), 
                'duracao': course.get('content_length')
            })
        
        # A própria API indica se existe próxima página
        url = data.get('next')
    
    return all_courses

# Salvar
dados = fetch_subscribed_courses()
df = pd.DataFrame(dados)
df.to_csv('meus_cursos.csv', index=False)
