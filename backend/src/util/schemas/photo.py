from pydantic import BaseModel, conlist
from typing import List, Optional

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
    description: str
    tags: List[str] = []

    class Config:
        orm_mode = True
        from_attributes = True

