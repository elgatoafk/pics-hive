from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas import user
from backend.src.util.db import SessionLocal
from backend.src.config.config import settings
from typing import Optional
from backend.src.util.crud import user
from backend.src.util.models import models

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    print('get_db')
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    print('verify_password')
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    print('get_password_hash')
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    print('authenticate_user')
    user = user.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    print('create_access_token')
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print('token : {}'.format(encoded_jwt))
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print('auth get_current_user')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = user.TokenData(email=email)
        print('token : {}'.format(token_data))

    except JWTError:
        raise credentials_exception
    
    user = user.get_user_by_email(db, email=token_data.email)
    print(user.email)

    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    print('get_current_active_user')
    print(current_user.email)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user