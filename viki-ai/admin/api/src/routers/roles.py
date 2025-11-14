"""
Roles Router for Admin API

This router provides endpoints for role management including
CRUD operations and role hierarchy management.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from viki_shared.utils.logger import getLogger
from viki_shared.utils.exceptions import exceptionToMap
from viki_shared.models.common import PaginationInfo
from google.cloud.firestore import AsyncClient

from settings import Settings, get_settings
from application.commands.role_commands import (
    RoleCommandHandler,
    CreateRoleCommand,
    UpdateRoleCommand,
    DeleteRoleCommand,
    RoleValidationService
)
from application.queries.role_queries import (
    RoleQueryHandler,
    GetRoleQuery,
    ListRolesQuery,
    SearchRolesQuery,
    GetRolePermissionsQuery,
    GetRoleDependenciesQuery
)
from infrastructure.adapters.role_firestore_adapter import RoleFirestoreAdapter
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = getLogger(__name__)

router = APIRouter()


# Request/Response Models
class RoleData(BaseModel):
    """Model for role data."""
    id: str
    name: str
    description: str
    permissions: List[str] = Field(default_factory=list)
    inherits: List[str] = Field(default_factory=list)
    active: bool = True


class RoleCreateRequest(BaseModel):
    """Request model for creating a role."""
    id: str = Field(..., description="Role ID in format 'domain:role_name'")
    name: str = Field(..., description="Display name for the role")
    description: str = Field(..., description="Human-readable description")
    permissions: List[str] = Field(default_factory=list, description="List of permissions")
    inherits: List[str] = Field(default_factory=list, description="List of role IDs to inherit from")


class RoleUpdateRequest(BaseModel):
    """Request model for updating a role."""
    name: Optional[str] = Field(None, description="Display name for the role")
    description: Optional[str] = Field(None, description="Human-readable description")
    permissions: Optional[List[str]] = Field(None, description="List of permissions")
    inherits: Optional[List[str]] = Field(None, description="List of role IDs to inherit from")
    active: Optional[bool] = Field(None, description="Whether the role is active")


class RoleResponse(BaseModel):
    """Response model for single role."""
    success: bool
    message: str
    data: RoleData


class RoleListResponse(BaseModel):
    """Response model for list of roles."""
    success: bool
    message: str
    data: List[RoleData]
    total: int
    pagination: PaginationInfo


class RoleDeleteResponse(BaseModel):
    """Response model for role deletion."""
    success: bool
    message: str
    deleted_id: str


class RolePermissionsResponse(BaseModel):
    """Response model for role effective permissions."""
    success: bool
    message: str
    role_id: str
    effective_permissions: List[str]


class RoleDependenciesResponse(BaseModel):
    """Response model for role dependencies."""
    success: bool
    message: str
    role_id: str
    dependent_roles: List[str]


# Dependency Functions
async def get_firestore_client(settings: Settings = Depends(get_settings)) -> AsyncClient:
    """Get Firestore client dependency."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        return AsyncClient()  # Use default database in emulator
    else:
        return AsyncClient(database=settings.GCP_FIRESTORE_DB)


async def get_role_command_handler(
    firestore_client: AsyncClient = Depends(get_firestore_client)
) -> RoleCommandHandler:
    """Get Role Command Handler with dependencies."""
    role_repository = RoleFirestoreAdapter(firestore_client)
    return RoleCommandHandler(role_repository)


async def get_role_query_handler(
    firestore_client: AsyncClient = Depends(get_firestore_client)
) -> RoleQueryHandler:
    """Get Role Query Handler with dependencies."""
    role_repository = RoleFirestoreAdapter(firestore_client)
    return RoleQueryHandler(role_repository)


# Helper Functions
def role_to_data(role) -> RoleData:
    """Convert Role domain model to RoleData response model."""
    return RoleData(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions,
        inherits=role.inherits,
        active=role.active
    )


# API Endpoints
@router.post(
    "",
    response_model=RoleResponse,
    summary="Create Role",
    description="Create a new role with permissions and inheritance."
)
async def create_role(
    role_request: RoleCreateRequest,
    command_handler: RoleCommandHandler = Depends(get_role_command_handler),
    current_user: User = RequireAuth
) -> RoleResponse:
    """
    Create a new role.

    Args:
        role_request: Role creation request
        command_handler: Command handler dependency
        current_user: Current authenticated user

    Returns:
        RoleResponse with created role data
    """
    extra = {
        "operation": "create_role",
        "role_id": role_request.id,
        "current_user": current_user.email
    }

    logger.info(f"Creating role: {role_request.id}", extra=extra)

    try:
        # Create command
        command = CreateRoleCommand(
            id=role_request.id,
            name=role_request.name,
            description=role_request.description,
            permissions=role_request.permissions,
            inherits=role_request.inherits,
            created_by=current_user.email
        )

        # Execute command
        role_id = await command_handler.handle_create_role(command)

        # Get the created role using the query handler dependency
        firestore_client = await get_firestore_client()
        role_repository = RoleFirestoreAdapter(firestore_client)
        query_handler = RoleQueryHandler(role_repository)
        query = GetRoleQuery(role_id=role_id)
        role = await query_handler.handle_get_role(query)

        if not role:
            raise HTTPException(status_code=500, detail="Failed to retrieve created role")

        return RoleResponse(
            success=True,
            message=f"Role created successfully: {role_id}",
            data=role_to_data(role)
        )

    except ValueError as e:
        logger.error(f"Validation error creating role: {str(e)}", extra=extra)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to create role: {str(e)}")


