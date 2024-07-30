from pydantic import BaseModel
from typing import List, Optional

class PhotoBase(BaseModel):
    """
    This class represents the base model for a photo, used for creating, updating, and retrieving photo information.
    It is a subclass of Pydantic's BaseModel and supports optional fields for description and tags.

    Attributes:
    description (Optional[str]): An optional description of the photo.
    url (str): The URL of the photo.
    tags (Optional[List[str]]): An optional list of tags associated with the photo.

    Note:
    This class is used as a base model for other photo-related classes (PhotoCreate, PhotoUpdate, PhotoResponse).
    """
    description: Optional[str] = None
    url: str
    tags: Optional[List[str]] = []

class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(PhotoBase):
    pass

class PhotoResponse(BaseModel):
    """
    This class represents a response for a photo, including its ID, text, user ID, and photo ID.
    It is designed to be used with Pydantic's BaseModel and supports ORM mode for database operations.

    Attributes:
    id (int): The unique identifier of the photo.
    text (str): Additional text associated with the photo.
    user_id (int): The ID of the user who owns the photo.
    photo_id (int): The ID of the photo itself.

    Config:
    orm_mode (bool): A flag indicating that this model should be used in ORM mode.
    """
    id: int
    text: str
    user_id: int
    photo_id: int

    class Config:
        from_attributes = True  #orm_mode = True

