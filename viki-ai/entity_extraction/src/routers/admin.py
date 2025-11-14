from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from adapters.cloudtask import CloudTaskAdapter

LOGGER = getLogger(__name__)

# Create router for admin endpoints
router = APIRouter(prefix="/admin", tags=["admin"])


class CreateCloudTaskQueueRequest(BaseModel):
    """Request model for creating a Cloud Task queue."""
    queue_name: str = Field(..., description="Name of the queue to create")
    location: Optional[str] = Field(None, description="GCP location (uses default if not provided)")
    max_concurrent_dispatches: Optional[int] = Field(None, description="Maximum number of concurrent dispatches")
    max_dispatches_per_second: Optional[float] = Field(None, description="Maximum dispatches per second")
    max_retry_duration_seconds: Optional[int] = Field(None, description="Maximum retry duration in seconds")
    min_backoff_seconds: Optional[int] = Field(None, description="Minimum backoff duration in seconds")
    max_backoff_seconds: Optional[int] = Field(None, description="Maximum backoff duration in seconds")
    max_attempts: Optional[int] = Field(None, description="Maximum number of retry attempts")


class CreateCloudTaskQueueResponse(BaseModel):
    """Response model for creating a Cloud Task queue."""
    success: bool = Field(..., description="Whether the operation was successful")
    queue_name: str = Field(..., description="Name of the created queue")
    queue_info: dict = Field(..., description="Detailed queue information from GCP")
    message: str = Field(..., description="Success or error message")


@router.post("/cloudtask", response_model=CreateCloudTaskQueueResponse)
async def create_cloudtask_queue(request: CreateCloudTaskQueueRequest, http_request: Request):
    """
    Create a new Cloud Task queue.
    
    This endpoint allows dynamic creation of Cloud Task queues without requiring
    Terraform configuration changes.
    """
    
    extra = {
        "http_request": {
            "method": "POST",
            "url": "/api/admin/cloudtask",
            "headers": dict(http_request.headers),
        },
        "queue_name": request.queue_name,
        "location": request.location,
        "max_concurrent_dispatches": request.max_concurrent_dispatches,
        "max_dispatches_per_second": request.max_dispatches_per_second,
        "max_retry_duration_seconds": request.max_retry_duration_seconds,
        "min_backoff_seconds": request.min_backoff_seconds,
        "max_backoff_seconds": request.max_backoff_seconds,
        "max_attempts": request.max_attempts
    }
    
    try:
        LOGGER.info(f"Creating Cloud Task queue: {request.queue_name}", extra=extra)
        
        # Create the CloudTaskAdapter
        adapter = CloudTaskAdapter()
        
        try:
            # Create the queue using the adapter
            queue_info = await adapter.create_queue(
                queue_name=request.queue_name,
                location=request.location,
                max_concurrent_dispatches=request.max_concurrent_dispatches,
                max_dispatches_per_second=request.max_dispatches_per_second,
                max_retry_duration_seconds=request.max_retry_duration_seconds,
                min_backoff_seconds=request.min_backoff_seconds,
                max_backoff_seconds=request.max_backoff_seconds,
                max_attempts=request.max_attempts
            )
            
            extra.update({
                "created_queue_name": queue_info.get("name", "unknown"),
                "queue_state": queue_info.get("state", "unknown")
            })
            LOGGER.info(f"Successfully created Cloud Task queue: {request.queue_name}", extra=extra)
            
            return CreateCloudTaskQueueResponse(
                success=True,
                queue_name=request.queue_name,
                queue_info=queue_info,
                message=f"Successfully created Cloud Task queue: {request.queue_name}"
            )
            
        finally:
            # Always close the adapter
            adapter.close()
            
    except Exception as e:
        error_msg = str(e)
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error creating Cloud Task queue {request.queue_name}: {error_msg}", extra=extra)
        
        # Check for specific error types to provide better HTTP status codes
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=409,
                detail=f"Queue '{request.queue_name}' already exists"
            )
        elif "permission" in error_msg.lower() or "unauthorized" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {error_msg}"
            )
        elif "not found" in error_msg.lower():
            raise HTTPException(
                status_code=404,
                detail=f"Resource not found: {error_msg}"
            )
        elif "invalid" in error_msg.lower() or "bad request" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid request: {error_msg}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating Cloud Task queue: {error_msg}"
            )


