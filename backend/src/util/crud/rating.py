from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from backend.src.util.models.rating import Rating
from backend.src.util.schemas.rating import RatingCreate
from sqlalchemy.future import select
from sqlalchemy import delete


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


async def create_rating(body: RatingCreate, db: AsyncSession, user_id: int) -> Rating:
    """
    Create a new rating in the database.

    Parameters:
    - body (RatingCreate): The rating data to be created. It should be an instance of the RatingCreate class.
    - user_id (int): The unique identifier of the user creating the rating.
    - db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

    Returns:
    - Rating: The newly created rating object.
    """
    rating_db = Rating(**body.dict(), id=user_id)
    db.add(rating_db)
    await db.commit()
    await db.refresh(rating_db)
    return rating_db


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


async def delete_rating(db: AsyncSession, rating_id: int) -> Rating:
    """
    Delete a rating from the database by its ID.

    Parameters:
    - rating_id (int): The unique identifier of the rating to delete.
    - db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

    Returns:
    - Rating: The deleted rating object if found and successfully deleted, otherwise None.
    """
    result = await db.execute(select(Rating).filter(Rating.id == rating_id))
    rating_db = result.scalars().first()

    if rating_db:
        await db.execute(delete(Rating).where(Rating.id == rating_id))
        await db.commit()

    return rating_db
