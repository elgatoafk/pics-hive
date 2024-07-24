from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

photo_tags = Table(
    'photo_tags', Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True))

class Photo(Base):
	__tablename__ = 'photos'

	id = Column(Integer, primary_key=True, index=True)
	description = Column(String,index=True)
	url = Column(String, index=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	owner = relationship("User", back_populates="photos")
	tags = relationship("Tag",secondary=photo_tags,back_populates="photos")
	comments = relationship("Comment", back_populates="photos")