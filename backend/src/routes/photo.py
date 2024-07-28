
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from backend.src.util.schemas.photo import PhotoCreate, PhotoUpdate, PhotoResponse
from backend.src.util.crud.photo import create_photo, get_photo, update_photo, delete_photo
from backend.src.util.db import get_db
from backend.src.services.photos import PhotoService
from backend.src.config.security import get_current_user
router = APIRouter()

@router.post("/photos/", response_model=PhotoResponse)
async def creat_photo_route(photo: PhotoCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Creates a new photo in the database.

    Parameters:
    photo (PhotoCreate): The photo data to be created.
    user_id (int): The ID of the user creating the photo.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The created photo data.
    """
    return await create_photo(db, photo, user_id)

@router.get("/photos/", response_model=PhotoResponse)
async def get_photo_route(photo_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a photo from the database based on the provided photo ID.

    Parameters:
    photo_id (int): The unique identifier of the photo to retrieve.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The retrieved photo data. If the photo is not found, returns None.
    """
    return await get_photo(db, photo_id)

@router.put("/photos/", response_model=PhotoResponse)
async def update_photo_route(photo: PhotoUpdate, photo_id: int, db: Session = Depends(get_db)):
    """
    Updates an existing photo in the database based on the provided photo ID.

    Parameters:
    photo (PhotoUpdate): The updated photo data.
    photo_id (int): The unique identifier of the photo to update.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    PhotoResponse: The updated photo data. If the photo is not found, raises a 404 HTTPException.
    """
    updated_photo = await update_photo(db, photo, photo_id)
    if not updated_photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return updated_photo

@router.delete("/photos/")
async def delete_photo_route(photo_id: int, db: Session = Depends(get_db)):
    """
    Deletes a photo from the database based on the provided photo ID.

    Parameters:
    photo_id (int): The unique identifier of the photo to delete.
    db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    dict: A dictionary with a 'detail' key indicating the success message. If the photo is not found, raises a 404 HTTPException.
    """
    photo_db = await get_photo(db, photo_id)
    if not photo_db:
        raise HTTPException(status_code=404, detail="Photo not found")
    else:
        await delete_photo(db, photo_db)
        return {"detail": "Photo deleted successfully"}


@router.post("photos/generate_qr_code")
async def generate_qr_code(
    photo_url: str, request: Request, user=Depends(get_current_user())
):
    """Generates a QR code for the given image URL.

    Args:
        photo_url (str): The URL of the image for which the QR code needs to be generated.
        request (Request): The FastAPI request object.
        user (User, optional): The authenticated user. Defaults to Depends(get_current_user()).

    Returns:
        Response: A FastAPI response object containing the generated QR code as a PNG image.
        The response has the following properties:
            - content: The QR code image data.
            - media_type: The MIME type of the content, which is "image/png".
            - headers: A dictionary containing the "content-disposition" header with the value "inline".
            - status_code: The HTTP status code, which is 200.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    if user:
        qr_code = await PhotoService.generate_qr_code(photo_url=photo_url)
        return Response(
            content=qr_code,
            media_type="image/png",
            headers={"content-disposition": "inline"},
            status_code=200,
        )
    else:
        raise HTTPException(status_code=401, detail="User not authenticated")

