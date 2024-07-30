from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas import user
from backend.src.util.db import AsyncSessionLocal as SessionLocal
from backend.src.config.config import settings
from typing import Optional
from backend.src.util.crud import user as crud_user
from backend.src.util.models import user as model_user, token as model_token
from datetime import datetime, timedelta
from backend.src.config.config import settings


from backend.src.util.models import token as crud_token
from backend.src.util.schemas.user import TokenData
from backend.src.util.db import get_db
from backend.src.util.logging_config import logger


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


async def create_access_token(data: dict, user_id: int, db: AsyncSession, expires_delta: Optional[timedelta] = None):
    """
    Create an access token with optional expiration time and store it in the database.

    Args:
        data (dict): The data to encode in the token.
        user_id (int): The ID of the user for whom the token is created.
        db (AsyncSession): The database session for storing the token.
        expires_delta (Optional[timedelta], optional): The time delta after which the token will expire. 
            If not provided, a default expiration time is used.

    Returns:
        str: The encoded JWT access token.
    """
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
    """
    Verify the validity of an access token, check its payload, and ensure it is not blacklisted.

    Args:
        token (str): The JWT access token to verify.
        db (Session, optional): The database session for checking the token blacklist.

    Raises:
        HTTPException: If the token is invalid, expired, or blacklisted.

    Returns:
        TokenData: The data extracted from the valid token.
    """
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





