
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.models import Tag


"""
Create a new tag in the database.

Parameters:
- db (AsyncSession): The asynchronous database session.
- tag_name (str): The name of the tag to be created.

Returns:
- Tag: The newly created tag object.

This function creates a new Tag object with the given tag_name, adds it to the database session, commits the changes, refreshes the tag object, and then returns it.
"""
async def create_tag(db: AsyncSession, tag_name: str) -> Tag:
    tag = Tag(tag_name=tag_name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


"""
Retrieve a tag from the database by its name.

Parameters:
- db (AsyncSession): The asynchronous database session.
- tag_name (str): The name of the tag to be retrieved.

Returns:
- Tag: The tag object with the given name, or None if no such tag exists.

This function uses the provided database session to execute a SQL query to retrieve a tag with the given name.
If a tag with the specified name exists in the database, it is returned. Otherwise, None is returned.
"""
async def get_tag_by_name(db: AsyncSession, tag_name: str) -> Tag:
    result = await db.execute(select(Tag).filter_by(name=tag_name))
    return result.scalars().first()
