import os
#from pydantic import BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PhotoShare"
    #SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    #ALGORITHM: str = "HS256"
    #ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_DB_NAME: str
    DATABASE_DOMAIN: str
    DATABASE_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_API_URL: str

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '.env'))


settings = Settings()

#print("Loaded settings:", settings.model_dump())  # This will print all settings




