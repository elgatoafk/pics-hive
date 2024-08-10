from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.src.util.db import Base
from app.src.util.models.photo import photo_m2m_tag


class Tag(Base):
    """
    A class representing a Tag in the database.

    Attributes
    ----------
    __tablename__ : str
        The name of the table in the database.
    tag_id : sqlalchemy.Column
        The primary key column for the Tag.
    name : sqlalchemy.Column
        The unique name of the Tag.

    Methods
    -------
    __repr__()
        Returns a string representation of the Tag.
    """

    __tablename__ = "tags"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    photos = relationship("Photo", secondary=photo_m2m_tag, back_populates="tags", lazy='selectin')

    def __repr__(self):
        return f"<Tag(tag_name={self.name})>"
