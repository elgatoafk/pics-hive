from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str
    password: str
class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    photos: List['PhotoResponse'] = []
    is_active: bool

    class Config:
        orm_mode = True