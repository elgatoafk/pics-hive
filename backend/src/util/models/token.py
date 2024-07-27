from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
#import datetime
from datetime import datetime as dt, timedelta
from sqlalchemy.orm import relationship
from .base import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    token = Column(String, primary_key=True, unique=True, index=True)
    blacklisted_on = Column(DateTime, default=dt.utcnow)

    def __repr__(self):
        return f"<BlacklistedToken(token={self.token}, blacklisted_on={self.blacklisted_on})>"


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=dt.utcnow)
    expires_at = Column(DateTime, default=lambda: dt.utcnow() + timedelta(minutes=30))

    user = relationship("User", back_populates="tokens")



    