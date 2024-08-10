import urllib
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
import urllib.parse
from jose import jwt, JWTError
from app.src.config.config import settings
from app.src.config.hash import hash_handler
from app.src.config.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, create_refresh_token, SECRET_KEY, \
    ALGORITHM
from app.src.util.crud.token import blacklist_token
from app.src.util.crud.user import get_user_by_email
from app.src.util.db import get_db
from datetime import timedelta, datetime
from app.src.config.logging_config import log_function
from app.src.util.models.user import UserRole
from app.src.util.schemas import user as user_schemas
from app.src.util.crud import user as user_crud

from sqlalchemy.ext.asyncio import AsyncSession

from app.src.util.schemas.user import Token

router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
@log_function
async def signup(request: Request, db: AsyncSession = Depends(get_db),
                 email: str = Form(...), password: str = Form(...)):
    """
    Handle user signup.

    This endpoint registers a new user in the database. It first checks if the provided
    email is already registered. If so, it raises an HTTP 409 Conflict error. If the email
    is not registered, it creates a new user and redirects to the signup form.

    Args:
        request (Request): The request object.
        db (AsyncSession): The asynchronous database session, obtained via dependency injection.
        email (str): The email of the user.
        password (str): The password of the user.

    Returns:
        TemplateResponse: Shows success message on signup form

    Raises:
        HTTPException: If the email is already registered (HTTP 409).
    """
    db_user = await get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    await user_crud.create_user(db, {"email": email, "password": password})
    message = "Profile created"
    encoded_message = urllib.parse.quote(message)
    return RedirectResponse(url=f"/auth/signup-form?message={encoded_message}", status_code=status.HTTP_302_FOUND)


@router.post("/login", response_model=user_schemas.Token)
@log_function
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db),
                request: Request = None, response: Response = None):
    """
    Logs in a user.

    This endpoint authenticates a user using the provided username and password. If the authentication
    is successful, it generates and returns a JWT access token that can be used for authenticated requests.
    If authentication fails, it raises an HTTP 401 Unauthorized error.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (AsyncSession): The asynchronous database session, obtained via dependency injection.

    Returns:
        RedirectResponse: Redirects to the home page with a session cookie containing the access token.

    Raises:
        HTTPException: If the email or password is incorrect (HTTP 401) or if the account is disabled (HTTP 423).
    """
    existing_token = request.cookies.get("access_token")
    if existing_token:
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="logged_in")
        response.delete_cookie(key="admin_access")
    db_user = await get_user_by_email(db, form_data.username)
    if not db_user or not hash_handler.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not db_user.is_active:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Your account was disabled by admin.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = await create_access_token(
        data={"sub": db_user.email}, user_id=db_user.id, db=db, expires_delta=access_token_expires
    )
    refresh_token = await create_refresh_token(
        data={"sub": db_user.email}, user_id=db_user.id, db=db, expires_delta=refresh_token_expires
    )
    db_user.last_login = datetime.utcnow()
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    response.set_cookie(key="refresh_token", value=f"Bearer {refresh_token}", httponly=True)
    response.set_cookie(key="logged_in", value=f"{db_user.username}", httponly=True)
    if db_user.role == UserRole.ADMIN or db_user.role == UserRole.MODERATOR:
        response.set_cookie(key="admin_access", value="true", httponly=True)
    return response


@router.post("/logout", status_code=status.HTTP_200_OK)
@log_function
async def logout(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Logs out the user.

    This endpoint logs out a user by invalidating their access token. The token is added to a blacklist
    to prevent further use. Upon successful logout, it returns an HTTP 200 OK status.

    Args:
        request (Request): The request object.
        db (AsyncSession): The asynchronous database session, obtained via dependency injection.

    Returns:
        RedirectResponse: Redirects to the home page after successful logout.
    """
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if access_token:
        await blacklist_token(db, access_token)
    if refresh_token:
        await blacklist_token(db, refresh_token)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("logged_in")

    if request.cookies.get("admin_access") == "true":
        response.delete_cookie("admin_access")

    return response

