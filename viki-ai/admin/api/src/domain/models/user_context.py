"""
User Context Management for Cross-Cutting Access

This module provides context variables that allow any layer of the application
to access the current authenticated user and user profile without violating
clean architecture principles.

Based on the pattern from entity_extraction service.
"""

import contextvars
from typing import Optional, Dict, Any
from datetime import datetime

from models.user import User


class UserContext:
    """
    Context manager for user-related data that needs to be accessible
    across all layers of the application.

    Uses Python's contextvars module to provide request-scoped storage
    that works correctly with asyncio and doesn't violate clean architecture.
    """

    # Context variables for user-related data
    current_user = contextvars.ContextVar('current_user', default=None)
    current_user_profile = contextvars.ContextVar('current_user_profile', default=None)
    user_metadata = contextvars.ContextVar('user_metadata', default=None)

    def __init__(self):
        """Initialize the context."""
        pass

    # User Context Methods
    async def set_user(self, user: User) -> None:
        """
        Set the current authenticated user in context.

        Args:
            user: The authenticated User object from JWT validation
        """
        self.current_user.set(user)

    def set_user_sync(self, user: User) -> None:
        """
        Synchronous version of set_user.

        Args:
            user: The authenticated User object from JWT validation
        """
        self.current_user.set(user)

    async def get_user(self) -> Optional[User]:
        """
        Get the current authenticated user from context.

        Returns:
            Optional[User]: The current user or None if not set
        """
        return self.current_user.get()

    def get_user_sync(self) -> Optional[User]:
        """
        Synchronous version of get_user.

        Returns:
            Optional[User]: The current user or None if not set
        """
        return self.current_user.get()

    async def get_user_email(self) -> Optional[str]:
        """
        Get the current user's email from context.

        Returns:
            Optional[str]: The user's email or None if no user
        """
        user = self.current_user.get()
        return user.email if user else None

    def get_user_email_sync(self) -> Optional[str]:
        """
        Synchronous version of get_user_email.

        Returns:
            Optional[str]: The user's email or None if no user
        """
        user = self.current_user.get()
        return user.email if user else None

    async def get_user_sub(self) -> Optional[str]:
        """
        Get the current user's subject identifier from context.

        Returns:
            Optional[str]: The user's sub claim or None if no user
        """
        user = self.current_user.get()
        return user.sub if user else None

    def get_user_sub_sync(self) -> Optional[str]:
        """
        Synchronous version of get_user_sub.

        Returns:
            Optional[str]: The user's sub claim or None if no user
        """
        user = self.current_user.get()
        return user.sub if user else None

    # UserProfile Context Methods
    async def set_user_profile(self, user_profile) -> None:
        """
        Set the current user profile in context.

        Args:
            user_profile: The resolved UserProfile domain object
        """
        self.current_user_profile.set(user_profile)

    def set_user_profile_sync(self, user_profile) -> None:
        """
        Synchronous version of set_user_profile.

        Args:
            user_profile: The resolved UserProfile domain object
        """
        self.current_user_profile.set(user_profile)

    async def get_user_profile(self):
        """
        Get the current user profile from context.

        Returns:
            Optional[UserProfile]: The current user profile or None if not set
        """
        return self.current_user_profile.get()

    def get_user_profile_sync(self):
        """
        Synchronous version of get_user_profile.

        Returns:
            Optional[UserProfile]: The current user profile or None if not set
        """
        return self.current_user_profile.get()

    # Metadata and Audit Context Methods
    async def set_user_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Set user-related metadata in context (for audit trails, etc.).

        Args:
            metadata: Dictionary of metadata to store
        """
        self.user_metadata.set(metadata)

    def set_user_metadata_sync(self, metadata: Dict[str, Any]) -> None:
        """
        Synchronous version of set_user_metadata.

        Args:
            metadata: Dictionary of metadata to store
        """
        self.user_metadata.set(metadata)

    async def get_user_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get user-related metadata from context.

        Returns:
            Optional[Dict[str, Any]]: The metadata dictionary or None
        """
        return self.user_metadata.get()

    def get_user_metadata_sync(self) -> Optional[Dict[str, Any]]:
        """
        Synchronous version of get_user_metadata.

        Returns:
            Optional[Dict[str, Any]]: The metadata dictionary or None
        """
        return self.user_metadata.get()

    # Convenience Methods
    def get_audit_context(self) -> Dict[str, Any]:
        """
        Get audit context information for logging and domain events.

        Returns:
            Dict[str, Any]: Dictionary containing audit information
        """
        user = self.current_user.get()
        user_profile = self.current_user_profile.get()
        metadata = self.user_metadata.get() or {}

        audit_context = {
            "timestamp": datetime.utcnow().isoformat(),
        }

        if user:
            audit_context.update({
                "user_sub": user.sub,
                "user_email": user.email,
                "user_name": user.name
            })

        if user_profile:
            audit_context.update({
                "profile_id": user_profile.id,
                "user_roles": user_profile.authorization.roles if hasattr(user_profile, 'authorization') else []
            })

        # Add any additional metadata
        if metadata:
            audit_context.update(metadata)

        return audit_context

    def has_user_context(self) -> bool:
        """
        Check if user context is available.

        Returns:
            bool: True if user context is set, False otherwise
        """
        return self.current_user.get() is not None

    def clear_context(self) -> None:
        """
        Clear all user context data.
        Useful for testing or cleanup operations.
        """
        self.current_user.set(None)
        self.current_user_profile.set(None)
        self.user_metadata.set(None)


