"""
UserProfile Context Resolver

This service handles the resolution of UserProfile data from User context,
providing automatic caching and lazy loading capabilities.
"""

from typing import Optional
from viki_shared.utils.logger import getLogger

from domain.models.user_context import get_current_user_sync, get_current_user_profile_sync, set_current_user_profile_sync
from domain.models.user_profile import UserProfile
from domain.ports.user_profile_ports import IUserProfileRepositoryPort

logger = getLogger(__name__)


class ProfileResolver:
    """
    Service for resolving UserProfile data from User context.

    This service provides lazy loading and caching of UserProfile data
    within the request scope, allowing any layer to access profile
    information without explicit dependency injection.
    """

    def __init__(self, profile_repository: IUserProfileRepositoryPort):
        """
        Initialize the profile resolver.

        Args:
            profile_repository: Repository for UserProfile operations
        """
        self.profile_repository = profile_repository

    async def resolve_current_user_profile(self) -> Optional[UserProfile]:
        """
        Resolve the current user's profile from context.

        This method first checks if a profile is already cached in context.
        If not, it attempts to load it from the repository using the current user's email.

        Returns:
            Optional[UserProfile]: The resolved user profile or None if not found
        """
        # Check if profile is already cached in context
        cached_profile = get_current_user_profile_sync()
        if cached_profile:
            logger.debug("Using cached user profile from context")
            return cached_profile

        # Get current user from context
        current_user = get_current_user_sync()
        if not current_user:
            logger.debug("No current user in context, cannot resolve profile")
            return None

        # Use email as profile ID (lowercased for consistency)
        profile_id = (current_user.email or current_user.sub).lower()

        extra = {
            "operation": "resolve_user_profile",
            "profile_id": profile_id,
            "user_sub": current_user.sub
        }

        logger.debug(f"Resolving user profile for: {profile_id}", extra=extra)

        try:
            # Load profile from repository
            profile = await self.profile_repository.get_profile(profile_id)

            if profile:
                # Cache the resolved profile in context for this request
                set_current_user_profile_sync(profile)
                logger.debug(f"Successfully resolved and cached profile: {profile_id}", extra=extra)
                return profile
            else:
                logger.debug(f"No profile found for user: {profile_id}", extra=extra)
                return None

        except Exception as e:
            logger.warning(f"Error resolving user profile: {str(e)}", extra={**extra, "error": str(e)})
            return None

    def resolve_current_user_profile_sync(self) -> Optional[UserProfile]:
        """
        Synchronous version of resolve_current_user_profile.

        Note: This method cannot perform repository operations since those are async.
        It only returns cached profiles from context.

        Returns:
            Optional[UserProfile]: The cached user profile or None
        """
        return get_current_user_profile_sync()

    async def ensure_current_user_profile(self) -> Optional[UserProfile]:
        """
        Ensure the current user's profile is available in context.

        This method will attempt to resolve the profile if it's not already cached.
        Useful for operations that require profile data.

        Returns:
            Optional[UserProfile]: The user profile or None if unavailable
        """
        profile = get_current_user_profile_sync()
        if profile:
            return profile

        # Profile not cached, try to resolve it
        return await self.resolve_current_user_profile()

    async def get_current_user_roles(self) -> list[str]:
        """
        Get the current user's roles from their profile.

        Returns:
            list[str]: List of role names or empty list if no profile
        """
        profile = await self.ensure_current_user_profile()
        if profile and hasattr(profile, 'authorization') and profile.authorization:
            return profile.authorization.roles
        return []

    async def get_current_user_organizations(self) -> list:
        """
        Get the current user's organizations from their profile.

        Returns:
            list: List of organization objects or empty list if no profile
        """
        profile = await self.ensure_current_user_profile()
        if profile and hasattr(profile, 'organizations') and profile.organizations:
            return profile.organizations
        return []

    def has_cached_profile(self) -> bool:
        """
        Check if a user profile is cached in context.

        Returns:
            bool: True if profile is cached, False otherwise
        """
        return get_current_user_profile_sync() is not None

    def clear_cached_profile(self) -> None:
        """
        Clear the cached user profile from context.
        Useful for testing or when profile data changes.
        """
        set_current_user_profile_sync(None)


# Global resolver instance for convenience functions
# Note: This will need to be properly initialized with repository dependency
_profile_resolver = None

def set_profile_resolver(resolver: ProfileResolver) -> None:
    """
    Set the global profile resolver instance.
    Should be called during application initialization.

    Args:
        resolver: The ProfileResolver instance to use globally
    """
    global _profile_resolver
    _profile_resolver = resolver

async def resolve_current_user_profile() -> Optional[UserProfile]:
    """
    Convenience function to resolve the current user's profile.

    Returns:
        Optional[UserProfile]: The resolved user profile or None
    """
    if _profile_resolver is None:
        logger.warning("Profile resolver not initialized")
        return None
    return await _profile_resolver.resolve_current_user_profile()

def get_cached_user_profile_sync() -> Optional[UserProfile]:
    """
    Convenience function to get cached user profile synchronously.

    Returns:
        Optional[UserProfile]: The cached user profile or None
    """
    return get_current_user_profile_sync()

async def ensure_current_user_profile() -> Optional[UserProfile]:
    """
    Convenience function to ensure user profile is available.

    Returns:
        Optional[UserProfile]: The user profile or None
    """
    if _profile_resolver is None:
        logger.warning("Profile resolver not initialized")
        return None
    return await _profile_resolver.ensure_current_user_profile()

async def get_current_user_roles() -> list[str]:
    """
    Convenience function to get current user's roles.

    Returns:
        list[str]: List of role names or empty list
    """
    if _profile_resolver is None:
        logger.warning("Profile resolver not initialized")
        return []
    return await _profile_resolver.get_current_user_roles()

async def get_current_user_organizations() -> list:
    """
    Convenience function to get current user's organizations.

    Returns:
        list: List of organization objects or empty list
    """
    if _profile_resolver is None:
        logger.warning("Profile resolver not initialized")
        return []
    return await _profile_resolver.get_current_user_organizations()