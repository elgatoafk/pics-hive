from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas.user import User, UserUpdate, UserCreate, UserProfile
from backend.src.util.models import user as model_user
from backend.src.config.dependencies import role_required
from backend.src.util.db import get_db
from backend.src.util import db
from typing import List
from backend.src.config.security import get_current_user, get_current_active_user
from util.crud.user import get_user_by_username, get_user_profile, update_user, deactivate_user

from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.logging_config import logger

router = APIRouter()


@router.get("/user/{username}", response_model=UserProfile)
async def read_user_profile(username: str, db: Session = Depends(get_db)):
    user_profile = await get_user_profile(db, username)
    if user_profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_profile


@router.put("/{user_id}", response_model=User)
@role_required("admin", "moderator")
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    logger.debug('user - update_user - get_user')
    db_user = await get_user_profile(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id != current_user.id and current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    logger.debug('user - update_user')
    updated_user = await update_user(db=db, user=db_user, user_update=user)
    return updated_user


@router.put("/users/me", response_model=UserProfile)
async def update_user_info(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await update_user(db, current_user.id, user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/me", response_model=UserProfile)
async def read_current_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_user_profile(db, current_user.username)

@router.put("/users/{user_id}/deactivate", response_model=UserProfile)
@role_required("admin")
async def deactivate_user_account(user_id: int, db: Session = Depends(get_db)):
    user = await deactivate_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.delete("/{user_id}", response_model=User)
@role_required("admin")
async def delete_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    logger.debug('test - delete_user')
    try:
        logger.debug('start - get_user')
        db_user = await get_user_profile(db, user_id=user_id)
        logger.debug('end - get_user')
        
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        logger.debug('start - delete_user')
        deleted_user = await delete_user(db=db, user_id=db_user.id)
        logger.debug('end - delete_user')

        return deleted_user
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
