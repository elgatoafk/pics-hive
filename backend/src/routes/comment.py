from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List

from backend.src.config.logging_config import log_function
from backend.src.util.crud.photo import get_photo
from backend.src.util.db import get_db
from backend.src.config.security import get_current_user
from backend.src.util.models.user import UserRole
from backend.src.util.schemas.comment import CommentCreate, CommentUpdate, Comment
from backend.src.util.crud.comment import delete_comment, create_comment, update_comment, get_comments, \
    get_comment_by_id, get_user_comment
from backend.src.util.schemas.user import User
from backend.src.config.dependency import role_required

router = APIRouter()


@router.post("/photos/{photo_id}/comments/", response_model=Comment)
@log_function
async def create_photo_comment(photo_id: int, comment: CommentCreate, db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
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
    photo = await get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return await create_comment(db=db, comment=comment, user_id=current_user.id, photo_id=photo_id)


@router.get("/photos/{photo_id}/comments/", response_model=List[Comment])
@log_function
async def read_photo_comments(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve all comments for a specific photo.

    Args:
        photo_id (int): The ID of the photo to get comments for.
        db (Session): The database session dependency.

    Returns:
        List[Comment]: A list of comments for the specified photo.
    """
    photo = await get_photo(db, photo_id)
    return await get_comments(db=db, photo_id=photo_id)


@router.put("/comments/{comment_id}/", response_model=Comment)
@log_function
async def update_photo_comment(comment_id: int, comment: CommentUpdate,
                               db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a specific comment.

    Args:
        comment_id (int): The ID of the comment to update.
        comment (CommentUpdate): The comment data to update.
        db (AsyncSession): The database session dependency.
        current_user (User): The current authenticated user dependency.

    Raises:
        HTTPException: If the comment is not found or does not belong to the current user.

    Returns:
        Comment: The updated comment.
    """

    db_comment = await get_user_comment(db, current_user.id, comment_id)
    if db_comment:
        return await update_comment(db=db, comment_id=comment_id, comment=comment)

@router.delete("/comments/{comment_id}/", response_model=Comment,
               dependencies=[Depends(role_required([UserRole.ADMIN, UserRole.MODERATOR]))])
@log_function
async def delete_photo_comment(comment_id: int, db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Delete a specific comment.

    Args:
        comment_id (int): The ID of the comment to delete.
        db (Session): The database session dependency.
        current_user (User): The current authenticated user dependency.

    Returns:
        Comment: The deleted comment.
    """
    result = await get_comment_by_id(db, comment_id)
    return await delete_comment(db=db, comment_id=result.id)
