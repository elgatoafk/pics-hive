from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from backend.src.util.models.comment import Comment
from backend.src.util.schemas.comment import CommentCreate, CommentUpdate
from sqlalchemy.future import select


async def create_comment(db: AsyncSession,comment: CommentCreate, user_id: int, photo_id: int):
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
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def get_comments(db: AsyncSession, photo_id: int):
    """
    Retrieve all comments for a specific photo.

    Args:
        db (Session): The database session.
        photo_id (int): The ID of the photo.

    Returns:
        List[Comment]: A list of comments for the photo.
    """
    result = await db.execute(select(Comment).filter(Comment.photo_id == photo_id))
    return result.scalars().all()

async def update_comment(db: AsyncSession, comment_id: int, comment: CommentUpdate):
    """
    Update an existing comment in the database.

    Args:
        db (Session): The database session.
        comment_id (int): The ID of the comment to update.
        comment (CommentUpdate): The comment update schema.

    Returns:
        Comment: The updated comment object.
    """
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    db_comment = result.scalars().first()

    if db_comment:
        db_comment.content = comment.content
        db_comment.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_comment)
    return db_comment

async def delete_comment(db: AsyncSession, comment_id: int ):
    """
    Delete a comment from the database.

    Args:
        db (Session): The database session.
        comment_id (int): The ID of the comment to delete.

    Returns:
        Comment: The deleted comment object.
    Raises:
        HTTPException: If the comment is not found.
    """
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    db_comment = result.scalars().first()

    if db_comment:
        await db.delete(db_comment)
        await db.commit()
        return db_comment

    raise HTTPException(status_code=404, detail="Comment not found")

