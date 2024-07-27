import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.util.schemas import tag as schema_tag
from backend.src.util.models import tag as model_tag
from backend.src.util.logging_config import logger

async def get_tags(db: AsyncSession, skip: int = 0, limit: int = 10):
    logger.debug('get_tags')
    result = await db.execute(select(model_tag.Tag).offset(skip).limit(limit))
    return result.scalars().all()

async def get_tag_by_name(db: AsyncSession, name: str):
    logger.debug('get_tag_by_name')
    result = await db.execute(select(model_tag.Tag).filter(model_tag.Tag.name == name))
    return result.scalars().first()

async def create_tag(db: AsyncSession, tag: schema_tag.TagCreate):
    logger.debug('create_tag')
    db_tag = model_tag.Tag(name=tag.name)
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag
