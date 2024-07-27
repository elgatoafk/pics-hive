#from sqlalchemy import Column, Integer, String, Boolean
#from sqlalchemy.orm import relationship
#from .base import Base

#class User(Base):
#    __tablename__ = "users"

#    id = Column(Integer, primary_key=True, index=True)
#    email = Column(String, unique=True, index=True)
#    hashed_password = Column(String)
#    disabled = Column(Boolean, default=False)
#    role = Column(String)

#    photos = relationship("Photo", back_populates="owner")
#    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")


from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from .base import Base

class User(AsyncAttrs, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(String)

    photos = relationship("Photo", back_populates="owner")
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")    