#  Production Automation Tool Backend

**Aluno: Jaquinei de Oliveira**

Este projeto faz parte do *MVP* do *Sprint 2* da Disciplina **Desenvolvimento Back-End Avançado**

O objetivo é apresentar o resultado prático obtido após o estudo do conteúdo apresentado ao longo das aulas da disciplinas apresentadas neste Sprint.

O MVP consiste em um Frontend, um Backend e acesso a uma API externa.

Este repositorio faz parte do MVP e contem o código para o Backend e o código usado para cesso a uma API externa. 
Dentro os cenários apresentados no documento com as instruções sobre os requisitos para o MVP, esse trabalho está enquadrado no Cenário 1.1, uma vez que o acesso a API externa está sendo realizado pelo Backend.

O Backend disponibilizado neste repositório contem o dockerFile possibilitando rodar containerizado. As instruções para fazer o build da imagem e rodar os container estão na seção [Como iniciar o Backend usando o docker](#como-iniciar-o-backend-usando-o-docker)

**Este conteúdo foca nos detalhes de uso do projeto do Backend.**

## Fluxograma

Arquitetura implementada.

TODO: Adicionar fluxograma aqui

## Backend (API)

O Backend foi feito usando Python: flask como servidor web e sqlite como banco de dados. O código do Backend está disponível neste repositorio.

### Como iniciar o Backend usando o docker:

Como iniciar o Backend usando o docker:

Certifique-se que o Docker esteja instalado

Cria a imagem

```
docker build -t backend_puc_rio_sprint_2_mvp .
```
- Mapeia a porta local 5002 do host para a porta 5002 do container
```
docker run -e API_EXTERNA_DATABASE_ID=XXXXXXXXXXX -e API_EXTERNA_TOKEN=YYYYYYYYYYYY  -d -p 5002:5002 backend_puc_rio_sprint_2_mvp
```
- Acesse a URL http://localhost:5002 no navegador para ter acesso ao SWAGGER

# Visão geral dos módulos do MVP

## Frontend (Interface)

O Frontend foi desenvolvido usando HTML, CSS e JavaScript e Bootstrap. Pode ser usado independentemente do Backend, mas para persistir os dados é necessário que o Backend esteja rodando.

O código do FrondEnd está disponível em outro repositório.

## Backend (API)

A REST API é disponibilizada pelo BackEnd e apresenta as seguintes rotas:

    GET /
Redireciona para o Swagger

    GET /docs
Swagger

    GET /tasks
Retorna a lista de tasks do database

    GET /notion-data
Acesso a API externa do Notion. (requer DATABASE_ID e TOKEN para acessar)

    DELETE /task{name}

    GET /task{task_id}

    OST /task{name, priority, product, start_date, task_type, end_date}
cadastra uma task

    POST /comment{task_id, text}
cadastra um comentario associado a task


Desenvolvimento Back-End Avançado

## Acesso a uma API externa

O acesso a API externa está sendo feito utilizando a API da Notion (https://developers.notion.com/)
Para o backend acessar a API é necessário utilizar as seguintes informações:
- Notion API URL
- Token Notion
- Database ID

Estas informações (Notion API URL, Token e Database ID) serão disponibilizadas no texto de submissão deste MVP.

Foi criada um Notion page com uma lista de Tasks. Essas tasks podem ser incluidas no Prodution Automation Tool. Para acessar a lista do Notion, diretamente, o seguinte link pode ser usado (https://www.notion.so/1ce16f12775a80da8366cacacaa3d3da?v=1ce16f12775a807e846d000c874669ac&pvs=4).


# Development environment 

## Como executar o Backend

### Dev
Será necessário ter instaladas todas as bibliotecas Python listadas no arquivo `requirements.txt`.

Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

Crie o *virtual environment
```
python -m venv env
```
Ative o *virtual environment*

Windows:
```
.\env\Scripts\Activate
```
macOS:
```
source env/bin/activate
```

Installe todas as dependencias necessárias para rodar o projeto
```
(env)$ pip install -r requirements.txt
```
> Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

Para executar o Backend que expõe a API:

```
(env)$ flask run --host 0.0.0.0 --port 5002
```
> A porta **5002** está hardcode no projeto do Frontend.
> Caso queira alterar a porta, ajuste a variável *SERVER_URL* no arquivo *scripts.js* do projeto do Frontend.

Abra o link [http://localhost:5002](http://localhost:5002/) no navegador para verificar o status da API em execução.

### Docker

- Certifique-se que o Docker esteja instalado
- Cria a imagem
```
docker build -t backend_puc_rio_sprint_2_mvp .
```
- Mapeia a porta local 5002 do host para a porta 5002 do container
```
docker run -d -p 5002:5002 backend_puc_rio_sprint_2_mvp
```
- Acesse a URL http://localhost:5002 no navegador para ter acesso ao SWAGGER