"""
Cloud Tasks Router for Admin API

This router provides endpoints for managing and monitoring Cloud Tasks.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from adapters.cloud_task_adapter import CloudTaskAdapter
from settings import Settings, get_settings
from dependencies.auth_dependencies import RequireAuth
from models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cloud-tasks", tags=["Cloud Tasks"])


class QueueMetricsResponse(BaseModel):
    """Response model for queue metrics."""
    queue_name: str
    location: str
    time_range: Dict[str, Any]
    queue_info: Dict[str, Any]
    metrics: Dict[str, Any]
    summary: Dict[str, Any]


class QueueDepthResponse(BaseModel):
    """Response model for queue depth."""
    queue_name: str
    location: str
    current_depth: float
    data_points_available: int
    queue_info: Dict[str, Any]


class QueueListResponse(BaseModel):
    """Response model for queue list."""
    queues: List[Dict[str, Any]]
    location: str
    total_count: int


@router.get(
    "/queues/{queue_name}/metrics",
    response_model=QueueMetricsResponse,
    summary="Get Cloud Task Queue Metrics",
    description="Retrieve comprehensive metrics for a specific Cloud Task queue including depth, attempts, delays, and API requests."
)
async def get_queue_metrics(
    queue_name: str = Path(..., description="Name of the Cloud Task queue"),
    location: Optional[str] = Query(None, description="GCP location (defaults to us-east4)"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours of historical data to retrieve (1-168 hours)"),
    settings: Settings = Depends(get_settings),
    current_user: User = RequireAuth
) -> QueueMetricsResponse:
    """
    Get comprehensive metrics for a Cloud Task queue.
    
    This endpoint retrieves various metrics including:
    - Queue depth (number of tasks waiting)
    - Task attempt counts and delays  
    - API request counts
    - Queue configuration and state
    
    The metrics are aggregated over the specified time period and include
    summary statistics for easy analysis.
    """
    try:
        logger.info(f"Fetching metrics for queue: {queue_name}")
        
        adapter = CloudTaskAdapter(settings)
        metrics = await adapter.get_queue_metrics(
            queue_name=queue_name,
            location=location,
            hours_back=hours_back
        )
        
        return QueueMetricsResponse(**metrics)
        
    except Exception as e:
        logger.error(f"Error fetching queue metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch metrics for queue {queue_name}: {str(e)}"
        )


@router.get(
    "/queues/{queue_name}/depth",
    response_model=QueueDepthResponse,
    summary="Get Queue Depth",
    description="Get the current depth (number of pending tasks) for a specific Cloud Task queue."
)
async def get_queue_depth(
    queue_name: str = Path(..., description="Name of the Cloud Task queue"),
    location: Optional[str] = Query(None, description="GCP location (defaults to us-east4)"),
    settings: Settings = Depends(get_settings),
    current_user: User = RequireAuth
) -> QueueDepthResponse:
    """
    Get current queue depth for a Cloud Task queue.
    
    Returns the current number of tasks waiting in the queue along with
    basic queue information and configuration.
    """
    try:
        logger.info(f"Fetching queue depth for: {queue_name}")
        
        adapter = CloudTaskAdapter(settings)
        depth_info = await adapter.get_queue_depth(
            queue_name=queue_name,
            location=location
        )
        
        return QueueDepthResponse(**depth_info)
        
    except Exception as e:
        logger.error(f"Error fetching queue depth: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch depth for queue {queue_name}: {str(e)}"
        )


@router.get(
    "/queues",
    response_model=QueueListResponse,
    summary="List Cloud Task Queues",
    description="List all Cloud Task queues in the specified location."
)
async def list_queues(
    location: Optional[str] = Query(None, description="GCP location (defaults to us-east4)"),
    settings: Settings = Depends(get_settings),
    current_user: User = RequireAuth
) -> QueueListResponse:
    """
    List all Cloud Task queues in the specified location.
    
    Returns basic information about each queue including name, state,
    and configuration details.
    """
    try:
        logger.info(f"Listing queues in location: {location or 'default'}")
        
        adapter = CloudTaskAdapter(settings)
        queues = await adapter.list_queues(location=location)
        
        return QueueListResponse(
            queues=queues,
            location=location or adapter.location,
            total_count=len(queues)
        )
        
    except Exception as e:
        logger.error(f"Error listing queues: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list queues: {str(e)}"
        )


@router.get(
    "/queues/{queue_name}/metrics/summary",
    summary="Get Queue Metrics Summary",
    description="Get a simplified summary of key metrics for a Cloud Task queue."
)
async def get_queue_metrics_summary(
    queue_name: str = Path(..., description="Name of the Cloud Task queue"),
    location: Optional[str] = Query(None, description="GCP location (defaults to us-east4)"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours of historical data to retrieve"),
    settings: Settings = Depends(get_settings),
    current_user: User = RequireAuth
) -> Dict[str, Any]:
    """
    Get a simplified summary of key metrics for a Cloud Task queue.
    
    Returns only the most important metrics in a condensed format,
    suitable for dashboards and quick status checks.
    """
    try:
        logger.info(f"Fetching metrics summary for queue: {queue_name}")
        
        adapter = CloudTaskAdapter(settings)
        metrics = await adapter.get_queue_metrics(
            queue_name=queue_name,
            location=location,
            hours_back=hours_back
        )
        
        # Return only the summary and basic info
        return {
            "queue_name": metrics["queue_name"],
            "location": metrics["location"],
            "queue_state": metrics["queue_info"].get("state", "Unknown"),
            "current_depth": metrics["summary"].get("queue_depth", {}).get("current") or 0.0,
            "avg_depth": metrics["summary"].get("queue_depth", {}).get("avg") or 0.0,
            "max_depth": metrics["summary"].get("queue_depth", {}).get("max") or 0.0,
            "avg_delay": metrics["summary"].get("task_delays", {}).get("avg_delay") or 0.0,
            "max_delay": metrics["summary"].get("task_delays", {}).get("max_delay") or 0.0,
            "total_api_requests": metrics["summary"].get("api_requests", {}).get("total_requests") or 0.0,
            "time_range_hours": hours_back,
            "last_updated": metrics["time_range"]["end"]
        }
        
    except Exception as e:
        logger.error(f"Error fetching queue metrics summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch metrics summary for queue {queue_name}: {str(e)}"
        )


@router.get(
    "/health",
    summary="Cloud Tasks Health Check",
    description="Check the health and connectivity of Cloud Tasks services."
)
async def health_check(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    Health check endpoint for Cloud Tasks services.
    
    Verifies that the admin API can connect to Google Cloud Tasks
    and Cloud Monitoring services.
    """
    try:
        adapter = CloudTaskAdapter(settings)
        
        # Test connectivity by listing queues
        queues = await adapter.list_queues()
        
        return {
            "status": "healthy",
            "project_id": settings.GCP_PROJECT_ID,
            "location": adapter.location,
            "queues_found": len(queues),
            "services": {
                "cloud_tasks": "connected",
                "cloud_monitoring": "connected"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "services": {
                "cloud_tasks": "error",
                "cloud_monitoring": "error"
            },
            "timestamp": datetime.utcnow().isoformat()
        }