
from datetime import datetime
from ..models.token import BlacklistedToken, Token
import time
from app.src.util.db import AsyncSessionLocal as SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio


async def blacklist_token(db: AsyncSession, token: str):
    stripped_token = token.replace("Bearer ", "")
    result = await db.execute(select(BlacklistedToken).filter(BlacklistedToken.token == stripped_token))
    blacklisted_token = result.scalars().first()
    if blacklisted_token:
        return
    blacklisted_token_new = BlacklistedToken(token=stripped_token)
    db.add(blacklisted_token_new)
    await db.commit()
    await db.refresh(blacklisted_token_new)
    return blacklisted_token_new


async def is_token_blacklisted(db: AsyncSession, token: str) -> bool:
    result = await db.execute(select(BlacklistedToken).filter(BlacklistedToken.token == token))
    blacklisted_token = result.scalars().first()
    return blacklisted_token is not None


async def remove_expired_tokens(db: AsyncSession):
    while True:
        async with SessionLocal() as db:
            await remove_expired_tokens(db)
        await asyncio.sleep(86400)  # Run once a day


def cleanup_expired_tokens():
    while True:
        db: AsyncSession = SessionLocal()
        remove_expired_tokens(db)
        time.sleep(86400)  # Run once a day



async def get_active_tokens_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Token).filter(Token.user_id == user_id, Token.expires_at > datetime.utcnow())
    )
    return result.scalars().all()
