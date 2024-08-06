from datetime import datetime
import bcrypt
from backend.src.config.hash import hash_handler
from backend.src.util.models.user import UserRole
from backend.src.util.schemas import user as schema_user
from backend.src.util.models import user as model_user, User
from backend.src.config.jwt import create_access_token
from backend.src.config.logging_config import log_function
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update


@log_function
async def create_user(db: AsyncSession, user: schema_user.UserCreate):
    """
    Create a new user in the database.

    This function creates a new user in the database by hashing the provided password
    and storing the user information. If the created user is the first user in the
    database (i.e., with ID 1), the user is assigned the "admin" role. After creating
    the user, an access token is generated for the user.

    Args:
        db (AsyncSession): The asynchronous database session.
        user (schema_user.UserCreate): The user creation schema containing the user's
                                       email and password.

    Returns:
        model_user.User: The newly created user object with all its attributes.

    Raises:
        ValueError: If the user creation schema is invalid or missing required fields.


    """
    user_count = await get_user_count(db)
    hashed_password = hash_handler.hash_password(user.password)
    if user_count == 0:
        role = UserRole.ADMIN
    else:
        role = UserRole.USER
    db_user = model_user.User(email=user.email, hashed_password=hashed_password, role=role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    await create_access_token(data={"sub": db_user.email}, user_id=db_user.id, db=db)
    return db_user


@log_function
async def get_user_by_email(db: AsyncSession, email: str):
    """
    Retrieve a user by email.

    Args:
        db (AsyncSession): The database session.
        email (str): The email of the user.

    Returns:
        model_user.User: The user object if found, None otherwise.

    """

    result = await db.execute(select(model_user.User).filter(model_user.User.email == email))
    user = result.scalars().first()
    return user


@log_function
async def get_user(db: AsyncSession, user_id: int):
    """
    Retrieve a user by user ID.

    Args:
        db (AsyncSession): The database session.
        user_id (int): The ID of the user.

    Returns:
        model_user.User: The user object if found, None otherwise.

    """

    result = await db.execute(select(model_user.User).filter(model_user.User.id == user_id))
    return result.scalars().first()


@log_function
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of users from the database.

    Args:
        db (AsyncSession): The database session.
        skip (int): The number of records to skip for pagination. Default is 0.
        limit (int): The maximum number of records to return. Default is 100.

    Returns:
        List[model_user.User]: A list of user objects.

    """
    result = await db.execute(select(model_user.User).offset(skip).limit(limit))
    return result.scalars().all()

@log_function
async def update_user_last_login(db: AsyncSession, user_id: int):
    """
        Updates the last_login field for a user.

        Args:
            db (AsyncSession): The asynchronous database session.
            user_id (int): The ID of the user whose last_login field needs to be updated.

        Returns:
            None
        """
    stmt = (update(User).where(User.id == user_id).values(last_login=datetime.utcnow()))
    await db.execute(stmt)
    await db.commit()


async def deactivate_user(db: AsyncSession, user_id: int):
    """
    Deactivates a user by setting the is_active field to False.

    Args:
        db (AsyncSession): The asynchronous database session.
        user_id (int): The ID of the user to deactivate.

    Returns:
        None
    """
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(is_active=False)
    )
    await db.execute(stmt)
    await db.commit()


async def get_user_count(db: AsyncSession) -> int:
    """
    Retrieves the count of users in the database.

    Args:
        db (AsyncSession): The asynchronous database session.

    Returns:
        int: The number of users in the database.
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return len(users)
