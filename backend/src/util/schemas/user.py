from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.src.util.models.user import UserRole


class Token(BaseModel):
    """
    Schema for token representation.

    Attributes:
        access_token (str): The access token string.
        token_type (str): The type of the token.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for token data, used for extracting user information from the token.

    Attributes:
        email (Optional[str]): The email of the user, optional.
    """
    email: Optional[str] = None


class BlacklistedToken(BaseModel):
    """
    Schema for blacklisted tokens.

    Attributes:
        token (str): The token string.
        blacklisted_on (datetime): The date and time when the token was blacklisted.
    """
    token: str
    blacklisted_on: datetime


class UserBase(BaseModel):
    """
    Base schema for user representation containing the email.

    Attributes:
        email (str): The email of the user.
    """
    email: str


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Inherits from UserBase.

    Attributes:
        email (str): The email of the user.
        password (str): The password for the user account.

    """
    password: str


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.

    Attributes:
        email (Optional[str]): The new email of the user, optional.
        password (Optional[str]): The new password of the user, optional.
        role (Optional[str]): The new role of the user, optional.
    """
    email: Optional[str] = None
    password: Optional[str] = None
    role: UserRole = None


class UserProfile(UserBase):
    """
    Schema for returning a user's profile.
    Inherits from UserBase.

    Attributes:
        id (int): The ID of the user.
        registered_at (datetime): The date and time when the user registered.
        photos_count (int): The count of photos uploaded by the user.
    """
    id: int
    registered_at: datetime
    is_active: bool
    photos_count: int


class PrivateUser(UserBase):
    """
        Schema for returning a user.
        Inherits from UserBase.

        Attributes:
            registered_at (datetime): The timestamp when the user was registered.
            last_login (datetime): The timestamp of the user's last login.
            photos_uploaded (int): The count of photos uploaded by the user.
        """
    registered_at: datetime
    last_login: datetime
    photos_uploaded: int

    class Config:
        """
        Pydantic configuration class for User schema.

        Attributes:
            from_attributes (bool): Enables loading data from SQLAlchemy models.
        """
        from_attributes = True  # This enables orm_mode to allow loading from SQLAlchemy models


class User(UserBase):
    """
    Schema for returning a user.
    Inherits from UserBase.

    Attributes:
        registered_at (datetime): The timestamp when the user was registered.
        """
    registered_at: datetime
    photos_uploaded: int

    class Config:
        """
        Pydantic configuration class for User schema.

        Attributes:
            from_attributes (bool): Enables loading data from SQLAlchemy models.
        """
        from_attributes = True  # This enables orm_mode to allow loading from SQLAlchemy models
