"""
Firestore adapter for UserProfile operations
"""

from typing import List, Optional, Dict, Any
from google.cloud.firestore import AsyncClient, Query
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
import os

from viki_shared.utils.logger import getLogger
from domain.models.user_profile import UserProfile
from domain.ports.user_profile_ports import IUserProfileRepositoryPort
from domain.models.user_context import get_current_user_sync, get_audit_context

logger = getLogger(__name__)


class UserProfileFirestoreAdapter(IUserProfileRepositoryPort):
    """Firestore implementation of the user profile repository port."""

    def __init__(self, firestore_client: AsyncClient):
        self.client = firestore_client
        self.collection_name = "admin_userprofiles"

    def _get_collection_ref(self):
        """Get reference to the main user profiles collection."""
        return self.client.collection(self.collection_name)

    def _get_archive_collection_ref(self, profile_id: str):
        """Get reference to the archive subcollection for a profile."""
        return (
            self.client
            .collection(self.collection_name)
            .document(profile_id)
            .collection("archive")
        )

    def _convert_firestore_doc_to_profile(self, doc) -> UserProfile:
        """Convert Firestore document to UserProfile domain model."""
        data = doc.to_dict()

        # Convert Firestore datetime objects to Python datetime instances
        datetime_fields = ["created_at", "modified_at"]
        for field in datetime_fields:
            if field in data and data[field] is not None:
                if hasattr(data[field], "timestamp"):
                    # Firestore DatetimeWithNanoseconds to Python datetime
                    data[field] = datetime.fromtimestamp(data[field].timestamp())
                elif isinstance(data[field], datetime):
                    # Already a datetime, just remove timezone
                    data[field] = data[field].replace(tzinfo=None)

        # Handle audit datetime fields if present
        if "audit" in data and data["audit"]:
            audit_datetime_fields = ["created_on", "modified_on"]
            for field in audit_datetime_fields:
                if field in data["audit"] and data["audit"][field] is not None:
                    if hasattr(data["audit"][field], "timestamp"):
                        data["audit"][field] = datetime.fromtimestamp(data["audit"][field].timestamp())
                    elif isinstance(data["audit"][field], datetime):
                        data["audit"][field] = data["audit"][field].replace(tzinfo=None)
                    elif isinstance(data["audit"][field], str):
                        # Parse ISO format string
                        try:
                            data["audit"][field] = datetime.fromisoformat(data["audit"][field].replace('Z', '+00:00').replace('+00:00', ''))
                        except:
                            data["audit"][field] = datetime.utcnow()

        return UserProfile.from_dict(data)

    async def create_profile(self, profile: UserProfile) -> str:
        """Create a new user profile."""
        # Get current user from context for audit purposes
        current_user = get_current_user_sync()
        current_user_email = current_user.email if current_user else "system"

        # Get audit context from user context (includes current user info)
        audit_context = get_audit_context()

        extra = {
            "operation": "create_user_profile",
            "profile_id": profile.id,
            "collection": self.collection_name,
            "acting_user": current_user_email,
            **audit_context  # Include user context for audit trail
        }

        logger.info("Creating user profile in Firestore", extra=extra)

        # Check if profile already exists
        doc_ref = self._get_collection_ref().document(profile.id)
        doc = await doc_ref.get()

        if doc.exists:
            raise ValueError(f"User profile already exists with ID: {profile.id}")

        # Inject current user into audit trail if profile has audit info
        profile_data = profile.to_dict()
        if "audit" in profile_data and profile_data["audit"]:
            # Override created_by and modified_by with current user from context
            profile_data["audit"]["created_by"] = current_user_email
            profile_data["audit"]["modified_by"] = current_user_email

        # Create the profile document
        await doc_ref.set(profile_data)

        logger.debug(f"Successfully created user profile: {profile.id} by {current_user_email}", extra=extra)
        return profile.id

    async def get_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Get a user profile by ID."""
        extra = {
            "operation": "get_user_profile",
            "profile_id": profile_id,
            "collection": self.collection_name
        }

        logger.debug("Getting user profile from Firestore", extra=extra)

        doc_ref = self._get_collection_ref().document(profile_id)
        doc = await doc_ref.get()

        if not doc.exists:
            logger.debug(f"User profile not found: {profile_id}", extra=extra)
            return None

        profile = self._convert_firestore_doc_to_profile(doc)
        logger.debug(f"Successfully retrieved user profile: {profile_id}", extra=extra)
        return profile

    async def update_profile(self, profile: UserProfile) -> None:
        """Update an existing user profile and archive the previous version."""
        # Get current user from context for audit purposes
        current_user = get_current_user_sync()
        current_user_email = current_user.email if current_user else "system"

        # Get audit context from user context
        audit_context = get_audit_context()

        extra = {
            "operation": "update_user_profile",
            "profile_id": profile.id,
            "collection": self.collection_name,
            "acting_user": current_user_email,
            **audit_context
        }

        logger.info("Updating user profile in Firestore", extra=extra)

        # Get the current profile for archiving
        current_profile = await self.get_profile(profile.id)
        if not current_profile:
            raise ValueError(f"User profile not found for update: {profile.id}")

        # Archive the current version
        await self.archive_profile(current_profile, "update")

        # Inject current user into audit trail if profile has audit info
        profile_data = profile.to_dict()
        if "audit" in profile_data and profile_data["audit"]:
            # Override modified_by with current user from context
            profile_data["audit"]["modified_by"] = current_user_email

        # Update the profile document
        doc_ref = self._get_collection_ref().document(profile.id)
        await doc_ref.set(profile_data)

        logger.debug(f"Successfully updated user profile: {profile.id} by {current_user_email}", extra=extra)

    async def delete_profile(self, profile_id: str, deleted_by: str) -> None:
        """Soft delete a user profile by setting active=False and archiving."""
        extra = {
            "operation": "delete_user_profile",
            "profile_id": profile_id,
            "deleted_by": deleted_by,
            "collection": self.collection_name
        }

        logger.debug("Soft deleting user profile in Firestore", extra=extra)

        # Get the current profile
        current_profile = await self.get_profile(profile_id)
        if not current_profile:
            raise ValueError(f"User profile not found for deletion: {profile_id}")

        # Archive the current version before deletion
        await self.archive_profile(current_profile, "delete")

        # Update the profile to set active=False
        now = datetime.utcnow()
        current_profile.active = False
        current_profile.modified_at = now
        current_profile.modified_by = deleted_by

        if current_profile.audit:
            current_profile.audit.modified_by = deleted_by
            current_profile.audit.modified_on = now

        # Save the updated profile
        doc_ref = self._get_collection_ref().document(profile_id)
        profile_data = current_profile.to_dict()
        await doc_ref.set(profile_data)

        logger.debug(f"Successfully soft deleted user profile: {profile_id}", extra=extra)

    async def list_profiles(
        self,
        active_only: bool = True,
        organization_filter: Optional[Dict[str, str]] = None,
        role_filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserProfile]:
        """List user profiles with optional filters."""
        extra = {
            "operation": "list_user_profiles",
            "active_only": active_only,
            "organization_filter": organization_filter,
            "role_filter": role_filter,
            "limit": limit,
            "offset": offset,
            "collection": self.collection_name
        }

        logger.debug("Listing user profiles from Firestore", extra=extra)

        # Start with base query
        query = self._get_collection_ref()

        # Apply active filter
        if active_only:
            query = query.where(filter=FieldFilter("active", "==", True))

        # Apply organization filter if provided
        if organization_filter:
            if "business_unit" in organization_filter:
                query = query.where(filter=FieldFilter("organizations", "array_contains", organization_filter))

        # Note: Firestore doesn't support querying nested arrays efficiently
        # Role filtering will be done in post-processing

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        docs = await query.get()
        profiles = []

        for doc in docs:
            profile = self._convert_firestore_doc_to_profile(doc)

            # Apply role filter in post-processing
            if role_filter:
                if role_filter not in profile.authorization.roles:
                    continue

            profiles.append(profile)

        logger.debug(f"Successfully retrieved {len(profiles)} user profiles", extra={**extra, "count": len(profiles)})
        return profiles

    async def archive_profile(self, profile: UserProfile, action: str) -> None:
        """Archive a profile version to the archive subcollection."""
        extra = {
            "operation": "archive_user_profile",
            "profile_id": profile.id,
            "action": action,
            "collection": self.collection_name
        }

        logger.debug("Archiving user profile version", extra=extra)

        # Create archive data
        archive_data = profile.create_archive_copy()
        archive_data["archive_action"] = action
        archive_data["archived_at"] = datetime.utcnow()

        # Generate unique archive document ID with timestamp
        archive_id = f"{action}_{datetime.utcnow().isoformat()}"

        # Save to archive subcollection
        archive_ref = self._get_archive_collection_ref(profile.id).document(archive_id)
        await archive_ref.set(archive_data)

        logger.debug(f"Successfully archived user profile version: {profile.id}/{archive_id}", extra=extra)

    async def get_profile_history(self, profile_id: str) -> List[Dict[str, Any]]:
        """Get the historical versions of a profile from the archive."""
        extra = {
            "operation": "get_user_profile_history",
            "profile_id": profile_id,
            "collection": self.collection_name
        }

        logger.debug("Getting user profile history from Firestore", extra=extra)

        # Query the archive subcollection
        archive_query = (
            self._get_archive_collection_ref(profile_id)
            .order_by("archived_at", direction=Query.DESCENDING)
        )

        docs = await archive_query.get()
        history = []

        for doc in docs:
            history_data = doc.to_dict()
            history_data["archive_id"] = doc.id
            history.append(history_data)

        logger.debug(f"Successfully retrieved {len(history)} historical versions for profile: {profile_id}",
                    extra={**extra, "count": len(history)})
        return history

    async def search_profiles(self, search_term: str) -> List[UserProfile]:
        """Search profiles by name or email."""
        extra = {
            "operation": "search_user_profiles",
            "search_term": search_term,
            "collection": self.collection_name
        }

        logger.debug("Searching user profiles in Firestore", extra=extra)

        # Firestore doesn't support full-text search natively
        # We'll do a simple implementation that searches by email prefix
        # For production, consider using Algolia or Elasticsearch

        search_term_lower = search_term.lower()
        profiles = []

        # Get all profiles and filter in memory (not ideal for large datasets)
        query = self._get_collection_ref()
        docs = await query.get()

        for doc in docs:
            profile = self._convert_firestore_doc_to_profile(doc)

            # Check if search term matches email or name
            if (search_term_lower in profile.user.email.lower() or
                search_term_lower in profile.user.name.lower()):
                profiles.append(profile)

        logger.debug(f"Found {len(profiles)} profiles matching search term", extra={**extra, "count": len(profiles)})
        return profiles