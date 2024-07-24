from sqlalchemy import Column, Integer,ForeignKey
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

class Rating(Base):
	__tablename__ = 'ratings'

	id = Column(Integer, primary_key=True, index=True)
	rating = Column(Integer, index=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	photo_id = Column(Integer, ForeignKey('photos.id'))
	owner = relationship("User")
	photo = relationship("Photo")