from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.n8n_client import enviar_perfil_n8n

app = FastAPI(title="Madasatec - Análise de Licitações")

# Monta os arquivos estáticos e templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    # Renderiza o formulário principal de entrada
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analisar", response_class=HTMLResponse)
def analisar_licitacao(
    request: Request,
    municipio: str = Form(...),
    periodo_anos: int = Form(...),
    ano: int = Form(...),
    numero_licitacao: str = Form(...),
    ibge_dataset: str = Form(...),
    link_transparencia: str = Form(...)
):
    # Envia os dados completos de forma síncrona para o n8n
    resultado = enviar_perfil_n8n(
        municipio=municipio.strip(),
        periodo_anos=periodo_anos,
        ano=ano,
        numero_licitacao=numero_licitacao.strip(),
        ibge_dataset=ibge_dataset.strip(),
        link_transparencia=link_transparencia.strip()
    )
    
    # Retorna a página de resultados com o JSON processado pelo n8n
    return templates.TemplateResponse("resultado.html", {"request": request, "resultado": resultado})
