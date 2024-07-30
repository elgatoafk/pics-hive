from io import BytesIO
from uuid import uuid4

import cloudinary
import cloudinary.uploader
import qrcode
from backend.src.util.crud.photo import get_photo
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.src.config.config import settings
from backend.src.util.models.user import User

# cloudinary.config(
#     cloud_name=settings.CLOUDINARY_CLOUD_NAME,
#     api_key=settings.CLOUDINARY_API_KEY,
#     api_secret=settings.CLOUDINARY_API_SECRET,
#     secure=True,
# )


class PhotoService:
    """
    A class that provides image-related services such as uploading, resizing, adding filters, and generating QR codes.
    """

    @staticmethod
    async def upload_photo(file):
        """Uploads an image to the cloud storage.

        """
        unique_filename = str(uuid4())
        public_id = f"f4aaafaf-7376-4506-976a-bae4d91b5e7c/{unique_filename}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            version=r.get("version")
        )
        return {"public_id": public_id, "url": src_url}

    @staticmethod
    async def resize_photo(
            photo_id: int, width: int, height: int, user: User, db: Session
    ):
        """Resizes an image using Cloudinary API.

        """
        photo = await get_photo(photo_id, db=db)
        transformed_url = cloudinary.uploader.explicit(
            photo.public_id,
            type="upload",
            eager=[
                {
                    "width": width,
                    "height": height,
                    "crop": "fill",
                    "gravity": "auto",
                },
                {"fetch_format": "auto"},
                {"radius": "max"},
            ],
        )
        try:
            url_to_return = transformed_url["eager"][0]["secure_url"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid width or height")
        return url_to_return

    @staticmethod
    async def add_filter(photo_id: int, filter: str, user: User, db: Session):
        """Apply a filter to an image and return the transformed URL.

        """
        filters = [
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
        ]
        effect = f"art:{filter}" if filter in filters else filter
        photo = await get_photo(photo_id, db=db)
        transformed_url = cloudinary.uploader.explicit(
            photo.public_id,
            type="upload",
            eager=[
                {
                    "effect": effect,
                },
                {"fetch_format": "auto"},
                {"radius": "max"},
            ],
        )
        try:
            url_to_return = transformed_url["eager"][0]["secure_url"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid filter")
        return url_to_return

    @staticmethod
    async def generate_qr_code(photo_url: str):
        """Generates a QR code image from the given image URL.

        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(photo_url)
        qr.make(fit=True)
        qr_code = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        qr_code.save(buffered, "PNG")
        qr_bytes = buffered.getvalue()
        return qr_bytes



