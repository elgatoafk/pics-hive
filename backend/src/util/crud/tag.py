from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from backend.src.util.db import get_db
from backend.src.util.models.tag import Tag
from backend.src.util.schemas.tag import TagCreate


async def get_tag(tag_name: str, db:AsyncSession = Depends(get_db)) -> Tag:
     return await db.execute(db.query(Tag).filter(Tag.name == tag_name).first())

async def create_tag(body: TagCreate, db:AsyncSession = Depends(get_db)) -> Tag:
    tag_db = Tag(name=body.name)
    db.add(tag_db)
    await db.commit()
    await db.refresh(tag_db)
    return tag_db
async def update_tag(body: TagCreate, tag_id: int, db:AsyncSession = Depends(get_db)) -> Tag:
    tag_db = db.execute(db.query(Tag).filter(Tag.id == tag_id).first())
    if tag_db:
        tag_db.name = body.name
        await db.commit()
        await db.refresh(tag_db)
        return tag_db
async def delete_tag(tag_name: str, db:AsyncSession = Depends(get_db)) -> Tag:
    tag_db = db.execute(db.query(Tag).filter(Tag.name == tag_name).first())
    if tag_db:
        await db.delete(tag_db)
        await db.commit()
        await db.refresh(tag_db)
        return tag_db


