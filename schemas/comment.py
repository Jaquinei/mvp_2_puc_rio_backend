from pydantic import BaseModel


class CommentSchema(BaseModel):
    """ Define a new comment to be added
    """
    task_id: int = 1
    text: str = "A simple text comment!"
