"""
UserProfile query models and handlers (CQRS - Query side)
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from viki_shared.utils.logger import getLogger
from domain.models.user_profile import UserProfile
from domain.ports.user_profile_ports import IUserProfileRepositoryPort

logger = getLogger(__name__)


@dataclass
class GetUserProfileQuery:
    """Query to get a user profile by ID."""
    profile_id: str  # Email


@dataclass
class ListUserProfilesQuery:
    """Query to list user profiles with filters."""
    active_only: bool = True
    organization_filter: Optional[Dict[str, str]] = None
    role_filter: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class SearchUserProfilesQuery:
    """Query to search user profiles by name or email."""
    search_term: str
    active_only: bool = True


@dataclass
class GetUserProfileHistoryQuery:
    """Query to get historical versions of a user profile."""
    profile_id: str  # Email


class UserProfileQueryHandler:
    """Handler for user profile queries."""

    def __init__(self, profile_repository: IUserProfileRepositoryPort):
        self.profile_repository = profile_repository

    async def handle_get_profile(self, query: GetUserProfileQuery) -> Optional[UserProfile]:
        """
        Handle get user profile query.

        Args:
            query: Get user profile query

        Returns:
            UserProfile if found, None otherwise
        """
        extra = {
            "operation": "get_user_profile",
            "profile_id": query.profile_id
        }

        logger.debug("Handling get user profile query", extra=extra)

        profile = await self.profile_repository.get_profile(query.profile_id)

        if profile:
            logger.debug(f"Successfully retrieved user profile: {query.profile_id}", extra=extra)
        else:
            logger.debug(f"User profile not found: {query.profile_id}", extra=extra)

        return profile

    async def handle_list_profiles(self, query: ListUserProfilesQuery) -> List[UserProfile]:
        """
        Handle list user profiles query.

        Args:
            query: List user profiles query

        Returns:
            List of UserProfile objects
        """
        extra = {
            "operation": "list_user_profiles",
            "active_only": query.active_only,
            "organization_filter": query.organization_filter,
            "role_filter": query.role_filter,
            "limit": query.limit,
            "offset": query.offset
        }

        logger.debug("Handling list user profiles query", extra=extra)

        profiles = await self.profile_repository.list_profiles(
            active_only=query.active_only,
            organization_filter=query.organization_filter,
            role_filter=query.role_filter,
            limit=query.limit,
            offset=query.offset
        )

        logger.debug(f"Successfully retrieved {len(profiles)} user profiles", extra={**extra, "count": len(profiles)})

        return profiles

    async def handle_search_profiles(self, query: SearchUserProfilesQuery) -> List[UserProfile]:
        """
        Handle search user profiles query.

        Args:
            query: Search user profiles query

        Returns:
            List of matching UserProfile objects
        """
        extra = {
            "operation": "search_user_profiles",
            "search_term": query.search_term,
            "active_only": query.active_only
        }

        logger.debug("Handling search user profiles query", extra=extra)

        profiles = await self.profile_repository.search_profiles(query.search_term)

        # Filter by active status if requested
        if query.active_only:
            profiles = [p for p in profiles if p.active]

        logger.debug(f"Found {len(profiles)} matching user profiles", extra={**extra, "count": len(profiles)})

        return profiles

    async def handle_get_profile_history(self, query: GetUserProfileHistoryQuery) -> List[Dict[str, Any]]:
        """
        Handle get user profile history query.

        Args:
            query: Get user profile history query

        Returns:
            List of archived profile versions
        """
        extra = {
            "operation": "get_user_profile_history",
            "profile_id": query.profile_id
        }

        logger.debug("Handling get user profile history query", extra=extra)

        history = await self.profile_repository.get_profile_history(query.profile_id)

        logger.debug(f"Found {len(history)} historical versions for profile: {query.profile_id}", extra={**extra, "count": len(history)})

        return history