"""
App Config Router for Admin API

This router provides endpoints for retrieving application configurations.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from pydantic import BaseModel
from viki_shared.utils.logger import getLogger
from viki_shared.utils.exceptions import exceptionToMap
from viki_shared.models.common import PaginationInfo

from contracts.paperglass import AppConfigResponse, AppConfigUpdateRequest, PaperglassPort
from adapters.paperglass_adapter import PaperglassAdapter
from settings import Settings, get_settings
from dependencies.auth_dependencies import RequireAuth
from models.user import User
from application.profile_resolver import ProfileResolver
from infrastructure.bindings import get_profile_resolver
from services.app_access_service import get_app_access_service

logger = getLogger(__name__)

router = APIRouter()


class AppConfigApiResponse(BaseModel):
    """API response wrapper for app config."""
    success: bool
    message: str
    data: AppConfigResponse = None


class AppConfigListApiResponse(BaseModel):
    """API response wrapper for list of app configs."""
    success: bool
    message: str
    data: List[AppConfigResponse] = []
    pagination: PaginationInfo


async def get_paperglass_adapter(settings: Settings = Depends(get_settings)) -> PaperglassAdapter:
    """Dependency to get Paperglass adapter instance."""
    return PaperglassAdapter(settings)


@router.get(
    "/app/{app_id}",
    response_model=AppConfigApiResponse,
    summary="Get App Configuration",
    description="Retrieve application configuration for the specified app_id from Paperglass API."
)
async def get_app_config(
    app_id: str = Path(..., description="Application identifier"),
    generate_if_missing: bool = Query(False, description="Generate default config if not found"),
    paperglass_adapter: PaperglassAdapter = Depends(get_paperglass_adapter),
    current_user: User = RequireAuth
) -> AppConfigApiResponse:
    """
    Get app configuration for the given app_id.
    
    This endpoint retrieves the application configuration from the Paperglass API
    which contains all the settings and parameters needed for the application.
    
    Args:
        app_id: The unique identifier of the application
        
    Returns:
        AppConfigApiResponse containing the configuration data
        
    Raises:
        HTTPException: If app not found (404) or error retrieving config (500)
    """
    extra = {
        "operation": "get_app_config",
        "app_id": app_id,
        "endpoint": "/api/v1/config/app/{app_id}"
    }
    
    try:
        logger.debug(f"Retrieving app config for app_id: {app_id}", extra=extra)
        
        # Get app config from Paperglass API
        app_config = await paperglass_adapter.get_app_config(app_id, generate_if_missing)
        
        if app_config is None:
            extra["config_found"] = False
            logger.warning(f"App config not found for app_id: {app_id}", extra=extra)
            
            raise HTTPException(
                status_code=404,
                detail=f"App configuration not found for app_id: {app_id}"
            )
        
        extra.update({
            "config_found": True,
            "config_active": app_config.active,
            "config_created_at": app_config.created_at.isoformat() if app_config.created_at else None
        })
        
        logger.debug(f"Successfully retrieved app config for app_id: {app_id}", extra=extra)
        
        return AppConfigApiResponse(
            success=True,
            message="App configuration retrieved successfully",
            data=app_config
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error retrieving app config for app_id {app_id}: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error based on the error type
        if "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Paperglass API unavailable: {str(e)}"
            )
        elif "Paperglass API error" in str(e):
            raise HTTPException(
                status_code=502,
                detail=f"Failed to retrieve config from Paperglass API: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error retrieving app config: {str(e)}"
            )


@router.get(
    "/apps",
    response_model=AppConfigListApiResponse,
    summary="List App Configurations",
    description="Retrieve all application configurations from Paperglass API with pagination support."
)
async def list_app_configs(
    limit: int = Query(50, ge=1, le=250, description="Maximum number of configs to return (1-250)"),
    offset: int = Query(0, ge=0, description="Number of configs to skip for pagination"),
    paperglass_adapter: PaperglassAdapter = Depends(get_paperglass_adapter),
    profile_resolver: ProfileResolver = Depends(get_profile_resolver),
    current_user: User = RequireAuth
) -> AppConfigListApiResponse:
    """
    List all app configurations with pagination.
    
    This endpoint retrieves all application configurations from the Paperglass API
    with support for pagination to handle large numbers of configurations.
    
    Args:
        limit: Maximum number of configurations to return (default: 50, max: 250)
        offset: Number of configurations to skip (default: 0)
        
    Returns:
        AppConfigListApiResponse containing the list of configuration data
        
    Raises:
        HTTPException: If error retrieving configs (500/503)
    """
    extra = {
        "operation": "list_app_configs",
        "limit": limit,
        "offset": offset,
        "endpoint": "/api/v1/config/apps"
    }
    
    try:
        logger.debug(f"Listing app configs with limit: {limit}, offset: {offset}", extra=extra)

        # Resolve current user profile for access filtering
        user_profile = await profile_resolver.resolve_current_user_profile()

        # Get app configs list from Paperglass API (get more than needed to account for filtering)
        # We'll fetch a larger batch and then apply filtering and pagination
        fetch_limit = min(250, limit * 3)  # Fetch up to 3x requested to account for filtering
        app_configs = await paperglass_adapter.list_app_configs(fetch_limit, 0)

        # Apply user access filtering
        access_service = get_app_access_service()
        filtered_app_configs = access_service.filter_apps_by_user_access(app_configs, user_profile)

        # Apply pagination to filtered results
        paginated_configs = filtered_app_configs[offset:offset + limit]

        extra.update({
            "raw_configs_found": len(app_configs),
            "filtered_configs_count": len(filtered_app_configs),
            "paginated_configs_returned": len(paginated_configs),
            "user_profile_id": user_profile.id if user_profile else None,
            "user_organizations_count": len(user_profile.organizations) if user_profile else 0
        })

        logger.debug(
            f"Retrieved {len(app_configs)} raw configs, filtered to {len(filtered_app_configs)}, "
            f"returning {len(paginated_configs)} for pagination",
            extra=extra
        )
        
        return AppConfigListApiResponse(
            success=True,
            message=f"Successfully retrieved {len(paginated_configs)} app configurations (filtered from {len(app_configs)} total)",
            data=paginated_configs,
            pagination=PaginationInfo(
                limit=limit,
                offset=offset,
                returned=len(paginated_configs),
                has_more=offset + len(paginated_configs) < len(filtered_app_configs)  # More if we haven't reached end of filtered results
            )
        )
        
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error listing app configs: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error based on the error type
        if "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Paperglass API unavailable: {str(e)}"
            )
        elif "Paperglass API error" in str(e):
            raise HTTPException(
                status_code=502,
                detail=f"Failed to retrieve configs from Paperglass API: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error listing app configs: {str(e)}"
            )


@router.put(
    "/app/{app_id}",
    response_model=AppConfigApiResponse,
    summary="Update App Configuration",
    description="Update application configuration for the specified app_id in Paperglass API with version management and archiving."
)
async def update_app_config(
    app_id: str = Path(..., description="Application identifier"),
    config_update: AppConfigUpdateRequest = ...,
    paperglass_adapter: PaperglassAdapter = Depends(get_paperglass_adapter),
    current_user: User = RequireAuth
) -> AppConfigApiResponse:
    """
    Update app configuration for the given app_id.
    
    This endpoint updates the application configuration in the Paperglass API.
    It supports versioning and archiving of the current configuration before applying updates.
    
    Args:
        app_id: The unique identifier of the application
        config_update: The configuration update request containing new config data
        
    Returns:
        AppConfigApiResponse containing the updated configuration data
        
    Raises:
        HTTPException: If app not found (404) or error updating config (500)
    """
    extra = {
        "operation": "update_app_config",
        "app_id": app_id,
        "archive_current": config_update.archive_current,
        "endpoint": "/api/v1/config/app/{app_id}"
    }
    
    try:
        logger.debug(f"Updating app config for app_id: {app_id}", extra=extra)
        
        # Update app config via Paperglass API
        updated_app_config = await paperglass_adapter.update_app_config(app_id, config_update)
        
        extra.update({
            "config_updated": True,
            "config_active": updated_app_config.active,
            "config_modified_at": updated_app_config.modified_at.isoformat() if updated_app_config.modified_at else None
        })
        
        logger.debug(f"Successfully updated app config for app_id: {app_id}", extra=extra)
        
        return AppConfigApiResponse(
            success=True,
            message="App configuration updated successfully",
            data=updated_app_config
        )
        
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        logger.error(f"Error updating app config for app_id {app_id}: {str(e)}", extra=extra)
        
        # Return appropriate HTTP error based on the error type
        if "not found" in str(e).lower() or "404" in str(e):
            raise HTTPException(
                status_code=404,
                detail=f"App configuration not found for app_id: {app_id}"
            )
        elif "Failed to connect" in str(e):
            raise HTTPException(
                status_code=503,
                detail=f"Paperglass API unavailable: {str(e)}"
            )
        elif "Paperglass API error" in str(e):
            raise HTTPException(
                status_code=502,
                detail=f"Failed to update config in Paperglass API: {str(e)}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal error updating app config: {str(e)}"
            )