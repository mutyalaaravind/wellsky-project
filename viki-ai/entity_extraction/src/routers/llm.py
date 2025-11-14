"""
LLM execution router.

This module contains the FastAPI router for LLM execution endpoints,
providing REST API access to LLM document processing capabilities.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from contracts.llm import LlmExecuteRequest, LlmExecuteResponse
from usecases.llm_executor import execute_llm_request

LOGGER = getLogger(__name__)

# Create router for LLM endpoints
router = APIRouter(prefix="/v1/llm", tags=["llm"])


@router.post("/execute", response_model=LlmExecuteResponse)
async def execute_llm(
    request: LlmExecuteRequest,
    http_request: Request
):
    """
    Execute an LLM prompt with a document stored in Google Cloud Storage.
    
    This endpoint processes a document from GCS using an LLM to generate
    structured responses based on the provided prompt and optional JSON schema.
    
    Args:
        request: LlmExecuteRequest containing GS URI, prompt, system instructions, and schema
        http_request: FastAPI request object for logging
        auth_info: Authentication information from service account
        
    Returns:
        LlmExecuteResponse: The response containing generated content and execution metadata
        
    Raises:
        HTTPException: If the request validation fails or execution errors occur
    """
    
    extra = {
        "http_request": {
            "method": "POST",
            "url": "/api/v1/llm/execute",
            "headers": dict(http_request.headers),
        },
        "gs_uri": request.gs_uri,
        "prompt_length": len(request.prompt),
        "has_system_instructions": request.system_instructions is not None,
        "has_json_schema": request.json_schema is not None,
        "metadata": request.metadata
    }
    
    try:
        LOGGER.info(f"Received LLM execution request for GS URI: {request.gs_uri}", extra=extra)
        
        # Execute the LLM request
        response = await execute_llm_request(request)
        
        # Log the result
        result_extra = {
            **extra,
            "success": response.success,
            "has_content": response.content is not None,
            "raw_response_length": len(response.raw_response) if response.raw_response else 0,
            "execution_metadata": response.execution_metadata
        }
        
        if response.success:
            LOGGER.info("LLM execution completed successfully", extra=result_extra)
        else:
            LOGGER.warning(f"LLM execution failed: {response.error_message}", extra=result_extra)
        
        return response
        
    except ValueError as e:
        # Handle validation errors
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Validation error in LLM execution request", extra=extra)
        raise HTTPException(
            status_code=422,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        # Handle unexpected errors
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Unexpected error in LLM execution", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )