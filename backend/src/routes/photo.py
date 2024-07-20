from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.util.schemas.photo import PhotoCreate, PhotoUpdate, PhotoResponse
from backend.src.util.crud.photo import create_photo, get_photo, update_photo, delete_photo
from backend.src.util.db import get_db
router = APIRouter()

@router.post("/photos/", response_model=PhotoResponse)
async def creat_photo_route(photo: PhotoCreate, user_id: int, db: Session = Depends(get_db)):
	return await create_photo(db, photo, user_id)


@router.get("/photos/", response_model=PhotoResponse)
async def get_photo_route():
	pass

@router.put("/photos/", response_model=PhotoResponse)
async def update_photo_route():
	pass
@router.delete("/photos/")
async def delete_photo_route():
	pass