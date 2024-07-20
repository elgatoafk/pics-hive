from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

class Tag(Base):
	__tablename__ = 'tags'

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, index=True)
	photos = relationship("Photo",secondary="photo_tags",back_populates="tags")