from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.src.config.logging_config import log_function
from app.src.util.crud.photo import get_photo
from app.src.util.models.comment import Comment
from app.src.util.schemas.comment import CommentUpdate
from sqlalchemy.future import select

@log_function
async def create_comment(db: AsyncSession, comment: str, user_id: int, photo_id: int):
    """
    Creates a new comment in the database.

    Parameters:
    db (AsyncSession): The database session.
    comment (CommentCreate): The comment data.
    user_id (int): The ID of the user making the comment.
    photo_id (int): The ID of the photo being commented on.

    Returns:
    Comment: The created comment.

    Raises:
    HTTPException: If the photo is not found.
    """
    photo_result = await get_photo(db, photo_id)
    if not photo_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    new_comment = Comment(
        content=comment,
        photo_id=photo_id,
        user_id=user_id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

@log_function
async def get_comments(db: AsyncSession, photo_id: int):
    """
    Retrieve all comments for a specific photo.

    Args:
        db (AsyncSession): The database session.
        photo_id (int): The ID of the photo.

    Returns:
        List[Comment]: A list of comments for the photo.

    Raises:
        HTTPException: If the photo is not found or if there is a database error.
    """
    try:

        photo_result = await get_photo(db, photo_id)
        if not photo_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
        comments_result = await db.execute(select(Comment).filter(Comment.photo_id == photo_id))
        comments = comments_result.scalars().all()
        return comments

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@log_function
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

@log_function
async def get_comment_by_id(db: AsyncSession, comment_id: int):
    """
    Retrieve a specific comment by its ID.

    Args:
        db (AsyncSession): The database session.
        comment_id (int): The ID of the comment to retrieve.

    Returns:
        Comment: The retrieved comment.

    Raises:
        HTTPException: If the comment is not found.
    """
    try:

        result = await db.execute(select(Comment).filter(Comment.id == comment_id))
        comment = result.scalars().first()

        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

        return comment

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@log_function
async def delete_comment(db: AsyncSession, comment_id: int):
    """
    Delete a comment from the database.

    Args:
        db (Session): The database session.
        comment_id (int): The ID of the comment to delete.

    Returns:
        Comment: The deleted comment object.
        """
    db_comment = await get_comment_by_id(db, comment_id)

    await db.delete(db_comment)
    await db.commit()
    return db_comment

@log_function
async def get_user_comment(db: AsyncSession, user_id: int, comment_id: int):
    """
    Retrieve a specific comment by a user.

    Args:
        db (AsyncSession): The database session dependency.
        user_id (int): The ID of the user who made the comment.
        comment_id (int): The ID of the comment to retrieve.

    Raises:
        HTTPException: If the comment is not found.

    Returns:
        Comment: The retrieved comment.
    """
    result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.user_id == user_id))
    db_comment = result.scalars().first()
    if db_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return db_comment
