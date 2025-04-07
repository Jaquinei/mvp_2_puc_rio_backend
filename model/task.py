from sqlalchemy import Column, String, Integer, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from model import Base, Comment


class Task(Base):
    __tablename__ = 'task'

    id = Column("pk_task", Integer, primary_key=True)
    name = Column(String(140), unique=True)    
    task_type = Column(Integer)
    product = Column(String(140), unique=True)
    priority = Column(SmallInteger)
    insertion_date = Column(DateTime, default=datetime.now())
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    # Definição do relacionamento entre o produto e o comentário.
    # Essa relação é implicita, não está salva na tabela 'produto',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    comments = relationship("Comment")

    def __init__(self, name:str, task_type:int, product:str, priority: int,
                 insertion_date:Union[DateTime, None] = None,
                 start_date:Union[DateTime, None] = None,
                 end_date: Union[DateTime, None] = None
                 ):
        """
        Create Task

        Arguments:
            name: name of the task
            task_type: the task type
            product: which product the task is related
            priority: the priority of the task            
            insertion_date: insertion date the task was added to the database
            start_date: date the task started
            end_date: date the task ended
            
            
        """
        self.name = name
        self.task_type = task_type
        self.product = product
        self.start_date = start_date
        self.end_date = end_date
        self.priority = priority

        # if not specified, will be the exact date/time it was added to the database
        if insertion_date:
            self.insertion_date = insertion_date
        
        if start_date:
            self.start_date = start_date

        if end_date:
            self.start_date = end_date


    def add_comment(self, comment:Comment):
        """ Add a new comment in a task
        """
        self.comments.append(comment)

