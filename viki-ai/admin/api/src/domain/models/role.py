"""
Role domain model for RBAC system.

This module defines the Role aggregate with inheritance validation
and effective permissions calculation.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set
from datetime import datetime

from viki_shared.models.common import AggBase
from domain.models.user_profile import Audit


@dataclass
class Role:
    """
    Role aggregate representing a system role with permissions and inheritance.

    Roles can inherit from other roles, creating a hierarchy of permissions.
    The system prevents circular references in the inheritance chain.
    """
    id: str
    name: str
    description: str
    permissions: List[str] = field(default_factory=list)
    inherits: List[str] = field(default_factory=list)
    active: bool = True
    audit: Optional[Audit] = None

    def __post_init__(self):
        """Validate role after initialization."""
        self._validate_id()
        self._validate_permissions()

    def _validate_id(self):
        """Validate role ID format (domain:role_name) with special case for 'superuser'."""
        if not self.id:
            raise ValueError("Role ID cannot be empty")

        # Special case: allow "superuser" without domain prefix
        if self.id == "superuser":
            return

        # Standard validation for domain:role_name format
        if ':' not in self.id:
            raise ValueError("Role ID must be in format 'domain:role_name' or be 'superuser'")

        domain, role_name = self.id.split(':', 1)
        if not domain or not role_name:
            raise ValueError("Both domain and role name must be non-empty")

    def _validate_permissions(self):
        """Validate permission format."""
        for permission in self.permissions:
            if not permission or not isinstance(permission, str):
                raise ValueError("All permissions must be non-empty strings")

    async def get_effective_permissions(self, role_repository) -> List[str]:
        """
        Calculate all effective permissions including inherited ones.

        Args:
            role_repository: Repository to fetch inherited roles

        Returns:
            List of all effective permissions (direct + inherited)

        Raises:
            ValueError: If circular reference is detected
        """
        visited = set()
        all_permissions = set()

        await self._collect_permissions_recursive(role_repository, visited, all_permissions)

        return sorted(list(all_permissions))

    async def _collect_permissions_recursive(self, role_repository, visited: Set[str],
                                     all_permissions: Set[str]):
        """
        Recursively collect permissions from this role and inherited roles.

        Args:
            role_repository: Repository to fetch roles
            visited: Set of already visited role IDs (for cycle detection)
            all_permissions: Set to collect all permissions

        Raises:
            ValueError: If circular reference is detected
        """
        if self.id in visited:
            raise ValueError(f"Circular reference detected in role inheritance chain: {self.id}")

        visited.add(self.id)

        # Add direct permissions
        all_permissions.update(self.permissions)

        # Recursively add inherited permissions
        for inherited_role_id in self.inherits:
            inherited_role = await role_repository.get_role(inherited_role_id)
            if inherited_role and inherited_role.active:
                await inherited_role._collect_permissions_recursive(
                    role_repository, visited.copy(), all_permissions
                )

    async def validate_inheritance_chain(self, role_repository, new_inherits: Optional[List[str]] = None) -> bool:
        """
        Validate that the inheritance chain doesn't create circular references.

        Args:
            role_repository: Repository to fetch roles
            new_inherits: Optional new inheritance list to validate (for updates)

        Returns:
            True if valid, False if circular reference would be created
        """
        inherits_to_check = new_inherits if new_inherits is not None else self.inherits

        try:
            # Create a temporary role with the new inheritance to test
            temp_role = Role(
                id=self.id,
                name=self.name,
                description=self.description,
                permissions=self.permissions,
                inherits=inherits_to_check,
                active=self.active,
                audit=self.audit
            )

            # Try to calculate effective permissions - will raise if circular
            await temp_role.get_effective_permissions(role_repository)
            return True

        except ValueError as e:
            if "circular reference" in str(e).lower():
                return False
            raise  # Re-raise other validation errors

    def can_be_deleted(self, role_repository) -> tuple[bool, List[str]]:
        """
        Check if this role can be safely deleted.

        Args:
            role_repository: Repository to check dependencies

        Returns:
            Tuple of (can_delete: bool, dependent_roles: List[str])
        """
        dependent_roles = role_repository.get_roles_inheriting_from(self.id)
        return len(dependent_roles) == 0, dependent_roles

    def get_inheritance_depth(self, role_repository, visited: Optional[Set[str]] = None) -> int:
        """
        Calculate the maximum depth of the inheritance chain.

        Args:
            role_repository: Repository to fetch roles
            visited: Set of visited roles (for cycle detection)

        Returns:
            Maximum depth of inheritance chain
        """
        if visited is None:
            visited = set()

        if self.id in visited:
            raise ValueError(f"Circular reference detected: {self.id}")

        if not self.inherits:
            return 0

        visited.add(self.id)
        max_depth = 0

        for inherited_role_id in self.inherits:
            inherited_role = role_repository.get_role(inherited_role_id)
            if inherited_role and inherited_role.active:
                depth = inherited_role.get_inheritance_depth(role_repository, visited.copy())
                max_depth = max(max_depth, depth + 1)

        return max_depth

    def to_dict(self) -> dict:
        """Convert role to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'inherits': self.inherits,
            'active': self.active,
            'audit': {
                'created_by': self.audit.created_by,
                'created_on': self.audit.created_on.isoformat() if isinstance(self.audit.created_on, datetime) else self.audit.created_on,
                'modified_by': self.audit.modified_by,
                'modified_on': self.audit.modified_on.isoformat() if isinstance(self.audit.modified_on, datetime) else self.audit.modified_on
            } if self.audit else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Role':
        """Create role from dictionary representation."""
        audit = None
        if data.get('audit'):
            audit_data = data['audit']
            audit = Audit(
                created_by=audit_data.get('created_by', 'system'),
                created_on=datetime.fromisoformat(audit_data['created_on'].replace('Z', '+00:00')) if isinstance(audit_data.get('created_on'), str) else audit_data.get('created_on'),
                modified_by=audit_data.get('modified_by', 'system'),
                modified_on=datetime.fromisoformat(audit_data['modified_on'].replace('Z', '+00:00')) if isinstance(audit_data.get('modified_on'), str) else audit_data.get('modified_on')
            )

        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            permissions=data.get('permissions', []),
            inherits=data.get('inherits', []),
            active=data.get('active', True),
            audit=audit
        )