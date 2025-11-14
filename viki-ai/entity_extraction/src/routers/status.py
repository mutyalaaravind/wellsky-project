from fastapi import APIRouter, HTTPException, Request, Depends
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from adapters.djt_client import get_djt_client
from typing import Dict, Any

LOGGER = getLogger(__name__)

# Create router for status endpoints
router = APIRouter(prefix="/status", tags=["status"])

@router.get("/{run_id}")
async def get_job_status(
    run_id: str,
    request: Request
):
    """Get job status by run_id from distributed job tracking service."""
    
    extra = {
        "http_request": {
            "method": "GET",
            "url": f"/api/status/{run_id}",
            "headers": dict(request.headers),
        },
        "run_id": run_id
    }
    
    try:
        LOGGER.info(f"Fetching job status for run_id: {run_id} from DJT API", extra)
        
        # Use the DJT client adapter to get job pipelines
        djt_client = get_djt_client()
        result = await djt_client.get_job_pipelines(run_id)

        LOGGER.debug("Successfully retrieved job status from DJT API: %s", result, extra=extra)
        
        return result
            
    except Exception as e:
        # Check if this is a DJT API error with a specific status code
        if hasattr(e, 'status_code'):
            extra.update({"status_code": e.status_code, "response_text": getattr(e, 'response_text', '')})
            LOGGER.warning(f"DJT API error for run_id: {run_id}", extra)
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Error from distributed job tracking service: {getattr(e, 'response_text', str(e))}"
            )
        
        # Handle network/connection errors
        if "Unable to connect" in str(e):
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Network error when calling DJT API for run_id: {run_id}", extra)
            raise HTTPException(
                status_code=503,
                detail=str(e)
            )
        
        # Handle all other errors
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Unexpected error getting job status for run_id: {run_id}", extra)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving job status: {str(e)}"
        )
