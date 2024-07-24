from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas import user as schema_user
from backend.src.util.models import user as model_user
from backend.src.util.crud import user as crud_user
from backend.src.config.dependencies import get_current_admin
from backend.src.util.db import get_db
from backend.src.util import db
from typing import List
from backend.src.config import security

router = APIRouter()


@router.get("/", response_model=List[schema_user.User])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(db.get_db)):
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schema_user.User)
async def read_user(user_id: int, db: Session = Depends(db.get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schema_user.User)
async def update_user(user_id: int, user: schema_user.UserUpdate, db: Session = Depends(db.get_db), current_user: schema_user.User = Depends(security.get_current_user)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated_user = crud_user.update_user(db=db, user=db_user, user_update=user)
    return updated_user

@router.delete("/{user_id}", response_model=schema_user.User)
async def delete_user(user_id: int, db: Session = Depends(db.get_db), current_user: schema_user.User = Depends(security.get_current_user)):
    try:
        print('delete_user')
        db_user = crud_user.get_user(db, user_id=user_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if db_user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        crud_user.delete_user(db=db, user=db_user)
        return db_user
    except Exception as e:
        print(f"An error occurred: {e}")  # Logging the error
        raise HTTPException(status_code=500, detail="Internal Server Error")