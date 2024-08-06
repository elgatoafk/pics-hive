from fastapi import APIRouter, Depends, HTTPException, status
from backend.src.config.dependency import role_required
from backend.src.util.models.user import UserRole, User
from backend.src.util.schemas import user as schema_user
from backend.src.util.crud import user as crud_user
from backend.src.util.db import get_db
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.logging_config import log_function
from backend.src.config.security import get_current_user
from fastapi.responses import Response

router = APIRouter()


@router.get("/users", response_model=List[schema_user.User])
@log_function
async def get_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of users with pagination.

    Args:
        skip (int): Number of users to skip.
        limit (int): Maximum number of users to return.
        db (AsyncSession): The database session dependency.

    Returns:
        List[schema_user.User]: A list of users.
    """
    users = await crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schema_user.User)
@log_function
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user by ID.

    Args:
        user_id (int): The ID of the user to retrieve.
        db (AsyncSession): The database session dependency.

    Raises:
        HTTPException: If the user is not found.

    Returns:
        schema_user.User: The retrieved user.
    """
    db_user = await crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/users/ban/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(role_required([UserRole.ADMIN]))])
@log_function
async def ban_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Deactivate a user.

    Args:
        user_id (int): The ID of the user to deactivate.
        db (AsyncSession): The asynchronous database session, obtained via dependency injection.
        current_user (User): The current authenticated user, injected via dependency.

    Returns:
        dict: A message indicating the user has been deactivated.

    Raises:
        HTTPException: If the user to deactivate does not exist.
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await crud_user.deactivate_user(db, user_id)
    return Response(content="User deactivated", status_code=status.HTTP_200_OK, media_type="text/plain")

