from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
from app.src.util.models import user as model_user, token as model_token
from datetime import datetime, timedelta
from app.src.config.config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


async def create_access_token(
        data: Dict[str, str],
        user_id: int,
        db: AsyncSession,
        expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a new access token, stores it in the database, and returns the encoded JWT.

    Args:
        data (Dict[str, str]): A dictionary containing the claims to encode in the JWT.
        user_id (int): The ID of the user for whom the token is being created.
        db (AsyncSession): The asynchronous database session used to store the token.
        expires_delta (Optional[timedelta]): Optional expiration time for the token.
            If not provided, the default expiration time from settings is used.

    Returns:
        str: The encoded JWT access token.

    Raises:
        HTTPException: If there is an issue storing the token in the database.

    Example:
        token_data = {"sub": "user@example.com"}
        token = await create_access_token(token_data, user_id=123, db=session)
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    token = model_token.Token(
        token=encoded_jwt,
        user_id=user_id,
        expires_at=expire
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)

    return encoded_jwt


async def create_refresh_token(
        data: Dict[str, str],
        user_id: int,
        db: AsyncSession,
        expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a new refresh token, stores it in the database, and returns the encoded JWT.

    Args:
        data (Dict[str, str]): A dictionary containing the claims to encode in the JWT.
        user_id (int): The ID of the user for whom the refresh token is being created.
        db (AsyncSession): The asynchronous database session used to store the token.
        expires_delta (Optional[timedelta]): Optional expiration time for the token.
            If not provided, the default expiration time from settings is used.

    Returns:
        str: The encoded JWT refresh token.

    Raises:
        HTTPException: If there is an issue storing the token in the database.

    Example:
        token_data = {"sub": "user@example.com"}
        refresh_token = await create_refresh_token(token_data, user_id=123, db=session)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    token = model_token.Token(
        token=encoded_jwt,
        user_id=user_id,
        expires_at=expire
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return encoded_jwt