@router.get(
    "/search",
    response_model=RoleListResponse,
    summary="Search Roles",
    description="Search roles by name or description."
)
async def search_roles(
    search_term: str = Query(..., description="Search term for name or description"),
    active_only: bool = Query(True, description="Only return active roles"),
    query_handler: RoleQueryHandler = Depends(get_role_query_handler),
    current_user: User = RequireAuth
) -> RoleListResponse:
    """
    Search roles by name or description.

    Args:
        search_term: Search term
        active_only: Only return active roles
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        RoleListResponse with matching roles
    """
    extra = {
        "operation": "search_roles",
        "search_term": search_term,
        "active_only": active_only,
        "current_user": current_user.email
    }

    logger.info(f"Searching roles: {search_term}", extra=extra)

    try:
        query = SearchRolesQuery(
            search_term=search_term,
            active_only=active_only
        )
        roles = await query_handler.handle_search_roles(query)

        roles_data = [role_to_data(role) for role in roles]

        pagination = PaginationInfo(
            limit=len(roles),
            offset=0,
            returned=len(roles),
            has_more=False
        )

        return RoleListResponse(
            success=True,
            message=f"Found {len(roles)} matching roles",
            data=roles_data,
            total=len(roles),
            pagination=pagination
        )

    except Exception as e:
        logger.error(f"Error searching roles: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to search roles: {str(e)}")


