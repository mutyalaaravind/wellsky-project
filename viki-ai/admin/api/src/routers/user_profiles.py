"""
User Profiles Router for Admin API

This router provides endpoints for user profile management.
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field, validator
from viki_shared.utils.logger import getLogger
from viki_shared.utils.exceptions import exceptionToMap
from viki_shared.models.common import PaginationInfo
from google.cloud.firestore import AsyncClient
from datetime import datetime

from settings import Settings, get_settings
from application.commands.user_profile_commands import (
    UserProfileCommandHandler,
    CreateUserProfileCommand,
    UpdateUserProfileCommand,
    DeleteUserProfileCommand
)
from application.queries.user_profile_queries import (
    UserProfileQueryHandler,
    GetUserProfileQuery,
    ListUserProfilesQuery,
    SearchUserProfilesQuery,
    GetUserProfileHistoryQuery
)
from application.queries.role_queries import RoleQueryHandler
from usecases.resolve_user_authorization_use_case import ResolveUserAuthorizationUseCase
from infrastructure.adapters.user_profile_firestore_adapter import UserProfileFirestoreAdapter
from infrastructure.adapters.role_firestore_adapter import RoleFirestoreAdapter
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = getLogger(__name__)

router = APIRouter()


# Request/Response Models
class OrganizationData(BaseModel):
    """Model for organization data."""
    business_unit: str
    solution_code: str


class AuthorizationData(BaseModel):
    """Model for authorization data."""
    roles: List[str] = Field(default_factory=list)


class SettingsData(BaseModel):
    """Model for settings data."""
    extract: Dict[str, Any] = Field(default_factory=dict)


class AuditData(BaseModel):
    """Model for audit data."""
    created_by: str
    created_on: str
    modified_by: str
    modified_on: str


class UserData(BaseModel):
    """Model for user data."""
    name: str
    email: str


class UserProfileData(BaseModel):
    """Model for user profile data."""
    id: str
    user: UserData
    organizations: List[OrganizationData] = Field(default_factory=list)
    authorization: AuthorizationData
    settings: SettingsData = Field(default_factory=SettingsData)
    active: bool = True
    audit: Optional[AuditData] = None


class UserProfileCreateRequest(BaseModel):
    """Request model for creating a user profile."""
    name: str
    email: str
    organizations: List[OrganizationData] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    settings: Optional[SettingsData] = None


class UserProfileUpdateRequest(BaseModel):
    """Request model for updating a user profile."""
    name: Optional[str] = None
    organizations: Optional[List[OrganizationData]] = None
    roles: Optional[List[str]] = None
    settings: Optional[SettingsData] = None
    active: Optional[bool] = None


class RoleData(BaseModel):
    """Model for role data in responses."""
    id: str
    name: str
    description: str
    permissions: List[str] = Field(default_factory=list)
    inherits: List[str] = Field(default_factory=list)
    active: bool = True


class UserProfileResponse(BaseModel):
    """Response model for single user profile."""
    success: bool
    message: str
    data: UserProfileData


class EnhancedUserProfileData(BaseModel):
    """Model for enhanced user profile data with resolved roles and permissions."""
    profile: UserProfileData
    resolvedRoles: List[RoleData] = Field(default_factory=list)
    resolvedPermissions: List[str] = Field(default_factory=list)


class EnhancedUserProfileResponse(BaseModel):
    """Response model for enhanced user profile with resolved roles and permissions."""
    success: bool
    message: str
    data: EnhancedUserProfileData


class UserProfileListResponse(BaseModel):
    """Response model for list of user profiles."""
    success: bool
    message: str
    data: List[UserProfileData]
    total: int
    pagination: PaginationInfo


class UserProfileDeleteResponse(BaseModel):
    """Response model for user profile deletion."""
    success: bool
    message: str
    deleted_id: str


class UserProfileHistoryResponse(BaseModel):
    """Response model for user profile history."""
    success: bool
    message: str
    profile_id: str
    history: List[Dict[str, Any]]
    total: int


# Dependency Functions
async def get_firestore_client(settings: Settings = Depends(get_settings)) -> AsyncClient:
    """Get Firestore client dependency."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        return AsyncClient()  # Use default database in emulator
    else:
        return AsyncClient(database=settings.GCP_FIRESTORE_DB)


