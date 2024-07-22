from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from backend.src.util.schemas import schemas
from backend.src.util.models import models
from backend.src.util.crud import crud
from backend.src.config import auth 
from backend.src.config.auth import get_db, get_current_active_user, get_password_hash, create_access_token
from backend.src.config.dependencies import get_current_admin
