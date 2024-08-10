from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from datetime import datetime as dt, timedelta
from app.src.util.db import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    __table_args__ = {'extend_existing': True}

    token = Column(String, primary_key=True, unique=True)
    blacklisted_on = Column(DateTime, default=dt.utcnow)

    def __repr__(self):
        return f"<BlacklistedToken(token={self.token}, blacklisted_on={self.blacklisted_on})>"


class Token(Base):
    __tablename__ = "tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=dt.utcnow)
    expires_at = Column(DateTime)





    