import os
import requests
from dotenv import load_dotenv

load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_API_KEY = os.getenv("N8N_API_KEY")

def enviar_perfil_n8n(
    municipio: str,
    periodo_anos: int,
    ano: int,
    numero_licitacao: str,
    ibge_dataset: str,
    link_transparencia: str
):
    payload = {
        "municipio": municipio,
        "periodo_anos": periodo_anos,
        "ano": ano,
        "numero_licitacao": numero_licitacao,
        "ibge_dataset": ibge_dataset,
        "link_transparencia": link_transparencia
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    if N8N_API_KEY:
        headers["x-api-pilates"] = N8N_API_KEY

    try:
        # Requisição síncrona aguardando o When Last Node Finishes do n8n
        response = requests.post(N8N_WEBHOOK_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}
