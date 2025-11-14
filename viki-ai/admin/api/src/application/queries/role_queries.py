"""
Role query handlers for RBAC system.

This module contains queries and query handlers for role read operations
including listing, searching, and retrieving role information.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer

from domain.models.role import Role
from domain.ports.role_ports import IRoleRepository


@dataclass
class GetRoleQuery:
    """Query to get a single role by ID."""
    role_id: str


@dataclass
class ListRolesQuery:
    """Query to list roles with pagination and filters."""
    active_only: bool = True
    limit: int = 100
    offset: int = 0


@dataclass
class SearchRolesQuery:
    """Query to search roles by name or description."""
    search_term: str
    active_only: bool = True


@dataclass
class GetRolePermissionsQuery:
    """Query to get effective permissions for a role."""
    role_id: str


@dataclass
class GetRoleDependenciesQuery:
    """Query to get roles that depend on (inherit from) a specific role."""
    role_id: str


class RoleQueryHandler:
    """Handler for role-related queries."""

    def __init__(self, role_repository: IRoleRepository):
        """
        Initialize query handler.

        Args:
            role_repository: Role repository for data operations
        """
        self.role_repository = role_repository

    async def handle_get_role(self, query: GetRoleQuery) -> Optional[Role]:
        """
        Handle get role query.

        Args:
            query: Get role query

        Returns:
            Role if found, None otherwise
        """
        return await self.role_repository.get_role(query.role_id)

    async def handle_list_roles(self, query: ListRolesQuery) -> List[Role]:
        """
        Handle list roles query.

        Args:
            query: List roles query

        Returns:
            List of roles matching the criteria
        """
        return await self.role_repository.list_roles(
            active_only=query.active_only,
            limit=query.limit,
            offset=query.offset
        )

    async def handle_search_roles(self, query: SearchRolesQuery) -> List[Role]:
        """
        Handle search roles query.

        Args:
            query: Search roles query

        Returns:
            List of roles matching the search term
        """
        return await self.role_repository.search_roles(
            search_term=query.search_term,
            active_only=query.active_only
        )

    async def handle_get_role_permissions(self, query: GetRolePermissionsQuery) -> List[str]:
        """
        Handle get role effective permissions query.

        Args:
            query: Get role permissions query

        Returns:
            List of effective permissions

        Raises:
            ValueError: If role not found
        """
        role = await self.role_repository.get_role(query.role_id)
        if not role:
            raise ValueError(f"Role with ID '{query.role_id}' not found")

        return await role.get_effective_permissions(self.role_repository)

    async def handle_get_role_dependencies(self, query: GetRoleDependenciesQuery) -> List[str]:
        """
        Handle get role dependencies query.

        Args:
            query: Get role dependencies query

        Returns:
            List of role IDs that inherit from the specified role
        """
        return await self.role_repository.get_roles_inheriting_from(query.role_id)

    async def get_total_roles_count(self, active_only: bool = True) -> int:
        """
        Get total count of roles.

        Args:
            active_only: Only count active roles

        Returns:
            Total number of roles
        """
        return await self.role_repository.count_roles(active_only=active_only)

    async def role_exists(self, role_id: str) -> bool:
        """
        Check if a role exists.

        Args:
            role_id: Role ID to check

        Returns:
            True if role exists, False otherwise
        """
        return await self.role_repository.role_exists(role_id)

    async def get_roles_by_ids(self, role_ids: List[str]) -> List[Role]:
        """
        Get multiple roles by their IDs.

        Args:
            role_ids: List of role IDs to fetch

        Returns:
            List of found roles
        """
        return await self.role_repository.get_roles_by_ids(role_ids)

    async def get_role_inheritance_tree(self, role_id: str) -> dict:
        """
        Build an inheritance tree for a role showing all inherited roles.

        Args:
            role_id: Root role ID to build tree for

        Returns:
            Dictionary representing the inheritance tree

        Raises:
            ValueError: If role not found
        """
        role = await self.role_repository.get_role(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")

        return await self._build_inheritance_tree(role)

    async def _build_inheritance_tree(self, role: Role, visited: Optional[set] = None) -> dict:
        """
        Recursively build inheritance tree for a role.

        Args:
            role: Role to build tree for
            visited: Set of visited roles (for cycle detection)

        Returns:
            Dictionary representing the role and its inheritance tree
        """
        if visited is None:
            visited = set()

        if role.id in visited:
            # Circular reference detected
            return {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions,
                'inherits': [],
                'error': 'Circular reference detected'
            }

        visited.add(role.id)

        # Build tree structure
        tree = {
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions': role.permissions,
            'active': role.active,
            'inherits': []
        }

        # Recursively add inherited roles
        for inherited_role_id in role.inherits:
            inherited_role = await self.role_repository.get_role(inherited_role_id)
            if inherited_role:
                inherited_tree = await self._build_inheritance_tree(
                    inherited_role, visited.copy()
                )
                tree['inherits'].append(inherited_tree)
            else:
                # Role not found
                tree['inherits'].append({
                    'id': inherited_role_id,
                    'name': 'Unknown',
                    'description': 'Role not found',
                    'permissions': [],
                    'active': False,
                    'inherits': [],
                    'error': 'Role not found'
                })

        return tree

    async def get_all_available_permissions(self) -> List[str]:
        """
        Get all unique permissions available across all roles.

        Returns:
            List of all unique permissions
        """
        all_roles = await self.role_repository.list_roles(active_only=True, limit=1000)
        all_permissions = set()

        for role in all_roles:
            all_permissions.update(role.permissions)

        return sorted(list(all_permissions))

    async def get_role_statistics(self) -> dict:
        """
        Get statistics about roles in the system.

        Returns:
            Dictionary with role statistics
        """
        active_roles = await self.role_repository.list_roles(active_only=True, limit=1000)
        inactive_roles = await self.role_repository.list_roles(active_only=False, limit=1000)
        inactive_count = len([r for r in inactive_roles if not r.active])

        total_permissions = set()
        inheritance_depths = []
        roles_with_inheritance = 0

        for role in active_roles:
            total_permissions.update(role.permissions)
            if role.inherits:
                roles_with_inheritance += 1
                try:
                    depth = role.get_inheritance_depth(self.role_repository)
                    inheritance_depths.append(depth)
                except Exception:
                    # Skip roles with circular references or errors
                    pass

        return {
            'total_active_roles': len(active_roles),
            'total_inactive_roles': inactive_count,
            'total_unique_permissions': len(total_permissions),
            'roles_with_inheritance': roles_with_inheritance,
            'average_inheritance_depth': (
                sum(inheritance_depths) / len(inheritance_depths)
                if inheritance_depths else 0
            ),
            'max_inheritance_depth': max(inheritance_depths) if inheritance_depths else 0
        }