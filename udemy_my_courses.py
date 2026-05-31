import requests
import pandas as pd
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Carrega variáveis de ambiente (CLIENT_ID, CLIENT_SECRET) do arquivo .env
load_dotenv()

CLIENT_ID = os.getenv("UDEMY_CLIENT_ID")
CLIENT_SECRET = os.getenv("UDEMY_CLIENT_SECRET")

def get_udemy_token():
    """Autentica o app e retorna um token de acesso válido."""
    auth_url = 'https://www.udemy.com/api-2.0/oauth2/access-token/'
    response = requests.post(auth_url, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET), data={'grant_type': 'client_credentials'})
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Erro na autenticação: {response.status_code} - {response.text}")

def fetch_all_subscribed_courses(token):
    """Percorre todas as páginas da API e retorna a lista de cursos."""
    all_courses = []
    # Endpoint da API para cursos inscritos
    url = 'https://www.udemy.com/api-2.0/users/me/subscribed-courses/'
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    params = {'page_size': 100}

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Erro ao buscar cursos: {response.status_code}")
            break
            
        data = response.json()
        for course in data.get('results', []):
            all_courses.append({
                'titulo': course.get('title'),
                'avaliacao': course.get('avg_rating', 0),
                # A API retorna duração em segundos, convertendo para horas
                'duracao_horas': round(course.get('content_length', 0) / 3600, 2),
                'url': f"https://www.udemy.com{course.get('url')}"
            })
        
        # Paginação automática fornecida pela API
        url = data.get('next')
    
    return all_courses

def main():
    try:
        print("Obtendo token de acesso...")
        token = get_udemy_token()
        
        print("Coletando cursos da API...")
        dados = fetch_all_subscribed_courses(token)
        
        if dados:
            df = pd.DataFrame(dados)
            df.to_csv('meus_cursos.csv', index=False, encoding='utf-8')
            print(f"Sucesso! {len(dados)} cursos salvos em 'meus_cursos.csv'.")
        else:
            print("Nenhum curso encontrado.")
            
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
