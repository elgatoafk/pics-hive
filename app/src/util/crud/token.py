from datetime import datetime
from sqlalchemy import delete
from ..models.token import BlacklistedToken, Token
from app.src.util.db import AsyncSessionLocal as SessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.src.config.logging_config import log_function


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


async def remove_expired_tokens():
    async for session in get_db():
        delete_stmt = delete(Token).where(Token.expires_at < datetime.utcnow())
        await session.execute(delete_stmt)
        await session.commit()

async def get_active_tokens_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Token).filter(Token.user_id == user_id, Token.expires_at > datetime.utcnow())
    )
    return result.scalars().all()

@log_function
async def remove_blacklisted_tokens():
    async for session in get_db():
        result = await session.execute(select(BlacklistedToken))
        tokens = result.scalars().all()
        for token in tokens:
            await session.delete(token)

        await session.commit()



