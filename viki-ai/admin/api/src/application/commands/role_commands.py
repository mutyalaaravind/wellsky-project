"""
Role command handlers for RBAC system.

This module contains commands and command handlers for role operations
including creation, updates, deletions, and validation logic.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from domain.models.user_profile import Audit
from domain.models.role import Role
from domain.ports.role_ports import IRoleRepository


@dataclass
class CreateRoleCommand:
    """Command to create a new role."""
    id: str
    name: str
    description: str
    permissions: List[str]
    inherits: List[str]
    created_by: str


@dataclass
class UpdateRoleCommand:
    """Command to update an existing role."""
    role_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    inherits: Optional[List[str]] = None
    active: Optional[bool] = None
    modified_by: str = "system"


@dataclass
class DeleteRoleCommand:
    """Command to delete a role (soft delete)."""
    role_id: str
    deleted_by: str


class RoleCommandHandler:
    """Handler for role-related commands."""

    def __init__(self, role_repository: IRoleRepository):
        """
        Initialize command handler.

        Args:
            role_repository: Role repository for data operations
        """
        self.role_repository = role_repository

    async def handle_create_role(self, command: CreateRoleCommand) -> str:
        """
        Handle role creation command.

        Args:
            command: Create role command

        Returns:
            Created role ID

        Raises:
            ValueError: If validation fails or role already exists
        """
        # Validate that all inherited roles exist and are active
        await self._validate_inherited_roles_exist(command.inherits)

        # Create role object with audit data
        audit_data = Audit(
            created_by=command.created_by,
            created_on=datetime.utcnow(),
            modified_by=command.created_by,
            modified_on=datetime.utcnow()
        )

        role = Role(
            id=command.id,
            name=command.name,
            description=command.description,
            permissions=command.permissions,
            inherits=command.inherits,
            active=True,
            audit=audit_data
        )

        # Validate inheritance chain for circular references
        if not await role.validate_inheritance_chain(self.role_repository):
            raise ValueError(f"Circular reference detected in inheritance chain for role '{command.id}'")

        # Create role in repository
        return await self.role_repository.create_role(role)

    async def handle_update_role(self, command: UpdateRoleCommand) -> None:
        """
        Handle role update command.

        Args:
            command: Update role command

        Raises:
            ValueError: If role not found or validation fails
        """
        # Get existing role
        existing_role = await self.role_repository.get_role(command.role_id)
        if not existing_role:
            raise ValueError(f"Role with ID '{command.role_id}' not found")

        # Create updated role with new values
        updated_role = Role(
            id=existing_role.id,
            name=command.name if command.name is not None else existing_role.name,
            description=command.description if command.description is not None else existing_role.description,
            permissions=command.permissions if command.permissions is not None else existing_role.permissions,
            inherits=command.inherits if command.inherits is not None else existing_role.inherits,
            active=command.active if command.active is not None else existing_role.active,
            audit=existing_role.audit  # Will be updated in repository
        )

        # If inherits is being updated, validate the inherited roles exist
        if command.inherits is not None:
            await self._validate_inherited_roles_exist(command.inherits)

            # Validate inheritance chain for circular references
            if not await updated_role.validate_inheritance_chain(self.role_repository, command.inherits):
                raise ValueError(f"Circular reference detected in inheritance chain for role '{command.role_id}'")

        # Set modified_by in audit
        updated_role.audit = Audit(
            created_by=existing_role.audit.created_by if existing_role.audit else "system",
            created_on=existing_role.audit.created_on if existing_role.audit else datetime.utcnow(),
            modified_by=command.modified_by,
            modified_on=datetime.utcnow()
        )

        # Update role in repository
        await self.role_repository.update_role(updated_role)

    async def handle_delete_role(self, command: DeleteRoleCommand) -> None:
        """
        Handle role deletion command (soft delete).

        Args:
            command: Delete role command

        Raises:
            ValueError: If role not found or cannot be deleted
        """
        # Get existing role
        existing_role = await self.role_repository.get_role(command.role_id)
        if not existing_role:
            raise ValueError(f"Role with ID '{command.role_id}' not found")

        if not existing_role.active:
            raise ValueError(f"Role '{command.role_id}' is already deleted")

        # Check if role can be safely deleted
        can_delete, dependent_roles = existing_role.can_be_deleted(self.role_repository)
        if not can_delete:
            raise ValueError(
                f"Cannot delete role '{command.role_id}' because it is inherited by: {', '.join(dependent_roles)}"
            )

        # Remove role from all inheritance chains
        await self.role_repository.remove_role_from_inheritance(command.role_id)

        # Soft delete the role
        await self.role_repository.delete_role(command.role_id)

    async def _validate_inherited_roles_exist(self, inherits: List[str]) -> None:
        """
        Validate that all inherited roles exist and are active.

        Args:
            inherits: List of role IDs to validate

        Raises:
            ValueError: If any inherited role doesn't exist or is not active
        """
        for inherited_role_id in inherits:
            inherited_role = await self.role_repository.get_role(inherited_role_id)

            if not inherited_role:
                raise ValueError(f"Inherited role '{inherited_role_id}' does not exist")

            if not inherited_role.active:
                raise ValueError(f"Inherited role '{inherited_role_id}' is not active")

    async def validate_role_dependencies(self, role_id: str) -> tuple[bool, List[str]]:
        """
        Check what depends on a role before deletion.

        Args:
            role_id: Role ID to check dependencies for

        Returns:
            Tuple of (can_delete: bool, dependent_roles: List[str])
        """
        role = await self.role_repository.get_role(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")

        return role.can_be_deleted(self.role_repository)

    async def get_role_effective_permissions(self, role_id: str) -> List[str]:
        """
        Get all effective permissions for a role (including inherited).

        Args:
            role_id: Role ID to get permissions for

        Returns:
            List of all effective permissions

        Raises:
            ValueError: If role not found or circular reference detected
        """
        role = await self.role_repository.get_role(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")

        return role.get_effective_permissions(self.role_repository)


class RoleValidationService:
    """Service for role validation operations."""

    def __init__(self, role_repository: IRoleRepository):
        """
        Initialize validation service.

        Args:
            role_repository: Role repository for data operations
        """
        self.role_repository = role_repository

    async def validate_circular_inheritance(
        self,
        role_id: str,
        inherits: List[str]
    ) -> bool:
        """
        Validate that the inheritance chain doesn't create circular references.

        Args:
            role_id: ID of the role being validated
            inherits: List of role IDs this role would inherit from

        Returns:
            True if valid, False if circular reference detected
        """
        # Create a temporary role for validation
        temp_role = Role(
            id=role_id,
            name="temp",
            description="temp",
            permissions=[],
            inherits=inherits
        )

        return temp_role.validate_inheritance_chain(self.role_repository, inherits)

    async def validate_permissions(self, permissions: List[str]) -> bool:
        """
        Validate that permissions follow the correct format.

        Args:
            permissions: List of permissions to validate

        Returns:
            True if all permissions are valid

        Raises:
            ValueError: If any permission is invalid
        """
        for permission in permissions:
            if not permission or not isinstance(permission, str):
                raise ValueError(f"Permission must be a non-empty string: {permission}")

            # Basic permission format validation (can be extended)
            if not permission.replace('_', '').replace('.', '').replace(':', '').isalnum():
                raise ValueError(f"Permission contains invalid characters: {permission}")

        return True

    async def get_inheritance_depth(self, role_id: str) -> int:
        """
        Get the inheritance depth for a role.

        Args:
            role_id: Role ID to check depth for

        Returns:
            Maximum inheritance depth

        Raises:
            ValueError: If role not found or circular reference detected
        """
        role = await self.role_repository.get_role(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")

        return role.get_inheritance_depth(self.role_repository)