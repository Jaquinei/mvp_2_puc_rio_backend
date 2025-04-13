import os
from datetime import datetime
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, jsonify, request
from urllib.parse import unquote
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError

from model import Session, Task, Comment
from logger import logger
from schemas import *
from flask_cors import CORS, cross_origin

import requests

notion_database = os.getenv("API_EXTERNA_DATABASE_ID")
notion_token = os.getenv("API_EXTERNA_TOKEN")
notion_api_url = f'https://api.notion.com/v1/databases/{notion_database}/query'

#print("INFO: DATABASE ", notion_database)
#print("INFO: TOKEN ", notion_token)

info = Info(title="Production Automation Tool API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app, resources={r"/task/*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080"]}},
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# definindo tags
home_tag = Tag(name="Documentation", description="Swagger documentation auto generated")
doc_tag = Tag(name="Choose Documentation", description="Choose which type of documentation do you wish to see")
task_tag = Tag(name="Task", description="Add, visualize and remote the tasks from the database")
comment_tag = Tag(name="Comment", description="Add a comment to the task added to the database")
task_from_notion_api_tag = Tag(name="TaskFromNotionAPI", description="Fetch and manage tasks from Notion API")

# Função para buscar dados do Notion
def get_notion_data():
    headers = {
        'Authorization': f'Bearer {notion_token}',
        'Notion-Version': '2021-05-13',
        'Content-Type': 'application/json'
    }
    if not notion_database or not notion_token:
        return {
            "unauthorized" : str('TOKEN and DATABASE info missing')
            }, 401
    try:
        response = requests.post(notion_api_url, headers=headers)

        if response.status_code != 200:
            raise Exception('Erro ao acessar a API do Notion')

        data = response.json()
        return data
    except Exception as e:
        return {"error": str(e)}
    

# Endpoint para buscar as tarefas do Notion
@app.get('/notion-data', tags=[task_from_notion_api_tag])
@cross_origin(
    origins=['http://localhost:8080', 'http://127.0.0.1:8080'],
    methods=["GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)
def notion_data():
    """Fetch tasks from the Notion database."""
    response_body = None
    status_code = 200

    data = get_notion_data()

    #print(data)

    if isinstance(data, tuple):
        response_body, status_code = data

    # Se houver um erro na requisição, retorna um erro
    if response_body is not None:
        if 'error' in response_body:
            return jsonify(response_body), status_code

        if 'unauthorized' in response_body:
            return jsonify(response_body), status_code

    if 'results' not in data:
        return {"message": "Missing 'results' in response data"}, 500
    
    #results = data.get('results', [])
    results = []
    for item in data['results']:
        task = {}

         # Get the page ID and add it to the task dictionary
        task['page_id'] = item.get('id', None)  # 'id' is the unique page ID
        print(task)
        # Safely access 'properties' in case it's missing
        properties = item.get('properties', {})

        # Iterate over all properties of the item
        for field, value in properties.items():
            # Check the type of the property and process accordingly
            if value.get("type") == "title":
                title = value.get("title", [])
                if title:
                    task[field] = title[0].get('text', {}).get('content', '')
                else:
                    task[field] = ''  # If title list is empty, assign empty string
            elif value.get("type") == "rich_text":
                rich_text = value.get("rich_text", [])
                if rich_text:
                    task[field] = rich_text[0].get('text', {}).get('content', '')
                else:
                    task[field] = ''  # If the list is empty, set the field as an empty string
            elif value.get("type") == "number":
                task[field] = value.get("number", None)
            elif value.get("type") == "select":
                task[field] = value.get("select", {}).get('name', None)
            elif value.get("type") == "date":
                task[field] = value.get("date", {}).get('start', None)
            else:
                task[field] = None  # For types not directly mapped

        results.append(task)

    return jsonify(results)


@app.get('/', tags=[home_tag])
def home():
    """Redirect to /openapi/swagger endpoint, if choose /openapi endpoint it allows to choose the documentation style
    """
    return redirect('/openapi/swagger')


@app.get('/docs', tags=[doc_tag])
def choose_documentation():
    """Redirect to /openapi endpoint, allows to choose the documentation style
    """
    return redirect('/openapi')


@app.post('/task', tags=[task_tag], 
          responses={"200": TaskViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_task(form: TaskSchema):
    """Add a new task to the database

    Return a task representation and the comments associated.
    """
    task = Task(
        name=form.name,
        task_type=form.task_type,
        product=form.product,
        priority=form.priority,
        insertion_date=datetime.now(),
        start_date=form.start_date if form.start_date else None,
        end_date=form.end_date if form.end_date else None
        )
    logger.debug(f"Adding task name: '{task.name}'")

    # creating the database connection
    session = Session()

    # 💥 Check if a task with the same name already exists
    existing = session.query(Task).filter_by(name=form.name).first()
    if existing:
        logger.debug(f"Task name already exists : '{task.name}'")
        return jsonify({"error": "Task name already exists."}), 409
    
    try:
        # creating a session with the database
        session = Session()
        # adding a task
        session.add(task)
        # performing the commit of the item in the database
        session.commit()
        logger.debug(f"Task name '{task.name}' added")
        return show_task(task), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Task name already saved in the database"
        logger.warning(f"Error while adding the product '{task.name}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Was not possible to save the new item"
        logger.warning(f"Error while adding the product '{task.name}', {error_msg}")
        return {"message": error_msg}, 400


@app.get('/tasks', tags=[task_tag],
         responses={"200": TaskListSchema, "404": ErrorSchema})
def get_tasks():
    """Perform the search for all tasks added to the database

    Return a representation of the task list.
    """
    logger.debug(f"Collecting tasks...")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    tasks = session.query(Task).all()

    if not tasks:
        # if there aren`t products in the database
        return {"tasks": []}, 200
    else:
        logger.debug(f"%d tasks found" % len(tasks))
        # reutrns the representation of the tasks
        print(tasks)
        return show_tasks(tasks), 200


@app.get('/task', tags=[task_tag],
         responses={"200": TaskViewSchema, "404": ErrorSchema})
def get_task(query: SearchTaskSchema):
    """Performs the search for a Task based in the id

    Returns a task representation and the associated comments.
    """
    task_id = query.id
    logger.debug(f"Getting the data about the task #{task_id}")
    # creating the database connection
    session = Session()
    # peform the search
    task = session.query(Task).filter(Task.id == task_id).first()

    if not task:
        # if the task was not found
        error_msg = f"Task id '{task_id}' not found in the database :/"
        logger.warning(f"Error while searching the task '{task_id}', {error_msg}")
        return {"message": error_msg}, 404
    else:
        logger.debug(f"Task not found: '{task.name}'")
        # returns the task representation
        return show_task(task), 200


@app.delete('/task/name', tags=[task_tag],
            responses={"200": TaskDelSchema, "404": ErrorSchema})
def del_task_by_name(query: SearchTaskSchemaByName):
    """Delete a task using the name of the task informed

    Return a message confirming the deletion.
    """
    task_name = unquote(query.name)
    print(task_name)
    logger.debug(f"Removing data from the task #{task_name}")
    # create the database connection
    session = Session()
    # performing the delete
    count = session.query(Task).filter(Task.name == task_name).delete()
    session.commit()

    if count:
        # return the message confirmation message representation
        logger.debug(f"Removing task #{task_name}")
        return {"message": "Task removed ", "name": task_name}
    else:
        # if the product was not found
        error_msg = "Task not found in the database :/"
        logger.warning(f"Error while removing the product #'{task_name}', {error_msg}")
        return {"message": error_msg}, 404

@app.delete('/task/id', tags=[task_tag],
            responses={"200": TaskDelSchema, "404": ErrorSchema})
@cross_origin(
    origins=['http://localhost:8080', 'http://127.0.0.1:8080'],
    methods=["DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)
def del_task_by_id(query: SearchTaskSchema):
    """Delete a task using the task id informed

    Return a message confirming the deletion.
    """
    task_id = query.id
    print(task_id)
    logger.debug(f"Removing data from the task #{task_id}")
    # create the database connection
    session = Session()
    # performing the delete
    count = session.query(Task).filter(Task.id == task_id).delete()
    session.commit()

    if count:
        # return the message confirmation message representation
        logger.debug(f"Removing task #{task_id}")
        return {"message": "Task removed ", "name": task_id}
    else:
        # if the product was not found
        error_msg = "Task not found in the database :/"
        logger.warning(f"Error while removing the product #'{task_id}', {error_msg}")
        return {"message": error_msg}, 404

#@app.put('/task/<int:id>',  tags=[task_tag], responses={ "200": TaskUpdateSchema,              "404": ErrorSchema,              "400": ErrorSchema       }        )
@app.route('/task/<int:id>', methods=["PUT", "OPTIONS"])
@cross_origin(
    origins=['http://localhost:8080', 'http://127.0.0.1:8080'], 
    methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)
def update_task(id: int):
    """Update an existing task by its ID

    Returns the updated task if successful.
    """
    logger.debug(f"Updating task with ID: {id}")
    if request.method == "OPTIONS":
        return '', 200

    try:
        # Parse the body using Pydantic manually
        data = request.json
        body = TaskSchema(**data)
    except ValidationError as e:
        return {"message": "Validation failed", "errors": e.errors()}, 400
    except Exception as e:
        return {"message": "Invalid request body", "error": str(e)}, 400

    # Validation for required fields could go here
    if not body:
        return {"message": "Missing required fields"}, 400

    session = Session()
    task = session.query(Task).filter_by(id=id).first()

    if not task:
        logger.warning(f"Task with ID '{id}' not found")
        return {"message": "Task not found"}, 404

    # Check if new name is already taken by another task
    if body.name != task.name:
        name_exists = session.query(Task).filter(Task.name == body.name).first()
        if name_exists:
            logger.warning(f"Task name '{body.name}' already exists")
            return {"message": "Task name already exists"}, 409

    try:
        # Update fields
        task.name = body.name
        task.task_type = body.task_type
        task.product = body.product
        task.priority = body.priority
        task.start_date = body.start_date if body.start_date else None
        task.end_date = body.end_date if body.end_date else None

        session.commit()
        logger.debug(f"Task with ID '{id}' successfully updated")
        return show_task(task), 200

    except IntegrityError:
        session.rollback()
        logger.error(f"IntegrityError while updating task with ID '{id}'")
        return {"message": "Could not update task due to database constraints"}, 400

    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error: {e}")
        return {"message": "An unexpected error occurred"}, 400

@app.post('/comment', tags=[comment_tag],
          responses={"200": TaskViewSchema, "404": ErrorSchema})
def add_comment(form: CommentSchema):
    """Add a new comment to the tasks added to the database. The task is identified by the task id

    Returns the task representation and the comments associated.
    """
    task_id  = form.task_id
    logger.debug(f"Adding comments to the task #{task_id}")
    # create a session to the database
    session = Session()
    # searching the task
    task = session.query(Task).filter(Task.id == task_id).first()

    if not task:
        # if the task was not found
        error_msg = "Task not found in the database :/"
        logger.warning(f"Error while adding the comment in the task '{task_id}', {error_msg}")
        return {"message": error_msg}, 404

    # criando o comentário
    text = form.text
    comment = Comment(text)

    # adding a comment in the task
    task.add_comment(comment)
    session.commit()

    logger.debug(f"Added comment to the task #{task_id}")

    # return the task representation
    return show_task(task), 200
