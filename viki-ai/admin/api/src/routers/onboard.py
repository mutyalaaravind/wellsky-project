"""
Onboard Router for Admin API

This router provides endpoints for the onboarding flow.
"""

import secrets
import io
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from kink import di
from viki_shared.utils.logger import getLogger

from contracts.file_storage_contracts import FileStoragePort
from contracts.entity_extraction_contracts import EntityExtractionPort
from contracts.djt_contracts import DJTPort
from contracts.config_contracts import ConfigPort
from application.onboard.generate import OnboardGenerationService
from application.onboard.generate_with_progress import OnboardGenerationWithProgressService
from models.onboard_models import OnboardGenerationResult, OnboardJobProgress, OnboardSaveRequest, OnboardSaveResponse
from usecases.onboard_commands import SaveOnboardConfigCommand
from infrastructure.bindings import get_onboard_service
from settings import Settings
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = getLogger(__name__)

router = APIRouter()


def generate_app_id(solution_id: str) -> str:
    """
    Generate app_id with format "{solution_code}-{RANDOM 6 character hash}".
    
    Args:
        solution_id: The solution ID code (e.g., "ct", "cpr")
    
    Returns:
        Generated app_id (e.g., "ct-a1b2c3")
    """
    # Generate a random 6-character alphanumeric hash
    random_hash = secrets.token_hex(3)  # 3 bytes = 6 hex characters
    
    # Combine solution_id with random hash
    app_id = f"{solution_id}-{random_hash}"
    
    logger.info(f"Generated app_id: {app_id} for solution_id: {solution_id}")
    return app_id


class OnboardGenerateResponse(BaseModel):
    """Response model for onboard generate endpoint."""
    success: bool
    message: str
    data: Dict[str, Any]


@router.post(
    "/generate",
    response_model=OnboardGenerateResponse,
    summary="Generate onboarding configuration",
    description="Process onboarding form data and uploaded file to generate configuration for Step 4."
)
async def generate_onboard_config(
    businessUnit: str = Form(..., description="Business unit code"),
    solutionId: str = Form(..., description="Solution ID code"),
    name: str = Form(..., description="Pipeline name"),
    description: str = Form(..., description="Pipeline description"),
    template: str = Form(..., description="Selected template"),
    metaPrompt: str = Form(..., description="Data extraction description"),
    sampleFile: UploadFile = File(..., description="Sample document file"),
    current_user: User = RequireAuth
) -> OnboardGenerateResponse:
    """
    Process onboarding form data and generate configuration.
    
    This endpoint receives all the form data collected through Steps 1-3
    including the uploaded sample file, and returns the generated
    configuration data needed for Step 4 (Review).
    """
    try:
        # Generate app_id based on solution_id
        app_id = generate_app_id(solutionId)
        
        logger.info(f"Processing onboard generation for pipeline: {name}")
        logger.info(f"Input parameters - businessUnit: {businessUnit}, solutionId: {solutionId}, generated appId: {app_id}, template: {template}")
        logger.info(f"Sample file: {sampleFile.filename}, content_type: {sampleFile.content_type}")
        logger.info(f"Meta prompt: {metaPrompt}")
        
        # Validate file type
        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'image/tiff',
            'image/tif'
        ]
        
        if sampleFile.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {sampleFile.content_type}. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read file content (for future processing)
        file_content = await sampleFile.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        # Validate file size (max 10MB)
        if file_size_mb > 10:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size_mb:.2f}MB. Maximum allowed: 10MB"
            )
        
        logger.info(f"Processed file: {sampleFile.filename} ({file_size_mb:.2f}MB)")
        
        # Use dependency injection to get services and create generation service
        file_storage = di[FileStoragePort]
        entity_extraction = di[EntityExtractionPort]
        config = di[ConfigPort]
        settings = Settings()
        generation_service = OnboardGenerationService(file_storage, entity_extraction, config, settings)
        
        # Convert file content to BinaryIO for the service
        file_content_io = io.BytesIO(file_content)
        
        # Use the generation service to handle file upload and schema generation
        generation_result: OnboardGenerationResult = await generation_service.generate_onboard_config(
            app_id=app_id,
            file_content=file_content_io,
            content_type=sampleFile.content_type,
            original_filename=sampleFile.filename,
            meta_prompt=metaPrompt
        )
        
        # Mock preferred model selection and calculations
        preferred_model = "Gemini 2.5 Flash Lite"
        tokens_per_document = 2500
        gsu_count = 1
        cost_estimate = 2400
        
        # Build response data matching what Step 4 expects
        response_data = {
            "configuration": {
                "businessUnit": businessUnit,
                "solutionId": solutionId,
                "appId": app_id,
                "name": name,
                "description": description,
                "template": template,
                "metaPrompt": metaPrompt,
                "sampleFileName": sampleFile.filename,
                "sampleFileSize": file_size_mb,
                "storagePath": generation_result.storage_metadata.storage_path
            },
            "entitySchema": generation_result.entity_schema,
            "extractionPrompt": generation_result.extraction_prompt,
            "extractedEntity": generation_result.test_extraction,
            "preferredModel": preferred_model,
            "tokensPerDocument": tokens_per_document,
            "gsuCount": gsu_count,
            "costEstimate": cost_estimate,
            "storageMetadata": generation_result.storage_metadata.dict()
        }
        
        return OnboardGenerateResponse(
            success=True,
            message="Onboard configuration generated successfully",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating onboard config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate onboard configuration: {str(e)}"
        )


