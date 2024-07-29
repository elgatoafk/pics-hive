from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from .base import Base


class User(AsyncAttrs, Base):
    """
    Represents a user in the application.

    Attributes:
    - id (int): Unique identifier for the user.
    - email (str): User's email address.
    - hashed_password (str): Hashed version of the user's password.
    - disabled (bool): Indicates whether the user is disabled or not.
    - role (str): User's role in the application.

    Relationships:
    - photos (List[Photo]): List of photos owned by the user.
    - tokens (List[Token]): List of tokens associated with the user.
    """

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
    comments = relationship("Comment", back_populates="user")
