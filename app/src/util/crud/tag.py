from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.config.logging_config import log_function
from app.src.util.models import Tag


async def create_tag(db: AsyncSession, tag_name: str) -> Tag:
    """
    Create a new tag in the database.

    Parameters:
    - db (AsyncSession): The asynchronous database session.
    - tag_name (str): The name of the tag to be created.

    Returns:
    - Tag: The newly created tag object.

    This function creates a new Tag object with the given tag_name, adds it to the database session, commits the changes, refreshes the tag object, and then returns it.
    """
    tag = Tag(tag_name=tag_name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_tag_by_name(db: AsyncSession, tag_name: str) -> Tag:
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
    result = await db.execute(select(Tag).filter(Tag.name == tag_name))
    tag = result.scalars().first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tag found with this name"
        )
    return tag


@log_function
async def parse_tags(db: AsyncSession, tag_names: list, max_number: int) -> list:
    tags = [tag.strip() for tag in tag_names[0].split(',')]
    if len(tags) > max_number:
        tags = tags[:max_number]
    tag_instances = []
    for tag_name in tags:
        tag_instance = await db.execute(select(Tag).where(Tag.name == tag_name))
        existing_tag = tag_instance.scalars().first()
        if existing_tag:
            tag_instances.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            try:
                await db.commit()
                await db.refresh(new_tag)
                tag_instances.append(new_tag)
            except IntegrityError:
                await db.rollback()
                tag_instance = await db.execute(select(Tag).where(Tag.name == tag_name))
                existing_tag = tag_instance.scalars().first()
                if existing_tag:
                    tag_instances.append(existing_tag)
    return tag_instances
