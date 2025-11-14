"""
UserProfile command models and handlers (CQRS - Command side)
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

from viki_shared.utils.logger import getLogger
from domain.models.user_profile import (
    UserProfile, UserInfo, Organization, Authorization, Settings, Audit
)
from domain.ports.user_profile_ports import IUserProfileRepositoryPort
from domain.ports.okta_integration_port import IOktaIntegrationPort

logger = getLogger(__name__)


@dataclass
class CreateUserProfileCommand:
    """Command to create a new user profile."""
    name: str
    email: str
    organizations: List[Dict[str, str]]
    roles: List[str]
    settings: Optional[Dict[str, Any]] = None
    created_by: str = None


@dataclass
class UpdateUserProfileCommand:
    """Command to update an existing user profile."""
    profile_id: str  # Email
    name: Optional[str] = None
    organizations: Optional[List[Dict[str, str]]] = None
    roles: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    modified_by: str = None


@dataclass
class DeleteUserProfileCommand:
    """Command to delete (soft delete) a user profile."""
    profile_id: str  # Email
    deleted_by: str


class UserProfileCommandHandler:
    """Handler for user profile commands."""

    def __init__(self, profile_repository: IUserProfileRepositoryPort, okta_integration: IOktaIntegrationPort):
        self.profile_repository = profile_repository
        self.okta_integration = okta_integration

    async def handle_create_profile(self, command: CreateUserProfileCommand) -> str:
        """
        Handle create user profile command.

        Args:
            command: Create user profile command

        Returns:
            Profile ID (email) of the created profile
        """
        extra = {
            "operation": "create_user_profile",
            "email": command.email,
            "name": command.name
        }

        logger.info("Handling create user profile command", extra=extra)

        # Lowercase email for consistent profile ID
        profile_id = command.email.lower()

        # Check if profile already exists
        existing_profile = await self.profile_repository.get_profile(profile_id)
        if existing_profile:
            # If profile exists but is inactive, we'll reactivate it with fresh settings
            if not existing_profile.active:
                logger.info(f"Found inactive profile for {command.email}, reactivating with fresh settings", extra=extra)
                return await self._reactivate_profile(existing_profile, command, extra)
            else:
                # Profile exists and is active - this is an error
                raise ValueError(f"User profile already exists for email: {command.email}")

        # Create UserInfo
        user_info = UserInfo(
            name=command.name,
            email=command.email
        )

        # Create Organizations
        organizations = [
            Organization(
                business_unit=org.get("business_unit", ""),
                solution_code=org.get("solution_code", "")
            )
            for org in command.organizations
        ]

        # Create Authorization
        authorization = Authorization(
            roles=command.roles
        )

        # Create Settings
        settings_data = command.settings or {}
        settings = Settings(
            extract=settings_data.get("extract", {})
        )

        # Create Audit
        now = datetime.utcnow()
        audit = Audit(
            created_by=command.created_by or command.email,
            created_on=now,
            modified_by=command.created_by or command.email,
            modified_on=now
        )

        # Create UserProfile aggregate with lowercased email as ID
        profile = UserProfile(
            id=profile_id,  # Use lowercased email as ID
            user=user_info,
            organizations=organizations,
            authorization=authorization,
            settings=settings,
            active=True,
            audit=audit,
            created_by=command.created_by or profile_id,
            modified_by=command.created_by or profile_id
        )

        # Save through repository
        profile_id = await self.profile_repository.create_profile(profile)

        # After successful profile creation, handle Okta integration
        await self._handle_okta_integration_on_create(command.email, command.roles, profile_id)

        logger.info(f"Successfully created user profile: {profile_id}", extra={**extra, "profile_id": profile_id})
        return profile_id

    async def handle_update_profile(self, command: UpdateUserProfileCommand) -> None:
        """
        Handle update user profile command.

        Args:
            command: Update user profile command
        """
        extra = {
            "operation": "update_user_profile",
            "profile_id": command.profile_id
        }

        logger.info("Handling update user profile command", extra=extra)

        # Lowercase profile ID for consistent lookup
        profile_id = command.profile_id.lower()

        # Get existing profile
        existing_profile = await self.profile_repository.get_profile(profile_id)

        if not existing_profile:
            raise ValueError(f"User profile not found: {command.profile_id}")

        # Update fields if provided
        if command.name is not None:
            existing_profile.user.name = command.name

        if command.organizations is not None:
            existing_profile.organizations = [
                Organization(
                    business_unit=org.get("business_unit", ""),
                    solution_code=org.get("solution_code", "")
                )
                for org in command.organizations
            ]

        if command.roles is not None:
            existing_profile.authorization.roles = command.roles

        if command.settings is not None:
            existing_profile.settings.extract = command.settings.get("extract", {})

        if command.active is not None:
            existing_profile.active = command.active

        # Update audit information
        now = datetime.utcnow()
        existing_profile.modified_at = now
        existing_profile.modified_by = command.modified_by or command.profile_id

        if existing_profile.audit:
            existing_profile.audit.modified_by = command.modified_by or command.profile_id
            existing_profile.audit.modified_on = now
        else:
            # Create audit if it doesn't exist
            existing_profile.audit = Audit(
                created_by=existing_profile.created_by or command.profile_id,
                created_on=existing_profile.created_at,
                modified_by=command.modified_by or command.profile_id,
                modified_on=now
            )

        # Save through repository (will handle archiving)
        await self.profile_repository.update_profile(existing_profile)

        logger.info(f"Successfully updated user profile: {command.profile_id}", extra=extra)

    async def handle_delete_profile(self, command: DeleteUserProfileCommand) -> None:
        """
        Handle delete user profile command (soft delete).

        Args:
            command: Delete user profile command
        """
        extra = {
            "operation": "delete_user_profile",
            "profile_id": command.profile_id,
            "deleted_by": command.deleted_by
        }

        logger.info("Handling delete user profile command", extra=extra)

        # Lowercase profile ID for consistent lookup
        profile_id = command.profile_id.lower()

        # Get existing profile
        existing_profile = await self.profile_repository.get_profile(profile_id)

        if not existing_profile:
            raise ValueError(f"User profile not found: {command.profile_id}")

        # Handle Okta access removal before profile deletion
        await self._handle_okta_integration_on_delete(existing_profile.user.email, existing_profile.authorization.roles)

        # Perform soft delete through repository
        await self.profile_repository.delete_profile(profile_id, command.deleted_by)

        logger.info(f"Successfully deleted user profile: {command.profile_id}", extra=extra)

    async def _handle_okta_integration_on_create(self, email: str, roles: List[str], profile_id: str) -> None:
        """
        Handle Okta integration for a user after profile creation.
        Validates user exists, assigns app access, and assigns to appropriate groups.

        Args:
            email: User's email address
            roles: User's roles for group assignment
            profile_id: Created profile ID
        """
        try:
            # Import here to avoid circular dependencies
            from settings import Settings
            settings = Settings()

            # Check if Okta integration is available and enabled
            if not hasattr(settings, 'OKTA_AUTO_ASSIGN_ENABLED') or not settings.OKTA_AUTO_ASSIGN_ENABLED:
                logger.info(f"Okta auto-assignment disabled, skipping for user: {email}")
                return

            extra = {
                "operation": "okta_integration_on_create",
                "email": email,
                "profile_id": profile_id,
                "roles": roles
            }

            logger.info("Handling Okta integration on profile creation", extra=extra)

            # Step 1: Validate user exists if validation is enabled
            if settings.OKTA_USER_VALIDATION_ENABLED:
                validation_result = await self.okta_integration.validate_user_exists(email)
                if not validation_result.user_exists:
                    error_msg = f"User {email} does not exist in Okta: {validation_result.error_message}"
                    logger.error(error_msg, extra=extra)
                    if settings.OKTA_FAIL_ON_USER_NOT_FOUND:
                        raise ValueError(error_msg)
                    return

            # Step 2: Assign to groups based on roles (groups provide app access)
            await self._assign_user_to_groups_by_roles(email, roles, extra)

            # Note: Users are no longer directly assigned to the app.
            # App access is inherited through group membership (Regular Users or Admin Users group).

        except ValueError:
            # Re-raise validation errors to fail profile creation
            raise
        except Exception as e:
            # Don't fail profile creation for other Okta issues
            logger.error(f"Unexpected error during Okta integration for {email}: {str(e)}", extra={
                **extra,
                "error": str(e)
            })

    async def _handle_okta_integration_on_delete(self, email: str, roles: List[str]) -> None:
        """
        Handle Okta integration for a user before profile deletion.
        Removes app access and group memberships.

        Args:
            email: User's email address
            roles: User's roles for group removal
        """
        try:
            # Import here to avoid circular dependencies
            from settings import Settings
            settings = Settings()

            # Check if Okta integration is available and enabled
            if not hasattr(settings, 'OKTA_AUTO_ASSIGN_ENABLED') or not settings.OKTA_AUTO_ASSIGN_ENABLED:
                logger.info(f"Okta auto-assignment disabled, skipping removal for user: {email}")
                return

            extra = {
                "operation": "okta_integration_on_delete",
                "email": email,
                "roles": roles
            }

            logger.info("Handling Okta integration on profile deletion", extra=extra)

            # Remove from groups based on roles (this removes app access)
            await self._remove_user_from_groups_by_roles(email, roles, extra)

            # Note: Users are no longer directly assigned to the app, so no direct removal needed.
            # App access is revoked through group membership removal.

        except Exception as e:
            # Don't fail profile deletion for Okta issues
            logger.error(f"Unexpected error during Okta integration cleanup for {email}: {str(e)}", extra={
                **extra,
                "error": str(e)
            })

    async def _assign_user_to_groups_by_roles(self, email: str, roles: List[str], extra: dict) -> None:
        """
        Assign user to Okta groups based on their roles.
        - Admin/superuser roles: Admin Users group
        - Regular users: Regular Users group

        Args:
            email: User's email address
            roles: User's roles
            extra: Logging context
        """
        try:
            from settings import Settings
            settings = Settings()

            # Assign to appropriate group based on roles
            if any(role in ['superuser', 'admin'] for role in roles):
                # Admin/superuser users go to Admin Users group
                if settings.OKTA_ADMIN_GROUP_ID:
                    group_result = await self.okta_integration.assign_user_to_group(email, settings.OKTA_ADMIN_GROUP_ID)
                    if group_result.success:
                        logger.info(f"Successfully assigned user {email} to admin group", extra=extra)
                    else:
                        logger.warning(f"Failed to assign user {email} to admin group: {group_result.error_message}", extra=extra)
                else:
                    logger.warning(f"OKTA_ADMIN_GROUP_ID not configured, skipping admin group assignment for {email}", extra=extra)
            else:
                # Regular users go to Regular Users group
                if settings.OKTA_REGULAR_USERS_GROUP_ID:
                    group_result = await self.okta_integration.assign_user_to_group(email, settings.OKTA_REGULAR_USERS_GROUP_ID)
                    if group_result.success:
                        logger.info(f"Successfully assigned user {email} to regular users group", extra=extra)
                    else:
                        logger.warning(f"Failed to assign user {email} to regular users group: {group_result.error_message}", extra=extra)
                else:
                    logger.warning(f"OKTA_REGULAR_USERS_GROUP_ID not configured, skipping regular users group assignment for {email}", extra=extra)

        except Exception as e:
            logger.error(f"Error assigning user {email} to groups: {str(e)}", extra=extra)

    async def _remove_user_from_groups_by_roles(self, email: str, roles: List[str], extra: dict) -> None:
        """
        Remove user from Okta groups based on their roles.
        - Admin/superuser roles: Remove from Admin Users group
        - Regular users: Remove from Regular Users group

        Args:
            email: User's email address
            roles: User's roles
            extra: Logging context
        """
        try:
            from settings import Settings
            settings = Settings()

            # Remove from appropriate group based on roles
            if any(role in ['superuser', 'admin'] for role in roles):
                # Remove admin/superuser users from Admin Users group
                if settings.OKTA_ADMIN_GROUP_ID:
                    group_result = await self.okta_integration.remove_user_from_group(email, settings.OKTA_ADMIN_GROUP_ID)
                    if group_result.success:
                        logger.info(f"Successfully removed user {email} from admin group", extra=extra)
                    else:
                        logger.warning(f"Failed to remove user {email} from admin group: {group_result.error_message}", extra=extra)
            else:
                # Remove regular users from Regular Users group
                if settings.OKTA_REGULAR_USERS_GROUP_ID:
                    group_result = await self.okta_integration.remove_user_from_group(email, settings.OKTA_REGULAR_USERS_GROUP_ID)
                    if group_result.success:
                        logger.info(f"Successfully removed user {email} from regular users group", extra=extra)
                    else:
                        logger.warning(f"Failed to remove user {email} from regular users group: {group_result.error_message}", extra=extra)

        except Exception as e:
            logger.error(f"Error removing user {email} from groups: {str(e)}", extra=extra)

    async def _reactivate_profile(self, existing_profile: UserProfile, command: CreateUserProfileCommand, extra: dict) -> str:
        """
        Reactivate an inactive user profile with fresh settings from the command.

        Args:
            existing_profile: The inactive profile to reactivate
            command: Create user profile command with fresh settings
            extra: Logging context

        Returns:
            Profile ID (email) of the reactivated profile
        """
        profile_id = existing_profile.id

        logger.info(f"Reactivating inactive profile: {profile_id}", extra=extra)

        # Archive the current inactive state before reactivation
        await self.profile_repository.archive_profile(existing_profile, "reactivate")

        # Update the profile with fresh data from the command
        existing_profile.user.name = command.name
        existing_profile.user.email = command.email

        # Replace organizations with fresh data
        existing_profile.organizations = [
            Organization(
                business_unit=org.get("business_unit", ""),
                solution_code=org.get("solution_code", "")
            )
            for org in command.organizations
        ]

        # Replace roles with fresh data
        existing_profile.authorization.roles = command.roles

        # Replace settings with fresh data (don't preserve old settings)
        settings_data = command.settings or {}
        existing_profile.settings.extract = settings_data.get("extract", {})

        # Reactivate the profile
        existing_profile.active = True

        # Update audit trail to reflect reactivation
        now = datetime.utcnow()
        existing_profile.created_at = now  # Reset created time for reactivation
        existing_profile.modified_at = now
        existing_profile.created_by = command.created_by or command.email
        existing_profile.modified_by = command.created_by or command.email

        if existing_profile.audit:
            existing_profile.audit.created_by = command.created_by or command.email
            existing_profile.audit.created_on = now  # Reset created time
            existing_profile.audit.modified_by = command.created_by or command.email
            existing_profile.audit.modified_on = now
        else:
            # Create new audit if it doesn't exist
            existing_profile.audit = Audit(
                created_by=command.created_by or command.email,
                created_on=now,
                modified_by=command.created_by or command.email,
                modified_on=now
            )

        # Save the reactivated profile
        await self.profile_repository.update_profile(existing_profile)

        # Handle Okta integration for the reactivated profile
        await self._handle_okta_integration_on_create(command.email, command.roles, profile_id)

        logger.info(f"Successfully reactivated user profile: {profile_id}", extra={**extra, "profile_id": profile_id})
        return profile_id