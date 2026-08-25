from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Aqui depois inseriremos o HTML da sua tela branca com botões pretos
    return "<h1>Plataforma Madasatec - Online</h1><p>Sistema operando na porta 3000.</p>"

@app.route('/health')
def health():
    return jsonify({"status": "Servidor Python rodando", "port": 3000})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
