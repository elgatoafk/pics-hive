from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .tag import photo_tag

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="photos")
    tags = relationship("Tag", secondary=photo_tag, back_populates="photos")


class TransformedImage(Base):
    __tablename__ = "transformed_images"

    id = Column(Integer, primary_key=True, index=True)
    original_photo_id = Column(Integer, ForeignKey("photos.id"))
    transformed_url = Column(String)
    qr_code_url = Column(String)    