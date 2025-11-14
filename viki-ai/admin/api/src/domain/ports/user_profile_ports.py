"""
Ports for UserProfile operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from domain.models.user_profile import UserProfile


class IUserProfileRepositoryPort(ABC):
    """Port for user profile repository operations."""

    @abstractmethod
    async def create_profile(self, profile: UserProfile) -> str:
        """
        Create a new user profile.

        Args:
            profile: UserProfile to create

        Returns:
            Profile ID (email) of the created profile
        """
        pass

    @abstractmethod
    async def get_profile(self, profile_id: str) -> Optional[UserProfile]:
        """
        Get a user profile by ID (email).

        Args:
            profile_id: Profile ID (email)

        Returns:
            UserProfile if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_profile(self, profile: UserProfile) -> None:
        """
        Update an existing user profile and archive the previous version.

        Args:
            profile: UserProfile with updated data
        """
        pass

    @abstractmethod
    async def delete_profile(self, profile_id: str, deleted_by: str) -> None:
        """
        Soft delete a user profile by setting active=False and archiving.

        Args:
            profile_id: Profile ID (email) to delete
            deleted_by: User performing the deletion
        """
        pass

    @abstractmethod
    async def list_profiles(
        self,
        active_only: bool = True,
        organization_filter: Optional[Dict[str, str]] = None,
        role_filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserProfile]:
        """
        List user profiles with optional filters.

        Args:
            active_only: If True, only return active profiles
            organization_filter: Optional filter by organization (business_unit, solution_code)
            role_filter: Optional filter by role
            limit: Maximum number of profiles to return
            offset: Number of profiles to skip

        Returns:
            List of UserProfile objects
        """
        pass

    @abstractmethod
    async def archive_profile(self, profile: UserProfile, action: str) -> None:
        """
        Archive a profile version to the archive subcollection.

        Args:
            profile: UserProfile to archive
            action: Action that triggered the archive (update, delete)
        """
        pass

    @abstractmethod
    async def get_profile_history(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        Get the historical versions of a profile from the archive.

        Args:
            profile_id: Profile ID (email)

        Returns:
            List of archived profile versions
        """
        pass

    @abstractmethod
    async def search_profiles(self, search_term: str) -> List[UserProfile]:
        """
        Search profiles by name or email.

        Args:
            search_term: Search term to match against name or email

        Returns:
            List of matching UserProfile objects
        """
        pass