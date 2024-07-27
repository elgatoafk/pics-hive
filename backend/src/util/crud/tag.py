
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.models import Tag, Photo


async def create_tag(db: AsyncSession, tag_name: str) -> Tag:
    tag = Tag(tag_name=tag_name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_tag_by_name(db: AsyncSession, tag_name: str) -> Tag:
    result = await db.execute(select(Tag).filter_by(name=tag_name))
    return result.scalars().first()