async def get_user_profile_command_handler(
    settings: Settings = Depends(get_settings)
) -> UserProfileCommandHandler:
    """Get UserProfile Command Handler with dependencies."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        firestore_client = AsyncClient()  # Use default database in emulator
    else:
        firestore_client = AsyncClient(database=settings.GCP_FIRESTORE_DB)
    profile_repository = UserProfileFirestoreAdapter(firestore_client)

    # Import here to avoid circular imports
    from infrastructure.adapters.okta_integration_adapter import OktaIntegrationAdapter
    okta_integration = OktaIntegrationAdapter(settings)

    return UserProfileCommandHandler(profile_repository, okta_integration)


async def get_user_profile_query_handler(
    settings: Settings = Depends(get_settings)
) -> UserProfileQueryHandler:
    """Get UserProfile Query Handler with dependencies."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        firestore_client = AsyncClient()  # Use default database in emulator
    else:
        firestore_client = AsyncClient(database=settings.GCP_FIRESTORE_DB)
    profile_repository = UserProfileFirestoreAdapter(firestore_client)
    return UserProfileQueryHandler(profile_repository)


async def get_role_query_handler(
    settings: Settings = Depends(get_settings)
) -> RoleQueryHandler:
    """Get Role Query Handler with dependencies."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        firestore_client = AsyncClient()  # Use default database in emulator
    else:
        firestore_client = AsyncClient(database=settings.GCP_FIRESTORE_DB)
    role_repository = RoleFirestoreAdapter(firestore_client)
    return RoleQueryHandler(role_repository)


async def get_resolve_user_authorization_use_case(
    role_query_handler: RoleQueryHandler = Depends(get_role_query_handler)
) -> ResolveUserAuthorizationUseCase:
    """Get Resolve User Authorization Use Case with dependencies."""
    return ResolveUserAuthorizationUseCase(role_query_handler)



# API Endpoints
@router.post(
    "",
    response_model=UserProfileResponse,
    summary="Create User Profile",
    description="Create a new user profile."
)
async def create_profile(
    profile_request: UserProfileCreateRequest,
    command_handler: UserProfileCommandHandler = Depends(get_user_profile_command_handler),
    current_user: User = RequireAuth
) -> UserProfileResponse:
    """
    Create a new user profile.

    Args:
        profile_request: User profile creation request
        command_handler: Command handler dependency
        current_user: Current authenticated user

    Returns:
        UserProfileResponse with created profile data
    """
    extra = {
        "operation": "create_user_profile",
        "email": profile_request.email,
        "current_user": current_user.email
    }

    logger.info(f"Creating user profile: {profile_request.email}", extra=extra)

    try:
        # Create command
        command = CreateUserProfileCommand(
            name=profile_request.name,
            email=profile_request.email,
            organizations=[org.dict() for org in profile_request.organizations],
            roles=profile_request.roles,
            settings=profile_request.settings.dict() if profile_request.settings else None,
            created_by=current_user.email
        )

        # Execute command
        profile_id = await command_handler.handle_create_profile(command)

        # Get the created profile
        query_handler = await get_user_profile_query_handler(Settings())
        query = GetUserProfileQuery(profile_id=profile_id)
        profile = await query_handler.handle_get_profile(query)

        if not profile:
            raise HTTPException(status_code=500, detail="Failed to retrieve created profile")

        # Convert to response
        profile_data = UserProfileData(
            id=profile.id,
            user=UserData(name=profile.user.name, email=profile.user.email),
            organizations=[
                OrganizationData(
                    business_unit=org.business_unit,
                    solution_code=org.solution_code
                )
                for org in profile.organizations
            ],
            authorization=AuthorizationData(roles=profile.authorization.roles),
            settings=SettingsData(extract=profile.settings.extract),
            active=profile.active,
            audit=AuditData(
                created_by=profile.audit.created_by,
                created_on=profile.audit.created_on.isoformat(),
                modified_by=profile.audit.modified_by,
                modified_on=profile.audit.modified_on.isoformat()
            ) if profile.audit else None
        )

        return UserProfileResponse(
            success=True,
            message=f"User profile created successfully: {profile_id}",
            data=profile_data
        )

    except ValueError as e:
        logger.error(f"Validation error creating user profile: {str(e)}", extra=extra)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to create user profile: {str(e)}")


@router.post(
    "/search",
    response_model=UserProfileListResponse,
    summary="Search User Profiles",
    description="Search user profiles by name or email."
)
async def search_profiles(
    search_term: str = Query(..., description="Search term for name or email"),
    active_only: bool = Query(True, description="Only return active profiles"),
    query_handler: UserProfileQueryHandler = Depends(get_user_profile_query_handler),
    current_user: User = RequireAuth
) -> UserProfileListResponse:
    """
    Search user profiles by name or email.

    Args:
        search_term: Search term
        active_only: Only return active profiles
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        UserProfileListResponse with matching profiles
    """
    extra = {
        "operation": "search_user_profiles",
        "search_term": search_term,
        "active_only": active_only,
        "current_user": current_user.email
    }

    logger.info(f"Searching user profiles: {search_term}", extra=extra)

    try:
        # Execute query
        query = SearchUserProfilesQuery(
            search_term=search_term,
            active_only=active_only
        )
        profiles = await query_handler.handle_search_profiles(query)

        # Convert to response
        profiles_data = [
            UserProfileData(
                id=profile.id,
                user=UserData(name=profile.user.name, email=profile.user.email),
                organizations=[
                    OrganizationData(
                        business_unit=org.business_unit,
                        solution_code=org.solution_code
                    )
                    for org in profile.organizations
                ],
                authorization=AuthorizationData(roles=profile.authorization.roles),
                settings=SettingsData(extract=profile.settings.extract),
                active=profile.active,
                audit=AuditData(
                    created_by=profile.audit.created_by,
                    created_on=profile.audit.created_on.isoformat(),
                    modified_by=profile.audit.modified_by,
                    modified_on=profile.audit.modified_on.isoformat()
                ) if profile.audit else None
            )
            for profile in profiles
        ]

        pagination = PaginationInfo(
            limit=len(profiles),
            offset=0,
            returned=len(profiles),
            has_more=False
        )

        return UserProfileListResponse(
            success=True,
            message=f"Found {len(profiles)} matching profiles",
            data=profiles_data,
            total=len(profiles),
            pagination=pagination
        )

    except Exception as e:
        logger.error(f"Error searching user profiles: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to search user profiles: {str(e)}")


@router.get(
    "/myprofile",
    response_model=EnhancedUserProfileResponse,
    summary="Get My Profile",
    description="Get or auto-provision current user's profile with resolved roles and permissions."
)
async def get_my_profile(
    query_handler: UserProfileQueryHandler = Depends(get_user_profile_query_handler),
    auth_use_case: ResolveUserAuthorizationUseCase = Depends(get_resolve_user_authorization_use_case),
    command_handler: UserProfileCommandHandler = Depends(get_user_profile_command_handler),
    current_user: User = RequireAuth
) -> EnhancedUserProfileResponse:
    """
    Get the current user's profile. Auto-provisions for superusers if not exists.

    Args:
        query_handler: Query handler dependency
        command_handler: Command handler dependency
        current_user: Current authenticated user with JWT claims

    Returns:
        UserProfileResponse with profile data
    """
    # Get the email to use as profile ID - prioritize email claim, fallback to sub
    email = current_user.email or current_user.sub
    if not email:
        logger.error("No email or sub found in user token", extra={"current_user": current_user.sub, "claims": current_user.claims})
        raise HTTPException(status_code=500, detail="No email found in user token")

    # Use lowercased email as consistent profile ID
    profile_id = email.lower()

    # Get display name with fallbacks
    display_name = current_user.name or email

    extra = {
        "operation": "get_my_profile",
        "email": email,
        "profile_id": profile_id,
        "current_user": current_user.sub
    }

    logger.info(f"Getting my profile: {profile_id}", extra=extra)

    try:
        # Try to fetch existing profile
        query = GetUserProfileQuery(profile_id=profile_id)
        profile = await query_handler.handle_get_profile(query)

        # If profile doesn't exist, check if we should auto-create for superuser
        if not profile:
            # Check if user has superuser role in group-roles claim
            group_roles = []
            if current_user.claims:
                # Handle both string and list formats for group-roles
                group_roles_claim = current_user.claims.get("group-roles", [])
                if isinstance(group_roles_claim, str):
                    group_roles = [group_roles_claim]
                elif isinstance(group_roles_claim, list):
                    group_roles = group_roles_claim
                else:
                    logger.warning(f"Unexpected group-roles format: {type(group_roles_claim)}", extra=extra)
                    group_roles = []
                logger.info(f"User group-roles: {group_roles}", extra=extra)
            else:
                logger.info("No claims found in user token", extra=extra)

            if "superuser" in group_roles:
                logger.info(f"Auto-provisioning superuser profile for: {email}", extra=extra)

                # Create superuser profile with wildcard permissions
                command = CreateUserProfileCommand(
                    name=display_name,
                    email=email,  # Use original case
                    organizations=[{
                        "business_unit": "*",
                        "solution_code": "*"
                    }],
                    roles=["superuser"],
                    settings={"extract": {}},
                    created_by=profile_id  # Use lowercased email
                )

                # Execute command to create profile
                try:
                    created_profile_id = await command_handler.handle_create_profile(command)
                    logger.info(f"Successfully created profile with ID: {created_profile_id}", extra=extra)
                except Exception as create_error:
                    logger.error(f"Failed to create superuser profile: {str(create_error)}", extra=extra)
                    raise HTTPException(status_code=500, detail=f"Failed to auto-create profile: {str(create_error)}")

                # Fetch the newly created profile
                profile = await query_handler.handle_get_profile(
                    GetUserProfileQuery(profile_id=created_profile_id)
                )

                if not profile:
                    logger.error(f"Profile creation succeeded but retrieval failed for ID: {created_profile_id}", extra=extra)
                    raise HTTPException(status_code=500, detail="Failed to retrieve auto-created profile")

                logger.info(f"Successfully auto-created and retrieved superuser profile: {created_profile_id}", extra=extra)
            else:
                # User is not a superuser and has no profile
                raise HTTPException(status_code=404, detail=f"User profile not found: {email}")

        # Convert to base profile data
        profile_data = UserProfileData(
            id=profile.id,
            user=UserData(name=profile.user.name, email=profile.user.email),
            organizations=[
                OrganizationData(
                    business_unit=org.business_unit,
                    solution_code=org.solution_code
                )
                for org in profile.organizations
            ],
            authorization=AuthorizationData(roles=profile.authorization.roles),
            settings=SettingsData(extract=profile.settings.extract),
            active=profile.active,
            audit=AuditData(
                created_by=profile.audit.created_by,
                created_on=profile.audit.created_on.isoformat(),
                modified_by=profile.audit.modified_by,
                modified_on=profile.audit.modified_on.isoformat()
            ) if profile.audit else None
        )

        # Resolve roles and permissions using the use case
        try:
            resolved_roles_dicts, resolved_permissions = await auth_use_case.execute(profile.authorization.roles)
            resolved_roles = [RoleData(**role_dict) for role_dict in resolved_roles_dicts]
        except Exception as role_error:
            logger.warning(f"Failed to resolve roles/permissions, returning basic profile: {str(role_error)}", extra=extra)
            # Fall back to empty resolved data if role resolution fails
            resolved_roles = []
            resolved_permissions = []

        # Create enhanced response
        enhanced_data = EnhancedUserProfileData(
            profile=profile_data,
            resolvedRoles=resolved_roles,
            resolvedPermissions=resolved_permissions
        )

        return EnhancedUserProfileResponse(
            success=True,
            message="User profile retrieved successfully",
            data=enhanced_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting my profile: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")


@router.get(
    "",
    response_model=UserProfileListResponse,
    summary="List User Profiles",
    description="Retrieve a list of user profiles with optional filters."
)
async def list_profiles(
    active_only: bool = Query(True, description="Only return active profiles"),
    business_unit: Optional[str] = Query(None, description="Filter by business unit"),
    solution_code: Optional[str] = Query(None, description="Filter by solution code"),
    role: Optional[str] = Query(None, description="Filter by role"),
    limit: int = Query(100, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    query_handler: UserProfileQueryHandler = Depends(get_user_profile_query_handler),
    current_user: User = RequireAuth
) -> UserProfileListResponse:
    """
    List user profiles with optional filters.

    Args:
        active_only: Only return active profiles
        business_unit: Optional business unit filter
        solution_code: Optional solution code filter
        role: Optional role filter
        limit: Maximum number of results
        offset: Number of results to skip
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        UserProfileListResponse with list of profiles
    """
    extra = {
        "operation": "list_user_profiles",
        "active_only": active_only,
        "business_unit": business_unit,
        "solution_code": solution_code,
        "role": role,
        "limit": limit,
        "offset": offset,
        "current_user": current_user.email
    }

    logger.info("Listing user profiles", extra=extra)

    try:
        # Build organization filter
        organization_filter = None
        if business_unit or solution_code:
            organization_filter = {}
            if business_unit:
                organization_filter["business_unit"] = business_unit
            if solution_code:
                organization_filter["solution_code"] = solution_code

        # Execute query
        query = ListUserProfilesQuery(
            active_only=active_only,
            organization_filter=organization_filter,
            role_filter=role,
            limit=limit,
            offset=offset
        )
        profiles = await query_handler.handle_list_profiles(query)

        # Convert to response
        profiles_data = [
            UserProfileData(
                id=profile.id,
                user=UserData(name=profile.user.name, email=profile.user.email),
                organizations=[
                    OrganizationData(
                        business_unit=org.business_unit,
                        solution_code=org.solution_code
                    )
                    for org in profile.organizations
                ],
                authorization=AuthorizationData(roles=profile.authorization.roles),
                settings=SettingsData(extract=profile.settings.extract),
                active=profile.active,
                audit=AuditData(
                    created_by=profile.audit.created_by,
                    created_on=profile.audit.created_on.isoformat(),
                    modified_by=profile.audit.modified_by,
                    modified_on=profile.audit.modified_on.isoformat()
                ) if profile.audit else None
            )
            for profile in profiles
        ]

        pagination = PaginationInfo(
            limit=limit,
            offset=offset,
            returned=len(profiles),
            has_more=len(profiles) == limit
        )

        return UserProfileListResponse(
            success=True,
            message=f"Retrieved {len(profiles)} user profiles",
            data=profiles_data,
            total=len(profiles),
            pagination=pagination
        )

    except Exception as e:
        logger.error(f"Error listing user profiles: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to list user profiles: {str(e)}")


@router.get(
    "/{profile_id}",
    response_model=UserProfileResponse,
    summary="Get User Profile",
    description="Retrieve a specific user profile by ID (email)."
)
async def get_profile(
    profile_id: str = Path(..., description="User profile ID (email)"),
    query_handler: UserProfileQueryHandler = Depends(get_user_profile_query_handler),
    current_user: User = RequireAuth
) -> UserProfileResponse:
    """
    Get a user profile by ID.

    Args:
        profile_id: User profile ID (email)
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        UserProfileResponse with profile data
    """
    # Lowercase profile ID for consistent lookup
    profile_id_lower = profile_id.lower()

    extra = {
        "operation": "get_user_profile",
        "profile_id": profile_id,
        "profile_id_lower": profile_id_lower,
        "current_user": current_user.email
    }

    logger.info(f"Getting user profile: {profile_id}", extra=extra)

    try:
        # Execute query with lowercased profile ID
        query = GetUserProfileQuery(profile_id=profile_id_lower)
        profile = await query_handler.handle_get_profile(query)

        if not profile:
            raise HTTPException(status_code=404, detail=f"User profile not found: {profile_id}")

        # Convert to response
        profile_data = UserProfileData(
            id=profile.id,
            user=UserData(name=profile.user.name, email=profile.user.email),
            organizations=[
                OrganizationData(
                    business_unit=org.business_unit,
                    solution_code=org.solution_code
                )
                for org in profile.organizations
            ],
            authorization=AuthorizationData(roles=profile.authorization.roles),
            settings=SettingsData(extract=profile.settings.extract),
            active=profile.active,
            audit=AuditData(
                created_by=profile.audit.created_by,
                created_on=profile.audit.created_on.isoformat(),
                modified_by=profile.audit.modified_by,
                modified_on=profile.audit.modified_on.isoformat()
            ) if profile.audit else None
        )

        return UserProfileResponse(
            success=True,
            message=f"User profile retrieved successfully",
            data=profile_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")


@router.put(
    "/{profile_id}",
    response_model=UserProfileResponse,
    summary="Update User Profile",
    description="Update an existing user profile."
)
async def update_profile(
    profile_id: str = Path(..., description="User profile ID (email)"),
    profile_request: UserProfileUpdateRequest = ...,
    command_handler: UserProfileCommandHandler = Depends(get_user_profile_command_handler),
    current_user: User = RequireAuth
) -> UserProfileResponse:
    """
    Update a user profile.

    Args:
        profile_id: User profile ID (email)
        profile_request: User profile update request
        command_handler: Command handler dependency
        current_user: Current authenticated user

    Returns:
        UserProfileResponse with updated profile data
    """
    # Lowercase profile ID for consistent lookup
    profile_id_lower = profile_id.lower()

    extra = {
        "operation": "update_user_profile",
        "profile_id": profile_id,
        "profile_id_lower": profile_id_lower,
        "current_user": current_user.email
    }

    logger.info(f"Updating user profile: {profile_id}", extra=extra)

    try:
        # Create command with original profile_id (will be lowercased in handler)
        command = UpdateUserProfileCommand(
            profile_id=profile_id,
            name=profile_request.name,
            organizations=[org.dict() for org in profile_request.organizations] if profile_request.organizations else None,
            roles=profile_request.roles,
            settings=profile_request.settings.dict() if profile_request.settings else None,
            active=profile_request.active,
            modified_by=current_user.email
        )

        # Execute command
        await command_handler.handle_update_profile(command)

        # Get the updated profile using lowercased ID
        query_handler = await get_user_profile_query_handler(Settings())
        query = GetUserProfileQuery(profile_id=profile_id_lower)
        profile = await query_handler.handle_get_profile(query)

        if not profile:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated profile")

        # Convert to response
        profile_data = UserProfileData(
            id=profile.id,
            user=UserData(name=profile.user.name, email=profile.user.email),
            organizations=[
                OrganizationData(
                    business_unit=org.business_unit,
                    solution_code=org.solution_code
                )
                for org in profile.organizations
            ],
            authorization=AuthorizationData(roles=profile.authorization.roles),
            settings=SettingsData(extract=profile.settings.extract),
            active=profile.active,
            audit=AuditData(
                created_by=profile.audit.created_by,
                created_on=profile.audit.created_on.isoformat(),
                modified_by=profile.audit.modified_by,
                modified_on=profile.audit.modified_on.isoformat()
            ) if profile.audit else None
        )

        return UserProfileResponse(
            success=True,
            message=f"User profile updated successfully",
            data=profile_data
        )

    except ValueError as e:
        logger.error(f"Validation error updating user profile: {str(e)}", extra=extra)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")


@router.delete(
    "/{profile_id}",
    response_model=UserProfileDeleteResponse,
    summary="Delete User Profile",
    description="Soft delete a user profile (sets active=False and archives)."
)
async def delete_profile(
    profile_id: str = Path(..., description="User profile ID (email)"),
    command_handler: UserProfileCommandHandler = Depends(get_user_profile_command_handler),
    current_user: User = RequireAuth
) -> UserProfileDeleteResponse:
    """
    Delete a user profile (soft delete).

    Args:
        profile_id: User profile ID (email)
        command_handler: Command handler dependency
        current_user: Current authenticated user

    Returns:
        UserProfileDeleteResponse with deletion confirmation
    """
    # Profile ID will be lowercased in the command handler
    extra = {
        "operation": "delete_user_profile",
        "profile_id": profile_id,
        "current_user": current_user.email
    }

    logger.info(f"Deleting user profile: {profile_id}", extra=extra)

    try:
        # Create command (profile_id will be lowercased in handler)
        command = DeleteUserProfileCommand(
            profile_id=profile_id,
            deleted_by=current_user.email
        )

        # Execute command
        await command_handler.handle_delete_profile(command)

        return UserProfileDeleteResponse(
            success=True,
            message=f"User profile deleted successfully",
            deleted_id=profile_id
        )

    except ValueError as e:
        logger.error(f"Validation error deleting user profile: {str(e)}", extra=extra)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting user profile: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to delete user profile: {str(e)}")


@router.get(
    "/{profile_id}/history",
    response_model=UserProfileHistoryResponse,
    summary="Get User Profile History",
    description="Retrieve historical versions of a user profile from the archive."
)
async def get_profile_history(
    profile_id: str = Path(..., description="User profile ID (email)"),
    query_handler: UserProfileQueryHandler = Depends(get_user_profile_query_handler),
    current_user: User = RequireAuth
) -> UserProfileHistoryResponse:
    """
    Get historical versions of a user profile.

    Args:
        profile_id: User profile ID (email)
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        UserProfileHistoryResponse with archived versions
    """
    # Lowercase profile ID for consistent lookup
    profile_id_lower = profile_id.lower()

    extra = {
        "operation": "get_user_profile_history",
        "profile_id": profile_id,
        "profile_id_lower": profile_id_lower,
        "current_user": current_user.email
    }

    logger.info(f"Getting user profile history: {profile_id}", extra=extra)

    try:
        # Execute query with lowercased profile ID
        query = GetUserProfileHistoryQuery(profile_id=profile_id_lower)
        history = await query_handler.handle_get_profile_history(query)

        return UserProfileHistoryResponse(
            success=True,
            message=f"Retrieved {len(history)} historical versions",
            profile_id=profile_id,
            history=history,
            total=len(history)
        )

    except Exception as e:
        logger.error(f"Error getting user profile history: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to get user profile history: {str(e)}")