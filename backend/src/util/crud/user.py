from sqlalchemy import func
import bcrypt

from sqlalchemy.orm.exc import NoResultFound
from backend.src.util.schemas import user as schema_user

from backend.src.util.models import user as model_user

from backend.src.util.crud import token as crud_token
from backend.src.config.jwt import create_access_token
from backend.src.util.logging_config import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.util.models.photo import Photo


async def get_user_profile(db: AsyncSession, username: str):
    """
    Retrieve the profile of a user by username.

    Args:
        db (Session): The database session.
        username (str): The username of the user.

    Returns:
        dict: A dictionary containing user profile information if the user exists, None otherwise.

    Profile Information:
        - id: User ID
        - username: Username
        - email: Email
        - full_name: Full name
        - registered_at: Registration date
        - is_active: Active status
        - photos_count: Number of photos uploaded by the user
    """
    result = await db.execute(select(model_user.User).filter(model_user.User.username == username))
    user = result.scalars().first()
    if user:
        photos_count_result = await db.execute(
            select(func.count().label('count')).filter(Photo.owner_id == user.id)
        )
        photos_count = photos_count_result.scalar()
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


async def get_user_by_email(db: AsyncSession, email: str):
    """
    Retrieve a user by email.

    Args:
        db (AsyncSession): The database session.
        email (str): The email of the user.
    Returns:
        model_user.User: The user object if found, None otherwise.

    Logs:
        A debug log indicating the function execution and the user's email if found.
    """
    logger.debug('get_user_by_email')
    result = await db.execute(select(model_user.User).filter(model_user.User.email == email))
    user = result.scalars().first()
    if user:
        logger.debug('get_user_by_email : user : {}'.format(user.email))

    return user


async def create_user(db: AsyncSession, user: schema_user.UserCreate):
    """
    Create a new user in the database.

    Args:
        db (AsyncSession): The database session.
        user (schema_user.UserCreate): The user creation schema.

    Returns:
        model_user.User: The newly created user object.

    Logs:
        A debug log indicating the function execution.
    """
    logger.debug('create_user')
    hashed_password = hash_password(user.password)
    db_user = model_user.User(email=user.email, hashed_password=hashed_password, role=user.role)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email}, user_id=db_user.id, db=db)
    return db_user


async def get_user(db: AsyncSession, user_id: int):
    """
    Retrieve a user by user ID.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.

    Returns:
        model_user.User: The user object if found, None otherwise.

    Logs:
        A debug log indicating the function execution.
    """
    logger.debug('get_user')
    result = await db.execute(select(model_user.User).filter(model_user.User.id == user_id))
    logger.debug('marina  {}'.format(result))
    logger.debug('result.scalars().first')
    
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of users from the database.

    Args:
        db (AsyncSession): The database session.
        skip (int): The number of records to skip for pagination. Default is 0.
        limit (int): The maximum number of records to return. Default is 100.

    Returns:
        List[model_user.User]: A list of user objects.

    Logs:
        A debug log indicating the function execution.
    """
    logger.debug('get_users')
    result = await db.execute(select(model_user.User).offset(skip).limit(limit))
    return result.scalars().all()


def hash_password(password: str) -> str:
    """
    Hash the given password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.

    Logs:
        A debug log indicating the function execution.
    """
    logger.debug('hash_password')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the given plain text password against the stored hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.

    Logs:
        A debug log indicating the function execution.
    """
    logger.debug('verify_password')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def update_user(db: AsyncSession, user: model_user.User, user_update: schema_user.UserUpdate):
    """
    Update the user's information in the database.

    Args:
        db (AsyncSession): The database session.
        user (model_user.User): The user object to update.
        user_update (schema_user.UserUpdate): The new user data to update.
    Returns:
        model_user.User: The updated user object.

    Logs:
        Various debug logs indicating the progress of the update process.
    """
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

async def delete_user(db: AsyncSession, user_id: int):
    """
    Delete a user from the database and blacklist all active tokens associated with the user.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user to delete.

    Returns:
        model_user.User: The deleted user object.

    Raises:
        ValueError: If no user is found with the given user_id.
    """
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
