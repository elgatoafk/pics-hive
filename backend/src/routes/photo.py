from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from backend.src.util.schemas import photo as schema_photo, user as schema_user, tag as schema_tag
from backend.src.util.models import photo as model_photo, user as model_user
from backend.src.util.crud import photo as crud_photo
from backend.src.config.security import get_current_active_user
from backend.src.util.db import get_db
from backend.src.config.dependencies import get_current_moderator, get_current_admin
from typing import List, Optional
import cloudinary
import cloudinary.uploader

#import qrcode


router = APIRouter()

@router.post("/photos/", response_model=schema_photo.Photo)
async def create_photo(
    description: str = Form(None),
    tags: str = Form(""),
    file: UploadFile = File(...),
    current_user: schema_user.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Upload file to Cloudinary
    upload_result = cloudinary.uploader.upload(file.file)
    
    # Convert comma-separated tags into a list of TagCreate objects
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    tags_objects = [schema_tag.TagCreate(name=tag) for tag in tag_list]
    
    # Create PhotoCreate schema instance
    photo_in = schema_photo.PhotoCreate(
        url=upload_result["secure_url"], 
        description=description, 
        tags=tags_objects
    )
    
    # Use CRUD function to create photo in the database
    return crud_photo.create_photo(db=db, photo=photo_in, user_id=current_user.id)


@router.get("/photos/{photo_id}", response_model=schema_photo.Photo)
def read_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = crud_photo.get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.put("/photos/{photo_id}", response_model=schema_photo.Photo)
def update_photo(
    photo_id: int,
    photo: schema_photo.PhotoCreate,
    db: Session = Depends(get_db),
    current_user: model_user.User = Depends(get_current_active_user)
):
    db_photo = crud_photo.get_photo(db, photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if db_photo.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_photo.update_photo(db, photo_id, photo)

@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: model_user.User = Depends(get_current_active_user)
):
    db_photo = crud_photo.get_photo(db, photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    if db_photo.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud_photo.delete_photo(db, photo_id)

@router.post("/photos/{photo_id}/transform", response_model=schema_photo.Photo)
def transform_photo(
    photo_id: int,
    transformation: str,
    db: Session = Depends(get_db)
):
    db_photo = db.query(model_photo.Photo).filter(model_photo.Photo.id == photo_id).first()
    if not db_photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        transformed_photo = crud_photo.transform_photo(db, db_photo, transformation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return transformed_photo