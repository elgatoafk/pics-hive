from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy import text

from backend.src.util.crud.photo import get_photo
from backend.src.util.db import get_db
from backend.src.services.photos import PhotoService
from backend.src.config.security import get_current_user, get_current_active_user
from backend.src.util.logging_config import logger
from backend.src.util.models import User
from backend.src.util.schemas.photo import PhotoResponse

router = APIRouter(prefix="/transformations", tags=["transformations"])


@router.post("/resize/{photo_id}")
async def resize(
        request: Request,
        photo_id: int,
        width: int,
        height: int,
        db=Depends(get_db),

):
    """
     Resize a photo to the specified dimensions.

    This endpoint allows authorized users to resize an existing photo identified by its ID. 
    The new dimensions for the photo are specified by width and height parameters.

    Parameters:
        request (Request): The request object, used to access various parts of the HTTP request.
        photo_id (int): The unique identifier of the photo to resize.
        width (int): The desired width of the photo after resizing.
        height (int): The desired height of the photo after resizing.
        db (Session, optional): The database session dependency to handle any database operations.


    Returns:
        A response object that includes the resized photo's details, or an error message if the operation cannot be completed.

    Raises:
        HTTPException: If the photo cannot be found

    """

    photo = await db.execute(text("SELECT * FROM photos WHERE id = :id"), {"id": photo_id})
    photo = photo.fetchone()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    try:
        return await PhotoService.resize_photo(
            photo_id=photo_id, width=width, height=height, db=db
        )
    except Exception as e:
        logger.exception("Failed to resize photo")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/filter/{photo_id}", response_model=PhotoResponse)
async def add_filter(
        request: Request,
        photo_id: int,
        photo_filter: str,
        db=Depends(get_db),
        current_user: User = Depends(get_current_active_user)

):
    """ Applies a specified filter to a photo.

    This endpoint enables authorized users to apply a graphical filter to a photo identified by its ID. 
    The type of filter to be applied is specified by the `photo_filter` parameter.

    Parameters:
        request (Request): The request object, used to access various parts of the HTTP request.
        photo_id (int): The unique identifier of the photo to which the filter will be applied.
        photo_filter (str): The name of the filter to apply. This should match one of the predefined filters
                            available in the system.
        db (Session, optional): The database session dependency to handle any database operations.
        user (User, optional): The current user performing the operation. This user must be authenticated
                               and authorized to modify the photo.

    Returns:
        A response object that includes the details of the photo with the applied filter, or an error message if the operation cannot be completed.

    Raises:
        HTTPException: If the photo cannot be found, or the user does not have permission to modify the photo,
                        or if the specified filter is not recognized or applicable.

    """
    photo = await get_photo(db, photo_id)
    url = await PhotoService.add_filter(
        photo_id=photo_id, filter=photo_filter, db=db, current_user=current_user
    )
    try:
        photo_with_filter = {
            "id": photo.id,
            "description": photo.description,
            "url": url,
            "user_id": photo.user_id,
            "filter": photo_filter,
        }
        return PhotoResponse(**photo_with_filter)
    except Exception as e:
        logger.exception("Failed to add filter")
        raise HTTPException(status_code=500, detail="Internal Server Error")