@router.get(
    "",
    response_model=RoleListResponse,
    summary="List Roles",
    description="Retrieve a list of roles with optional filters and pagination."
)
async def list_roles(
    active_only: bool = Query(True, description="Only return active roles"),
    limit: int = Query(100, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    query_handler: RoleQueryHandler = Depends(get_role_query_handler),
    current_user: User = RequireAuth
) -> RoleListResponse:
    """
    List roles with optional filters and pagination.

    Args:
        active_only: Only return active roles
        limit: Maximum number of results
        offset: Number of results to skip
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        RoleListResponse with list of roles
    """
    extra = {
        "operation": "list_roles",
        "active_only": active_only,
        "limit": limit,
        "offset": offset,
        "current_user": current_user.email
    }

    logger.info("Listing roles", extra=extra)

    try:
        query = ListRolesQuery(
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        roles = await query_handler.handle_list_roles(query)
        total = await query_handler.get_total_roles_count(active_only=active_only)

        roles_data = [role_to_data(role) for role in roles]

        pagination = PaginationInfo(
            limit=limit,
            offset=offset,
            returned=len(roles),
            has_more=len(roles) == limit
        )

        return RoleListResponse(
            success=True,
            message=f"Retrieved {len(roles)} roles",
            data=roles_data,
            total=total,
            pagination=pagination
        )

    except Exception as e:
        logger.error(f"Error listing roles: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to list roles: {str(e)}")


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get Role",
    description="Retrieve a specific role by ID."
)
async def get_role(
    role_id: str = Path(..., description="Role ID to retrieve"),
    query_handler: RoleQueryHandler = Depends(get_role_query_handler),
    current_user: User = RequireAuth
) -> RoleResponse:
    """
    Get a role by ID.

    Args:
        role_id: Role ID to retrieve
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        RoleResponse with role data
    """
    extra = {
        "operation": "get_role",
        "role_id": role_id,
        "current_user": current_user.email
    }

    logger.info(f"Getting role: {role_id}", extra=extra)

    try:
        query = GetRoleQuery(role_id=role_id)
        role = await query_handler.handle_get_role(query)

        if not role:
            raise HTTPException(status_code=404, detail=f"Role not found: {role_id}")

        return RoleResponse(
            success=True,
            message="Role retrieved successfully",
            data=role_to_data(role)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to get role: {str(e)}")


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update Role",
    description="Update an existing role."
)
async def update_role(
    role_id: str = Path(..., description="Role ID to update"),
    role_request: RoleUpdateRequest = ...,
    command_handler: RoleCommandHandler = Depends(get_role_command_handler),
    current_user: User = RequireAuth
) -> RoleResponse:
    """
    Update a role.

    Args:
        role_id: Role ID to update
        role_request: Role update request
        command_handler: Command handler dependency
        current_user: Current authenticated user

    Returns:
        RoleResponse with updated role data
    """
    extra = {
        "operation": "update_role",
        "role_id": role_id,
        "current_user": current_user.email
    }

    logger.info(f"Updating role: {role_id}", extra=extra)

    try:
        # Create command
        command = UpdateRoleCommand(
            role_id=role_id,
            name=role_request.name,
            description=role_request.description,
            permissions=role_request.permissions,
            inherits=role_request.inherits,
            active=role_request.active,
            modified_by=current_user.email
        )

        # Execute command
        await command_handler.handle_update_role(command)

        # Get the updated role using the query handler dependency
        firestore_client = await get_firestore_client()
        role_repository = RoleFirestoreAdapter(firestore_client)
        query_handler = RoleQueryHandler(role_repository)
        query = GetRoleQuery(role_id=role_id)
        role = await query_handler.handle_get_role(query)

        if not role:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated role")

        return RoleResponse(
            success=True,
            message="Role updated successfully",
            data=role_to_data(role)
        )

    except ValueError as e:
        logger.error(f"Validation error updating role: {str(e)}", extra=extra)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating role: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")


@router.delete(
    "/{role_id}",
    response_model=RoleDeleteResponse,
    summary="Delete Role",
    description="Soft delete a role (sets active=False)."
)
async def delete_role(
    role_id: str = Path(..., description="Role ID to delete"),
    command_handler: RoleCommandHandler = Depends(get_role_command_handler),
    current_user: User = RequireAuth
) -> RoleDeleteResponse:
    """
    Delete a role (soft delete).

    Args:
        role_id: Role ID to delete
        command_handler: Command handler dependency
        current_user: Current authenticated user

    Returns:
        RoleDeleteResponse with deletion confirmation
    """
    extra = {
        "operation": "delete_role",
        "role_id": role_id,
        "current_user": current_user.email
    }

    logger.info(f"Deleting role: {role_id}", extra=extra)

    try:
        # Create command
        command = DeleteRoleCommand(
            role_id=role_id,
            deleted_by=current_user.email
        )

        # Execute command
        await command_handler.handle_delete_role(command)

        return RoleDeleteResponse(
            success=True,
            message="Role deleted successfully",
            deleted_id=role_id
        )

    except ValueError as e:
        logger.error(f"Validation error deleting role: {str(e)}", extra=extra)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting role: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")


@router.get(
    "/{role_id}/permissions",
    response_model=RolePermissionsResponse,
    summary="Get Role Effective Permissions",
    description="Get all effective permissions for a role including inherited ones."
)
async def get_role_permissions(
    role_id: str = Path(..., description="Role ID to get permissions for"),
    query_handler: RoleQueryHandler = Depends(get_role_query_handler),
    current_user: User = RequireAuth
) -> RolePermissionsResponse:
    """
    Get effective permissions for a role.

    Args:
        role_id: Role ID to get permissions for
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        RolePermissionsResponse with effective permissions
    """
    extra = {
        "operation": "get_role_permissions",
        "role_id": role_id,
        "current_user": current_user.email
    }

    logger.info(f"Getting role permissions: {role_id}", extra=extra)

    try:
        query = GetRolePermissionsQuery(role_id=role_id)
        permissions = await query_handler.handle_get_role_permissions(query)

        return RolePermissionsResponse(
            success=True,
            message="Role permissions retrieved successfully",
            role_id=role_id,
            effective_permissions=permissions
        )

    except ValueError as e:
        logger.error(f"Error getting role permissions: {str(e)}", extra=extra)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting role permissions: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to get role permissions: {str(e)}")


@router.get(
    "/{role_id}/dependencies",
    response_model=RoleDependenciesResponse,
    summary="Get Role Dependencies",
    description="Get roles that depend on (inherit from) this role."
)
async def get_role_dependencies(
    role_id: str = Path(..., description="Role ID to check dependencies for"),
    query_handler: RoleQueryHandler = Depends(get_role_query_handler),
    current_user: User = RequireAuth
) -> RoleDependenciesResponse:
    """
    Get roles that depend on this role.

    Args:
        role_id: Role ID to check dependencies for
        query_handler: Query handler dependency
        current_user: Current authenticated user

    Returns:
        RoleDependenciesResponse with dependent roles
    """
    extra = {
        "operation": "get_role_dependencies",
        "role_id": role_id,
        "current_user": current_user.email
    }

    logger.info(f"Getting role dependencies: {role_id}", extra=extra)

    try:
        query = GetRoleDependenciesQuery(role_id=role_id)
        dependent_roles = await query_handler.handle_get_role_dependencies(query)

        return RoleDependenciesResponse(
            success=True,
            message="Role dependencies retrieved successfully",
            role_id=role_id,
            dependent_roles=dependent_roles
        )

    except Exception as e:
        logger.error(f"Error getting role dependencies: {str(e)}", extra={**extra, **exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to get role dependencies: {str(e)}")