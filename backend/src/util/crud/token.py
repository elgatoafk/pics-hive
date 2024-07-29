from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models.token import BlacklistedToken, Token
import time
from sqlalchemy.orm import Session
from backend.src.util.db import AsyncSessionLocal as SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
import asyncio


async def add_token_to_blacklist(db: AsyncSession, token: str):
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    await db.commit()
    await db.refresh(blacklisted_token)
    return blacklisted_token


async def is_token_blacklisted(db: AsyncSession, token: str) -> bool:
    result = await db.execute(select(BlacklistedToken).filter(BlacklistedToken.token == token))
    return result.scalars().first() is not None


async def remove_expired_tokens(db: AsyncSession):
    while True:
        async with SessionLocal() as db:
            await remove_expired_tokens(db)
        await asyncio.sleep(86400)  # Run once a day


def cleanup_expired_tokens():
    while True:
        db: AsyncSession = SessionLocal()
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
