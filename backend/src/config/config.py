import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv, dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict


#@Everyone, create .env file in this folder
# with the required fields (SECRET_KEY, DATABASE_URL),
# each one who works on DB should set up Postgres in Docker


load_dotenv()

class Settings(BaseSettings):
    
    PROJECT_NAME: str = "PhotoShare"
    DESCRIPTION: str = "API for PhotoShare application"
    VERSION: str = "1.0"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost/dbname")
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DB_NAME: str
    DATABASE_DOMAIN: str
    DATABASE_PORT: int

    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET")
    cloudinary_name: str = os.getenv("CLOUDINARY_name")

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '.env'))



settings = Settings()


