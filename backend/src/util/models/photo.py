from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

photo_m2m_tag = Table(
    "photo_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo", Integer, ForeignKey("photos.id", ondelete="CASCADE")),
    Column("tag", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
    extend_existing=True)


class Photo(Base):
    """
    This class represents a photo in the application. It is associated with a user,
    can have multiple tags, and can have comments.

    Attributes:
    id (int): The unique identifier of the photo.
    description (str): A brief description of the photo.
    url (str): The URL of the photo.
    user_id (int): The foreign key to the user who owns the photo.
    owner (User): The user who owns the photo.
    tags (List[Tag]): The list of tags associated with the photo.
    comments (List[Comment]): The list of comments associated with the photo.
    """

    __tablename__ = 'photos'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    description = Column(String)
    url = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="photos")
    tags = relationship("Tag", secondary=photo_m2m_tag, back_populates="photos")
    comments = relationship ('Comment', back_populates='photo')