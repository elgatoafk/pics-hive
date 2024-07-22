from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas import user as schema_user

from backend.src.util.models import models
from backend.src.util.crud import user as crud_user
from backend.src.config import auth 
from backend.src.config.auth import get_db, get_current_active_user, get_password_hash, create_access_token
from backend.src.config.dependencies import get_current_admin


router = APIRouter()

@router.post("/users/", response_model=schema_user.User)
def create_user(user: schema_user.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user.create_user(db=db, user=user)

@router.get("/users/me/", response_model=schema_user.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    print('read_users_me')
    return current_user


@router.get("/users/", response_model=list[schema_user.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    print('read_users')
    users = crud_user.get_users(db, skip=skip, limit=limit)
    print(users)
    return users


@router.post("/token", response_model=schema_user.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

