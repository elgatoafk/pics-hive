from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.models.photo import Photo
from backend.src.util.schemas.photo import PhotoCreate
from backend.src.util.db import get_db


async def get_photo(photo_id:int, db:AsyncSession = Depends(get_db) ):
    return await db.execute(db.query(Photo).filter(Photo.id == photo_id).first())
async def create_photo (body: PhotoCreate,user_id: int,db:AsyncSession = Depends (get_db)):
    db_photo = Photo (**body.dict (),user_id=user_id)
    db.add (db_photo)
    await db.commit ()
    await db.refresh (db_photo)
    return db_photo
async def update_photo(body: PhotoCreate, photo_id: int, db: AsyncSession = Depends(get_db)):
    db_photo = db.execute(db.query(Photo).filter(Photo.id == photo_id).first())
    if db_photo:
        for key, value in body.dict().items():
            setattr(db_photo, key, value)
    await db.commit()
    await db.refresh (db_photo)
    return db_photo
async def delete_photo(photo_id: int ,db: AsyncSession = Depends(get_db)):
    db_photo = db.execute(db.query(Photo).filter(Photo.id == photo_id).first())
    if db_photo:
        await db.delete(db_photo)
        await db.commit()
        await db.refresh(db_photo)
        return db_photo
