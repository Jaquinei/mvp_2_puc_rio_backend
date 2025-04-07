from datetime import datetime
from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Task, Comment
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Production Automation Tool API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentation", description="Swagger documentation auto generated")
doc_tag = Tag(name="Choose Documentation", description="Choose which type of documentation do you wish to see")
task_tag = Tag(name="Task", description="Add, visualize and remote the tasks from the database")
comment_tag = Tag(name="Comment", description="Add a comment to the task added to the database")


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
        end_date=form.end_date if form.end_date else None)
    logger.debug(f"Adding task name: '{task.name}'")
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
        error_msg = "Task name already saved in the database :/"
        logger.warning(f"Error while adding the product '{task.name}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Was not possible to save the new item :/"
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


@app.delete('/task', tags=[task_tag],
            responses={"200": TaskDelSchema, "404": ErrorSchema})
def del_task(query: SearchTaskSchemaByName):
    """Delete a task using the name of the task informed

    Return a message confirming the deletion.
    """
    task_name = unquote(unquote(query.name))
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
