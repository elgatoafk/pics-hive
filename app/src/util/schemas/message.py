from pydantic import BaseModel


class Message(BaseModel):
    "Schema for message passed in a function"
    detail: str
