from pydantic import BaseModel, validator
from typing import List, Optional
from . import tag


class PhotoBase(BaseModel):
    url: str
    description: Optional[str] = None
    tags: List[str] = []

    @validator('tags')
    def validate_tags(cls, tags):
        if len(tags) > 5:
            raise ValueError('A photo cannot have more than 5 tags.')
        return tags

    class Config:
        from_attributes = True  # orm_mode = True


class PhotoCreate(BaseModel):
    url: str
    description: Optional[str] = None
    tags: Optional[List[tag.TagCreate]] = None


class Photo(PhotoBase):
    id: int
    owner_id: int
    tags: List[str] = []

    class Config:
        from_attributes = True  # orm_mode = True


class TransformedImageBase(BaseModel):
    original_photo_id: int


class TransformedImageCreate(TransformedImageBase):
    transformed_url: str


class TransformedImage(TransformedImageBase):
    id: int
    transformed_url: str
    qr_code_url: str

    class Config:
        from_attributes = True  # orm_mode = True
