from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select

from backend.src.config.hash import hash_handler
from backend.src.util.db import get_db
from fastapi.responses import Response
from datetime import timedelta
from backend.src.config.logging_config import log_function
from backend.src.util.models import user
from backend.src.util.models.user import UserRole, User
from backend.src.util.schemas import user as user_schemas
from backend.src.util.crud import user as user_crud, token as crud_token
from backend.src.config import security, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.util.schemas.user import UserCreate

router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
@log_function
async def signup(user: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Handle user signup.

    This endpoint registers a new user in the database. It first checks if the provided
    email is already registered. If so, it raises an HTTP 409 Conflict error. If the email
    is not registered, it creates a new user and returns an HTTP 201 Created status code.

    Args:
        user (user_schemas.UserCreate): The user creation schema containing the user's email
                                        and password.
        db (AsyncSession): The asynchronous database session, obtained via dependency injection.

    Returns:
        Response: An HTTP 201 status code on successful user creation.

    Raises:
        HTTPException: If the email is already registered (HTTP 409).
    """
    db_user = await user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    await user_crud.create_user(db, user)
    return Response(content="User created", status_code=status.HTTP_201_CREATED, media_type="text/plain")


@router.post("/login", response_model=user_schemas.Token)
@log_function
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Logs in a user.

    This endpoint authenticates a user using the provided username and password. If the authentication
    is successful, it generates and returns a JWT access token that can be used for authenticated requests.
    If authentication fails, it raises an HTTP 401 Unauthorized error.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (AsyncSession): The asynchronous database session, obtained via dependency injection.

    Returns:
        dict: A dictionary containing the access token and its type.

    Raises:
        HTTPException: If the username or password is incorrect (HTTP 401).
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    db_user = result.scalars().first()

    if not db_user or not hash_handler.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Your account was disabled by admin.")
    access_token_expires = timedelta(minutes=jwt.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = await jwt.create_access_token(
        data={"sub": db_user.email}, user_id=db_user.id, db=db, expires_delta=access_token_expires
    )
    await user_crud.update_user_last_login(db, db_user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
@log_function
async def logout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login")), db: AsyncSession = Depends(get_db)):
    """
    Logs out the user.

    This endpoint logs out a user by invalidating their access token. The token is added to a blacklist
    to prevent further use. Upon successful logout, it returns an HTTP 200 OK status.

    Args:
        token (str): The access token to be invalidated, obtained via dependency injection.
        db (AsyncSession): The asynchronous database session, obtained via dependency injection.

    Returns:
        Response: An HTTP 200 OK status code on successful logout.
    """
    await crud_token.add_token_to_blacklist(db, token)
    return Response(content="Logout successful", status_code=status.HTTP_200_OK, media_type="text/plain")