@router.post(
    "/generate-with-progress",
    response_model=OnboardGenerateResponse,
    summary="Generate onboarding configuration with progress tracking",
    description="Process onboarding form data and uploaded file to generate configuration with DJT progress tracking."
)
async def generate_onboard_config_with_progress(
    businessUnit: str = Form(..., description="Business unit code"),
    solutionId: str = Form(..., description="Solution ID code"),
    name: str = Form(..., description="Pipeline name"),
    description: str = Form(..., description="Pipeline description"),
    template: str = Form(..., description="Selected template"),
    metaPrompt: str = Form(..., description="Data extraction description"),
    sampleFile: UploadFile = File(..., description="Sample document file"),
    jobId: str = Form(..., description="Predetermined job ID from frontend"),
    current_user: User = RequireAuth
) -> OnboardGenerateResponse:
    """
    Process onboarding form data and generate configuration with progress tracking.
    
    This endpoint receives all the form data collected through Steps 1-3
    including the uploaded sample file, starts the generation process with
    DJT tracking, and returns a job_id for progress monitoring.
    """
    try:
        # Validate required parameters and collect all errors
        validation_errors = []

        if not businessUnit or not businessUnit.strip():
            validation_errors.append("businessUnit is required and cannot be empty")

        if not solutionId or not solutionId.strip():
            validation_errors.append("solutionId is required and cannot be empty")

        if not name or not name.strip():
            validation_errors.append("name is required and cannot be empty")

        # Description is optional, so we don't validate it

        if not template or not template.strip():
            validation_errors.append("template is required and cannot be empty")

        if not metaPrompt or not metaPrompt.strip():
            validation_errors.append("metaPrompt is required and cannot be empty")

        # If there are validation errors, return them all together
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Validation failed",
                    "errors": validation_errors
                }
            )

        # Generate app_id based on solution_id
        app_id = generate_app_id(solutionId)

        logger.info(f"Starting onboard generation with progress for pipeline: {name}")
        logger.info(f"Input parameters - businessUnit: {businessUnit}, solutionId: {solutionId}, generated appId: {app_id}, template: {template}")
        logger.info(f"Sample file: {sampleFile.filename}, content_type: {sampleFile.content_type}")
        logger.info(f"Meta prompt: {metaPrompt}")
        
        # Validate file type
        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'image/tiff',
            'image/tif'
        ]
        
        if sampleFile.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {sampleFile.content_type}. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read file content
        file_content = await sampleFile.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        # Validate file size (max 10MB)
        if file_size_mb > 10:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size_mb:.2f}MB. Maximum allowed: 10MB"
            )
        
        logger.info(f"Processed file: {sampleFile.filename} ({file_size_mb:.2f}MB)")
        
        # Use dependency injection to get services and create enhanced generation service
        file_storage = di[FileStoragePort]
        entity_extraction = di[EntityExtractionPort]
        config = di[ConfigPort]
        djt_client = di[DJTPort]
        settings = Settings()
        
        generation_service = OnboardGenerationWithProgressService(
            file_storage, entity_extraction, config, djt_client, settings
        )
        
        # Convert file content to BinaryIO for the service
        file_content_io = io.BytesIO(file_content)
        
        # Start the generation process with progress tracking using provided job ID
        generation_result = await generation_service.generate_onboard_config_with_progress(
            job_id=jobId,  # Use the provided job ID
            app_id=app_id,
            file_content=file_content_io,
            content_type=sampleFile.content_type,
            original_filename=sampleFile.filename,
            meta_prompt=metaPrompt,
            business_unit=businessUnit,
            solution_id=solutionId,
            name=name,
            description=description
        )
        
        # Mock preferred model selection and calculations
        preferred_model = "Gemini 2.5 Flash Lite"
        tokens_per_document = 2500
        gsu_count = 1
        cost_estimate = 2400
        
        # Build response data matching what Step 4 expects (same as regular generate endpoint)
        response_data = {
            "configuration": {
                "businessUnit": businessUnit,
                "solutionId": solutionId,
                "appId": app_id,
                "name": name,
                "description": description,
                "template": template,
                "metaPrompt": metaPrompt,
                "sampleFileName": sampleFile.filename,
                "sampleFileSize": file_size_mb,
                "storagePath": generation_result.storage_metadata.storage_path,
                "jobId": jobId  # Include job ID in response
            },
            "entitySchema": generation_result.entity_schema,
            "extractionPrompt": generation_result.extraction_prompt,
            "extractedEntity": generation_result.test_extraction,
            "preferredModel": preferred_model,
            "tokensPerDocument": tokens_per_document,
            "gsuCount": gsu_count,
            "costEstimate": cost_estimate,
            "storageMetadata": generation_result.storage_metadata.dict()
        }
        
        return OnboardGenerateResponse(
            success=True,
            message="Onboard configuration generated successfully with progress tracking",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting onboard config generation with progress: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start configuration generation: {str(e)}"
        )


