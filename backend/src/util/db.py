from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config.config import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import URL

DATABASE_URL = f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_DOMAIN}/{settings.DATABASE_DB_NAME}"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


