from pydantic import BaseModel, conlist
from typing import List


class TagCreate(BaseModel):
    """Schema for creating a new tag.

    Attributes:
        tag_name (str): The name of the tag.
    """
    name: str


class PhotoTaggingRequest(BaseModel):
    """Schema for a photo tagging request.

    Attributes:
        tags (conlist): A list of tags to be added to the photo.
                        Must contain between 1 and 5 tags.

    """
    tags: conlist(TagCreate, min_length=1, max_length=5)


class PhotoTaggingResponse(BaseModel):
    """Schema for a photo tagging response.

    Attributes:
        photo_id (int): The ID of the photo.
        tags (List[str]): A list of tag names associated with the photo.
    """
    photo_id: int
    tags: List[str]

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    name: str