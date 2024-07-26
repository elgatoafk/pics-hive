import os
from pydantic import BaseSettings
from dotenv import load_dotenv, dotenv_values

#@Everyone, create .env file in this folder
# with the required fields (SECRET_KEY, DATABASE_URL),
# each one who works on DB should set up Postgres in Docker


load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "PhotoShare"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost/dbname")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET")
    cloudinary_name: str = os.getenv("CLOUDINARY_name")


settings = Settings()


