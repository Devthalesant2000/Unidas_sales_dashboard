import requests
import pandas as pd
import time
import streamlit as st

class PipefyAuth:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://app.pipefy.com/oauth/token"
        self.access_token = None
        self.token_expiry = None
    
    def get_token(self):
        if self.access_token and self.token_expiry and time.time() < self.token_expiry:
            return self.access_token
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.token_url, json=data)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expiry = time.time() + token_data["expires_in"]
            return self.access_token
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter token: {e}")
            return None


client_id = st.secrets["pipefy"]["client_id"]
client_secret = st.secrets["pipefy"]["client_secret"]

auth = PipefyAuth(client_id, client_secret)

PIPE_ID = st.secrets["pipefy"]["PIPE_ID"]
PIPE_REPORT_ID = st.secrets["pipefy"]["PIPE_REPORT_ID"]
GRAPHQL_URL = "https://api.pipefy.com/graphql"

def iniciar_exportacao(auth):
    token = auth.get_token()
    if not token:
        return None

    query = f"""
    mutation {{
      exportPipeReport(input: {{
        pipeId: {PIPE_ID},
        pipeReportId: {PIPE_REPORT_ID}
      }}) {{
        pipeReportExport {{
          id
        }}
      }}
    }}
    """
    response = requests.post(GRAPHQL_URL, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, json={"query": query})
    resp = response.json()
    print("Início da exportação:", resp)
    try:
        return resp['data']['exportPipeReport']['pipeReportExport']['id']
    except:
        print("Erro ao iniciar exportação:", resp)
        return None

def verificar_status(auth, export_id):
    token = auth.get_token()
    if not token:
        return None

    query = f"""
    {{
        pipeReportExport(id: {export_id}) {{
            fileURL
            finishedAt
        }}
    }}
    """
    response = requests.post(GRAPHQL_URL, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, json={"query": query})
    resp = response.json()
    try:
        export = resp['data']['pipeReportExport']
        if export['finishedAt']:
            # Baixar
            r = requests.get(export['fileURL'])
            filename = 'relatorio.xlsx'
            with open(filename, 'wb') as f:
                f.write(r.content)
            print("Baixado:", filename)
            return filename
        else:
            print("Ainda não pronto.")
            return None
    except:
        print("Erro ao verificar:", resp)
        return None

def main():
    export_id = iniciar_exportacao(auth)
    if not export_id:
        print("Falha ao iniciar.")
        return
    print(f"ID da exportação: {export_id}")

    while True:
        arquivo = verificar_status(auth, export_id)
        if arquivo:
            break
        print("Aguardando 10s...")
        time.sleep(10)

    # Carregar no pandas
    if arquivo.endswith('.csv'):
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)
    return df