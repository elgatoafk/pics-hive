from fastapi import APIRouter, Request, Depends,  HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi.responses import HTMLResponse
from app.src.config.config import templates, FrontEndpoints
from app.src.config.security import get_current_user
from app.src.util.db import get_db
from app.src.util.models import User, Photo
from app.src.util.models.comment import Comment
from app.src.util.models.rating import Rating


router = APIRouter()


@router.get(FrontEndpoints.ADMIN_DASHBOARD.value, response_class=HTMLResponse)
async def get_admin_panel(request: Request, current_user: User = Depends(get_current_user)):
    """
    Renders the Admin Panel dashboard page.

    Args:
        request (Request): The HTTP request object.
        current_user (User): The current user.

    Returns:
        TemplateResponse: The rendered admin_panel.html template.
    """

    if not request.cookies.get('admin_access'):
        raise HTTPException(status_code=403, detail="Access forbidden")
    return templates.TemplateResponse("admin_base.html", {"request": request, "role": current_user.role.value})


@router.get(FrontEndpoints.ADMIN_BAN_USER.value, response_class=HTMLResponse)
async def get_ban_user_page(
        request: Request,
        db: AsyncSession = Depends(get_db),
        message: str = Query(None),
        error: str = Query(None),
        current_user: User = Depends(get_current_user)
):
    """
    Renders the Ban User page with a list of users and optional messages.

    Args:
        request (Request): The HTTP request object.
        db (AsyncSession): The database session.
        message (str): Optional success message to display.
        error (str): Optional error message to display.
        current_user: The current user.

    Returns:
        TemplateResponse: The rendered ban_user.html template.
    """

    result = await db.execute(
        select(User).filter(User.is_active == True, User.username != current_user.username)
    )
    users = result.scalars().all()

    context = {
        "request": request,
        "users": users,
        "message": message,
        "error": error,
        "role": current_user.role.value,
    }

    return templates.TemplateResponse("ban_user.html", context)


@router.get(FrontEndpoints.ADMIN_DELETE_PHOTO.value, response_class=HTMLResponse)
async def get_photos_for_deletion(
        request: Request,
        db: AsyncSession = Depends(get_db), message: str = Query(None), error: str = Query(None),
        current_user: User = Depends(get_current_user)

):
    """
    Renders the Delete Photo page with all available photos and optional messages.

    Args:
        request (Request): The HTTP request object.
        db (AsyncSession): The database session.
        current_user (User): The current authenticated user.
        message (str): Optional success message to display.
        error (str): Optional error message to display.

    Returns:
        TemplateResponse: The rendered delete_photo.html template.
    """
    result = await db.execute(select(Photo))
    photos = result.scalars().all()

    context = {
        "request": request,
        "photos": photos,
        "message": message,
        "error": error,
        "role": current_user.role.value,
    }

    return templates.TemplateResponse("delete_photo.html", context)


@router.get(FrontEndpoints.ADMIN_RATINGS.value, response_class=HTMLResponse)
async def view_all_ratings(request: Request, db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    """
    Display a list of all ratings with associated photos and users.
    """

    result = await db.execute(
        select(Rating)
        .options(selectinload(Rating.photo), selectinload(Rating.owner))
    )
    ratings = result.scalars().all()
    return templates.TemplateResponse("admin_ratings.html", {
        "request": request,
        "ratings": ratings,
        "role": current_user.role.value,
    })


@router.get(FrontEndpoints.ADMIN_COMMENTS.value, response_class=HTMLResponse)
async def view_all_comments(request: Request, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    """
    Display a list of all comments with associated photos and users.
    """

    result = await db.execute(
        select(Comment)
        .options(selectinload(Comment.photo), selectinload(Comment.user))
    )
    comments = result.scalars().all()
    return templates.TemplateResponse("admin_comments.html", {
        "request": request,
        "comments": comments,
        "role": current_user.role.value,
    })
