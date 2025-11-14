from fastapi import APIRouter, HTTPException, Depends
from kink import inject
from typing import Dict, Any

from contracts.demo_contracts import (
    DemoSubjectResponse,
    DemoSubjectListResponse,
    DemoSubjectDeleteResponse,
    SubjectConfigResponse
)
from contracts.paperglass import PaperglassPort
from models.demo_models import (
    CreateSubjectRequest,
    UpdateSubjectRequest,
    UpdateSubjectConfigRequest
)
from usecases.demo_service import DemoSubjectService
from usecases.demo_commands import (
    CreateDemoSubjectCommand,
    UpdateDemoSubjectCommand,
    DeleteDemoSubjectCommand,
    UpdateSubjectConfigCommand,
    GetDemoSubjectsQuery,
    GetDemoSubjectQuery,
    GetSubjectConfigQuery
)

from dependencies.auth_dependencies import RequireAuth
from models.user import User

router = APIRouter()


@inject
async def get_demo_service() -> DemoSubjectService:
    """Dependency to get demo subject service instance."""
    from infrastructure.bindings import get_demo_subject_service
    return get_demo_subject_service()


@inject
async def get_paperglass_service() -> PaperglassPort:
    """Dependency to get paperglass service instance."""
    from infrastructure.bindings import get_paperglass_service
    return get_paperglass_service()


@router.get("/{app_id}/config", response_model=SubjectConfigResponse)
async def get_subject_config(
    app_id: str,
    service: DemoSubjectService = Depends(get_demo_service),
    current_user: User = RequireAuth
):
    """Get subject configuration for an app"""
    query = GetSubjectConfigQuery(app_id=app_id)
    config = await service.get_subject_config(query)
    
    return SubjectConfigResponse(
        success=True,
        message="Subject configuration retrieved successfully",
        data=config
    )


@router.put("/{app_id}/config", response_model=SubjectConfigResponse)
async def update_subject_config(
    app_id: str,
    config_data: UpdateSubjectConfigRequest,
    service: DemoSubjectService = Depends(get_demo_service),
    current_user: User = RequireAuth
):
    """Update subject configuration for an app"""
    command = UpdateSubjectConfigCommand(app_id=app_id, label=config_data.label)
    config = await service.handle_update_subject_config(command)
    
    return SubjectConfigResponse(
        success=True,
        message="Subject configuration updated successfully",
        data=config
    )


@router.get("/{app_id}/subjects", response_model=DemoSubjectListResponse)
async def list_subjects(
    app_id: str,
    service: DemoSubjectService = Depends(get_demo_service),
    current_user: User = RequireAuth
):
    """List all demo subjects for an app"""
    query = GetDemoSubjectsQuery(app_id=app_id)
    subjects = await service.get_demo_subjects(query)
    
    return DemoSubjectListResponse(
        success=True,
        message="Demo subjects retrieved successfully",
        data=subjects,
        total=len(subjects)
    )


@router.get("/{app_id}/subjects/{subject_id}", response_model=DemoSubjectResponse)
async def get_subject(
    app_id: str,
    subject_id: str,
    service: DemoSubjectService = Depends(get_demo_service),
    current_user: User = RequireAuth
):
    """Get a specific demo subject by ID"""
    query = GetDemoSubjectQuery(app_id=app_id, subject_id=subject_id)
    subject = await service.get_demo_subject(query)
    
    if not subject:
        raise HTTPException(status_code=404, detail="Demo subject not found")
    
    return DemoSubjectResponse(
        success=True,
        message="Demo subject retrieved successfully",
        data=subject
    )


@router.post("/{app_id}/subjects", response_model=DemoSubjectResponse)
async def create_subject(
    app_id: str,
    subject_data: CreateSubjectRequest,
    service: DemoSubjectService = Depends(get_demo_service),
    current_user: User = RequireAuth
):
    """Create a new demo subject"""
    command = CreateDemoSubjectCommand(app_id=app_id, name=subject_data.name)
    
    try:
        created_subject = await service.handle_create_demo_subject(command)
        
        return DemoSubjectResponse(
            success=True,
            message="Demo subject created successfully",
            data=created_subject
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{app_id}/subjects/{subject_id}", response_model=DemoSubjectResponse)
async def update_subject(
    app_id: str,
    subject_id: str,
    subject_data: UpdateSubjectRequest,
    service: DemoSubjectService = Depends(get_demo_service),
    current_user: User = RequireAuth
):
    """Update an existing demo subject"""
    command = UpdateDemoSubjectCommand(app_id=app_id, subject_id=subject_id, name=subject_data.name)
    
    try:
        updated_subject = await service.handle_update_demo_subject(command)
        
        return DemoSubjectResponse(
            success=True,
            message="Demo subject updated successfully",
            data=updated_subject
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{app_id}/subjects/{subject_id}", response_model=DemoSubjectDeleteResponse)
async def delete_subject(
    app_id: str,
    subject_id: str,
    service: DemoSubjectService = Depends(get_demo_service),
    current_user: User = RequireAuth
):
    """Soft delete a demo subject"""
    command = DeleteDemoSubjectCommand(app_id=app_id, subject_id=subject_id)
    
    deleted = await service.handle_delete_demo_subject(command)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Demo subject not found")
    
    return DemoSubjectDeleteResponse(
        success=True,
        message="Demo subject deleted successfully",
        deleted_id=subject_id
    )


@router.get("/{app_id}/subjects/{subject_id}/documents/{document_id}/status")
async def get_document_status(
    app_id: str,
    subject_id: str,
    document_id: str,
    paperglass_service: PaperglassPort = Depends(get_paperglass_service)
) -> Dict[str, Any]:
    """Get document processing status from PaperGlass API"""
    try:
        status = await paperglass_service.get_document_status(
            document_id=document_id,
            app_id=app_id,
            tenant_id="admin-experiment",  # Use admin-experiment to match document submission
            patient_id=subject_id
        )

        # No status translation needed - use Paperglass status values directly
        # Admin API now standardized on Paperglass status format: NOT_STARTED, QUEUED, IN_PROGRESS, COMPLETED, FAILED

        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document status: {str(e)}")


@router.post("/internal/status-change-callback/{run_id}")
async def status_change_callback(run_id: str) -> Dict[str, Any]:
    """Callback endpoint for status changes from DJT"""
    # For now, just acknowledge the callback
    # In the future, this could update document status in Firestore
    return {"success": True, "run_id": run_id, "message": "Status change callback received"}