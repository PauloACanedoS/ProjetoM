from fastapi import FastAPI, Form, HTTPException
from app.n8n_client import enviar_para_n8n

app = FastAPI(title="Madasatec - Análise de Licitações")

# Rota simples para confirmar que o container está rodando perfeitamente[cite: 1]
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Rota que receberá os filtros digitados pelo usuário no formulário do site
@app.post("/analisar")
def processar_formulario(
    municipio: str = Form(...),
    ano: int = Form(...),
    numero_licitacao: str = Form(...)
):
    # 1. Valida e normaliza os valores (etapa de segurança)[cite: 1]
    municipio = municipio.strip()
    numero_licitacao = numero_licitacao.strip()
    
    # 2. Envia os dados limpos para o cliente do n8n processar[cite: 1]
    resultado = enviar_para_n8n(municipio, ano, numero_licitacao)
    
    if resultado.get("status") == "erro":
        raise HTTPException(status_code=500, detail="Falha na comunicação com o n8n.")
        
    # 3. Exibe o resultado ao usuário sem revelar credenciais internas[cite: 1]
    return {
        "mensagem": "Consulta processada com sucesso!",
        "dados_retornados": resultado
    }
