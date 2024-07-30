from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from backend.src.util.schemas.rating import RatingCreate, RatingResponse
from backend.src.util.crud.rating import create_rating, get_rating, update_rating, delete_rating
from backend.src.util.db import get_db
from sqlalchemy.future import select
from backend.src.util.models.photo import Photo
from backend.src.util.models.rating import Rating
from backend.src.config.security import get_current_user
from backend.src.util.models import User

router = APIRouter()


@router.post("/ratings/", response_model=RatingResponse)
async def create_rating_route(photo_id: int, rating: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Creates a new rating for a specified photo by a given user. The function checks if the user
    is rating their own photo or if they have already rated this photo before proceeding to create a new rating.

    Args:
        photo_id (int): The ID of the photo to be rated.
        rating (int): The score of the rating.
        user_id (int): The ID of the user who is creating the rating.
        db (AsyncSession, optional): The database session used for executing queries asynchronously.

    Returns:
        RatingResponse: A Pydantic schema representing the created rating.

    Raises:
        HTTPException: With status code 404 if the photo is not found.
                       With status code 423 if the user tries to rate their own photo or rate the same photo twice.
    """
    # Fetch the photo to check ownership and existence
    photo = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = photo.scalars().first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found.")

    if photo.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="Cannot rate your own photo.")

    # Check if the user has already rated this photo
    existing_rating = await db.execute(select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == user_id))
    existing_rating = existing_rating.scalars().first()
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="You have already rated this photo.")

    # Create a new rating
    new_rating = Rating(photo_id=photo_id, user_id=user_id, rating=rating)
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)

    return RatingResponse.from_orm(new_rating)


@router.get("/ratings/", response_model=RatingResponse)
async def get_rating_route(rating_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a rating by its ID.

    Parameters:
    rating_id (int): The ID of the rating to retrieve.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    RatingResponse: The retrieved rating. If the rating is not found, returns None.
    """
    return await get_rating(db, rating_id)


@router.delete("/ratings/")
async def delete_rate(rate_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    """
    The delete_rate function deletes a rate from the database.
        The function takes in an integer, which is the id of the rate to be deleted.
        It also takes in a Session object and a User object as parameters,
        which are used to access and delete data from the database.

    Arguments:
        rate_id (int): rate id to be removed
        current_user (User): the current user
        db (Session): SQLAlchemy session object for accessing the database

    Returns:
        None
    """
    deleted_rate = await delete_rating(rate_id, db, current_user)
    if deleted_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found or not available.")
    return deleted_rate



