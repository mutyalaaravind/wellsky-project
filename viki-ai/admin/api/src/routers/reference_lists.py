"""
Reference Lists Router for Admin API

This router provides endpoints for fetching reference data like business units and solutions.
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from viki_shared.utils.logger import getLogger
from viki_shared.utils.exceptions import exceptionToMap
from google.cloud.firestore import AsyncClient

from settings import Settings, get_settings
from infrastructure.adapters.reference_lists_firestore_adapter import ReferenceListsFirestoreAdapter
from application.commands.reference_lists_commands import (
    ReferenceListsCommandHandler,
    UpdateBusinessUnitsCommand,
    UpdateSolutionsCommand
)
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = getLogger(__name__)

router = APIRouter()


# Request Models
class BusinessUnitRequest(BaseModel):
    """Request model for business unit data."""
    bu_code: str = Field(..., description="Business unit code")
    name: str = Field(..., description="Business unit name")


class SolutionRequest(BaseModel):
    """Request model for solution data."""
    solution_id: str = Field(..., description="Unique solution identifier")
    code: str = Field(..., description="Solution code")
    name: str = Field(..., description="Solution name")
    description: Optional[str] = Field(None, description="Solution description")
    bu_code: str = Field(..., description="Associated business unit code")


class BusinessUnitsUpdateRequest(BaseModel):
    """Request model for updating business units list."""
    business_units: List[BusinessUnitRequest] = Field(..., description="List of business units to update")


class SolutionsUpdateRequest(BaseModel):
    """Request model for updating solutions list."""
    solutions: List[SolutionRequest] = Field(..., description="List of solutions to update")


# Response Models
class BusinessUnitResponse(BaseModel):
    """Response model for business unit data."""
    bu_code: str = Field(..., description="Business unit code")
    name: str = Field(..., description="Business unit name")


class SolutionResponse(BaseModel):
    """Response model for solution data."""
    solution_id: str = Field(..., description="Unique solution identifier")
    code: str = Field(..., description="Solution code")
    name: str = Field(..., description="Solution name")
    description: Optional[str] = Field(None, description="Solution description")
    bu_code: str = Field(..., description="Associated business unit code")


class BusinessUnitsListResponse(BaseModel):
    """Response model for business units list."""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field(default="Business units retrieved successfully")
    data: List[BusinessUnitResponse] = Field(..., description="List of business units")


class SolutionsListResponse(BaseModel):
    """Response model for solutions list."""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field(default="Solutions retrieved successfully")
    data: List[SolutionResponse] = Field(..., description="List of solutions")


class AllReferenceDataResponse(BaseModel):
    """Response model for all reference data."""
    success: bool = Field(True, description="Whether the request was successful")
    message: str = Field(default="Reference data retrieved successfully")
    data: Dict[str, Any] = Field(..., description="All reference data")


class UpdateResponse(BaseModel):
    """Response model for update operations."""
    success: bool = Field(True, description="Whether the update was successful")
    message: str = Field(..., description="Update operation result message")


# Dependency to get Firestore client
async def get_firestore_client(settings: Settings = Depends(get_settings)) -> AsyncClient:
    """Get Firestore client."""
    # Use default database for emulator, specific database for production
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        return AsyncClient()  # Use default database in emulator
    else:
        return AsyncClient(database=settings.GCP_FIRESTORE_DB)


async def get_reference_adapter(client: AsyncClient = Depends(get_firestore_client)) -> ReferenceListsFirestoreAdapter:
    """Get reference lists adapter."""
    return ReferenceListsFirestoreAdapter(client)


async def get_reference_command_handler(adapter: ReferenceListsFirestoreAdapter = Depends(get_reference_adapter)) -> ReferenceListsCommandHandler:
    """Get reference lists command handler."""
    return ReferenceListsCommandHandler(adapter)


@router.get(
    "/business-units",
    response_model=BusinessUnitsListResponse,
    summary="Get Business Units",
    description="Retrieve all available business units"
)
async def get_business_units(
    current_user: User = RequireAuth,
    adapter: ReferenceListsFirestoreAdapter = Depends(get_reference_adapter)
) -> BusinessUnitsListResponse:
    """
    Get all business units from the reference lists.

    Returns a list of business units with their codes and names.
    """
    try:
        logger.info(f"Getting business units for user: {current_user.email if current_user else 'unknown'}")

        business_units = await adapter.get_business_units()

        response_data = [
            BusinessUnitResponse(
                bu_code=bu.bu_code,
                name=bu.name
            ) for bu in business_units
        ]

        return BusinessUnitsListResponse(
            success=True,
            message=f"Retrieved {len(response_data)} business units",
            data=response_data
        )

    except Exception as e:
        logger.error(f"Error getting business units: {str(e)}")
        error_map = exceptionToMap(e)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to retrieve business units: {error_map.get('message', 'Unknown error')}",
                "error": error_map
            }
        )


@router.get(
    "/solutions",
    response_model=SolutionsListResponse,
    summary="Get Solutions",
    description="Retrieve all solutions, optionally filtered by business unit"
)
async def get_solutions(
    bu_code: Optional[str] = Query(None, description="Filter solutions by business unit code"),
    current_user: User = RequireAuth,
    adapter: ReferenceListsFirestoreAdapter = Depends(get_reference_adapter)
) -> SolutionsListResponse:
    """
    Get solutions from the reference lists.

    Optionally filter by business unit code to get solutions for a specific business unit.
    """
    try:
        logger.info(f"Getting solutions (bu_code: {bu_code}) for user: {current_user.email if current_user else 'unknown'}")

        solutions = await adapter.get_solutions(bu_code=bu_code)

        response_data = [
            SolutionResponse(
                solution_id=sol.solution_id,
                code=sol.code,
                name=sol.name,
                description=sol.description,
                bu_code=sol.bu_code
            ) for sol in solutions
        ]

        message = f"Retrieved {len(response_data)} solutions"
        if bu_code:
            message += f" for business unit '{bu_code}'"

        return SolutionsListResponse(
            success=True,
            message=message,
            data=response_data
        )

    except Exception as e:
        logger.error(f"Error getting solutions: {str(e)}")
        error_map = exceptionToMap(e)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to retrieve solutions: {error_map.get('message', 'Unknown error')}",
                "error": error_map
            }
        )


@router.get(
    "/solutions/{bu_code}",
    response_model=SolutionsListResponse,
    summary="Get Solutions by Business Unit",
    description="Retrieve solutions for a specific business unit"
)
async def get_solutions_by_business_unit(
    bu_code: str = Path(..., description="Business unit code"),
    current_user: User = RequireAuth,
    adapter: ReferenceListsFirestoreAdapter = Depends(get_reference_adapter)
) -> SolutionsListResponse:
    """
    Get solutions for a specific business unit.
    """
    try:
        logger.info(f"Getting solutions for bu_code: {bu_code} for user: {current_user.email if current_user else 'unknown'}")

        solutions = await adapter.get_solutions(bu_code=bu_code)

        response_data = [
            SolutionResponse(
                solution_id=sol.solution_id,
                code=sol.code,
                name=sol.name,
                description=sol.description,
                bu_code=sol.bu_code
            ) for sol in solutions
        ]

        return SolutionsListResponse(
            success=True,
            message=f"Retrieved {len(response_data)} solutions for business unit '{bu_code}'",
            data=response_data
        )

    except Exception as e:
        logger.error(f"Error getting solutions for bu_code {bu_code}: {str(e)}")
        error_map = exceptionToMap(e)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to retrieve solutions for business unit '{bu_code}': {error_map.get('message', 'Unknown error')}",
                "error": error_map
            }
        )


@router.get(
    "/all",
    response_model=AllReferenceDataResponse,
    summary="Get All Reference Data",
    description="Retrieve all reference lists data (business units and solutions) in one call"
)
async def get_all_reference_data(
    current_user: User = RequireAuth,
    adapter: ReferenceListsFirestoreAdapter = Depends(get_reference_adapter)
) -> AllReferenceDataResponse:
    """
    Get all reference data in a single call.

    Returns both business units and solutions.
    """
    try:
        logger.info(f"Getting all reference data for user: {current_user.email if current_user else 'unknown'}")

        reference_data = await adapter.get_all_reference_data()

        response_data = {
            "business_units": [
                {
                    "bu_code": bu.bu_code,
                    "name": bu.name
                } for bu in reference_data.business_units
            ],
            "solutions": [
                {
                    "solution_id": sol.solution_id,
                    "code": sol.code,
                    "name": sol.name,
                    "description": sol.description,
                    "bu_code": sol.bu_code
                } for sol in reference_data.solutions
            ]
        }

        total_items = len(reference_data.business_units) + len(reference_data.solutions)

        return AllReferenceDataResponse(
            success=True,
            message=f"Retrieved all reference data ({len(reference_data.business_units)} business units, {len(reference_data.solutions)} solutions)",
            data=response_data
        )

    except Exception as e:
        logger.error(f"Error getting all reference data: {str(e)}")
        error_map = exceptionToMap(e)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to retrieve reference data: {error_map.get('message', 'Unknown error')}",
                "error": error_map
            }
        )


@router.put(
    "/business-units",
    response_model=UpdateResponse,
    summary="Update Business Units",
    description="Update the complete list of business units"
)
async def update_business_units(
    request: BusinessUnitsUpdateRequest,
    current_user: User = RequireAuth,
    command_handler: ReferenceListsCommandHandler = Depends(get_reference_command_handler)
) -> UpdateResponse:
    """
    Update business units list.

    Replaces the entire business units list with the provided data.
    """
    try:
        logger.info(f"Updating {len(request.business_units)} business units for user: {current_user.email if current_user else 'unknown'}")

        # Convert request models to domain models
        from domain.models.reference_lists import BusinessUnit
        business_units = [
            BusinessUnit(
                bu_code=bu.bu_code,
                name=bu.name
            ) for bu in request.business_units
        ]

        # Create and execute command
        command = UpdateBusinessUnitsCommand(
            business_units=business_units,
            updated_by=current_user.email if current_user else "system"
        )

        success = await command_handler.handle_update_business_units(command)

        return UpdateResponse(
            success=True,
            message=f"Successfully updated {len(business_units)} business units"
        )

    except ValueError as ve:
        logger.warning(f"Validation error updating business units: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": f"Validation error: {str(ve)}"
            }
        )
    except Exception as e:
        logger.error(f"Error updating business units: {str(e)}")
        error_map = exceptionToMap(e)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to update business units: {error_map.get('message', 'Unknown error')}",
                "error": error_map
            }
        )


@router.put(
    "/solutions",
    response_model=UpdateResponse,
    summary="Update Solutions",
    description="Update the complete list of solutions"
)
async def update_solutions(
    request: SolutionsUpdateRequest,
    current_user: User = RequireAuth,
    command_handler: ReferenceListsCommandHandler = Depends(get_reference_command_handler)
) -> UpdateResponse:
    """
    Update solutions list.

    Replaces the entire solutions list with the provided data.
    """
    try:
        logger.info(f"Updating {len(request.solutions)} solutions for user: {current_user.email if current_user else 'unknown'}")

        # Convert request models to domain models
        from domain.models.reference_lists import Solution
        solutions = [
            Solution(
                solution_id=sol.solution_id,
                code=sol.code,
                name=sol.name,
                description=sol.description,
                bu_code=sol.bu_code
            ) for sol in request.solutions
        ]

        # Create and execute command
        command = UpdateSolutionsCommand(
            solutions=solutions,
            updated_by=current_user.email if current_user else "system"
        )

        success = await command_handler.handle_update_solutions(command)

        return UpdateResponse(
            success=True,
            message=f"Successfully updated {len(solutions)} solutions"
        )

    except ValueError as ve:
        logger.warning(f"Validation error updating solutions: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": f"Validation error: {str(ve)}"
            }
        )
    except Exception as e:
        logger.error(f"Error updating solutions: {str(e)}")
        error_map = exceptionToMap(e)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to update solutions: {error_map.get('message', 'Unknown error')}",
                "error": error_map
            }
        )