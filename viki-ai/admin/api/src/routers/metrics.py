from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from viki_shared.adapters.metrics_adapter import MetricsAdapter

from dependencies.auth_dependencies import RequireAuth
from models.user import User

router = APIRouter()


async def get_metrics_adapter() -> MetricsAdapter:
    """Dependency to get metrics adapter instance."""
    return MetricsAdapter()


@router.get("/{metric_name}")
async def get_metric_stats(
    metric_name: str,
    hours_back: Optional[int] = Query(default=24, ge=1, le=168, description="Hours back to retrieve data (1-168)"),
    aggregation_period_minutes: Optional[int] = Query(default=60, ge=15, le=1440, description="Aggregation period in minutes (15-1440)"),
    adapter: MetricsAdapter = Depends(get_metrics_adapter),
    current_user: User = RequireAuth
):
    """
    Get statistics for a Google Cloud Logging metric.
    
    Args:
        metric_name: Name of the log metric (e.g., 'pipeline_start_metric')
        hours_back: How many hours back to look for data (1-168 hours, default 24)
        aggregation_period_minutes: Period for aggregating data points (15-1440 minutes, default 60)
    
    Returns:
        Metric statistics including time series data and aggregated statistics
    """
    try:
        stats = await adapter.get_log_metric_stats(
            metric_name=metric_name,
            hours_back=hours_back,
            aggregation_period_minutes=aggregation_period_minutes
        )
        
        if stats.get("status") == "error":
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve metrics: {stats.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve metric statistics: {str(e)}"
        )


@router.get("/{metric_name}/definition")
async def get_metric_definition(
    metric_name: str,
    adapter: MetricsAdapter = Depends(get_metrics_adapter),
    current_user: User = RequireAuth
):
    """
    Get the definition of a specific log metric.
    
    Args:
        metric_name: Name of the log metric
    
    Returns:
        Metric definition details including filter and description
    """
    try:
        definition = await adapter.get_metric_definition(metric_name)
        
        if definition.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Metric '{metric_name}' not found"
            )
        elif definition.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve metric definition: {definition.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "data": definition
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metric definition: {str(e)}"
        )


@router.get("")
async def list_metrics(
    adapter: MetricsAdapter = Depends(get_metrics_adapter),
    current_user: User = RequireAuth
):
    """
    List all available log metrics.
    
    Returns:
        List of available metrics with their definitions
    """
    try:
        metrics = await adapter.list_available_metrics()
        
        return {
            "success": True,
            "data": metrics,
            "total": len(metrics)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list metrics: {str(e)}"
        )