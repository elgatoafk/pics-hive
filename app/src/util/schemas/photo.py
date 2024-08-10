from pydantic import BaseModel, conlist
from typing import List, Optional

from app.src.util.schemas.tag import TagResponse


class PhotoBase(BaseModel):
    description: str
    url: str
    tags: conlist(str, max_length=5)

class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(PhotoBase):
    pass

class PhotoResponse(BaseModel):

    id: int
    user_id: int
    url: str
    description: Optional[str] = "No description provided"
    tags: Optional[List[TagResponse]] = "No tags provided"

    class Config:
        from_attributes = True