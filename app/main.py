@app.post("/login")
def login(usuario: str = Form(...), senha: str = Form(...)):
    # Validação simples de credenciais (substitua pelas suas se necessário)
    if usuario != "promotor" or senha != "senha123":
        return HTMLResponse(content="<h3>Credenciais inválidas</h3>", status_code=401)
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="promotor_usuario", value=usuario)
    response.set_cookie(key="promotor_senha", value=senha)
    return response
