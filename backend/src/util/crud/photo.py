from sqlalchemy.orm import joinedload
from fastapi import status
from backend.src.util.models.photo import Photo
from backend.src.util.schemas.photo import PhotoUpdate
from backend.src.util.models.tag import Tag
from sqlalchemy.future import select
from io import BytesIO
from uuid import uuid4
import cloudinary
import cloudinary.uploader
import qrcode
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from backend.src.config.config import settings
from backend.src.util.models.user import User
from backend.src.util.schemas.photo import PhotoResponse

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


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
        return src_url

    @staticmethod
    async def resize_photo(
            photo_id: int, width: int, height: int, db: AsyncSession
    ):
        """Resizes an image using Cloudinary API.

        """
        photo = await get_photo(db, photo_id)

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
    async def add_filter(photo_id: int, filter: str, db: AsyncSession, current_user: User):
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
        photo = await get_photo(db, photo_id)
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        if photo.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        transformed_url = cloudinary.uploader.explicit(
            photo.id,
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


async def create_photo_in_db(description: str, file, user_id: int, db: AsyncSession, tag_names: list) -> Photo:
    """
        Creates a Photo record in the database and uploads the image to Cloudinary.

        Args:
            description (str): The description of the photo.
            file: The file object of the photo.
            user_id (int): The ID of the user who is uploading the photo.
            db (AsyncSession): The database session.
            tag_names (list): List of tag names associated with the photo.

        Returns:
            Photo: The created Photo object.
        """
    photo_url = await PhotoService.upload_photo(file)
    tags = []
    for name in tag_names:
        tag = await db.execute(select(Tag).where(Tag.name == name))
        tag = tag.scalars().first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        tags.append(tag)
    new_photo = Photo(
        description=description,
        url=photo_url,
        user_id=user_id,
        tags=tags
    )
    db.add(new_photo)
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalars().first()
    if user:
        user.photos_uploaded = user.photos_uploaded + 1
        db.add(user)

    await db.commit()
    await db.refresh(new_photo)
    return new_photo


async def get_photo(db: AsyncSession, photo_id: int):
    """
    Asynchronously retrieves a photo from the database by its ID.

    Parameters:
    - db (AsyncSession): The SQLAlchemy AsyncSession object for database operations.
    - photo_id (int): The unique identifier of the photo to retrieve.


    Returns:
    - PhotoResponse: A response object containing the photo's details.

    Raises:
    - HTTPException: If the photo is not found in the database, a 404 Not Found error is raised.
    - HTTPException: If an error occurs during database operations, a 500 Internal Server Error is raised.
    """
    try:
        result = await db.execute(select(Photo).options(joinedload(Photo.tags)).filter(Photo.id == photo_id))
        db_photo = result.scalars().first()
        if not db_photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
        tags = [tag.name for tag in db_photo.tags]
        response = PhotoResponse(id=db_photo.id, user_id=db_photo.user_id, url=db_photo.url,
                                 description=db_photo.description, tags=tags)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_photo_description(photo_id: int, new_description: str, db: AsyncSession) -> Photo:
    """
    Updates the description of a photo in the database.

    Args:
        photo_id (int): The ID of the photo to update.
        new_description (str): The new description for the photo.
        db (AsyncSession): The database session.

    Returns:
        Photo: The updated Photo object.
    """
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    photo.description = new_description
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def delete_photo(db: AsyncSession, photo_id: int):
    """
    Deletes a photo from the database and decrements the owner's photo counter.

    Parameters:
    db (AsyncSession): The database session.
    photo_id (int): The ID of the photo to delete.

    Raises:
    HTTPException: If the photo is not found.
    """
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    user_result = await db.execute(select(User).where(User.id == photo.user_id))
    user = user_result.scalars().first()
    if user:
        user.photos_uploaded -= 1
        db.add(user)

    await db.delete(photo)
    await db.commit()
