from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from app.src.config.config import templates, FrontEndpoints
from app.src.config.security import get_current_user_cookies
from app.src.util.crud.photo import get_photos_with_details
from app.src.util.db import get_db
from app.src.util.models import User


router = APIRouter()


@router.get(FrontEndpoints.HOME.value, response_class=HTMLResponse)
async def read_root(request: Request, db: AsyncSession = Depends(get_db),
                    current_user_username: User = Depends(get_current_user_cookies)):
    """
        Displays the home page with photos and user-specific navigation links.

        Args:
            request (Request): The request object.
            db (AsyncSession): The asynchronous database session.
            current_user_username: The username of current authenticated user.

        Returns:
            TemplateResponse: The rendered home page template with photos and user-specific navigation.
        """

    photos_with_details = await get_photos_with_details(db)
    return templates.TemplateResponse("index.html", {"request": request, "photos": photos_with_details,
                                                     "current_user": current_user_username})