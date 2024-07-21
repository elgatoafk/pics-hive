from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from util.db import get_db
from auth import get_current_user
from util.schemas.comment import Comment, CommentCreate, CommentUpdate
from util.crud.comment import create_comment, get_comments, update_comment, delete_comment
from util.schemas.user import User

router = APIRouter()

@router.post("/photos/{photo_id}/comments/", response_model=Comment)
def create_photo_comment(photo_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_comment(db=db, comment=comment, user_id=current_user.id, photo_id=photo_id)

@router.get("/photos/{photo_id}/comments/", response_model=List[Comment])
def read_photo_comments(photo_id: int, db: Session = Depends(get_db)):
    return get_comments(db=db, photo_id=photo_id)

@router.put("/comments/{comment_id}/", response_model=Comment)
def update_photo_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return update_comment(db=db, comment_id=comment_id, comment=comment)

@router.delete("/comments/{comment_id}/", response_model=Comment)
def delete_photo_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return delete_comment(db=db, comment_id=comment_id)