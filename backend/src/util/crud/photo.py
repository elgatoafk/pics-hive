from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.models.photo import Photo, photo_m2m_tag
from backend.src.util.schemas.photo import PhotoCreate
from sqlalchemy.future import select

from backend.src.util.logging_config import logger
from backend.src.util.models import User

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


async def update_photo(db: AsyncSession, body: PhotoCreate,user: User, photo_id: int ):
    """
    Update an existing photo in the database.

    Parameters:
    - body (PhotoCreate): The updated photo data. It should be an instance of the PhotoCreate schema.
    - photo_id (int): The unique identifier of the photo to update.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The updated photo object. If the photo with the given ID does not exist, it returns None.
    """
    await db.commit ()
    try:
        result = await db.execute (select(Photo).filter(Photo.id == photo_id))
        db_photo = result.scalars ().first ()

        if not db_photo:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

        for key, value in body.dict ().items ():
            setattr (db_photo, key, value)

        await db.commit ()
        await db.refresh (db_photo)
        return db_photo

    except SQLAlchemyError as e:
        logger.error (f"Error updating photo: {e}")
        raise HTTPException (status_code=500, detail="Internal Server Error")

async def delete_photo(db: AsyncSession, photo_id: int):
    try:
        # Deleting tags associated with the photo
        tags_to_delete = await db.execute(
            select(photo_m2m_tag).filter(photo_m2m_tag.c.photo_id == photo_id)
        )
        for tag in tags_to_delete:
            await db.delete(tag)

        # Deleting the photo
        photo_to_delete = await db.execute(
            select(Photo).filter(Photo.id == photo_id)
        )
        photo = photo_to_delete.scalars().first()

        if photo:
            await db.delete(photo)
            await db.commit()
        else:
            raise HTTPException(status_code=404, detail="Photo not found")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting photo: {str(e)}")