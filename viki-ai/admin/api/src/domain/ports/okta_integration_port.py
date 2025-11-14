"""
Okta Integration Port - Domain interface for Okta operations
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OktaUser:
    """Domain model for Okta user."""
    id: str
    email: str
    login: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: str = "ACTIVE"
    created: Optional[datetime] = None
    activated: Optional[datetime] = None
    status_changed: Optional[datetime] = None
    last_login: Optional[datetime] = None


@dataclass
class AppAssignment:
    """Domain model for application assignment."""
    id: str
    user_id: str
    app_id: str
    app_name: str
    status: str
    created: datetime
    credentials: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None


@dataclass
class OktaAppAssignmentResult:
    """Result of Okta app assignment operation."""
    success: bool
    user_id: Optional[str] = None
    app_id: Optional[str] = None
    assignment: Optional[AppAssignment] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


@dataclass
class OktaUserValidationResult:
    """Result of Okta user validation."""
    user_exists: bool
    user_id: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class OktaAppRemovalResult:
    """Result of Okta app assignment removal operation."""
    success: bool
    user_id: Optional[str] = None
    app_id: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


@dataclass
class OktaGroupAssignmentResult:
    """Result of Okta group assignment operation."""
    success: bool
    operation: str  # "assigned" or "removed"
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class IOktaIntegrationPort(ABC):
    """
    Port interface for Okta integration operations.
    Defines the contract for interacting with Okta services.
    """

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[OktaUser]:
        """
        Get Okta user by email address.

        Args:
            email: User's email address

        Returns:
            OktaUser if found, None otherwise
        """
        pass

    @abstractmethod
    async def check_user_app_assignment(self, email: str, app_id: str) -> bool:
        """
        Check if a user has access to a specific application.

        Args:
            email: User's email address
            app_id: Okta application ID

        Returns:
            True if user has access, False otherwise
        """
        pass

    @abstractmethod
    async def assign_app_to_user(self, email: str, app_id: str) -> OktaAppAssignmentResult:
        """
        Assign an application to a user.

        Args:
            email: User's email address
            app_id: Okta application ID to assign

        Returns:
            OktaAppAssignmentResult with assignment details or error
        """
        pass

    @abstractmethod
    async def list_user_apps(self, email: str) -> List[AppAssignment]:
        """
        List all applications assigned to a user.

        Args:
            email: User's email address

        Returns:
            List of AppAssignment objects
        """
        pass

    @abstractmethod
    async def verify_and_grant_access(self, email: str, app_id: str) -> OktaAppAssignmentResult:
        """
        Verify if user has app access and grant it if not.
        This is a convenience method that combines check and assign operations.

        Args:
            email: User's email address
            app_id: Okta application ID

        Returns:
            OktaAppAssignmentResult with operation outcome
        """
        pass

    @abstractmethod
    async def validate_user_exists(self, email: str) -> OktaUserValidationResult:
        """
        Validate that a user exists in Okta before attempting operations.

        Args:
            email: User's email address

        Returns:
            OktaUserValidationResult with validation outcome
        """
        pass

    @abstractmethod
    async def remove_app_assignment(self, email: str, app_id: str) -> OktaAppRemovalResult:
        """
        Remove an application assignment from a user.

        Args:
            email: User's email address
            app_id: Okta application ID to remove

        Returns:
            OktaAppRemovalResult with removal details or error
        """
        pass

    @abstractmethod
    async def assign_user_to_group(self, email: str, group_id: str) -> OktaGroupAssignmentResult:
        """
        Assign a user to an Okta group.

        Args:
            email: User's email address
            group_id: Okta group ID

        Returns:
            OktaGroupAssignmentResult with assignment details or error
        """
        pass

    @abstractmethod
    async def remove_user_from_group(self, email: str, group_id: str) -> OktaGroupAssignmentResult:
        """
        Remove a user from an Okta group.

        Args:
            email: User's email address
            group_id: Okta group ID

        Returns:
            OktaGroupAssignmentResult with removal details or error
        """
        pass