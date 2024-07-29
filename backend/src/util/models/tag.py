from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .photo import photo_m2m_tag

class Tag(Base):
    """
    A class representing a Tag in the database.

    Attributes
    ----------
    __tablename__ : str
        The name of the table in the database.
    tag_id : sqlalchemy.Column
        The primary key column for the Tag.
    tag_name : sqlalchemy.Column
        The unique name of the Tag.

    Methods
    -------
    __repr__()
        Returns a string representation of the Tag.
    """

    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tag_name = Column(String, unique=True, nullable=False, index=True)
    photos = relationship("Photo", secondary=photo_m2m_tag, back_populates="tags")


    def __repr__(self):
        """
        Returns a string representation of the Tag.

        Returns
        -------
        str
            The tag_name of the Tag.
        """
        return self.tag_name