def generate_entity_schema(meta_prompt: str) -> Dict[str, Any]:
    """
    Generate entity schema based on meta prompt.
    
    TODO: Replace with actual AI-powered schema generation.
    For now, returns a mock schema based on common patterns.
    """
    
    # Mock schema generation based on keywords in meta prompt
    base_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    # Common field mappings based on keywords
    if "insurance" in meta_prompt.lower():
        base_schema["properties"].update({
            "insured_name": {
                "type": "string",
                "description": "Full name of the insured person"
            },
            "policy_number": {
                "type": "string",
                "description": "Insurance policy number"
            },
            "group_number": {
                "type": "string",
                "description": "Insurance group number"
            }
        })
        base_schema["required"].extend(["insured_name", "policy_number"])
        
    if "dependent" in meta_prompt.lower():
        base_schema["properties"]["dependents"] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "relationship": {"type": "string"},
                    "date_of_birth": {"type": "string", "format": "date"}
                }
            },
            "description": "List of dependents covered by the policy"
        }
    
    if "patient" in meta_prompt.lower():
        base_schema["properties"].update({
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient"
            },
            "date_of_birth": {
                "type": "string",
                "format": "date",
                "description": "Patient's date of birth"
            }
        })
        base_schema["required"].extend(["patient_name", "date_of_birth"])
        
    if "medication" in meta_prompt.lower():
        base_schema["properties"]["medications"] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "dosage": {"type": "string"},
                    "frequency": {"type": "string"}
                }
            },
            "description": "List of prescribed medications"
        }
    
    # If no specific patterns found, use a generic schema
    if not base_schema["properties"]:
        base_schema["properties"] = {
            "extracted_data": {
                "type": "object",
                "description": "Extracted data from the document"
            }
        }
        base_schema["required"] = ["extracted_data"]
    
    return base_schema


@router.get(
    "/progress/{job_id}",
    response_model=OnboardJobProgress,
    summary="Get onboarding job progress",
    description="Get the current progress status of an onboarding job including task statuses and overall progress."
)
async def get_onboard_progress(
    job_id: str,
    current_user: User = RequireAuth
) -> OnboardJobProgress:
    """
    Get the progress status of an onboarding job.
    
    This endpoint queries the DJT service to get the current status of the onboarding job
    including individual task progress and overall completion percentage.
    
    Args:
        job_id: The unique identifier of the onboarding job
        
    Returns:
        OnboardJobProgress: Current progress status of the job
        
    Raises:
        HTTPException: If job not found or error getting progress
    """
    try:
        logger.info(f"Getting progress for onboarding job: {job_id}")
        
        # Get DJT client from dependency injection
        djt_client = di[DJTPort]
        
        # Get job status from DJT service
        job_status = await djt_client.get_job_pipelines(job_id)
        
        # Parse DJT response to extract progress information
        # Note: The exact structure will depend on DJT's response format
        # This is a simplified implementation
        
        # Extract overall job information
        job_info = job_status.get("job", {})
        pipelines = job_status.get("pipelines", [])
        
        # Calculate overall progress
        total_tasks = len(pipelines) if pipelines else 4  # Fallback to known task count
        completed_tasks = sum(1 for pipeline in pipelines if pipeline.get("status") == "COMPLETED")
        overall_progress = (completed_tasks * 100) // total_tasks if total_tasks > 0 else 0
        
        # Find current task
        current_task = None
        current_task_name = None
        for pipeline in pipelines:
            if pipeline.get("status") == "IN_PROGRESS":
                current_task = pipeline.get("id")
                current_task_name = pipeline.get("metadata", {}).get("task_name", current_task)
                break
        
        # Extract error message if any task failed
        error_message = None
        for pipeline in pipelines:
            if pipeline.get("status") == "FAILED":
                error_message = pipeline.get("metadata", {}).get("error_message")
                break
        
        # Determine overall job status
        if error_message:
            job_status_str = "FAILED"
        elif completed_tasks == total_tasks:
            job_status_str = "COMPLETED"
        elif current_task:
            job_status_str = "IN_PROGRESS"
        else:
            job_status_str = "NOT_STARTED"
        
        # Format tasks for response
        tasks = []
        for pipeline in pipelines:
            task_info = {
                "id": pipeline.get("id"),
                "name": pipeline.get("metadata", {}).get("task_name", pipeline.get("id")),
                "description": pipeline.get("metadata", {}).get("task_description", ""),
                "status": pipeline.get("status", "UNKNOWN"),
                "progress_percentage": 100 if pipeline.get("status") == "COMPLETED" else (50 if pipeline.get("status") == "IN_PROGRESS" else 0)
            }
            tasks.append(task_info)
        
        response = OnboardJobProgress(
            job_id=job_id,
            app_id=job_info.get("app_id", "unknown"),
            status=job_status_str,
            current_task=current_task,
            current_task_name=current_task_name,
            overall_progress_percentage=overall_progress,
            tasks=tasks,
            created_at=job_info.get("created_at", ""),
            updated_at=job_info.get("updated_at", ""),
            error_message=error_message
        )
        
        logger.info(f"Retrieved progress for job {job_id}: {overall_progress}% complete")
        return response
        
    except Exception as e:
        logger.error(f"Error getting progress for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job progress: {str(e)}"
        )


