from sqlalchemy.orm import Session
from fastapi import Depends
from backend.src.util.db import get_db
from backend.src.util.models.user import User
from backend.src.util.schemas.user import UserCreate
from backend.src.config.security import get_password_hash


def get_user(user_id: int, db:Session = Depends(get_db)) -> User:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(email: str,db:Session = Depends(get_db)) -> User:
	return db.query(User).filter(User.email == email).first()

def create_user(body: UserCreate, db:Session = Depends(get_db)) -> User:
	hashed_password = get_password_hash(body.password)
	user = User(email=body.email, password=hashed_password,username=body.username)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user

def update_user(db: Session, user_id: int) :
	pass

def delete_user(db: Session, user_id: int) :
    pass


