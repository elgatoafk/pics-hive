from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from backend.src.config.hash import hash_handler
from backend.src.util.schemas import user as schema_user
from backend.src.util.crud.user import get_user_by_email
from backend.src.util.models import user as model_user
from backend.src.util.db import get_db
from backend.src.config import jwt as config_jwt
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.logging_config import log_function


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@log_function
async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticate a user by their email and password.

    This function checks if the provided email exists in the database and verifies the
    provided password against the stored hashed password. If the authentication is
    successful, it returns the user object; otherwise, it returns False.

    Args:
        db (AsyncSession): The asynchronous database session.
        email (str): The email address of the user.
        password (str): The plain text password of the user.

    Returns:
        model_user.User | bool: The authenticated user object if authentication is successful,
                                otherwise False.
    """
    user = await get_user_by_email(db, email)
    if not user or hash_handler.verify_password(password, user.hashed_password):
        return False
    return user


@log_function
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
        Retrieves the current authenticated user based on the provided JWT token.

        Args:
            token (str): The JWT token provided by the OAuth2PasswordBearer dependency.
            db (AsyncSession): The asynchronous database session, obtained via dependency injection.

        Returns:
            model_user.User: The authenticated user object.

        Raises:
            HTTPException: If the credentials are invalid or the user does not exist.
        """
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

        user = await get_user_by_email(db, email=token_data.email)
    except Exception as e:

        raise HTTPException(status_code=500, detail="Internal Server Error")

    if user is None:
        raise credentials_exception

    return user


@log_function
async def get_current_active_user(current_user: model_user.User = Depends(get_current_user)):
    """
        Retrieves the current authenticated and active user.

        Args:
            current_user (model_user.User): The current authenticated user, injected via dependency.

        Returns:
            model_user.User: The authenticated and active user object.

        Raises:
            HTTPException: If the user is inactive.
        """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
