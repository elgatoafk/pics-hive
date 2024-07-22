from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
#from backend.src.util.db import Base
from sqlalchemy.ext.declarative import declarative_base 


Base = declarative_base()

def create_models():

    photo_tag = Table('photo_tag', Base.metadata,
                    Column('photo_id', Integer, ForeignKey('photos.id')),
                    Column('tag_id', Integer, ForeignKey('tags.id'))
                )

    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True)
        hashed_password = Column(String)
        disabled = Column(Boolean, default=False)
        role = Column(String)

        photos = relationship("Photo", back_populates="owner")

    class Photo(Base):
        __tablename__ = "photos"

        id = Column(Integer, primary_key=True, index=True)
        url = Column(String)
        description = Column(String)
        owner_id = Column(Integer, ForeignKey("users.id"))

        owner = relationship("User", back_populates="photos")
        tags = relationship("Tag", secondary=photo_tag, back_populates="photos")

    class Tag(Base):
        __tablename__ = "tags"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, unique=True, index=True)
        photos = relationship("Photo", secondary=photo_tag, back_populates="tags")

    class TransformedImage(Base):
        __tablename__ = "transformed_images"

        id = Column(Integer, primary_key=True, index=True)
        original_photo_id = Column(Integer, ForeignKey("photos.id"))
        transformed_url = Column(String)
        qr_code_url = Column(String)

    return User, Photo, Tag, TransformedImage

User, Photo, Tag, TransformedImage = create_models()


