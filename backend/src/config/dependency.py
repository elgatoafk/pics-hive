from fastapi import HTTPException, status, Depends
from typing import List

from backend.src.config.security import get_current_user
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
