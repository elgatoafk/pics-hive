from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.src.util.models.token import BlacklistedToken, Token
import time
from sqlalchemy.orm import Session

from backend.src.util.db import AsyncSessionLocal as SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import asyncio

from datetime import datetime
from ..models.token import BlacklistedToken, Token
import time



async def add_token_to_blacklist(db: AsyncSession, token: str):
    """
    Add a token to the blacklist.

    Args:
        db (AsyncSession): The database session to use for the operation.
        token (str): The token to be blacklisted.

    Returns:
        BlacklistedToken: The newly created blacklisted token.
    """
    blacklisted_token = BlacklistedToken(token=token)
    db.add(blacklisted_token)
    await db.commit()
    await db.refresh(blacklisted_token)
    return blacklisted_token


async def is_token_blacklisted(db: AsyncSession, token: str) -> bool:
    """
    Check if a token is blacklisted.

    Args:
        db (AsyncSession): The database session to use for the operation.
        token (str): The token to check.

    Returns:
        bool: True if the token is blacklisted, False otherwise.
    """
    result = await db.execute(select(BlacklistedToken).filter(BlacklistedToken.token == token))
    return result.scalars().first() is not None


async def remove_expired_tokens(db: AsyncSession):

    """
    Remove expired tokens from the database in an infinite loop running once a day.

    Args:
        db (AsyncSession): The database session to use for the operation.
    """
    while True:
        async with SessionLocal() as db:
            await remove_expired_tokens(db)
        await asyncio.sleep(86400)  # Run once a day


def cleanup_expired_tokens():
    """
    Remove expired tokens from the database in an infinite loop running once a day (synchronous version).
    """
    while True:
        db: AsyncSession = SessionLocal()
        try:
            remove_expired_tokens(db)
        finally:
            db.close()
        time.sleep(86400)  # Run once a day


async def get_active_tokens_for_user(db: AsyncSession, user_id: int):
    """
    Retrieve all active tokens for a given user.

    Args:
        db (AsyncSession): The database session to use for the operation.
        user_id (int): The ID of the user.

    Returns:
        List[Token]: A list of active tokens for the user.
    """
    result = await db.execute(
        select(Token).filter(Token.user_id == user_id, Token.expires_at > datetime.utcnow())
    )
    return result.scalars().all()

