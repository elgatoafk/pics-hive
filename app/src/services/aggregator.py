from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.util.crud.photo import get_photo, PhotoService


class Aggregator:
    """Class for storing shared logic for various endpoints."""
    @staticmethod
    async def generate_qr(photo_id: int, db: AsyncSession):
        """
        Shared logic for generating a QR code for a photo.

        Args:
            photo_id (int): The unique identifier of the photo.
            db (AsyncSession): The SQLAlchemy asynchronous session.

        Returns:
            QR code image or raises an HTTPException if the photo is not found.
        """

        photo = await get_photo(db, photo_id)
        if photo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not Found")

        qr_code = await PhotoService.generate_qr_code(photo.url)
        if qr_code is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR Code not Found")

        return qr_code
