from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from app.src.config.config import settings
from app.src.util.crud.token import is_token_blacklisted
from app.src.util.crud.user import get_user_by_email
from app.src.util.models import User
from app.src.util.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.config.logging_config import log_function
from fastapi.responses import JSONResponse
from app.src.config.jwt import create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_email_from_token(token: str) -> str:
    """
    Extracts the email (subject) from a JWT token.

    Args:
        token (str): The JWT token from which to extract the email.

    Returns:
        str: The email extracted from the token.

    Raises:
        HTTPException: If the token is invalid, expired, or does not contain an email (subject).

    Example:
        token = "your.jwt.token"
        email = get_email_from_token(token)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain an email",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@log_function
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """
        Retrieves the current authenticated user based on the provided access or refresh token.

        This function checks the validity of the access token stored in the user's cookies. If the access token is
        blacklisted, it attempts to use the refresh token to generate a new access token. If both tokens are
        blacklisted or invalid, the user is considered unauthenticated, and an HTTP 401 Unauthorized error is raised.

        Args:
            request (Request): The FastAPI request object, used to access cookies and other request-related data.
            db (AsyncSession): The database session dependency, used to interact with the database asynchronously.

        Returns:
            User: The authenticated user object retrieved from the database.

        Raises:
            HTTPException:
                - If no valid access or refresh token is provided.
                - If both access and refresh tokens are blacklisted or invalid.
                - If the token does not contain a valid email (subject).
                - If the user associated with the token cannot be found in the database.
                - In each case, a 401 Unauthorized error is raised with an appropriate message.

    """

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    def clear_cookies(response: JSONResponse):
        """
            Clears authentication-related cookies from the client's browser.

            This function deletes the following cookies from the response:
            - "access_token": The JWT access token used for authenticating the user.
            - "refresh_token": The JWT refresh token used for obtaining new access tokens.
            - "logged_in": A cookie indicating whether the user is logged in.
            - "admin_access": A cookie indicating whether the user has admin privileges.

            Args:
                response (JSONResponse): The FastAPI JSONResponse object to which the
                                         cookies will be cleared.

            Example:
                response = JSONResponse(content={"detail": "Logged out successfully"})
                clear_cookies(response)
            """
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("logged_in")
        response.delete_cookie("admin_access")

    if not access_token and not refresh_token:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"}
        )
        clear_cookies(response)
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
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Both access and refresh tokens are blacklisted"}
            )
            clear_cookies(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Both access and refresh tokens are blacklisted",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:

            email = get_email_from_token(refresh_token)
            user = await get_user_by_email(db, email=email)
            if not user:
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Could not validate credentials"}
                )
                clear_cookies(response)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            new_access_token = await create_access_token(data={"sub": email}, user_id=user.id, db=db)
            response = JSONResponse(
                content={"detail": "New access token issued"}
            )
            response.set_cookie(key="access_token", value=new_access_token, httponly=True)
            token_to_use = new_access_token

    if not token_to_use:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"}
        )
        clear_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token_to_use, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Could not validate credentials"}
            )
            clear_cookies(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Could not validate credentials"}
        )
        clear_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_email(db, email=email)
    if user is None:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Could not validate credentials"}
        )
        clear_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_cookies(request: Request) -> str:
    """
        Retrieves the username of the currently logged-in user from the request cookies.

        This function accesses the "logged_in" cookie from the client's request and returns
        the associated username, if present.

        Args:
            request (Request): The FastAPI Request object that contains the cookies.

        Returns:
            str: The username of the currently logged-in user, or None if the cookie is not set.


    """
    username = request.cookies.get("logged_in")
    return username
