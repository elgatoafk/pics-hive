from sqlalchemy.orm import Session
from fastapi import Depends
from backend.src.util.db import get_db
from backend.src.util.models.rating import Rating
from backend.src.util.schemas.rating import RatingCreate


def get_rating(rating_id: int, db:Session = Depends(get_db)) -> Rating:
    return db.query(Rating).filter(Rating.id == rating_id).first()

def create_rating(body: RatingCreate, user_id : int, db:Session = Depends(get_db)) -> Rating:
    rating_db = Rating(**body.dict(), id=user_id)
    db.add(rating_db)
    db.commit()
    db.refresh(rating_db)
    return rating_db

def update_rating(rating_id: int, body: RatingCreate, db:Session =Depends(get_db)) -> Rating:
    rating_db = db.query(Rating).filter(Rating.id == rating_id).first()
    if rating_db:
        rating_db.rating = body.rating
        db.commit()
        db.refresh(rating_db)
        return rating_db
def delete_rating(rating_id: int, db:Session =Depends(get_db))-> Rating:
    rating_db = db.query(Rating).filter(Rating.id == rating_id).first()
    if rating_db:
        db.delete(rating_db)
        db.commit()
        db.refresh(rating_db)
        return rating_db