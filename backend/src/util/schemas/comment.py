from datetime import datetime
from pydantic import BaseModel

class CommentBase(BaseModel):
    """
    Base schema for comments containing the content of the comment.
    
    Attributes:
        content (str): The content of the comment.
    """
    content: str

class CommentCreate(CommentBase):
    """
    Schema for creating a new comment.
    Inherits from CommentBase.
    
    Attributes:
        content (str): The content of the comment.
    """
    pass

class CommentUpdate(CommentBase):
    """
    Schema for updating an existing comment.
    Inherits from CommentBase.
    
    Attributes:
        content (str): The updated content of the comment.
    """
    pass

class Comment(CommentBase):
    """
    Schema for returning a comment, includes additional fields.
    
    Attributes:
        id (int): The ID of the comment.
        photo_id (int): The ID of the associated photo.
        user_id (int): The ID of the user who made the comment.
        created_at (datetime): The timestamp when the comment was created.
        updated_at (datetime): The timestamp when the comment was last updated.
    """
    id: int
    photo_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
