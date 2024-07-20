from sqlalchemy.orm import Session
from fastapi import Depends
from backend.src.util.db import get_db
from backend.src.util.models.comment import Comment
from backend.src.util.schemas.comment import CommentCreate


def get_comment(comment_id: int, db:Session = Depends(get_db)) -> Comment:
    return db.query(Comment).filter(Comment.id == comment_id).first()

def create_comment(body: CommentCreate, user_id : int, db:Session = Depends(get_db)) -> Comment:
	db_comment = Comment(**body.dict(), user_id=user_id)
	db.add(db_comment)
	db.commit()
	db.refresh(db_comment)
	return db_comment

def update_comment() :
	pass

def delete_comment() :
    pass


