from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from backend.src.util import models, schemas, db
from sqlalchemy import and_
from typing import List

router = APIRouter()


@router.post("/photos/{photo_id}/tags", response_model=schemas.PhotoTaggingResponse)
async def add_tags_to_photo(
        photo_id: int, tagging_request: schemas.PhotoTaggingRequest, db: AsyncSession = Depends(db.get_db)
):
    # Fetch the photo from the database
    result = await db.execute(select(models.Photo).filter_by(id=photo_id))
    photo = result.scalars().first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    tags = []
    for tag_data in tagging_request.tags:
        # Check if the tag already exists
        result = await db.execute(select(models.Tag).filter_by(name=tag_data.name))
        tag = result.scalars().first()

        if not tag:
            # Create the new tag
            tag = models.Tag(tag_name=tag_data.name)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)

        tags.append(tag)

    if len(photo.tags) + len(tags) > 5:
        raise HTTPException(status_code=400, detail="Cannot add more than 5 tags to a photo")

    # Add tags to the photo
    photo.tags.extend(tags)
    await db.commit()

    return schemas.PhotoTaggingResponse(
        photo_id=photo.id,
        tags=[tag.name for tag in photo.tags]
    )


@router.get("/tags/", response_model=TagResponse)
async def get_tag_route(tag_name: str, db: Session = Depends(get_db)):
    return await get_tag(db, tag_name)

