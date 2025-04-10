# imagem base python
FROM python:3.13

# diretorio da REST API dentro do container
WORKDIR /app

# copia o arquivo para o diretório /app
COPY requirements.txt .

# instala as dependencias do projeto / cmd não bloqueante
RUN pip install --no-cache-dir  -r requirements.txt

ENV API_EXTERNA_DATABASE_ID=""
ENV API_EXTERNA_TOKEN=""

# copia todo o código para o diretório /app
COPY .  .

# executa o servidor -/ cmd bloqueante
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5002"]
