
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.models.photo import Photo
from backend.src.util.schemas.photo import PhotoUpdate, PhotoResponse
from sqlalchemy.future import select


async def get_photo(db: AsyncSession, photo_id: int ):
    """
    Asynchronously retrieves a photo from the database by its ID.

    Parameters:
    - db (AsyncSession): The SQLAlchemy AsyncSession object for database operations.
    - photo_id (int): The unique identifier of the photo to retrieve.

    Returns:
    - PhotoResponse: A response object containing the photo's details.

    Raises:
    - HTTPException: If the photo is not found in the database, a 404 Not Found error is raised.
    - HTTPException: If an error occurs during database operations, a 500 Internal Server Error is raised.
    """
    try:
        result = await db.execute(select(Photo).options(joinedload(Photo.tags)).filter(Photo.id == photo_id))
        db_photo = result.scalars().first()
        if not db_photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

        tags = [tag.tag_name for tag in db_photo.tags]
        response = PhotoResponse (id=db_photo.id, user_id=db_photo.user_id, url=db_photo.url, description=db_photo.description, tags=tags)
        return response

    except Exception as e:
        raise HTTPException (status_code=500, detail=str (e))

async def update_photo (db: AsyncSession, body: PhotoUpdate, photo_id: int) -> Photo:
    """
    Asynchronously updates a photo in the database by its ID.

    Parameters:
    - db (AsyncSession): The SQLAlchemy AsyncSession object for database operations.
    - body (PhotoUpdate): The updated photo data.
    - photo_id (int): The unique identifier of the photo to update.

    Returns:
    - Photo: The updated photo object.

    Raises:
    - HTTPException: If the photo is not found in the database, a 404 Not Found error is raised.
    - HTTPException: If an error occurs during database operations, a 500 Internal Server Error is raised.
    """
    try:
        result = await db.execute (select (Photo).options (joinedload (Photo.tags)).filter (Photo.id == photo_id))
        db_photo = result.scalars ().first ()
        if not db_photo:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

        for key, value in body.dict ().items ():
            setattr (db_photo, key, value)

        await db.commit ()
        await db.refresh (db_photo)
        return db_photo

    except Exception as e:
        await db.rollback ()
        raise HTTPException (status_code=500, detail=str (e))

async def delete_photo(db: AsyncSession, photo_id: int):
    """
    Asynchronously deletes a photo from the database by its ID.

    Parameters:
    - db (AsyncSession): The SQLAlchemy AsyncSession object for database operations.
    - photo_id (int): The unique identifier of the photo to delete.

    Returns:
    - Photo: The deleted photo object.

    Raises:
    - HTTPException: If the photo is not found in the database, a 404 Not Found error is raised.
    - HTTPException: If an error occurs during database operations, a 500 Internal Server Error is raised.
    """
    try:
        result = await db.execute(select(Photo).filter(Photo.id == photo_id))
        db_photo = result.scalars ().first ()
        if not db_photo:
            raise HTTPException (status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
        await db.delete(db_photo)
        await db.commit()
        return db_photo

    except Exception as e:
        raise HTTPException (status_code=500, detail=str (e))
