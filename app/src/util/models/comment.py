from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.src.util.db import Base

class Comment(Base):
    """
    This class represents a comment in a photo-sharing application.

    Attributes:
    - id (int): The unique identifier of the comment.
    - content (str): The content of the comment.
    - photo_id (int): The foreign key referencing the photo the comment belongs to.
    - user_id (int): The foreign key referencing the user who made the comment.
    - created_at (datetime): The timestamp of when the comment was created.
    - updated_at (datetime): The timestamp of when the comment was last updated.
    - user (User): The user who made the comment.
    - photo (Photo): The photo the comment belongs to.
    """

    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    content = Column(String)
    photo_id = Column(Integer, ForeignKey("photos.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="comments", lazy='selectin')
    photo = relationship("Photo", backref="comments", lazy='selectin')