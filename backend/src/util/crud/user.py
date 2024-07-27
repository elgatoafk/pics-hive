from sqlalchemy.orm import Session
from util.models.photo import Photo
from util.models.user import User
from util.schemas.user import UserCreate, UserUpdate

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_profile(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        photos_count = db.query(Photo).filter(Photo.owner_id == user.id).count()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "registered_at": user.registered_at,
            "is_active": user.is_active,
            "photos_count": photos_count
        }
    return None

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()