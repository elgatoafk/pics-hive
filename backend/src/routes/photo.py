import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.src.util.schemas.photo import PhotoCreate, PhotoUpdate, PhotoResponse
from backend.src.util.crud.photo import create_photo, get_photo, update_photo, delete_photo
from backend.src.util.db import get_db
from backend.src.services.photos import PhotoService
from starlette.responses import StreamingResponse
router = APIRouter()

@router.post("/photos/", response_model=PhotoResponse)
async def creat_photo_route(photo: PhotoCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Creates a new photo in the database.

    Parameters:
    photo (PhotoCreate): The photo data to be created.
    user_id (int): The ID of the user creating the photo.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The created photo data.
    """
    return await create_photo(db, photo, user_id)

@router.get("/photos/", response_model=PhotoResponse)
async def get_photo_route(photo_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a photo from the database based on the provided photo ID.

    Parameters:
    photo_id (int): The unique identifier of the photo to retrieve.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The retrieved photo data. If the photo is not found, returns None.
    """
    return await get_photo(db, photo_id)

@router.put("/photos/", response_model=PhotoResponse)
async def update_photo_route(photo: PhotoUpdate, photo_id: int, db: Session = Depends(get_db)):
    """
    Updates an existing photo in the database based on the provided photo ID.

    Parameters:
    photo (PhotoUpdate): The updated photo data.
    photo_id (int): The unique identifier of the photo to update.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The updated photo data. If the photo is not found, raises a 404 HTTPException.
    """
    updated_photo = await update_photo(db, photo, photo_id)
    if not updated_photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return updated_photo

@router.delete("/photos/")
async def delete_photo_route(photo_id: int, db: Session = Depends(get_db)):
    """
    Deletes a photo from the database based on the provided photo ID.

    Parameters:
    photo_id (int): The unique identifier of the photo to delete.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    dict: A dictionary with a 'detail' key indicating the success message. If the photo is not found, raises a 404 HTTPException.
    """
    await delete_photo(db, photo_id)
    return {"detail": "Photo deleted successfully"}


@router.post("/generate_qrcode/{photo_id}")
async def generate_qr_code(
    photo_id: int, db: Session = Depends(get_db)
):
    """Generates a QR code for the given photo ID.

    Args:
        photo_ID (str): The ID of the image for which the QR code needs to be generated.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
         image/png: streamingresponse

    Raises:
        HTTPException: If the photo is not found
    """
    photo = await get_photo(photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    qr_code = await PhotoService.generate_qr_code(photo.photo_url)
    if qr_code is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return StreamingResponse(qr_code, media_type="image/png", status_code=status.HTTP_201_CREATED)

