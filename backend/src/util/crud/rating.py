from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from backend.src.util.db import get_db
from backend.src.util.models.rating import Rating
from backend.src.util.schemas.rating import RatingCreate


async def get_rating(rating_id: int, db:AsyncSession = Depends(get_db)) ->Rating:
    return await db.execute(db.query(Rating).filter(Rating.id == rating_id).first())

async def create_rating(body: RatingCreate, user_id : int, db:AsyncSession = Depends(get_db)) -> Rating:
    rating_db = Rating(**body.dict(), id=user_id)
    db.add(rating_db)
    await db.commit()
    await db.refresh(rating_db)
    return rating_db

async def update_rating(rating_id: int, body: RatingCreate, db:AsyncSession =Depends(get_db)) -> Rating:
    rating_db = await db.execute(db.query(Rating).filter(Rating.id == rating_id).first())
    if rating_db:
        rating_db.rating = body.rating
        await db.commit()
        await db.refresh(rating_db)
        return rating_db
async def delete_rating(rating_id: int, db:AsyncSession =Depends(get_db))-> Rating:
    rating_db =  await db.execute(db.query(Rating).filter(Rating.id == rating_id).first())
    if rating_db:
        await db.delete(rating_db)
        await db.commit()
        await db.refresh(rating_db)
        return rating_db