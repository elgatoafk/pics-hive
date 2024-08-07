from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.util.schemas.tag import PhotoTaggingResponse,PhotoTaggingRequest
from backend.src.util import models, schemas, db
from backend.src.util.db import get_db
from backend.src.util.crud.tag import get_tag_by_name


router = APIRouter()


@router.post("/photos/{photo_id}/tags", response_model=List[PhotoTaggingResponse], status_code=status.HTTP_201_CREATED)
async def add_tags_to_photo(
        photo_id: int, tagging_request: PhotoTaggingRequest, db: AsyncSession = Depends(db.get_db)
):
    """
    Adds tags to a photo in the database.

    This function retrieves a photo from the database based on the provided photo ID,
    checks if the photo exists, and then adds tags to the photo. If the photo does not exist,
    a 404 Not Found error is raised. If the number of tags to be added exceeds 5, a 400 Bad Request
    error is raised.

    Parameters:
    photo_id (int): The ID of the photo to which tags will be added.
    tagging_request (schemas.PhotoTaggingRequest): The request containing the tags to be added.
    db (AsyncSession): The database session to use for querying and updating. This parameter is optional and defaults to the session provided by the `get_db` dependency.

    Returns:
    schemas.PhotoTaggingResponse: A response containing the ID of the photo and the list of tags added.
    """

    result = await db.execute(select(models.Photo).filter_by(id=photo_id))
    photo = result.scalars().first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    tags = []
    for tag_data in tagging_request.tags:

        result = await db.execute(select(models.Tag).filter_by(name=tag_data.name))
        tag = result.scalars().first()

        if not tag:
            
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

@router.get("/tags/", response_model=PhotoTaggingResponse)
async def get_tag_route(tag_name: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a tag by its name.

    This function retrieves a tag from the database based on the provided tag name.
    If the tag is found, it is returned. If the tag is not found, a 404 Not Found error is raised.

    Parameters:
    tag_name (str): The name of the tag to retrieve.
    db (Session): The database session to use for querying. This parameter is optional and defaults to the session provided by the `get_db` dependency.

    Returns:
    Tag: The retrieved tag if found. If the tag is not found, a 404 Not Found error is raised.
    """
    return await get_tag_by_name(db, tag_name)

