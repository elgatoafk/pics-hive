from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.src.config.dependency import role_required, verify_api_key
from app.src.util.crud.photo import get_photo
from app.src.util.models.user import UserRole
from app.src.util.schemas.rating import RatingResponse
from app.src.util.crud.rating import get_rating, delete_rating
from app.src.util.db import get_db
from sqlalchemy.future import select
from app.src.util.models.rating import Rating
from app.src.config.security import get_current_user
from app.src.util.models import User
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/photos/{photo_id}/rating", response_model=float, dependencies=[Depends(verify_api_key)])
async def get_photo_rating(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
        Retrieve the average rating for a specific photo.

        This endpoint retrieves the average rating for a photo based on all ratings submitted by users.

        Parameters:
        photo_id (int): The unique identifier of the photo.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

        Returns:
        float: The average rating of the photo. If no ratings are found, returns 0.
        """
    result = await db.execute(select(func.avg(Rating.rating)).where(Rating.photo_id == photo_id))
    average_rating = result.scalar()
    if average_rating is None:
        return 0
    return average_rating


@router.post("/photos/rate")
async def rate_photo(photo_id: int = Form(...), rating: int = Form(...), db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    """
    Submit a rating for a specific photo.

    This endpoint allows authenticated users to submit a rating for a photo. If the user has already rated the photo,
    their previous rating will be updated.

    Parameters:
    photo_id (int): The unique identifier of the photo to be rated.
    rating (int): The rating value to be submitted (must be between 1 and 5).
    db (AsyncSession, optional): The database session. Defaults to Depends(get_db).
    current_user (User, optional): The current authenticated user. Defaults to Depends(get_current_user).

    Returns:
    RedirectResponse to photo page if successful.

    Raises:
    HTTPException: If the rating value is not between 1 and 5, or if the user tries to rate their own photo,
    or if the user tries to change an existing rating.
    """
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and 5")

    photo = await get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    if photo.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot rate your own photo")

    existing_rating = await db.execute(
        select(Rating).where(Rating.photo_id == photo_id, Rating.user_id == current_user.id))
    existing_rating = existing_rating.scalars().first()

    if existing_rating:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You cannot change your rating")

    new_rating = Rating(rating=rating, user_id=current_user.id, photo_id=photo_id)
    db.add(new_rating)
    await db.commit()

    return RedirectResponse(url=f"/photo/{photo_id}", status_code=status.HTTP_302_FOUND)


@router.get("/ratings/", response_model=RatingResponse,dependencies=[Depends(verify_api_key)])
async def get_rating_route(rating_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a rating by its ID.

    Parameters:
    rating_id (int): The ID of the rating to retrieve.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    RatingResponse: The retrieved rating. If the rating is not found, returns None.
    """
    return await get_rating(db, rating_id)


@router.delete("/rating/delete/", dependencies=[Depends(role_required([UserRole.ADMIN, UserRole.MODERATOR]))])
async def delete_rate(rate_id: int, db: AsyncSession = Depends(get_db),
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
