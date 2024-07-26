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
    return await create_photo(db, photo, user_id)

@router.get("/photos/", response_model=PhotoResponse)
async def get_photo_route(photo_id: int, db: Session = Depends(get_db)):
    return await get_photo(db, photo_id)

@router.put("/photos/", response_model=PhotoResponse)
async def update_photo_route(photo: PhotoUpdate, photo_id: int, db: Session = Depends(get_db)):
    updated_photo = await update_photo(db, photo, photo_id)
    if not updated_photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return updated_photo

@router.delete("/photos/")
async def delete_photo_route(photo_id: int, db: Session = Depends(get_db)):
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

    """
    if user:
        qr_code = await PhotoService.generate_qr_code(photo_url=photo_url)
        return Response(
            content=qr_code,
            media_type="image/png",
            headers={"content-disposition": "inline"},
            status_code=200,
        )