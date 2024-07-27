from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None        

class BlacklistedToken(BaseModel):
    token: str
    blacklisted_on: datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    role: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UserProfile(UserBase):
    id: int
    full_name: Optional[str] = None
    registered_at: datetime
    is_active: bool
    photos_count: int

class User(UserBase):
    id: int

    class Config:
        from_attributes = True #orm_mode = True
