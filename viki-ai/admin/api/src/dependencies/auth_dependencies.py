"""
Authentication dependencies for FastAPI routes.
Optimized to use user context already validated by AuthMiddleware.
"""

from fastapi import Depends, HTTPException, status, Request
from typing import Optional

from models.user import User


async def get_current_user(request: Request) -> User:
    """
    Dependency to get the current authenticated user from request state.
    The user has already been validated by AuthMiddleware.
    
    Args:
        request: FastAPI request object with user set by middleware
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If no authenticated user found in request state
    """
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_optional_user(request: Request) -> Optional[User]:
    """
    Dependency to optionally get the current authenticated user from request state.
    Returns None if no authenticated user is found.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Optional[User]: The authenticated user object or None
    """
    return getattr(request.state, 'user', None)


# Common dependency for routes that require authentication
RequireAuth = Depends(get_current_user)

# Common dependency for routes with optional authentication
OptionalAuth = Depends(get_optional_user)