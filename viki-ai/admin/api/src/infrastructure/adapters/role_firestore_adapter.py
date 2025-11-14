"""
Firestore implementation of role repository.

This module provides the Firestore-based implementation for role
storage using the admin_rbac_roles collection.
"""

from typing import List, Optional
from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime

from domain.models.user_profile import Audit
from domain.models.role import Role
from domain.ports.role_ports import IRoleRepository


class RoleFirestoreAdapter(IRoleRepository):
    """Firestore implementation of the role repository."""

    COLLECTION_NAME = "admin_rbac_roles"

    def __init__(self, firestore_client: AsyncClient):
        """
        Initialize the role repository.

        Args:
            firestore_client: Firestore async client
        """
        self.client = firestore_client
        self.collection = firestore_client.collection(self.COLLECTION_NAME)

    async def create_role(self, role: Role) -> str:
        """
        Create a new role in Firestore.

        Args:
            role: Role to create

        Returns:
            Created role ID

        Raises:
            ValueError: If role already exists
        """
        # Check if role already exists
        doc_ref = self.collection.document(role.id)
        doc = await doc_ref.get()

        if doc.exists:
            raise ValueError(f"Role with ID '{role.id}' already exists")

        # Set audit data for creation
        now = datetime.utcnow()
        role.audit = Audit(
            created_by=role.audit.created_by if role.audit else "system",
            created_on=now,
            modified_by=role.audit.created_by if role.audit else "system",
            modified_on=now
        )

        # Store role in Firestore
        await doc_ref.set(role.to_dict())

        return role.id

    async def get_role(self, role_id: str) -> Optional[Role]:
        """
        Get a role by ID from Firestore.

        Args:
            role_id: Role ID to fetch

        Returns:
            Role if found, None otherwise
        """
        doc_ref = self.collection.document(role_id)
        doc = await doc_ref.get()

        if not doc.exists:
            return None

        return Role.from_dict(doc.to_dict())

    async def update_role(self, role: Role) -> None:
        """
        Update an existing role in Firestore.

        Args:
            role: Role with updated data

        Raises:
            ValueError: If role not found
        """
        doc_ref = self.collection.document(role.id)
        doc = await doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Role with ID '{role.id}' not found")

        # Update audit data for modification
        existing_role = Role.from_dict(doc.to_dict())
        now = datetime.utcnow()

        role.audit = Audit(
            created_by=existing_role.audit.created_by if existing_role.audit else "system",
            created_on=existing_role.audit.created_on if existing_role.audit else now,
            modified_by=role.audit.modified_by if role.audit else "system",
            modified_on=now
        )

        # Update role in Firestore
        await doc_ref.update(role.to_dict())

    async def delete_role(self, role_id: str) -> None:
        """
        Soft delete a role (set active=False) in Firestore.

        Args:
            role_id: Role ID to delete

        Raises:
            ValueError: If role not found
        """
        doc_ref = self.collection.document(role_id)
        doc = await doc_ref.get()

        if not doc.exists:
            raise ValueError(f"Role with ID '{role_id}' not found")

        # Soft delete by setting active=False
        await doc_ref.update({
            'active': False,
            'audit.modified_on': datetime.utcnow()
        })

    async def list_roles(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Role]:
        """
        List roles with pagination from Firestore.

        Args:
            active_only: Only return active roles
            limit: Maximum number of roles to return
            offset: Number of roles to skip

        Returns:
            List of roles
        """
        query = self.collection

        if active_only:
            query = query.where(filter=FieldFilter('active', '==', True))

        # Order by creation date for consistent pagination
        query = query.order_by('audit.created_on')

        # Apply pagination
        if offset > 0:
            query = query.offset(offset)

        query = query.limit(limit)

        # Execute query
        docs = await query.get()

        roles = []
        for doc in docs:
            try:
                role = Role.from_dict(doc.to_dict())
                roles.append(role)
            except Exception as e:
                # Log error but continue processing other roles
                print(f"Error parsing role {doc.id}: {e}")
                continue

        return roles

    async def get_roles_inheriting_from(self, role_id: str) -> List[str]:
        """
        Get list of role IDs that inherit from the given role.

        Args:
            role_id: Role ID to check dependencies for

        Returns:
            List of role IDs that inherit from the given role
        """
        # Query roles where the inherits array contains the given role_id
        query = self.collection.where(filter=FieldFilter('inherits', 'array_contains', role_id))
        query = query.where(filter=FieldFilter('active', '==', True))

        docs = await query.get()

        return [doc.id for doc in docs]

    async def count_roles(self, active_only: bool = True) -> int:
        """
        Count total number of roles in Firestore.

        Args:
            active_only: Only count active roles

        Returns:
            Total number of roles
        """
        query = self.collection

        if active_only:
            query = query.where(filter=FieldFilter('active', '==', True))

        # Get all documents and count them
        # Note: Firestore doesn't have a direct count operation
        docs = await query.get()
        return len(docs)

    async def role_exists(self, role_id: str) -> bool:
        """
        Check if a role exists in Firestore.

        Args:
            role_id: Role ID to check

        Returns:
            True if role exists, False otherwise
        """
        doc_ref = self.collection.document(role_id)
        doc = await doc_ref.get()

        return doc.exists

    async def remove_role_from_inheritance(self, role_id_to_remove: str) -> None:
        """
        Remove a role from all inheritance chains.

        This is used during role deletion to maintain data integrity.

        Args:
            role_id_to_remove: Role ID to remove from all inheritance lists
        """
        # Find all roles that inherit from the role being removed
        dependent_roles = await self.get_roles_inheriting_from(role_id_to_remove)

        # Update each dependent role to remove the inheritance
        for dependent_role_id in dependent_roles:
            doc_ref = self.collection.document(dependent_role_id)
            doc = await doc_ref.get()

            if doc.exists:
                role_data = doc.to_dict()
                inherits_list = role_data.get('inherits', [])

                # Remove the role from the inherits list
                if role_id_to_remove in inherits_list:
                    inherits_list.remove(role_id_to_remove)

                    # Update the document
                    await doc_ref.update({
                        'inherits': inherits_list,
                        'audit.modified_on': datetime.utcnow()
                    })

    async def get_roles_by_ids(self, role_ids: List[str]) -> List[Role]:
        """
        Get multiple roles by their IDs.

        Args:
            role_ids: List of role IDs to fetch

        Returns:
            List of found roles
        """
        roles = []

        for role_id in role_ids:
            role = await self.get_role(role_id)
            if role:
                roles.append(role)

        return roles

    async def search_roles(self, search_term: str, active_only: bool = True) -> List[Role]:
        """
        Search roles by name or description.

        Args:
            search_term: Term to search for
            active_only: Only search active roles

        Returns:
            List of matching roles

        Note:
            Firestore has limited text search capabilities.
            This implementation does a simple contains check.
        """
        # Get all roles (Firestore doesn't support complex text search)
        all_roles = await self.list_roles(active_only=active_only, limit=1000)

        # Filter roles that match the search term
        search_term_lower = search_term.lower()
        matching_roles = []

        for role in all_roles:
            if (search_term_lower in role.name.lower() or
                search_term_lower in role.description.lower() or
                search_term_lower in role.id.lower()):
                matching_roles.append(role)

        return matching_roles