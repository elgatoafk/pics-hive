from nanoid import generate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.config.config import settings
from app.src.util.models import User


async def generate_unique_username(db: AsyncSession, size=settings.USERNAME_LENGTH) -> str:
    """
        Generates a unique username using the nanoid library and checks for its uniqueness in the database.

        Args:
            db (AsyncSession): The database session.
            size (int): The size of the unique username.

        Returns:
            str: A unique username.
        """
    while True:
        username = generate(size=size)
        result = await db.execute(select(User).where(User.username == username))
        existing_user = result.scalars().first()
        if not existing_user:
            return username
