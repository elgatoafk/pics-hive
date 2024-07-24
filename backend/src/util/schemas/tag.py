
from pydantic import BaseModel
from typing import List, Optional



class TagBase(BaseModel):
    name: str

class TagCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True #orm_mode = True


class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True #orm_mode = True



