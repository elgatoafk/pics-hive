from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List
from app.src.config.logging_config import log_function
from app.src.util.crud.photo import get_photo
from app.src.util.db import get_db
from app.src.config.security import get_current_user
from app.src.util.models.comment import Comment
from app.src.util.models.user import UserRole
from app.src.util.schemas.comment import Comment as CommentSchema
from app.src.util.crud.comment import delete_comment, create_comment, update_comment, get_comments, \
    get_user_comment, get_comment_by_id
from app.src.util.schemas.user import User
from app.src.config.dependency import role_required
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.post("/photos/create_comment/{photo_id}/")
@log_function
async def create_photo_comment(photo_id: int, content: str = Form(...), db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(get_current_user), next: str = Form("/")):
    """
    Create a new comment for a specific photo.

    Args:
        photo_id (int): The ID of the photo to comment on.
        content(str) The comment data to create.
        db (Session): The database session dependency.
        current_user (User): The current authenticated user dependency.
        next (str): The next URL to redirect to.

    Returns:
        The created comment.
    """
    photo = await get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    await create_comment(db=db, comment=content, user_id=current_user.id, photo_id=photo_id)
    return RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)


@router.get("/photos/{photo_id}/comments/", response_model=List[CommentSchema])
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


@router.put("/comments/{comment_id}/", response_model=CommentSchema)
@log_function
async def update_photo_comment(comment_id: int, comment_content: str = Form(...),
                               db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a specific comment and redirect to the photo detail view.

    Args:
        comment_id (int): The ID of the comment to update.
        comment_content (str): The new content for the comment.
        db (AsyncSession): The database session dependency.
        current_user (User): The current authenticated user dependency.

    Raises:
        HTTPException: If the comment is not found or does not belong to the current user.

    Returns:
        RedirectResponse: Redirects to the photo detail view after updating the comment.
    """

    db_comment = await get_user_comment(db, current_user.id, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    update_data = CommentUpdate(content=comment_content)
    await update_comment(db=db, comment_id=comment_id, comment=update_data)

    return RedirectResponse(url=f"/photo/{db_comment.photo_id}", status_code=status.HTTP_302_FOUND)


@router.delete("/comments/{comment_id}/", response_model=CommentSchema,
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

    Raises:
        HTTPException: If the comment is not found or does not belong to the current user.

    Returns:
        Comment: The deleted comment.
    """
    result = await get_comment_by_id(db, comment_id)
    await delete_comment(db=db, comment_id=result.id)
    return RedirectResponse(url="/admin/comments", status_code=status.HTTP_303_SEE_OTHER)
