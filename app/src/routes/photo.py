import base64
from io import BytesIO
import qrcode
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File, Request, Body
from pydantic import conlist
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from base64 import b64encode

from starlette.responses import StreamingResponse

from app.src.config.config import templates
from app.src.util.models import Photo
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.config.dependency import owner_or_admin_dependency, PhotoDependency, verify_api_key
from app.src.config.logging_config import log_function
from app.src.config.security import get_current_user
from app.src.util.crud.tag import get_tag_by_name
from app.src.util.crud.photo import delete_photo, create_photo_in_db, update_photo_description
from app.src.util.models import User
from app.src.util.db import get_db
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, Depends, HTTPException
from app.src.util.crud.photo import get_photo, PhotoService, update_photo_url
from app.src.util.schemas.photo import PhotoResponse
from app.src.util.schemas.tag import TagResponse
from fastapi.responses import RedirectResponse

from app.src.services.aggregator import Aggregator

router = APIRouter()


@router.post("/photos/new/")
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
             TemplateResponse: Shows success message on upload form
        """
    try:
        new_photo = await create_photo_in_db(description, file, current_user.id, db, tags)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return RedirectResponse("/profile/my-photos", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/photos/{photo_id}", response_model=PhotoResponse, dependencies=[Depends(verify_api_key)])
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
    result = await db.execute(select(Photo).options(joinedload(Photo.tags)).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    tags = [TagResponse(id=tag.id, name=tag.name) for tag in photo.tags]
    photo_with_tags = PhotoResponse(
        id=photo.id,
        description=photo.description,
        url=photo.url,
        user_id=photo.user_id,
        tags=tags
    )
    return photo_with_tags


@router.put("/photos/{photo_id}/description", status_code=status.HTTP_200_OK)
async def update_description(
        photo_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        _=Depends(owner_or_admin_dependency(PhotoDependency, "photo_id"))
):
    """
    Update the description of a photo.
    """
    data = await request.json()
    new_description = data.get("new_description")

    if not new_description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Description cannot be empty")

    try:
        updated_photo = await update_photo_description(photo_id, new_description, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Photo description updated successfully", "photo_id": updated_photo.id,
                 "description": updated_photo.description}
    )


@router.delete("/photos/delete-photo/{photo_id}", status_code=status.HTTP_303_SEE_OTHER)
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
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/photos/generate_qrcode/{photo_id}", dependencies=[Depends(verify_api_key)])
@log_function
async def generate_qr_code(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
        Generate and display a QR code for the photo URL in response to a POST request.

        Args:
            photo_id (int): The unique identifier of the photo.
            db (AsyncSession): The SQLAlchemy asynchronous session.


        Returns:
            TemplateResponse: The rendered template with the QR code.
        """
    qr_code = await Aggregator.generate_qr(photo_id, db)
    return StreamingResponse(qr_code, media_type="image/png")



@router.get("/photo/tags/", response_model=TagResponse, dependencies=[Depends(verify_api_key)])
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


@router.post("/photos/resize/{photo_id}")
async def resize(
        photo_id: int,
        width: int = Form(...),
        height: int = Form(...),
        db=Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
     Resize a photo to the specified dimensions.

    This endpoint allows authorized users to resize an existing photo identified by its ID.
    The new dimensions for the photo are specified by width and height parameters.

    Parameters:
        request (Request): The request object, used to access various parts of the HTTP request.
        photo_id (int): The unique identifier of the photo to resize.
        width (int): The desired width of the photo after resizing.
        height (int): The desired height of the photo after resizing.
        db (Session, optional): The database session dependency to handle any database operations.


    Returns:
        A response object that includes the resized photo's details, or an error message if the operation cannot be completed.

    Raises:
        HTTPException: If the photo cannot be found

    """

    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    try:
        result = await PhotoService.resize_photo(photo.public_id, width=width, height=height)
        await update_photo_url(db, photo_id, result)
        return RedirectResponse(url=f"/photo/edit/{photo_id}", status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/photos/filter/{photo_id}", response_model=PhotoResponse)
async def add_filter(
        photo_id: int,
        photo_filter: str = Form(...),  # Expecting `photo_filter` in the request body
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """ Applies a specified filter to a photo.

    This endpoint enables authorized users to apply a graphical filter to a photo identified by its ID.
    The type of filter to be applied is specified by the `photo_filter` parameter.

    Parameters:

        photo_id (int): The unique identifier of the photo to which the filter will be applied.
        photo_filter (str): The name of the filter to apply. This should match one of the predefined filters
                            available in the system.
        db (Session, optional): The database session dependency to handle any database operations.
        user (User, optional): The current user performing the operation. This user must be authenticated
                               and authorized to modify the photo.

    Returns:
        A response object that includes the details of the photo with the applied filter, or an error message if the operation cannot be completed.

    Raises:
        HTTPException: If the photo cannot be found, or the user does not have permission to modify the photo,
                        or if the specified filter is not recognized or applicable.

    Available filters:
            "al_dente",
            "athena",
            "audrey",
            "aurora",
            "daguerre",
            "eucalyptus",
            "fes",
            "frost",
            "hairspray",
            "hokusai",
            "incognito",
            "primavera",
            "quartz",
            "red_rock",
            "refresh",
            "sizzle",
            "sonnet",
            "ukulele",
            "zorro",

    """
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    url = await PhotoService.add_filter(photo.public_id, photo_filter)
    if not url:
        raise HTTPException(status_code=400, detail="Invalid filter or transformation failed")

    await update_photo_url(db, photo_id, url)
    return RedirectResponse(url=f"/photo/edit/{photo_id}", status_code=302)
