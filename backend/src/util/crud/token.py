from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.src.util.models.token import BlacklistedToken, Token
import time
from sqlalchemy.orm import Session

from backend.src.util.db import AsyncSessionLocal as SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio


async def add_token_to_blacklist(db: AsyncSession, token: str):
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    await db.commit()
    await db.refresh(blacklisted_token)
    return blacklisted_token


def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None

def remove_expired_tokens(db: Session):
    expiration_time = datetime.utcnow() - timedelta(days=30)  # Set your TTL here
    db.query(BlacklistedToken).filter(BlacklistedToken.blacklisted_on < expiration_time).delete()
    db.commit()

def cleanup_expired_tokens():
    while True:
        db: Session = SessionLocal()
        try:
            remove_expired_tokens(db)
        finally:
            db.close()
        time.sleep(86400)  # Run once a day
 

async def get_active_tokens_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Token).filter(Token.user_id == user_id, Token.expires_at > datetime.utcnow())
    )
    return result.scalars().all()
