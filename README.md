#  Production Automation Tool API

Este pequeno projeto faz parte do *MVP* do *Sprint 1* da Disciplina **Desenvolvimento Back-End Avançado**

O objetivo é apresentar o resultado prático obtido após o estudo do conteúdo apresentado ao longo das aulas da disciplina deste Sprint.

**Aluno: Jaquinei de Oliveira**

---

Este conteúdo foca na API do Backend.

---
## Como executar

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
