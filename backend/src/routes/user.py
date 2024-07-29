from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from backend.src.util.schemas import user as schema_user

from backend.src.util.crud import user as crud_user

from backend.src.config.dependencies import role_required
from backend.src.util.db import get_db
from typing import List
from backend.src.config import security


from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.logging_config import logger
from src.config.security import get_current_active_user
from src.util.crud.user import get_user_profile

router = APIRouter()



@router.get("/", response_model=List[schema_user.User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
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
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
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
    logger.debug('user - read user')
    db_user = await crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



@router.put("/{user_id}", response_model=schema_user.User)
@role_required("admin", "moderator")
async def update_user(
    user_id: int,
    user: schema_user.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: schema_user.User = Depends(security.get_current_active_user)
):
    """
    Update a user by ID.

    Args:
        user_id (int): The ID of the user to update.
        user (schema_user.UserUpdate): The updated user data.
        db (AsyncSession): The database session dependency.
        current_user (schema_user.User): The current authenticated user dependency.

    Raises:
        HTTPException: If the user is not found or the current user does not have enough permissions.

    Returns:
        schema_user.User: The updated user.
    """
    logger.debug('user - update_user - get_user')
    db_user = await crud_user.get_user(db, user_id=user_id)

@router.get("/user/{username}", response_model=schema_user.UserProfile)
async def read_user_profile(username: str, db: Session = Depends(get_db)):
    """
    Retrieve a user profile by username.

    Args:
        username (str): The username of the user to retrieve.
        db (Session): The database session dependency.

    Raises:
        HTTPException: If the user is not found.

    Returns:
        schema_user.UserProfile: The retrieved user profile.
    """
    user_profile = await get_user_profile(db, username)
    if user_profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_profile


@router.put("/{user_id}", response_model=schema_user.User)
@role_required("admin", "moderator")
async def update_user(
    user_id: int,
    user: schema_user.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: schema_user.User = Depends(get_current_active_user)
):
    """
    Update a user by ID.

    Args:
        user_id (int): The ID of the user to update.
        user (schema_user.UserUpdate): The updated user data.
        db (AsyncSession): The database session dependency.
        current_user (schema_user.User): The current authenticated user dependency.

    Raises:
        HTTPException: If the user is not found or the current user does not have enough permissions.

    Returns:
        schema_user.User: The updated user.
    """
    logger.debug('user - update_user - get_user')
    db_user = await get_user_profile(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id != current_user.id and current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    logger.debug('user - update_user')

    updated_user = await crud_user.update_user(db=db, user=db_user, user_update=user)
    return updated_user



@router.delete("/{user_id}", response_model=schema_user.User)

@role_required("admin")
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 

    current_user: schema_user.User = Depends(security.get_current_active_user)

):
    """
    Delete a user by ID.

    Args:
        user_id (int): The ID of the user to delete.
        db (AsyncSession): The database session dependency.
        current_user (schema_user.User): The current authenticated user dependency.

    Raises:
        HTTPException: If the user is not found or the current user does not have enough permissions.

    Returns:
        schema_user.User: The deleted user.
    """
    logger.debug('test - delete_user')
    try:
        logger.debug('start - get_user')

        db_user = await crud_user.get_user(db, user_id=user_id)


        logger.debug('end - get_user')
        
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        logger.debug('start - delete_user')

        deleted_user = await crud_user.delete_user(db=db, user_id=db_user.id)

        logger.debug('end - delete_user')

        return deleted_user
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
