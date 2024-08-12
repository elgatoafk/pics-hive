from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.src.util.models.rating import Rating
from app.src.util.schemas.rating import RatingCreate
from sqlalchemy.future import select
from app.src.util.models import User, Photo

async def get_rating(db: AsyncSession, rating_id: int) -> Rating:
    """
    Retrieve a rating by its ID from the database.

    Parameters:
    - rating_id (int): The unique identifier of the rating to retrieve.
    - db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

    Returns:
    - Rating: The retrieved rating object if found, otherwise None.
    """
    result = await db.execute(select(Rating).filter(Rating.id == rating_id))
    rating = result.scalars().first()
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    return rating


async def create_rating(photo_id: int, rate: int, user_id, db: AsyncSession) -> Rating:
    """
    Asynchronously rates a photo by a given user if not already rated by them and if the photo does not belong to them.

    This function performs several checks before adding a new rating:
    - It ensures the photo exists.
    - It prevents users from rating their own photos.
    - It prevents users from rating the same photo more than once.

    Args:
        photo_id (int): The ID of the photo to be rated.
        rate (int): The rating score to be assigned to the photo.
        user_id: The user_id
        db (AsyncSession): The database session used to execute asynchronous queries.

    Returns:
        Rating: An instance of the Rating model with the new rating details if successful.

    Raises:
        HTTPException: An error with status code 404 if no photo is found,
                       with status code 423 if the user tries to rate their own photo or rate the same photo twice.

    Example:
        >>> user = User(id=1, name="John Doe")
        >>> db_session = AsyncSession()
        >>> await rate_photo(photo_id=123, rate=5, user=user, db=db_session)
        <Rating>
    """
    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    photo = result.scalars().first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found.")
    is_self_photo = photo.user_id == user_id

    result = await db.execute(select(Rating).filter(Rating.photo_id == photo_id, Rating.user_id == user_id))
    already_rated = result.scalars().first()

    if is_self_photo:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="It's not possible to rate own photo.")
    if already_rated:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail="It's not possible to rate twice.")

    new_rating = Rating(photo_id=photo_id, rate=rate, user_id=user_id)
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)
    return new_rating



async def update_rating(db: AsyncSession, rating_id: int, body: RatingCreate) -> Rating:
    """
    Update an existing rating in the database.

    Parameters:
    - rating_id (int): The unique identifier of the rating to update.
    - body (RatingCreate): The updated rating data. It should be an instance of the RatingCreate class.
    - db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

    Returns:
    - Rating: The updated rating object if found and successfully updated, otherwise None.
    """
    result = await db.execute(select(Rating).filter(Rating.id == rating_id))
    rating_db = result.scalars().first()

    if rating_db:

        for key, value in body.dict().items():
            setattr(rating_db, key, value)

        await db.commit()
        await db.refresh(rating_db)

    return rating_db


async def delete_rating(rate_id: int, db: AsyncSession, user: User) -> None:
    """
    The delete_rating function deletes a rating from the database.

    Args:
        rate_id (int): The id of the rating to be deleted.
        db (Session): A connection to the database.
        user (User): The User object that removes the rate.

    Returns:
        None
    """
    result = await db.execute(select(Rating).filter(Rating.id == rate_id))
    rate = result.scalars().first()

    if rate:
        await db.delete(rate)  # Perform deletion
        await db.commit()  # Commit the transaction
        return rate
    return None




