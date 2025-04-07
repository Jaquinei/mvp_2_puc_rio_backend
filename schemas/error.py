from pydantic import BaseModel


class ErrorSchema(BaseModel):
    """ Define how the error message will be represented
    """
    mesage: str
