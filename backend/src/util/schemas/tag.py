
from pydantic import BaseModel, conlist
from typing import List


class TagCreate(BaseModel):
    name: str

class PhotoTaggingRequest(BaseModel):
    tags: conlist(TagCreate, min_length=1, max_length=5)

class PhotoTaggingResponse(BaseModel):
    photo_id: int
    tags: List[str]

    class Config:
        orm_mode = True
