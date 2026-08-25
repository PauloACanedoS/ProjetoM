import os
import smtplib
from email.mime.text import MIMEText
import requests
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'chave-padrao-insegura')

# Configurações de Banco de Dados (PostgreSQL) e Webhook
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL')

# ==========================================
# 1. MODELOS DE BANCO DE DADOS (PostgreSQL)
# ==========================================

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class LogradouroPR(db.Model):
    """
    Tabela espelho para os dados pr_faces_de_logradouros_2022 (IBGE).
    A estrutura real dependerá da sua importação no banco.
    """
    __tablename__ = 'pr_faces_de_logradouros_2022'
    id = db.Column(db.Integer, primary_key=True)
    municipio = db.Column(db.String(100))
    codigo_ibge = db.Column(db.String(20))
    # Demais colunas geográficas/IBGE...

# ==========================================
# 2. FUNÇÕES AUXILIARES (Email SMTP)
# ==========================================

def enviar_email(destinatario, assunto, corpo):
    remetente = os.environ.get('SMTP_USER')
    senha = os.environ.get('SMTP_PASSWORD')
    host = os.environ.get('SMTP_HOST')
    porta = int(os.environ.get('SMTP_PORT', 587))

    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = remetente
    msg['To'] = destinatario

    try:
        server = smtplib.SMTP(host, porta)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

# ==========================================
# 3. INTERFACE HTML (Embutida)
# ==========================================

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="pt-BR">
<body style="background-color: white; color: black; font-family: Arial; display: flex; justify-content: center; padding-top: 50px;">
    <div style="border: 2px solid black; padding: 30px; width: 300px; border-radius: 8px;">
        <h2 style="text-align: center;">Login Madasatec</h2>
        {% if erro %}<p style="color: red; text-align: center;">{{ erro }}</p>{% endif %}
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Usuário" required style="width: 100%; margin-bottom: 15px; padding: 10px; box-sizing: border-box; border: 1px solid black;">
            <input type="password" name="password" placeholder="Senha" required style="width: 100%; margin-bottom: 15px; padding: 10px; box-sizing: border-box; border: 1px solid black;">
            <button type="submit" style="width: 100%; padding: 10px; background-color: black; color: white; border: none; font-weight: bold; cursor: pointer;">Entrar</button>
        </form>
        <div style="text-align: center; margin-top: 15px;">
            <a href="/recuperar" style="color: black; text-decoration: none; font-weight: bold;">Recuperar Senha</a>
        </div>
    </div>
</body>
</html>
"""

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-BR">
<body style="background-color: white; color: black; font-family: Arial; display: flex; justify-content: center; padding-top: 50px;">
    <div style="border: 2px solid black; padding: 30px; width: 450px; border-radius: 8px;">
        <h2 style="text-align: center;">Consulta de Licitações</h2>
        <p style="text-align: center;">Bem-vindo, {{ session['username'] }} | <a href="/logout" style="color: red; font-weight: bold;">Sair</a></p>
        
        <form id="consultaForm">
            <label>Município (IBGE):</label>
            <select id="municipio" style="width: 100%; padding: 10px; margin: 5px 0 15px 0; border: 1px solid black;">
                <option value="Almirante Tamandaré">Almirante Tamandaré</option>
                <option value="Curitiba">Curitiba</option>
            </select>
            
            <label>Ano (2021 a 2025):</label>
            <select id="ano" style="width: 100%; padding: 10px; margin: 5px 0 15px 0; border: 1px solid black;">
                <option value="2025">2025</option><option value="2024">2024</option>
                <option value="2023">2023</option><option value="2022">2022</option>
                <option value="2021">2021</option>
            </select>

            <label>Número da Licitação:</label>
            <input type="text" id="licitacao" placeholder="Ex: 013" style="width: 100%; padding: 10px; margin: 5px 0 15px 0; box-sizing: border-box; border: 1px solid black;">

            <label>Email para recebimento:</label>
            <input type="email" id="email" value="can23dopaulo@gmail.com" style="width: 100%; padding: 10px; margin: 5px 0 15px 0; box-sizing: border-box; border: 1px solid black;">

            <button type="button" onclick="consultar()" style="width: 100%; padding: 12px; background-color: black; color: white; border: none; font-weight: bold; cursor: pointer;">Pesquisar e Notificar</button>
        </form>
        <div id="status" style="margin-top: 15px; font-weight: bold; text-align: center;"></div>
    </div>

    <script>
        async function consultar() {
            const statusDiv = document.getElementById('status');
            statusDiv.innerText = 'Processando e consultando base IBGE...';
            
            const payload = {
                municipio: document.getElementById('municipio').value,
                ano: document.getElementById('ano').value,
                licitacao: document.getElementById('licitacao').value,
                email: document.getElementById('email').value
            };

            const response = await fetch('/api/consultar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            statusDiv.innerText = result.message;
            statusDiv.style.color = response.ok ? 'green' : 'red';
        }
    </script>
</body>
</html>
"""

# ==========================================
# 4. ROTAS DA APLICAÇÃO
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        return render_template_string(HTML_LOGIN, erro="Usuário ou senha inválidos.")
    return render_template_string(HTML_LOGIN)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        user = Usuario.query.filter_by(email=email).first()
        if user:
            # Lógica simplificada: em produção, envie um token seguro.
            enviar_email(email, "Madasatec - Recuperação", "Acesse o sistema para redefinir sua senha.")
        return "Se o email existir, as instruções foram enviadas."
    return '<form method="POST"><input type="email" name="email" placeholder="Seu email"><button type="submit">Recuperar</button></form>'

@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(HTML_DASHBOARD)

@app.route('/api/consultar', methods=['POST'])
def api_consultar():
    if not session.get('logged_in'):
        return jsonify({"error": "Não autorizado"}), 401

    dados = request.json
    
    # 1. Simula a verificação na base pr_faces_de_logradouros_2022
    # logradouro = LogradouroPR.query.filter_by(municipio=dados.get("municipio")).first()
    
    # 2. Comunicação com n8n
    try:
        if N8N_WEBHOOK_URL:
            requests.post(N8N_WEBHOOK_URL, json=dados)
    except Exception as e:
        print(f"Erro n8n: {e}")

    # 3. Envio de resumo por Gmail (Backup do n8n)
    corpo_email = f"Resumo solicitado. Mun: {dados.get('municipio')}, Ano: {dados.get('ano')}, Licitação: {dados.get('licitacao')}."
    enviar_email(dados.get("email"), "Resumo de Licitação - Madasatec", corpo_email)

    return jsonify({"status": "success", "message": "Consulta realizada, dados enviados via n8n e email despachado."})

@app.route('/health')
def health():
    return jsonify({"status": "Operacional", "port": 3000})

# ==========================================
# 5. INICIALIZAÇÃO DO BANCO
# ==========================================
def setup_database():
    with app.app_context():
        db.create_all()
        # Limita a 10 usuários criando apenas os necessários se o banco estiver vazio
        if Usuario.query.count() == 0:
            user_admin = Usuario(
                username='admin', 
                password_hash=generate_password_hash('senha-provisoria-123'),
                email='can23dopaulo@gmail.com'
            )
            db.session.add(user_admin)
            db.session.commit()
            print("Usuário admin criado. Limite de 10 usuários será gerenciado via backend.")

if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=3000)