@router.get("/cloudtask/{queue_name}")
async def get_cloudtask_queue(queue_name: str, location: Optional[str] = None, http_request: Request = None):
    """
    Get information about a specific Cloud Task queue.
    """
    
    extra = {
        "http_request": {
            "method": "GET",
            "url": f"/api/admin/cloudtask/{queue_name}",
            "headers": dict(http_request.headers) if http_request else {},
        },
        "queue_name": queue_name,
        "location": location
    }
    
    try:
        LOGGER.info(f"Getting Cloud Task queue info: {queue_name}", extra=extra)
        
        # Create the CloudTaskAdapter
        adapter = CloudTaskAdapter()
        
        try:
            # Get the queue information
            queue_info = await adapter.get_queue(queue_name=queue_name, location=location)
            
            if queue_info is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Queue '{queue_name}' not found"
                )
            
            LOGGER.info(f"Successfully retrieved Cloud Task queue info: {queue_name}", extra=extra)
            
            return {
                "success": True,
                "queue_name": queue_name,
                "queue_info": queue_info
            }
            
        finally:
            # Always close the adapter
            adapter.close()
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error getting Cloud Task queue {queue_name}: {error_msg}", extra=extra)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving Cloud Task queue: {error_msg}"
        )


@router.get("/cloudtask")
async def list_cloudtask_queues(location: Optional[str] = None, page_size: int = 100, http_request: Request = None):
    """
    List all Cloud Task queues in the specified location.
    """
    
    extra = {
        "http_request": {
            "method": "GET",
            "url": "/api/admin/cloudtask",
            "headers": dict(http_request.headers) if http_request else {},
        },
        "location": location,
        "page_size": page_size
    }
    
    try:
        LOGGER.info(f"Listing Cloud Task queues in location: {location or 'default'}", extra=extra)
        
        # Create the CloudTaskAdapter
        adapter = CloudTaskAdapter()
        
        try:
            # List the queues
            queues = await adapter.list_queues(location=location, page_size=page_size)
            
            extra.update({"queue_count": len(queues)})
            LOGGER.info(f"Successfully listed {len(queues)} Cloud Task queues", extra=extra)
            
            return {
                "success": True,
                "location": location or adapter.location,
                "queue_count": len(queues),
                "queues": queues
            }
            
        finally:
            # Always close the adapter
            adapter.close()
            
    except Exception as e:
        error_msg = str(e)
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error listing Cloud Task queues: {error_msg}", extra=extra)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error listing Cloud Task queues: {error_msg}"
        )


@router.delete("/cloudtask/{queue_name}")
async def delete_cloudtask_queue(queue_name: str, location: Optional[str] = None, http_request: Request = None):
    """
    Delete a Cloud Task queue.
    """
    
    extra = {
        "http_request": {
            "method": "DELETE",
            "url": f"/api/admin/cloudtask/{queue_name}",
            "headers": dict(http_request.headers) if http_request else {},
        },
        "queue_name": queue_name,
        "location": location
    }
    
    try:
        LOGGER.info(f"Deleting Cloud Task queue: {queue_name}", extra=extra)
        
        # Create the CloudTaskAdapter
        adapter = CloudTaskAdapter()
        
        try:
            # Delete the queue
            deleted = await adapter.delete_queue(queue_name=queue_name, location=location)
            
            if not deleted:
                raise HTTPException(
                    status_code=404,
                    detail=f"Queue '{queue_name}' not found"
                )
            
            LOGGER.info(f"Successfully deleted Cloud Task queue: {queue_name}", extra=extra)
            
            return {
                "success": True,
                "queue_name": queue_name,
                "message": f"Successfully deleted Cloud Task queue: {queue_name}"
            }
            
        finally:
            # Always close the adapter
            adapter.close()
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error deleting Cloud Task queue {queue_name}: {error_msg}", extra=extra)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting Cloud Task queue: {error_msg}"
        )
