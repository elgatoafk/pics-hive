from abc import ABC, abstractmethod
from urllib.parse import urlparse
from fastapi import HTTPException, status, Depends, Path
from typing import List, Type, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config.security import get_current_user
from backend.src.util.db import get_db
from backend.src.util.models import Photo
from backend.src.util.models.comment import Comment
from backend.src.util.models.user import UserRole, User


def role_required(allowed_roles: List[UserRole]):
    """
    Dependency function to enforce role-based access control for routes.

    This function checks if the current authenticated user's role is in the list of allowed roles.
    If the user's role is not permitted, it raises an HTTP 403 Forbidden error.

    Args:
        allowed_roles (List[UserRole]): A list of roles that are allowed to access the route.

    Returns:
        Callable: A dependency function that checks the current user's role.

    Raises:
        HTTPException: If the current user's role is not in the list of allowed roles, an HTTP 403 Forbidden error is raised.
    """

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
        return current_user

    return role_checker


class Dependency(ABC):
    """
    Abstract base class for dependency checks.

    This class defines the abstract method is_owner_or_admin, which needs to be implemented
    by any class inheriting from it. The method is used to check if a user is the owner of
    a resource or an admin.
    """

    @staticmethod
    @abstractmethod
    async def is_owner_or_admin(resource_id: int, user_id: int, db: AsyncSession):
        """
        Checks if the user is the owner of the resource or an admin.

        This method should be implemented by subclasses to perform the actual ownership
        or admin check.

        Args:
            resource_id (int): The ID of the resource to check.
            user_id (int): The ID of the user to check.
            db (AsyncSession): The database session.

        Raises:
            HTTPException: If the user is not the owner or an admin.
        """
        pass


class PhotoDependency(Dependency):
    """
    Dependency class for photo-related operations.

    This class implements the is_owner_or_admin method to check if a user is the owner of
    a photo or an admin.
    """

    @staticmethod
    async def is_owner_or_admin(photo_id: int, user_id: int, db: AsyncSession):
        """
        Checks if the user is the owner of the photo or an admin.

        Args:
            photo_id (int): The ID of the photo to check.
            user_id (int): The ID of the user to check.
            db (AsyncSession): The database session.

        Raises:
            HTTPException: If the photo is not found or the user is not the owner or an admin.
        """
        result = await db.execute(select(Photo).where(Photo.id == photo_id))
        photo = result.scalars().first()
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
        if not (photo.user_id == user_id or user.role == UserRole.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")


class CommentDependency(Dependency):
    """
    Dependency class for comment-related operations.

    This class implements the is_owner_or_admin method to check if a user is the owner of
    a comment or an admin.
    """

    @staticmethod
    async def is_owner_or_admin(comment_id: int, user_id: int, db: AsyncSession):
        """
        Checks if the user is the owner of the comment or an admin.

        Args:
            comment_id (int): The ID of the comment to check.
            user_id (int): The ID of the user to check.
            db (AsyncSession): The database session.

        Raises:
            HTTPException: If the comment is not found or the user is not the owner or an admin.
        """
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        comment = result.scalars().first()
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if not (comment.user_id == user_id or user.role == UserRole.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")


def owner_or_admin_dependency(dependency_class: Type[Dependency], resource_id_name: str) -> Callable:
    """
    Creates a dependency function to check if the user is the owner of a resource or an admin.

    Args:
        dependency_class (Type[Dependency]): The dependency class to use for the check.
        resource_id_name (str): The name of the resource ID parameter in the route.

    Returns:
        Callable: A dependency function that performs the ownership or admin check.
    """

    async def dependency_check(
            resource_id: int = Path(..., alias=resource_id_name),
            current_user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
    ):
        """
        Checks if the user is the owner of the resource or an admin.

        Args:
            resource_id (int): The ID of the resource to check.
            current_user (User): The current authenticated user, injected via dependency.
            db (AsyncSession): The asynchronous database session, injected via dependency.

        Raises:
            HTTPException: If the user is not the owner or an admin.
        """
        await dependency_class.is_owner_or_admin(resource_id, current_user.id, db)

    return dependency_check