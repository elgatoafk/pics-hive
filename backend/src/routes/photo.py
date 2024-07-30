import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import io

from backend.src.util.schemas.photo import PhotoCreate, PhotoUpdate, PhotoResponse
from backend.src.util.crud.photo import get_photo, update_photo, delete_photo
from backend.src.util.models import Photo
from backend.src.services.photos import PhotoService
from starlette.responses import StreamingResponse
from backend.src.util.db import get_db

from backend.src.util.models import Tag

router = APIRouter()

@router.post ("/photos/", response_model=PhotoResponse)
async def create_photo_route (body: PhotoCreate, user_id: int, db: AsyncSession = Depends (get_db)):
    """
    Creates a new photo in the database.

    Parameters:
    body (PhotoCreate): The data for the new photo, including description, URL, and tags.
    user_id (int): The ID of the user creating the photo.
    db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The created photo data, including its ID, user ID, URL, description, and tags.

    Raises:
    HTTPException: If an internal server error occurs during the creation process.
    """
    try:
        db_photo = Photo (description=body.description, url=body.url, user_id=user_id)

        if body.tags:
            tags_list = []
            for tag_name in body.tags:

                result = await db.execute (select (Tag).filter (Tag.tag_name == tag_name))
                tag = result.scalars().first ()
                if not tag:
                    tag = Tag (tag_name=tag_name)
                    db.add (tag)
                    await db.flush()
                tags_list.append (tag)
            db_photo.tags = tags_list

        db.add (db_photo)
        await db.commit ()
        await db.refresh (db_photo)


        stmt = select (Photo).options(joinedload(Photo.tags)).filter_by(id=db_photo.id)
        result = await db.execute (stmt)
        db_photo = result.scalars().first()

        response = PhotoResponse (id=db_photo.id, user_id=db_photo.user_id, url=db_photo.url, description=db_photo.description,
            tags=[tag.tag_name for tag in db_photo.tags])

        return response

    except Exception as e:
        raise HTTPException (status_code=500, detail="Internal Server Error")

@router.get("/photos/{photo_id}", response_model=PhotoResponse)
async def get_photo_route(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a photo from the database based on the provided photo ID.

    Parameters:
    photo_id (int): The unique identifier of the photo to retrieve.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The retrieved photo data. If the photo is not found, returns None.
    """
    return await get_photo(db, photo_id)

@router.put("/photos/{photo_id}", response_model=PhotoResponse)
async def update_photo_route(body: PhotoUpdate, photo_id: int, db: AsyncSession = Depends(get_db)):
    updated_photo = await update_photo(db, body, photo_id)
    return updated_photo

@router.delete("/photos/")
async def delete_photo_route(photo_id: int, db: AsyncSession = Depends(get_db)):
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
async def generate_qr_code(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Generates a QR code for a photo based on its ID.

    Parameters:
    photo_id (int): The unique identifier of the photo for which to generate the QR code.
    db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
    StreamingResponse: A response object containing the generated QR code image in PNG format.
    If the photo is not found, raises a 404 HTTPException.
    If the QR code generation fails, also raises a 404 HTTPException.
    """
    photo = await get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    qr_code = await PhotoService.generate_qr_code(photo.url)

    if qr_code is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    if isinstance(qr_code, int):
        qr_code = str(qr_code).encode('utf-8')
    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png", status_code=status.HTTP_201_CREATED)

@router.post("/generate_qrcode/{photo_id}")
async def generate_qr_code(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Generates a QR code for a photo based on its ID.

    Parameters:
    photo_id (int): The unique identifier of the photo for which to generate the QR code.
    db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
    StreamingResponse: A response object containing the generated QR code image in PNG format.
    If the photo is not found, raises a 404 HTTPException.
    If the QR code generation fails, also raises a 404 HTTPException.
    """
    photo = await get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    qr_code = await PhotoService.generate_qr_code(photo.url)

    if qr_code is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    if isinstance(qr_code, int):
        qr_code = str(qr_code).encode('utf-8')
    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png", status_code=status.HTTP_201_CREATED)