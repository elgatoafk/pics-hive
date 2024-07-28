from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.models.photo import Photo
from backend.src.util.schemas.photo import PhotoCreate
from backend.src.util.db import get_db



async def get_photo(photo_id:int, db:AsyncSession = Depends(get_db) ):
    """
    Retrieve a photo by its ID from the database.

    Parameters:
    - photo_id (int): The unique identifier of the photo to retrieve.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The retrieved photo object if found, otherwise None.
    """
    return await db.execute(db.query(Photo).filter(Photo.id == photo_id).first())

async def create_photo (body: PhotoCreate,user_id: int,db:AsyncSession = Depends (get_db)):
    """
    Create a new photo in the database.

    Parameters:
    - body (PhotoCreate): The photo data to be created. It should be an instance of the PhotoCreate schema.
    - user_id (int): The unique identifier of the user who is creating the photo.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The newly created photo object.
    """
    db_photo = Photo (**body.dict (),user_id=user_id)
    db.add (db_photo)
    await db.commit ()
    await db.refresh (db_photo)
    return db_photo

async def update_photo(body: PhotoCreate, photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Update an existing photo in the database.

    Parameters:
    - body (PhotoCreate): The updated photo data. It should be an instance of the PhotoCreate schema.
    - photo_id (int): The unique identifier of the photo to update.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The updated photo object. If the photo with the given ID does not exist, it returns None.
    """
    db_photo = db.execute(db.query(Photo).filter(Photo.id == photo_id).first())
    if db_photo:
        for key, value in body.dict().items():
            setattr(db_photo, key, value)
    await db.commit()
    await db.refresh (db_photo)
    return db_photo


async def update_photo(body: PhotoCreate, photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Updates an existing photo in the database.

    Parameters:
    - body (PhotoCreate): The updated photo data. It should be an instance of the PhotoCreate schema.
    - photo_id (int): The unique identifier of the photo to update.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The updated photo object. If the photo with the given ID does not exist, it returns None.
    """
    db_photo = db.execute(db.query(Photo).filter(Photo.id == photo_id).first())
    if db_photo:
        for key, value in body.dict().items():
            setattr(db_photo, key, value)
    await db.commit()
    await db.refresh (db_photo)
    return db_photo


async def delete_photo(photo_id: int ,db: AsyncSession = Depends(get_db)):
    """
    Delete a photo from the database by its ID.

    Parameters:
    - photo_id (int): The unique identifier of the photo to delete.
    - db (AsyncSession): The asynchronous database session. It is optional and will be injected by the FastAPI framework.

    Returns:
    - Photo: The deleted photo object if found and successfully deleted, otherwise None.
    """
    db_photo = await db.execute(db.query(Photo).filter(Photo.id == photo_id).first())
    if db_photo:
        await db.delete(db_photo)
        await db.commit()
        await db.refresh(db_photo)
        return db_photo

