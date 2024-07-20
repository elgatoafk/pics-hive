from pydantic import BaseModel

class CommentBase(BaseModel):
    text : str

class CommentCreate(CommentBase):
    photo_id: int

class commentResponse(CommentBase):
    id: int
    user_id: int
    photo_id: int

    class Config:
        orm_mode = True