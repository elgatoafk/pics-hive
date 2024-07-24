from pydantic import BaseModel

class RatingBase(BaseModel):
    rating: int

class RatingCreate(RatingBase):
    photo_id: int

class RatingResponse(RatingBase):
    id: int
    user_id: int
    photo_id: int

    class Config:
        orm_mode = True
