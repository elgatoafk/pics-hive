
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas import user as schema_user
from backend.src.util.db import SessionLocal
from backend.src.config.config import settings
from typing import Optional
from backend.src.util.crud import user as crud_user
from backend.src.util.models import user as model_user
from backend.src.util.db import get_db
from backend.src.config import jwt as config_jwt



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def verify_password(plain_password, hashed_password):
    print('verify_password')
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    print('get_password_hash')
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    print('authenticate_user')
    user = crud_user.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print('security get_current_user')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config_jwt.SECRET_KEY, algorithms=[config_jwt.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schema_user.TokenData(email=email)
        print('token : {}'.format(token_data))

    except JWTError:
        raise credentials_exception
    
    try:
        user = crud_user.get_user_by_email(db, email=token_data.email)
        print(user.email)
    except Exception as e:
        print(f"An error occurred: {e}")  # Logging the error
        raise HTTPException(status_code=500, detail="Internal Server Error")
        

    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: model_user.User = Depends(get_current_user)):
    print('get_current_active_user')
    print(current_user.email)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user