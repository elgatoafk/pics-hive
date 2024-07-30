from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime as dt, timedelta
from sqlalchemy.orm import relationship
from .base import Base


class BlacklistedToken(Base):
    """
    Represents a blacklisted token in the database.

    Attributes:
        token (str): The token string that has been blacklisted.
        blacklisted_on (datetime): The date and time when the token was blacklisted.
    """
    __tablename__ = "blacklisted_tokens"

    token = Column(String, primary_key=True, unique=True, index=True)
    blacklisted_on = Column(DateTime, default=dt.utcnow)

    def __repr__(self):
        """
        Provide a string representation of the BlacklistedToken instance.

        Returns:
            str: A string representation of the blacklisted token.
        """
        return f"<BlacklistedToken(token={self.token}, blacklisted_on={self.blacklisted_on})>"


class Token(Base):
    """
    Represents an access token in the database.

    Attributes:
        id (int): The unique identifier for the token.
        token (str): The token string.
        user_id (int): The ID of the user to whom the token belongs.
        created_at (datetime): The date and time when the token was created.
        expires_at (datetime): The date and time when the token will expire.
        user (User): The relationship to the User model.
    """
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=dt.utcnow)
    expires_at = Column(DateTime, default=lambda: dt.utcnow() + timedelta(minutes=30))

    user = relationship("User", back_populates="tokens")
