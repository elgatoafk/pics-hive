from pydantic import BaseModel

class TagBase(BaseModel):
    tag_name: str

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagResponse(TagBase):
    id: int

    class Config:
        orm_mode = True
