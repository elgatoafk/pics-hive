
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.src.util.db import get_db
from backend.src.config.security import get_current_user
from backend.src.util.schemas.comment import Comment, CommentCreate, CommentUpdate
from backend.src.util.crud.comment import delete_comment, create_comment, update_comment, get_comments
from backend.src.util.schemas.user import User

from backend.src.config.dependencies import role_required

router = APIRouter()

@router.post("/photos/{photo_id}/comments/", response_model=Comment)
async def create_photo_comment(photo_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new comment for a specific photo.

    Args:
        photo_id (int): The ID of the photo to comment on.
        comment (CommentCreate): The comment data to create.
        db (Session): The database session dependency.
        current_user (User): The current authenticated user dependency.

    Returns:
        The created comment.
    """
    return await create_comment(db=db, comment=comment, user_id=current_user.id, photo_id=photo_id)

@router.get("/photos/{photo_id}/comments/", response_model=List[Comment])
async def read_photo_comments(photo_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all comments for a specific photo.

    Args:
        photo_id (int): The ID of the photo to get comments for.
        db (Session): The database session dependency.

    Returns:
        List[Comment]: A list of comments for the specified photo.
    """
    return await get_comments(db=db, photo_id=photo_id)

@router.put("/comments/{comment_id}/", response_model=Comment)
async def update_photo_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a specific comment.

    Args:
        comment_id (int): The ID of the comment to update.
        comment (CommentUpdate): The comment data to update.
        db (Session): The database session dependency.
        current_user (User): The current authenticated user dependency.

    Raises:
        HTTPException: If the comment is not found or does not belong to the current user.

    Returns:
        Comment: The updated comment.
    """
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return await update_comment(db=db, comment_id=comment_id, comment=comment)

@router.delete("/comments/{comment_id}/", response_model=Comment)
@role_required("admin", "moderator")
async def delete_photo_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a specific comment.

    Args:
        comment_id (int): The ID of the comment to delete.
        db (Session): The database session dependency.
        current_user (User): The current authenticated user dependency.

    Raises:
        HTTPException: If the comment is not found or does not belong to the current user.

    Returns:
        Comment: The deleted comment.
    """
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return await delete_comment(db=db, comment_id=comment_id)

