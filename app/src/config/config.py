import os
from enum import Enum
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.templating import Jinja2Templates

load_dotenv()

templates = Jinja2Templates(directory="app/src/templates")


class FrontEndpoints(Enum):
    """Class representing frontend-endpoints, which are used to map custom exception handler in FastAPI"""
    HOME = "/"
    SIGNUP_FORM = "/auth/signup-form"
    LOGIN_FORM = "/auth/login-form"
    LOGOUT_FORM = "/auth/logout-form"
    PEOPLE_FORM = "/discover/people"
    PHOTO_UPLOAD_FORM = "/photo/upload-form"
    PROFILE_MY_PHOTOS = "/profile/my-photos"
    ADMIN_DASHBOARD = "/admin/dashboard"
    ADMIN_BAN_USER = "/admin/ban-user"
    ADMIN_DELETE_PHOTO = "/admin/delete-photo"
    ADMIN_RATINGS = "/admin/ratings"
    ADMIN_COMMENTS = "/admin/comments"


url_to_endpoint = {
    "/auth": FrontEndpoints.LOGIN_FORM.value,
    "/photo": FrontEndpoints.PHOTO_UPLOAD_FORM.value,
    "/admin": FrontEndpoints.ADMIN_DASHBOARD.value,
}


class Settings(BaseSettings):
    """
    Class that stores project-wide configurations.
    """
    PROJECT_NAME: str = "PhotoShare"
    DESCRIPTION: str = "API for PhotoShare application"
    VERSION: str = "1.5"

    DEV_API_KEY: str = os.getenv("DEV_API_KEY")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")

    MAX_TAGS: int = 5
    USERNAME_LENGTH: int = 8

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 4320

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
