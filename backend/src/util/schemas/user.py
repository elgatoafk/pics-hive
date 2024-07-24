from pydantic import BaseModel
from typing import List, Optional


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None        

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True #orm_mode = True