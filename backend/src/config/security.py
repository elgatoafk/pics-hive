from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.src.util.schemas import user as schema_user
from backend.src.util.crud import user as crud_user
from backend.src.util.models import user as model_user
from backend.src.util.db import get_db
from backend.src.config import jwt as config_jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.util.schemas import user as schema_user
from src.config.config import settings
from typing import Optional
from src.util.crud import user as crud_user
from src.util.models import user as model_user
from src.util.db import get_db
from src.config import jwt as config_jwt
from src.util.logging_config import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """
    Verify that a plain password matches the hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Hash a plain text password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticate a user by their email and password.

    Args:
        db (AsyncSession): The database session to query the user.
        email (str): The user's email address.
        password (str): The user's plain text password.

    Returns:
        Union[model_user.User, bool]: The authenticated user if credentials are correct, False otherwise.
    """
    user = await crud_user.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Retrieve the current user based on the provided JWT token.

    Args:
        token (str, optional): The JWT access token.
        db (AsyncSession, optional): The database session to query the user.

    Raises:
        HTTPException: If the token is invalid or the user cannot be found.

    Returns:
        model_user.User: The current authenticated user.
    """
    logger.debug('test - get_current_user')
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
    except JWTError:
        raise credentials_exception

    try:
        logger.debug('test - get_user_by_email')
        user = await crud_user.get_user_by_email(db, email=token_data.email)
    except Exception as e:
        logger.error(f"An error occurred: {e}")  # Use logging instead of print
        raise HTTPException(status_code=500, detail="Internal Server Error")

    if user is None:
        raise credentials_exception

    logger.debug('get_current_user - return : {}'.format(user))
    return user

async def get_current_active_user(current_user: model_user.User = Depends(get_current_user)):
    """
    Ensure the current user is active.

    Args:
        current_user (model_user.User, optional): The current authenticated user.

    Raises:
        HTTPException: If the user is inactive.

    Returns:
        model_user.User: The current active user.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
