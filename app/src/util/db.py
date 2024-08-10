from sqlalchemy.exc import OperationalError

from app.src.config.config import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_DOMAIN}/{settings.DATABASE_DB_NAME}"

Base = declarative_base()

async_engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    pool_recycle=1800,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except OperationalError as e:
            await session.rollback()
            raise e