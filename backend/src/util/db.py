from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.src.config.config import settings
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


#def get_db():
#    db = SessionLocal()
#    try:
#        yield db
#    finally:
#        db.close()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
           yield session
        finally:
           await session.close()

