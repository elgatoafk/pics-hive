from fastapi import Depends, HTTPException, status
from backend.src.util.models import user as model_user
from backend.src.config.security import get_current_active_user
from functools import wraps, update_wrapper
from typing import Callable


def role_required(*roles: str):
    """
    Decorator to enforce role-based access control on an endpoint.

    Args:
        roles (str): Variable length argument list of roles that are allowed access.

    Returns:
        Callable: A decorator function that wraps the original function with role-checking logic.
    """
    
    def decorator(func: Callable):
        """
        Inner decorator function that wraps the original function.

        Args:
            func (Callable): The original function to be decorated.

        Returns:
            Callable: The wrapped function with added role-checking logic.
        """
        async def wrapper(*args, current_user: model_user.User = Depends(get_current_active_user), **kwargs):
            """
            Checks if the current user has the required role.

            Args:
                *args: Positional arguments passed to the original function.
                current_user (model_user.User, optional): The current active user, injected by dependency.
                **kwargs: Keyword arguments passed to the original function.

            Raises:
                HTTPException: If the current user's role is not in the allowed roles.

            Returns:
                Any: The result of the original function if the user has the required role.
            """
            if current_user.role not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
            return await func(*args, current_user=current_user, **kwargs)
        
        return update_wrapper(wrapper, func)
    
    return decorator

