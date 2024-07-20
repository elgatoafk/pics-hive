from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.util.schemas.rating import RatingCreate, RatingResponse
from backend.src.util.crud.rating import create_rating, get_rating, update_rating, delete_rating
from backend.src.util.db import get_db

router = APIRouter()

@router.post("/ratings/", response_model=RatingResponse)
async def creat_rating_route(photo: RatingCreate, user_id: int, db: Session = Depends(get_db)):
	return await create_rating(db, photo, user_id)

@router.get("/ratings/", response_model=RatingResponse)
async def get_rating_route():
	pass

@router.put("/ratings/", response_model=RatingResponse)
async def update_rating_route():
	pass
@router.delete("/ratings/")
async def delete_rating_route():
	pass