"""
Role domain ports/interfaces for RBAC system.

This module defines the abstract interfaces for role repository
and related domain services.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.models.role import Role


class IRoleRepository(ABC):
    """Interface for role repository operations."""

    @abstractmethod
    async def create_role(self, role: Role) -> str:
        """
        Create a new role.

        Args:
            role: Role to create

        Returns:
            Created role ID

        Raises:
            ValueError: If role already exists or validation fails
        """
        pass

    @abstractmethod
    async def get_role(self, role_id: str) -> Optional[Role]:
        """
        Get a role by ID.

        Args:
            role_id: Role ID to fetch

        Returns:
            Role if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_role(self, role: Role) -> None:
        """
        Update an existing role.

        Args:
            role: Role with updated data

        Raises:
            ValueError: If role not found or validation fails
        """
        pass

    @abstractmethod
    async def delete_role(self, role_id: str) -> None:
        """
        Soft delete a role (set active=False).

        Args:
            role_id: Role ID to delete

        Raises:
            ValueError: If role not found
        """
        pass

    @abstractmethod
    async def list_roles(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Role]:
        """
        List roles with pagination.

        Args:
            active_only: Only return active roles
            limit: Maximum number of roles to return
            offset: Number of roles to skip

        Returns:
            List of roles
        """
        pass

    @abstractmethod
    async def get_roles_inheriting_from(self, role_id: str) -> List[str]:
        """
        Get list of role IDs that inherit from the given role.

        Args:
            role_id: Role ID to check dependencies for

        Returns:
            List of role IDs that inherit from the given role
        """
        pass

    @abstractmethod
    async def count_roles(self, active_only: bool = True) -> int:
        """
        Count total number of roles.

        Args:
            active_only: Only count active roles

        Returns:
            Total number of roles
        """
        pass

    @abstractmethod
    async def role_exists(self, role_id: str) -> bool:
        """
        Check if a role exists.

        Args:
            role_id: Role ID to check

        Returns:
            True if role exists, False otherwise
        """
        pass

    @abstractmethod
    async def remove_role_from_inheritance(self, role_id_to_remove: str) -> None:
        """
        Remove a role from all inheritance chains.

        This is used during role deletion to maintain data integrity.

        Args:
            role_id_to_remove: Role ID to remove from all inheritance lists
        """
        pass


class IRoleValidationService(ABC):
    """Interface for role validation operations."""

    @abstractmethod
    async def validate_circular_inheritance(
        self,
        role_id: str,
        inherits: List[str],
        role_repository: IRoleRepository
    ) -> bool:
        """
        Validate that the inheritance chain doesn't create circular references.

        Args:
            role_id: ID of the role being validated
            inherits: List of role IDs this role would inherit from
            role_repository: Repository to fetch role data

        Returns:
            True if valid, False if circular reference detected
        """
        pass

    @abstractmethod
    async def validate_permissions(self, permissions: List[str]) -> bool:
        """
        Validate that permissions follow the correct format.

        Args:
            permissions: List of permissions to validate

        Returns:
            True if all permissions are valid
        """
        pass

    @abstractmethod
    async def get_effective_permissions(
        self,
        role_id: str,
        role_repository: IRoleRepository
    ) -> List[str]:
        """
        Get all effective permissions for a role (including inherited).

        Args:
            role_id: Role ID to get permissions for
            role_repository: Repository to fetch role data

        Returns:
            List of all effective permissions
        """
        pass