from sqlalchemy.orm import Session
from models import Tag
from schemas import TagCreate, TagUpdate

def create_tag(session: Session, tag_data: TagCreate):
    new_tag = Tag(tag_name=tag_data.tag_name)
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)
    return new_tag

def get_tag(session: Session, tag_id: int):
    return session.query(Tag).filter(Tag.id == tag_id).first()

def get_all_tags(session: Session):
    return session.query(Tag).all()

def update_tag(session: Session, tag_id: int, tag_data: TagUpdate):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        tag.tag_name = tag_data.tag_name
        session.commit()
        session.refresh(tag)
    return tag

def delete_tag(session: Session, tag_id: int):
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        session.delete(tag)
        session.commit()
    return tag