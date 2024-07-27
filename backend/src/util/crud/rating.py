from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from backend.src.util.db import get_db
from backend.src.util.models.rating import Rating
from backend.src.util.schemas.rating import RatingCreate


"""
Retrieve a rating by its ID from the database.

Parameters:
- rating_id (int): The unique identifier of the rating to retrieve.
- db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

Returns:
- Rating: The retrieved rating object if found, otherwise None.
"""
async def get_rating(rating_id: int, db:AsyncSession = Depends(get_db)) ->Rating:
    return await db.execute(db.query(Rating).filter(Rating.id == rating_id).first())

"""
Create a new rating in the database.

Parameters:
- body (RatingCreate): The rating data to be created. It should be an instance of the RatingCreate class.
- user_id (int): The unique identifier of the user creating the rating.
- db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

Returns:
- Rating: The newly created rating object.
"""
async def create_rating(body: RatingCreate, user_id : int, db:AsyncSession = Depends(get_db)) -> Rating:
    rating_db = Rating(**body.dict(), id=user_id)
    db.add(rating_db)
    await db.commit()
    await db.refresh(rating_db)
    return rating_db

"""
Update an existing rating in the database.

Parameters:
- rating_id (int): The unique identifier of the rating to update.
- body (RatingCreate): The updated rating data. It should be an instance of the RatingCreate class.
- db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

Returns:
- Rating: The updated rating object if found and successfully updated, otherwise None.
"""
async def update_rating(rating_id: int, body: RatingCreate, db:AsyncSession =Depends(get_db)) -> Rating:
    rating_db = await db.execute(db.query(Rating).filter(Rating.id == rating_id).first())
    if rating_db:
        rating_db.rating = body.rating
        await db.commit()
        await db.refresh(rating_db)
        return rating_db
"""
Delete a rating from the database by its ID.

Parameters:
- rating_id (int): The unique identifier of the rating to delete.
- db (AsyncSession): The database session object. It is optional and defaults to the result of calling the `get_db` function.

Returns:
- Rating: The deleted rating object if found and successfully deleted, otherwise None.
"""
async def delete_rating(rating_id: int, db:AsyncSession =Depends(get_db))-> Rating:
    rating_db =  await db.execute(db.query(Rating).filter(Rating.id == rating_id).first())
    if rating_db:
        await db.delete(rating_db)
        await db.commit()
        await db.refresh(rating_db)
        return rating_db