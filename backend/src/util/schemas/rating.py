from pydantic import BaseModel
from pydantic import BaseModel

class RatingBase(BaseModel):
    """
    Base model for rating attributes.

    Attributes:
    rating (int): The rating value.
    """
    rating: int

class RatingCreate(RatingBase):
    """
    Model for creating a new rating. Inherits from RatingBase.

    Attributes:
    photo_id (int): The ID of the photo being rated.
    """
    photo_id: int

class RatingResponse(RatingBase):
    """
    Model for rating response. Inherits from RatingBase.

    Attributes:
    id (int): The unique identifier of the rating.
    user_id (int): The ID of the user who made the rating.
    photo_id (int): The ID of the photo being rated.

    Config:
    orm_mode (bool): Indicates that this model is used with an ORM.
    """
    id: int
    user_id: int
    photo_id: int

    class Config:
        orm_mode = True