from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from typing import Union

from  model import Base


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    text = Column(String(4000))
    insertion_date = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre o comentário e um produto.
    # Aqui está sendo definido a coluna 'produto' que vai guardar
    # a referencia ao produto, a chave estrangeira que relaciona
    # um produto ao comentário.
    task = Column(Integer, ForeignKey("task.pk_task"), nullable=False)

    def __init__(self, text:str, insertion_date:Union[DateTime, None] = None):
        """
        Add a new CommentCria um Comentário

        Arguments:
            text: commentary text.
            insertion_date: the datetime the comment was added to the datbase
        """
        self.text = text
        if insertion_date:
            self.insertion_date = insertion_date