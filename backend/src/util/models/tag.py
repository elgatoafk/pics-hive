
from sqlalchemy import Column, Integer, String, ForeignKey
from backend.src.util.db import Base


class Tag(Base):
    __tablename__ = "tags"
    tag_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tag_name = Column(String, unique=True, nullable=False, index=True)
    
    
    def __repr__(self):
        return self.tag_name

