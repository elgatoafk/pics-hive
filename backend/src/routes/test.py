import asyncio

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException

from backend.src.config.config import settings
from backend.src.config.logging_config import log_function

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)
async def resize_photo(
        public_id: str, width: int, height: int):
    """Resizes an image using Cloudinary API.

    """

    transformed_url = cloudinary.uploader.explicit(
        public_id,
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



@log_function
async def add_filter(public_id: str, filter: str):
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
    transformed_url = cloudinary.uploader.explicit(
        public_id,
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


print(asyncio.run(add_filter("f4aaafaf-7376-4506-976a-bae4d91b5e7c/f6e96ca9-a6a7-4442-9c06-19b107606f1a", "sizzle")))
print(asyncio.run(resize_photo("f4aaafaf-7376-4506-976a-bae4d91b5e7c/f6e96ca9-a6a7-4442-9c06-19b107606f1a", 400, 600)))