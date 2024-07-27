from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

# Many-to-Many relationship table between Image and Tag
photo_m2m_tag = Table(
    "photo_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo", Integer, ForeignKey("photos.id", ondelete="CASCADE")),
    Column("tag", Integer, ForeignKey("tags.id", ondelete="CASCADE")),

class Photo(Base):
	__tablename__ = 'photos'

	id = Column(Integer, primary_key=True, index=True)
	description = Column(String,index=True)
	url = Column(String, index=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	owner = relationship("User", back_populates="photos")
	tags = relationship("Tag",secondary=photo_m2m_tag,back_populates="photos")
	comments = relationship("Comment", back_populates="photos")

