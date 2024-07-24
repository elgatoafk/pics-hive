feature/adding-comments
from sqlalchemy.orm import Session
from datetime import datetime
from models.comment import Comment
from schemas.comment import CommentCreate, CommentUpdate

def create_comment(db: Session, comment: CommentCreate, user_id: int, photo_id: int):
    db_comment = Comment(**comment.dict(), user_id=user_id, photo_id=photo_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments(db: Session, photo_id: int):
    return db.query(Comment).filter(Comment.photo_id == photo_id).all()

def update_comment(db: Session, comment_id: int, comment: CommentUpdate):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db_comment.content = comment.content
        db_comment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment

