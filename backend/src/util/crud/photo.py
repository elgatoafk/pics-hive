from fastapi import Depends
from sqlalchemy.orm import Session
from backend.src.util.models.photo import Photo
from backend.src.util.models.tag import Tag
from backend.src.util.schemas.photo import PhotoCreate
from backend.src.util.db import get_db


def get_photo(photo_id:int, db:Session = Depends(get_db) ):
    return db.query(Photo).filter(Photo.id == photo_id).first()

def create_photo (body: PhotoCreate,user_id: int,db: Session = Depends (get_db)):
    db_photo = Photo (**body.dict (),user_id=user_id)
    db.add (db_photo)
    db.commit ()
    db.refresh (db_photo)
    return db_photo
def update_photo(body: PhotoCreate, photo_id: int, db: Session = Depends(get_db)):
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if db_photo:
        for key, value in body.dict().items():
            setattr(db_photo, key, value)
    db.commit()
    db.refresh (db_photo)
    return db_photo
def delete_photo(photo_id: int ,db: Session = Depends(get_db)):
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if db_photo:
        db.delete(db_photo)
        db.commit()
        db.refresh(db_photo)
        return db_photo
