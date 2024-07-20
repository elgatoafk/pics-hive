from sqlalchemy import String,Integer,Boolean,Column
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, index=True)
	email = Column(String, unique=True, index=True)
	password_hash = Column(String)
	is_active = Column(Boolean, default=True)
	is_admin = Column(Boolean, default=False)
	is_moderator= Column(Boolean, default=False)
	photos = relationship("Photo", back_populates="owner")
	comments = relationship("Comment", back_populates="owner")