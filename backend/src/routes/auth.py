from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from backend.src.config import security
from backend.src.config import jwt
from backend.src.util.db import get_db

from datetime import timedelta

from backend.src.util.schemas import user as user_schemas
from backend.src.util.crud import user as user_crud, token as crud_token

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.util.logging_config import logger

router = APIRouter()

@router.post("/signup", response_model=user_schemas.User)
async def signup(user: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    logger.debug('test signup')
    db_user = await user_crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    logger.debug('before create_user')
    result = await user_crud.create_user(db, user)
    return result



@router.get("/me", response_model=user_schemas.User)
async def read_users_me(current_user: user_schemas.User = Depends(security.get_current_user)):
    logger.debug('me - read_users_me')
    return current_user


@router.post("/token", response_model=user_schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    
    logger.debug('token - authenticate_user')    

    user = await security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=jwt.ACCESS_TOKEN_EXPIRE_MINUTES)

    logger.debug('token - create_access_token')

    access_token = await jwt.create_access_token(
        data={"sub": user.email}, user_id=user.id, db=db, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")), db: AsyncSession = Depends(get_db)):
    await crud_token.add_token_to_blacklist(db, token)

    return {"msg": "Successfully logged out"}