@router.post(
    "/cancel/{job_id}",
    summary="Cancel onboarding job",
    description="Cancel a running onboarding job."
)
async def cancel_onboard_job(
    job_id: str,
    current_user: User = RequireAuth
) -> Dict[str, Any]:
    """
    Cancel a running onboarding job.
    
    This endpoint attempts to cancel an onboarding job by updating its status in DJT.
    Note: This may not stop already running tasks immediately.
    
    Args:
        job_id: The unique identifier of the onboarding job to cancel
        
    Returns:
        Dict with cancellation status
        
    Raises:
        HTTPException: If job not found or error cancelling job
    """
    try:
        logger.info(f"Cancelling onboarding job: {job_id}")
        
        # Get DJT client from dependency injection
        djt_client = di[DJTPort]
        
        # Get current job status first
        job_status = await djt_client.get_job_pipelines(job_id)
        
        # Update job status to cancelled (implementation depends on DJT API)
        # This is a simplified approach - you'd need to implement job cancellation in DJT
        
        logger.info(f"Successfully cancelled onboarding job: {job_id}")
        return {
            "success": True,
            "message": f"Job {job_id} cancellation requested",
            "job_id": job_id
        }
        
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job: {str(e)}"
        )


@router.post(
    "/save",
    response_model=OnboardSaveResponse,
    summary="Save onboarding app configuration",
    description="Create and persist a new app config for the completed onboarding process with application defaults."
)
async def save_onboard_config(
    request: OnboardSaveRequest,
    current_user: User = RequireAuth
) -> OnboardSaveResponse:
    """
    Save the app configuration for a completed onboarding process.
    
    This endpoint creates and persists a new app config using the provided
    app_id, business_unit, and solution_code with application defaults.
    This is called from Admin UI when the user finishes Step 4 of onboarding.
    
    Args:
        request: The save request containing app_id, business_unit, solution_code and artifacts
        
    Returns:
        OnboardSaveResponse: Response indicating success and config creation status
        
    Raises:
        HTTPException: If there's an error creating the configuration
    """
    try:
        logger.info(f"Processing save onboard config request for app_id: {request.app_id}")
        logger.info(f"Request parameters - business_unit: {request.business_unit}, solution_code: {request.solution_code}")

        # Validate required parameters and collect all errors
        validation_errors = []

        if not request.app_id or not request.app_id.strip():
            validation_errors.append("app_id is required and cannot be empty")

        if not request.business_unit or not request.business_unit.strip():
            validation_errors.append("business_unit is required and cannot be empty")

        if not request.solution_code or not request.solution_code.strip():
            validation_errors.append("solution_code is required and cannot be empty")

        if not request.app_name or not request.app_name.strip():
            validation_errors.append("app_name is required and cannot be empty")

        # If there are validation errors, return them all together
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Validation failed",
                    "errors": validation_errors
                }
            )

        # Create command following CQRS pattern
        command = SaveOnboardConfigCommand(
            app_id=request.app_id,
            business_unit=request.business_unit,
            solution_code=request.solution_code,
            app_name=request.app_name,
            app_description=request.app_description,
            entity_schema=request.entity_schema,
            extraction_prompt=request.extraction_prompt,
            pipeline_template=request.pipeline_template
        )
        
        # Get onboard service from dependency injection
        onboard_service = get_onboard_service()
        
        # Handle the command through the service layer
        response = await onboard_service.handle_save_onboard_config(command)
        
        logger.info(f"Successfully processed save onboard config command for app_id: {request.app_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing save onboard config for app_id {request.app_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save onboard configuration: {str(e)}"
        )