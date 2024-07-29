from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.models.photo import Photo
from backend.src.util.schemas.photo import PhotoCreate
from backend.src.util.db import get_db
from sqlalchemy.future import select


async def get_photo(db: AsyncSession, photo_id: int ):
    """
    Retrieve a photo by its ID from the database.

    Parameters:
    - photo_id (int): The unique identifier of the photo to retrieve.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The retrieved photo object if found, otherwise None.
    """
    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    return result.scalars().first()


async def create_photo(db: AsyncSession, body: PhotoCreate, user_id: int):
    """
    Create a new photo in the database.

    Parameters:
    - body (PhotoCreate): The photo data to be created. It should be an instance of the PhotoCreate schema.
    - user_id (int): The unique identifier of the user who is creating the photo.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The newly created photo object.
    """
    db_photo = Photo(**body.dict(), user_id=user_id)
    db.add(db_photo)
    await db.commit()
    await db.refresh(db_photo)
    return db_photo


async def update_photo(db: AsyncSession, body: PhotoCreate, photo_id: int ):
    """
    Update an existing photo in the database.

    Parameters:
    - body (PhotoCreate): The updated photo data. It should be an instance of the PhotoCreate schema.
    - photo_id (int): The unique identifier of the photo to update.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The updated photo object. If the photo with the given ID does not exist, it returns None.
    """
    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    db_photo = result.scalars().first()

    if not db_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    for key, value in body.dict().items():
        setattr(db_photo, key, value)

    await db.commit()
    await db.refresh(db_photo)
    return db_photo


async def delete_photo(db: AsyncSession,photo_id: int):
    """
    Delete a photo from the database by its ID.

    Parameters:
    - photo_id (int): The unique identifier of the photo to delete.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The deleted photo object if found and successfully deleted, otherwise None.
    """
    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    db_photo = result.scalars().first()

    if not db_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    await db.delete(db_photo)
    await db.commit()
    return db_photo
