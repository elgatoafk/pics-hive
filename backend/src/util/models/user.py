from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from backend.src.util.db import Base
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Class representing user roles."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

class User(AsyncAttrs, Base):
    """
    User model for the users table.

    Attributes:
        id (int): The primary key of the user.
        email (str): The unique email of the user.
        hashed_password (str): The hashed password of the user.
        role (str): The role of the user.
        registered_at (datetime): The timestamp when the user was registered.
        is_active (bool): Indicates if the user is active.
        last_login (datetime): The timestamp of the user's last login.
        photos_uploaded(int): The number of photos uploaded.
    """

    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=None, nullable=True)
    is_active = Column(Boolean, default=True)
    photos_uploaded = Column(Integer, default=0)

    tokens = relationship("Token", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return self.email

    def __str__(self):
        return self.email
