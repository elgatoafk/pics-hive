from sqlalchemy.orm import Session
from fastapi import Depends
from backend.src.util.db import get_db
from backend.src.util.models.tag import Tag
from backend.src.util.schemas.tag import TagCreate


def get_tag(tag_name: str, db:Session = Depends(get_db)) -> Tag:
    return db.query(Tag).filter(Tag.name == tag_name).first()

def create_tag(body: TagCreate, db:Session = Depends(get_db)) -> Tag:
	tag_db = Tag(name=body.name)
	db.add(tag_db)
	db.commit()
	db.refresh(tag_db)
	return tag_db

def update_tag() :
	pass

def delete_tag() :
    pass


