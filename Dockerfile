# imagem base python
FROM python:3.13

# diretorio da REST API dentro do container
WORKDIR /app

# copia o arquivo para o diretório /app
COPY requirements.txt .

# instala as dependencias do projeto
RUN pip install --no-cache-dir  -r requirements.txt

# copia todo o código para o diretório /app
COPY .  .

# executa o servidor 
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5002"]
