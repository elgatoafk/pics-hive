from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.src.config.config import settings
from typing import Optional

from datetime import datetime, timedelta
from jose import JWTError, jwt

from backend.src.util.models import token as crud_token
from backend.src.util.schemas.user import TokenData

from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.db import get_db

from backend.src.util.logging_config import logger


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


async def create_access_token(data: dict, user_id: int, db: AsyncSession, expires_delta: Optional[timedelta] = None):
    logger.debug('create_access_token test')
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Store the token in the tokens table
    token = crud_token.Token(
        token=encoded_jwt,
        user_id=user_id,
        expires_at=expire
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)

    return encoded_jwt




def verify_token(token: str, db: Session = Depends(get_db)):
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
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    if crud_token.is_token_blacklisted(db, token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted")
    
    return token_data




