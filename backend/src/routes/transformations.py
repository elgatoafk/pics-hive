
from fastapi import APIRouter, Request, Depends

from backend.src.util.db import get_db
from backend.src.services.photos import PhotoService
from backend.src.config.security import get_current_user

router = APIRouter(prefix="/transformations", tags=["transformations"])


@router.post("/resize/{photo_id}")
async def resize(
        request: Request,
        photo_id: int,
        width: int,
        height: int,
        db=Depends(get_db),
        user=Depends(get_current_user),
):
    """
    Resizes an image to the specified width and height.

    """
    return await PhotoService.resize_photo(
        photo_id=photo_id, width=width, height=height, user=user, db=db
    )


@router.post("/filter/{photo_id}")
async def add_filter(
        request: Request,
        photo_id: int,
        photo_filter: str,
        db=Depends(get_db),
        user=Depends(get_current_user),
):
    """Adds a filter to the specified image.


    """
    return await PhotoService.add_filter(
        photo_id=photo_id, filter=photo_filter, user=user, db=db
    )
