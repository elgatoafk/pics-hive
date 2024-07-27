from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.util.schemas import tag as schema_tag
from backend.src.util.crud import tag as crud_tag
from backend.src.config.security import get_current_active_user
from backend.src.util.db import get_db

router = APIRouter()

@router.get("/tags/", response_model=list[schema_tag.Tag])
async def read_tags(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    tags = await crud_tag.get_tags(db, skip=skip, limit=limit)
    return tags

@router.post("/tags/")
async def create_tag(tag: schema_tag.TagCreate, db: AsyncSession = Depends(get_db)):
    db_tag = await crud_tag.get_tag_by_name(db, name=tag.name)
    if db_tag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")
    # Create and add the new tag to the database
    return await crud_tag.create_tag(db=db, tag=tag)