from pydantic import BaseModel
from typing import List, Optional

class PhotoBase(BaseModel):
    description: Optional[str] = None
    url: str
    tags: Optional[List[str]] = []

class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(PhotoBase):
    pass

class PhotoResponse(BaseModel):
    id: int
    text: str
    user_id: int
    photo_id: int

    class Config:
        orm_mode = True
