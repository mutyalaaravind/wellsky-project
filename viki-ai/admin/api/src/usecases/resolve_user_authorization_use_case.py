"""
Resolve User Authorization Use Case.

This use case handles the business logic for resolving user roles and permissions
including inheritance hierarchy and caching for performance optimization.
"""

from typing import List, Tuple
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer

from application.queries.role_queries import RoleQueryHandler, ListRolesQuery, GetRoleQuery
from domain.models.role import Role


class ResolveUserAuthorizationUseCase:
    """Use case for resolving user authorization including roles and permissions."""

    def __init__(self, role_query_handler: RoleQueryHandler):
        """
        Initialize the use case.

        Args:
            role_query_handler: Role query handler for data operations
        """
        self.role_query_handler = role_query_handler

    @cached(ttl=300, cache=Cache.MEMORY, serializer=PickleSerializer())
    async def execute(self, user_role_ids: List[str]) -> Tuple[List[dict], List[str]]:
        """
        Execute the use case to resolve user roles and permissions with caching.

        Args:
            user_role_ids: List of role IDs from user profile

        Returns:
            Tuple of (resolved_roles_dicts, resolved_permissions)
        """
        resolved_roles = await self._resolve_user_roles(user_role_ids)
        resolved_permissions = self._resolve_permissions_from_roles(resolved_roles)

        # Convert roles to dicts for API serialization
        resolved_roles_dicts = [
            {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions,
                'inherits': role.inherits,
                'active': role.active
            }
            for role in resolved_roles
        ]

        return resolved_roles_dicts, resolved_permissions

    async def _resolve_user_roles(self, user_role_ids: List[str]) -> List[Role]:
        """
        Resolve user roles including inheritance hierarchy.

        Args:
            user_role_ids: List of role IDs from user profile

        Returns:
            List of resolved role objects with inheritance
        """
        resolved_roles = set()

        # Special case: if user has superuser role, return all active roles
        if "superuser" in user_role_ids:
            all_roles_query = ListRolesQuery(active_only=True, limit=1000)
            all_roles = await self.role_query_handler.handle_list_roles(all_roles_query)
            return all_roles

        # For non-superuser, resolve inheritance for each role
        for role_id in user_role_ids:
            await self._collect_roles_recursive(role_id, resolved_roles, set())

        # Convert to list and sort by role ID for consistency
        return sorted(list(resolved_roles), key=lambda x: x.id)

    async def _collect_roles_recursive(self, role_id: str, resolved_roles: set, visited: set) -> None:
        """
        Recursively collect roles following inheritance chain.

        Args:
            role_id: Current role ID to process
            resolved_roles: Set to collect resolved roles
            visited: Set to track visited roles (prevent cycles)
        """
        if role_id in visited:
            return  # Prevent infinite loops

        visited.add(role_id)

        role_query = GetRoleQuery(role_id=role_id)
        role = await self.role_query_handler.handle_get_role(role_query)

        if role and role.active:
            resolved_roles.add(role)

            # Recursively collect inherited roles
            for inherited_role_id in role.inherits:
                await self._collect_roles_recursive(inherited_role_id, resolved_roles, visited.copy())

    def _resolve_permissions_from_roles(self, resolved_roles: List[Role]) -> List[str]:
        """
        Resolve effective permissions from resolved roles.

        Args:
            resolved_roles: List of resolved role objects

        Returns:
            Sorted list of unique permission strings
        """
        all_permissions = set()

        # Collect all permissions from all resolved roles
        for role in resolved_roles:
            all_permissions.update(role.permissions)

        # Return sorted unique permissions
        return sorted(list(all_permissions))