from pydantic import BaseModel
from typing import List, Optional
from . import tag



class PhotoBase(BaseModel):
    url: str
    description: Optional[str] = None

class PhotoCreate(PhotoBase):
    tags: Optional[List[tag.TagCreate]] = None

class Photo(PhotoBase):
    id: int
    url: str
    owner_id: int
    tags: List[str] = []

    class Config:
        from_attributes = True #orm_mode = True


class TransformedImageBase(BaseModel):
    original_photo_id: int

class TransformedImageCreate(TransformedImageBase):
    transformed_url: str

class TransformedImage(TransformedImageBase):
    id: int
    transformed_url: str
    qr_code_url: str

    class Config:
        from_attributes = True #orm_mode = True