# Global context instance for convenience functions
_user_context_instance = UserContext()

# Convenience Functions for Easy Access

async def set_current_user(user: User) -> None:
    """
    Convenience function to set the current user in context.

    Args:
        user: The authenticated User object
    """
    await _user_context_instance.set_user(user)

def set_current_user_sync(user: User) -> None:
    """
    Synchronous convenience function to set the current user in context.

    Args:
        user: The authenticated User object
    """
    _user_context_instance.set_user_sync(user)

async def get_current_user() -> Optional[User]:
    """
    Convenience function to get the current user from context.

    Returns:
        Optional[User]: The current user or None if not set
    """
    return await _user_context_instance.get_user()

def get_current_user_sync() -> Optional[User]:
    """
    Synchronous convenience function to get the current user from context.

    Returns:
        Optional[User]: The current user or None if not set
    """
    return _user_context_instance.get_user_sync()

async def set_current_user_profile(user_profile) -> None:
    """
    Convenience function to set the current user profile in context.

    Args:
        user_profile: The UserProfile domain object
    """
    await _user_context_instance.set_user_profile(user_profile)

def set_current_user_profile_sync(user_profile) -> None:
    """
    Synchronous convenience function to set the current user profile in context.

    Args:
        user_profile: The UserProfile domain object
    """
    _user_context_instance.set_user_profile_sync(user_profile)

async def get_current_user_profile():
    """
    Convenience function to get the current user profile from context.

    Returns:
        Optional[UserProfile]: The current user profile or None if not set
    """
    return await _user_context_instance.get_user_profile()

def get_current_user_profile_sync():
    """
    Synchronous convenience function to get the current user profile from context.

    Returns:
        Optional[UserProfile]: The current user profile or None if not set
    """
    return _user_context_instance.get_user_profile_sync()

async def get_current_user_email() -> Optional[str]:
    """
    Convenience function to get the current user's email.

    Returns:
        Optional[str]: The user's email or None
    """
    return await _user_context_instance.get_user_email()

def get_current_user_email_sync() -> Optional[str]:
    """
    Synchronous convenience function to get the current user's email.

    Returns:
        Optional[str]: The user's email or None
    """
    return _user_context_instance.get_user_email_sync()

def get_audit_context() -> Dict[str, Any]:
    """
    Convenience function to get audit context for logging and events.

    Returns:
        Dict[str, Any]: Audit context information
    """
    return _user_context_instance.get_audit_context()

def has_user_context() -> bool:
    """
    Convenience function to check if user context is available.

    Returns:
        bool: True if user context is set, False otherwise
    """
    return _user_context_instance.has_user_context()

def clear_user_context() -> None:
    """
    Convenience function to clear all user context data.
    """
    _user_context_instance.clear_context()