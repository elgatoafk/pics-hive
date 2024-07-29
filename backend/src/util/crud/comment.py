from sqlalchemy.orm import Session
from datetime import datetime
from backend.src.util.models.comment import Comment
from backend.src.util.schemas.comment import CommentCreate, CommentUpdate

def create_comment(db: Session, comment: CommentCreate, user_id: int, photo_id: int):
    """
    Create a new comment in the database.

    Args:
        db (Session): The database session.
        comment (CommentCreate): The comment creation schema.
        user_id (int): The ID of the user creating the comment.
        photo_id (int): The ID of the photo being commented on.

    Returns:
        Comment: The created comment object.
    """
    db_comment = Comment(**comment.dict(), user_id=user_id, photo_id=photo_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments(db: Session, photo_id: int):
    """
    Retrieve all comments for a specific photo.

    Args:
        db (Session): The database session.
        photo_id (int): The ID of the photo.

    Returns:
        List[Comment]: A list of comments for the photo.
    """
    return db.query(Comment).filter(Comment.photo_id == photo_id).all()

def update_comment(db: Session, comment_id: int, comment: CommentUpdate):
    """
    Update an existing comment in the database.

    Args:
        db (Session): The database session.
        comment_id (int): The ID of the comment to update.
        comment (CommentUpdate): The comment update schema.

    Returns:
        Comment: The updated comment object.
    """
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db_comment.content = comment.content
        db_comment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    """
    Delete a comment from the database.

    Args:
        db (Session): The database session.
        comment_id (int): The ID of the comment to delete.

    Returns:
        Comment: The deleted comment object.
    """
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment

