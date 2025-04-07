from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from model.task import Task

from schemas import CommentSchema


class TaskSchema(BaseModel):
    """ Define a new task to be inserted
    """
    name: str = "Build Project"
    task_type: int = 1
    product: str = "Product 01"
    priority: int = Field (gt=0, lt=10)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @validator('start_date', 'end_date', pre=True)
    def validate_date_field(cls, v):
        if v == "":
            return None
        return v

class SearchTaskSchemaByName(BaseModel):
    """ Define who will be the structure that represents the search. It will be
        done oly based on the name of the task
    """
    name: str = "Build"

class SearchTaskSchema(BaseModel):
    """ Define who will be the structure that represents the search. It will be
        done oly based on the name of the task
    """
    id: int = 1


class TaskListSchema(BaseModel):
    """ Define a list of tasks that will be returned
    """
    tasks:List[TaskSchema]


def show_tasks(tasks: List[Task]):
    """ Returns the task representation following the schema defined in    
        TaskViewSchema
    """
    result = []
    for task in tasks:
        result.append({
            "name": task.name,
            "task_type": task.task_type,
            "product": task.product,
            "priority": task.priority,
            "start_date": task.start_date,
            "end_date": task.end_date,
        })

    return {"tasks": result}


class TaskViewSchema(BaseModel):
    """ Define how the task will return: task + comments
    """
    id: int = 1
    name: str = "Build"
    task_type: int = 12
    product: int = 12
    priority: int = 1
    start_date: datetime
    end_date: datetime
    qtde_comments: int = 1
    comments:List[CommentSchema]


class TaskDelSchema(BaseModel):
    """ Define how will be the structured data returned after a delete
        requisition
    """
    message: str
    name: str

def show_task(task: Task):
    """ Returns the task representation following the defined schema
        TaskViewSchema
    """ 
    return {
        "id": task.id,
        "name": task.name,
        "task_type": task.task_type,
        "product": task.product,
        "priority": task.priority,
        "start_date": task.start_date,
        "end_date": task.end_date,
        "qtde_comments": len(task.comments),
        "comments": [{"text": c.text} for c in task.comments]
    }