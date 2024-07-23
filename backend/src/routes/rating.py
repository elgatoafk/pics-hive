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
async def get_rating_route(rating_id: int, db: Session = Depends(get_db)):
    return await get_rating(db, rating_id)

@router.put("/ratings/", response_model=RatingResponse)
async def update_rating_route(rating: RatingCreate, rating_id: int, db: Session = Depends(get_db)):
    updated_rating = await update_rating(rating, rating_id, db)
    if not updated_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return updated_rating

@router.delete("/ratings/")
async def delete_rating_route(rating_id: int, db: Session = Depends(get_db)):
    rating_db = await get_rating(db, rating_id)
    if not rating_db:
        raise HTTPException(status_code=404, detail="Rating not found")
    else:
        await delete_rating(db, rating_id)
        return {"detail": "Rating deleted"}