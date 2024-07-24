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
def update_tag(body: TagCreate, tag_id: int, db:Session = Depends(get_db)) -> Tag:
    tag_db = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag_db:
        tag_db.name = body.name
        db.commit()
        db.refresh(tag_db)
        return tag_db
def delete_tag(tag_name: str, db:Session = Depends(get_db)) -> Tag:
    tag_db = db.query(Tag).filter(Tag.name == tag_name).first()
    if tag_db:
        db.delete(tag_db)
        db.commit()
        db.refresh(tag_db)
        return tag_db


