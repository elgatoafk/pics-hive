from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from pydantic import conlist
import io
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.config.dependency import owner_or_admin_dependency, PhotoDependency
from backend.src.config.logging_config import log_function
from backend.src.config.security import get_current_user
from backend.src.util.crud.tag import get_tag_by_name
from backend.src.util.schemas.photo import PhotoResponse
from backend.src.util.crud.photo import get_photo, delete_photo, create_photo_in_db, PhotoService, \
    update_photo_description
from backend.src.util.models import User
from starlette.responses import StreamingResponse
from backend.src.util.db import get_db
from fastapi.responses import JSONResponse

from backend.src.util.schemas.tag import TagResponse

router = APIRouter()


@router.post("/photos/", response_model=dict, status_code=status.HTTP_201_CREATED)
@log_function
async def create_photo(description: str = Form(None),
                       tags: conlist(str, max_length=5) = Form(None),
                       file: UploadFile = File(...),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    """
        Handle photo upload and description.

        This endpoint allows users to upload a photo with a description and tags. The photo is uploaded to Cloudinary,
        and the URL is stored in the database along with the description and tags.

        Args:
            description (str): The description of the photo.
            tags (List[str]): The list of tags associated with the photo.
            file (UploadFile): The uploaded photo file.
            db (AsyncSession): The asynchronous database session.
            current_user (User): The current authenticated user.

        Returns:
            JSONResponse: A JSON response containing the photo ID and URL.
        """
    try:
        new_photo = await create_photo_in_db(description, file, current_user.id, db, tags)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Photo uploaded successfully", "photo_id": new_photo.id, "url": new_photo.url}
    )


@router.get("/photos/{photo_id}", response_model=PhotoResponse)
@log_function
async def get_photo_route(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a photo from the database based on the provided photo ID.

    Parameters:
    photo_id (int): The unique identifier of the photo to retrieve.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The retrieved photo data. If the photo is not found, returns None.
    """
    photo = await get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    tags = [tag.name for tag in photo.tags]

    return PhotoResponse(
        id=photo.id,
        description=photo.description,
        url=photo.url,
        user_id=photo.user_id,
        tags=tags
    )


@router.put("/photos/{photo_id}/description", response_model=PhotoResponse, status_code=status.HTTP_200_OK)
async def update_description(
    photo_id: int,
    new_description: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _=Depends(owner_or_admin_dependency(PhotoDependency, "photo_id"))
):
    """
    Update the description of a photo.

    This endpoint allows users to update the description of their photos.

    Args:
        photo_id (int): The ID of the photo to update.
        new_description (str): The new description for the photo.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current authenticated user.

    Returns:
        JSONResponse: A JSON response containing the updated photo ID and description.
    """
    try:
        updated_photo = await update_photo_description(photo_id, new_description, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Photo description updated successfully", "photo_id": updated_photo.id, "description": updated_photo.description}
    )

@router.delete("/photos/{photo_id}", response_model=dict, status_code=status.HTTP_200_OK)
@log_function
async def delete_photo_route(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(owner_or_admin_dependency(PhotoDependency, "photo_id"))
):
    """
    Deletes a photo from the database based on the provided photo ID.

    Parameters:
    photo_id (int): The unique identifier of the photo to delete.
    db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
    JSONResponse: A JSON response with a 'detail' key indicating the success message. If the photo is not found, raises a 404 HTTPException.
    """
    await delete_photo(db, photo_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "Photo deleted successfully"}
    )


@router.post("/generate_qrcode/{photo_id}")
@log_function
async def generate_qr_code(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Generates a QR code for a photo based on its ID.

    Parameters:
    photo_id (int): The unique identifier of the photo for which to generate the QR code.
    db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
    StreamingResponse: A response object containing the generated QR code image in PNG format.
    If the photo is not found, raises a 404 HTTPException.
    If the QR code generation fails, also raises a 404 HTTPException.
    """
    photo = await get_photo(db, photo_id)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not Found")

    qr_code = await PhotoService.generate_qr_code(photo.url)

    if qr_code is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    if isinstance(qr_code, int):
        qr_code = str(qr_code).encode('utf-8')
    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png", status_code=status.HTTP_201_CREATED)

@router.get("photo/tags/", response_model=TagResponse)
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

