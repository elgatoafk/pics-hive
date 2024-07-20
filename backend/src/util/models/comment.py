from sqlalchemy import Column, \
	Integer, \
	String, \
	ForeignKey
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

class Comment(Base):
	__tablename__ = 'comments'

	id = Column (Integer,primary_key=True)
	text = Column (String)
	user_id = Column (Integer,ForeignKey ('users.id'))
	photo_id = Column (Integer,ForeignKey ('photos.id'))
	owner = relationship ("User",back_populates="comments")
	photo = relationship ("Photo",back_populates="comments")