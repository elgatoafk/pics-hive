import base64

from fastapi import APIRouter, Request, Depends, Path, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.src.config.logging_config import log_function
from fastapi.responses import HTMLResponse
from app.src.config.config import templates, FrontEndpoints
from app.src.config.security import get_current_user, get_current_user_cookies
from app.src.util.crud.photo import get_post_by_id, get_photo, PhotoService
from app.src.util.db import get_db
from app.src.util.models import User, Photo
from app.src.util.schemas.user import User as UserSchema, UserProfile
from src.services.aggregator import Aggregator

router = APIRouter()


@router.get(FrontEndpoints.SIGNUP_FORM.value, response_class=HTMLResponse)
async def signup_form(request: Request, message: str = None):
    """
    Handles GET requests to the signup form endpoint without a message.

    Renders the signup form template.
    """
    return templates.TemplateResponse("signup.html",
                                      {"request": request, "message": message if message is not None else ""})


@router.get(FrontEndpoints.LOGIN_FORM.value, response_class=HTMLResponse)
@log_function
async def get_login_form(request: Request, next: str = "/", error: str = None):
    """
    Render the login form without a message

    Args:
        request (Request): The request object.
        next (str, optional): The URL to redirect to after a successful login. Defaults to "/".


    Returns:
        TemplateResponse: The rendered login form template
    """
    return templates.TemplateResponse("login.html", {"request": request, "next": next, "error": error})


@router.get(FrontEndpoints.LOGOUT_FORM.value, response_class=HTMLResponse)
@log_function
async def get_logout_form(request: Request):
    """
    Render the logout form

    Args:
        request (Request): The request object.


    Returns:
        TemplateResponse: The rendered logout form template
    """
    return templates.TemplateResponse("logout.html", {"request": request})


@router.get(FrontEndpoints.PEOPLE_FORM.value, response_class=HTMLResponse)
async def get_user_profiles(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handles GET requests to the user profiles endpoint.

    Args:
        request (Request): The HTTP request object.
        db (AsyncSession): The database session.

    Returns:
        HTMLResponse: Renders the user profiles template with the user data.
    """
    result = await db.execute(select(User).filter(User.is_active == True))
    users = result.scalars().all()
    user_profiles = [UserSchema.from_orm(user).dict() for user in users]
    return templates.TemplateResponse("people.html", {"request": request, "users": user_profiles})


@router.get("/user/{username}", response_class=HTMLResponse)
async def get_user_detail(request: Request, username: str, db: AsyncSession = Depends(get_db)):
    """
    Handles GET requests to the detailed user profile endpoint.

    Args:
        request (Request): The HTTP request object.
        username (str): The username of the user.
        db (AsyncSession): The database session.

    Returns:
        HTMLResponse: Renders the detailed user profile template with the user data and photos.
    """
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_profile = UserSchema.from_orm(user).dict()

    photo_result = await db.execute(select(Photo).filter(Photo.user_id == user.id))
    photos = photo_result.scalars().all()

    return templates.TemplateResponse("user_profile.html", {"request": request, "user": user_profile, "photos": photos})


@router.get(FrontEndpoints.PHOTO_UPLOAD_FORM.value, response_class=HTMLResponse)
@log_function
async def upload_photo_form(request: Request, message: str = None):
    """
    Render the photo upload form.

    This endpoint renders a form that allows users to upload a photo with a description and tags.

    Args:
        request (Request): The request object.

    Returns:
        TemplateResponse: The rendered upload form template.
    """
    return templates.TemplateResponse("upload_photo.html", {"request": request, "message": message})


@router.get("/photo/{photo_id}", response_class=HTMLResponse)
async def view_photo(photo_id: int, request: Request, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user_cookies)):
    """
    Display the details of a specific photo, including its description, tags,
    uploader's username, average rating, and comments.

    Args:
        photo_id (int): The unique identifier of the photo.
        request (Request): The HTTP request object.
        db (AsyncSession): The SQLAlchemy asynchronous session.
        current_user (User): The current authenticated user.

    Returns:
        TemplateResponse: The rendered photo detail template with the photo details.

    Raises:
        HTTPException: If the photo is not found.
    """
    photo = await get_post_by_id(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return templates.TemplateResponse("photo_detail.html", {
        "request": request,
        "photo": photo,
        "current_user": current_user,
    })

@router.get("/photo/edit/{photo_id}", response_class=HTMLResponse)
async def edit_photo(photo_id: int, request: Request, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """
    Render the edit photo page.

    This endpoint renders a page that allows the user to edit the photo.
    The user can resize the photo, add filters, edit the description, or delete the photo.

    Args:
        photo_id (int): The ID of the photo to edit.
        request (Request): The HTTP request object.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.

    Returns:
        HTMLResponse: The rendered HTML template for editing the photo.
    """

    photo = await get_photo(db, photo_id)

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")


    if photo.owner.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to edit this photo")

    return templates.TemplateResponse("edit_photo.html",
                                      {"request": request, "photo": photo, "current_user": current_user})


@router.get(FrontEndpoints.PROFILE_MY_PHOTOS.value, response_class=HTMLResponse)
async def get_user_photos(request: Request, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """
    Render a page showing all photos uploaded by the current user, along with descriptions, tags, and average ratings.
    """
    user_photos = await db.execute(
        select(Photo)
        .where(Photo.user_id == current_user.id)
        .options(selectinload(Photo.tags))
    )
    photos = user_photos.scalars().all()

    return templates.TemplateResponse("user_photos.html", {"request": request, "photos": photos})


@router.get("/photo/show-qr/{photo_id}", response_class=HTMLResponse)
async def display_qr_code(photo_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Display the QR code for a photo URL by calling the existing POST endpoint.

    Args:
        photo_id (int): The unique identifier of the photo.
        db (AsyncSession): The SQLAlchemy asynchronous session.
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: The rendered template with the QR code.
    """
    qr_code = await Aggregator.generate_qr(photo_id, db)
    ref = request.headers.get("referer")
    return templates.TemplateResponse("qr_code.html", {
        "request": request,
        "qr_code": qr_code,
        "referer": ref,
    })



