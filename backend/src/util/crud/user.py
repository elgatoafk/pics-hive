import bcrypt
from sqlalchemy.orm import Session
from backend.src.util.schemas import user as schema_user
from backend.src.util.models import user as model_user


dbg = True

def get_user(db: Session, user_id: int):
    if dbg: print('get_user')
    return db.query(model_user.User).filter(model_user.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    if dbg: print('get_user_by_email')
    return db.query(model_user.User).filter(model_user.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    if dbg: print('get_users')
    return db.query(model_user.User).offset(skip).limit(limit).all()

def hash_password(password: str) -> str:
    if dbg: print('hash_password')
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if dbg: print('verify_password')
    # Verify the given password against the stored hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(db: Session, user: schema_user.UserCreate):
    if dbg: print('create_user')
    hashed_password = hash_password(user.password)
    db_user = model_user.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: model_user.User, user_update: schema_user.UserUpdate):
    if dbg: print('update_user')
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = hash_password(user_update.password)
    if user_update.role is not None:
        user.role = user_update.role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: model_user.User):
    if dbg: print('delete_user')
    db.delete(user)
    db.commit()