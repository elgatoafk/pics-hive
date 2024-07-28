import os
from dotenv import load_dotenv, dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "PhotoShare"
    DESCRIPTION: str = "API for PhotoShare application"
    VERSION: str = "1.0"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_USER: str = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD")
    DATABASE_DOMAIN: str = os.getenv("DATABASE_DOMAIN")
    DATABASE_DB_NAME: str = os.getenv("DATABASE_DB_NAME")

    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")
    CLOUDINARY_API_URL: str = os.getenv("CLOUDINARY_API_URL")

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '.env'))



settings = Settings()

#print("Loaded settings:", settings.model_dump())  # This will print all settings
