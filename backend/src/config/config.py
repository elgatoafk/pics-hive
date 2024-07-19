import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PhotoShare"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

settings = Settings()
