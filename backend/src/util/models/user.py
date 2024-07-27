
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from util.db import Base
from datetime import datetime

class User(AsyncAttrs, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(String)
    registered_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    photos = relationship("Photo", back_populates="owner")
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")    
