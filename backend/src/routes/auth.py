from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
#from src.util.schemas.user import UserCreate, User
from src.config import security
from src.config.jwt import create_access_token
from src.util import db
from src.util.db import get_db
#from src.util.models.user import User as UserModel
#from src.util.crud.user import get_user_by_username, create_user

from datetime import timedelta

from ..util import db
from ..util.schemas import user as user_schemas
from ..util.crud import user as user_crud
from ..config import security, jwt

router = APIRouter()

@router.post("/signup", response_model=user_schemas.User)
async def signup(user: user_schemas.UserCreate, db: Session = Depends(db.get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db=db, user=user)

@router.post("/login", response_model=user_schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)):
    db_user = security.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=user_schemas.User)
async def read_users_me(current_user: user_schemas.User = Depends(security.get_current_user)):
    return current_user


@router.post("/token", response_model=user_schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=jwt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

