from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.n8n_client import enviar_perfil_n8n

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def tela_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def autenticar(request: Request, usuario: str = Form(...), senha: str = Form(...)):
    # Validação estrita de credenciais
    if usuario != "promotor" or senha != "senha123":
        return HTMLResponse(content="<h3 style='color:red;'>Usuário ou senha incorretos!</h3><a href='/'>Voltar</a>", status_code=401)
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="promotor_usuario", value=usuario)
    return response

@app.get("/dashboard")
def dashboard(request: Request):
    usuario = request.cookies.get("promotor_usuario")
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analisar")
def analisar_licitacao(
    request: Request,
    municipio: str = Form(...),
    periodo_anos: int = Form(...),
    ano: int = Form(...),
    numero_licitacao: str = Form(...),
    ibge_dataset: str = Form(...),
    link_transparencia: str = Form(...)
):
    usuario = request.cookies.get("promotor_usuario")
    if not usuario:
        return RedirectResponse(url="/", status_code=303)
    
    enviar_perfil_n8n(
        municipio=municipio.strip(),
        periodo_anos=periodo_anos,
        ano=ano,
        numero_licitacao=numero_licitacao.strip(),
        ibge_dataset=ibge_dataset.strip(),
        link_transparencia=link_transparencia.strip(),
        promotor_usuario=usuario,
        promotor_senha=""
    )
    return HTMLResponse(content="""
        <div style='font-family:sans-serif; padding:40px; text-align:center;'>
            <h2>Auditoria Iniciada com Sucesso!</h2>
            <p>O relatório está sendo processado pelo n8n.</p>
            <a href='/dashboard'>Voltar ao painel</a>
        </div>
    """)
