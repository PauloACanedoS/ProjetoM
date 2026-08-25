# Usa uma imagem leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código para o container
COPY . .

# Expõe a porta 3000
EXPOSE 3000

# Comando para iniciar a aplicação usando Gunicorn (servidor de produção para Python)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "app:app"]
