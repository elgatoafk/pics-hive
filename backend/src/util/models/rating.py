from sqlalchemy import Column, Integer,ForeignKey
from sqlalchemy.orm import relationship
from backend.src.util.db import Base

class Rating(Base):
    """
    This class represents a rating in a photo-sharing application. It is associated with a user and a photo.

    Attributes:
    - id (int): The unique identifier of the rating.
    - rating (int): The rating value, typically an integer between 1 and 5.
    - user_id (int): The foreign key referencing the user who made the rating.
    - photo_id (int): The foreign key referencing the photo being rated.
    - owner (User): The relationship with the User who made the rating.
    - photo (Photo): The relationship with the Photo being rated.
    """

    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    photo_id = Column(Integer, ForeignKey('photos.id'))
    owner = relationship("User")
    photo = relationship("Photo")