from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.src.config.config import settings
from app.src.util.crud.token import is_token_blacklisted
from app.src.util.crud.user import get_user_by_email
from app.src.util.models import User
from app.src.util.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.config.logging_config import log_function
from app.src.util.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@log_function
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token and not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_to_use = access_token

    if access_token:
        token_to_use = access_token.replace("Bearer ", "")
        if await is_token_blacklisted(db, token_to_use):
            token_to_use = None
    if not token_to_use and refresh_token:
        token_to_use = refresh_token.replace("Bearer ", "")
        if await is_token_blacklisted(db, token_to_use):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Both access and refresh tokens are blacklisted",
                headers={"WWW-Authenticate": "Bearer"},
            )

    if not token_to_use:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token_to_use, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user



async def get_current_user_cookies(request: Request) -> User:
    username = request.cookies.get("logged_in")
    return username
