from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
#from src.util.schemas.user import UserCreate, User
from src.config import security
from src.config.jwt import create_access_token
#from src.util.db import get_db
#from src.util.models.user import User as UserModel
#from src.util.crud.user import get_user_by_username, create_user

router = APIRouter()