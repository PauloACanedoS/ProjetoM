import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis configuradas no .env do servidor
load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_API_KEY = os.getenv("N8N_API_KEY")

def enviar_para_n8n(municipio: str, ano: int, numero_licitacao: str):
    # O Python constrói o 'body' que antes estava vazio
    payload = {
        "municipio": municipio,
        "ano": ano,
        "numero_licitacao": numero_licitacao
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-pilates": N8N_API_KEY
    }

    try:
        # Envia a requisição com timeout de 30 segundos, conforme recomendado
        resposta = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=30)
        resposta.raise_for_status()
        
        # Retorna o JSON de sucesso que definimos no contrato de dados
        return resposta.json()
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}
