import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from backend.src.util.schemas import user as schema_user
from backend.src.util.models import user as model_user
from backend.src.util.crud import token as crud_token
from backend.src.config.jwt import create_access_token
from backend.src.util.logging_config import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

#async def get_user_by_email(db: AsyncSession, email: str):
#    logger.debug('get_user_by_email')
#    result = await db.execute(select(model_user.User).filter(model_user.User.email == email))
#    logger.debug('get_user_by_email : result : {}'.format(type(result)))
    
#    return result.scalars().first()



async def get_user_by_email(db: AsyncSession, email: str):
    logger.debug('get_user_by_email')
    result = await db.execute(select(model_user.User).filter(model_user.User.email == email))
    user = result.scalars().first()
    if user :
        logger.debug('get_user_by_email : user : {}'.format(user.email))
    
    return user



async def create_user(db: AsyncSession, user: schema_user.UserCreate):
    logger.debug('create_user')
    hashed_password = hash_password(user.password)
    db_user = model_user.User(email=user.email, hashed_password=hashed_password, role=user.role)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email}, user_id=db_user.id, db=db)
    return db_user


async def get_user(db: AsyncSession, user_id: int):
    logger.debug('get_user')
    result = await db.execute(select(model_user.User).filter(model_user.User.id == user_id))
    return result.scalars().first()

#def get_user_by_email(db: Session, email: str):
#    logger.debug('get_user_by_email')
#    return db.query(model_user.User).filter(model_user.User.email == email).first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    logger.debug('get_users')
    #return db.query(model_user.User).offset(skip).limit(limit).all()
    result = await db.execute(select(model_user.User).offset(skip).limit(limit))
    return result.scalars().all()


def hash_password(password: str) -> str:
    logger.debug('hash_password')
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug('verify_password')
    # Verify the given password against the stored hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

#def create_user(db: Session, user: schema_user.UserCreate):
#    logger.debug('create_user')
#    hashed_password = hash_password(user.password)
#    db_user = model_user.User(email=user.email, hashed_password=hashed_password, role=user.role)
#    db.add(db_user)
#    db.commit()
#    db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email}, user_id=db_user.id, db=db)
    return db_user

#def update_user(db: Session, user: model_user.User, user_update: schema_user.UserUpdate):
#    logger.debug('update_user')
#    if user_update.email is not None:
#        user.email = user_update.email
#    if user_update.password is not None:
#        user.hashed_password = hash_password(user_update.password)
#    if user_update.role is not None:
#        user.role = user_update.role
#    db.add(user)
#    db.commit()
#    db.refresh(user)
#    return user

async def update_user(db: AsyncSession, user: model_user.User, user_update: schema_user.UserUpdate):
    logger.debug('update_user')
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = hash_password(user_update.password)
        logger.debug('done - hash_password')
    if user_update.role is not None:
        user.role = user_update.role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.debug('done - update_user')
    return user


#def delete_user(db: Session, user_id: int):
#    logger.debug('crud: delete_user')
#    try:
#        user = db.query(model_user.User).filter(model_user.User.id == user_id).one()
#        logger.debug('user: {}'.format(user))
#        
#        active_tokens = crud_token.get_active_tokens_for_user(db, user_id) 

#        for token in active_tokens:
#            logger.debug('TEST token: {}'.format(token.token))
#            crud_token.add_token_to_blacklist(db, token.token)
        
#        logger.debug('delete test')
#        db.delete(user)
#        db.commit()
#    except NoResultFound:
#        raise ValueError(f"User with id {user_id} does not exist")
    

async def delete_user(db: AsyncSession, user_id: int):
    logger.debug('crud: delete_user')
    try:
        result = await db.execute(select(model_user.User).filter(model_user.User.id == user_id))
        user = result.scalar_one()
        logger.debug(f'user: {user}')
        
        logger.debug(f'start : delete_user: get_active_tokens_for_user')
        active_tokens = await crud_token.get_active_tokens_for_user(db, user_id) 
        logger.debug(f'end : delete_user: get_active_tokens_for_user')


        for token in active_tokens:
            logger.debug(f'TEST token: {token.token}')
            await crud_token.add_token_to_blacklist(db, token.token)
        
        logger.debug('delete test')
        await db.delete(user)
        await db.commit()
        return user
    except NoResultFound:
        raise ValueError(f"User with id {user_id} does not exist")

