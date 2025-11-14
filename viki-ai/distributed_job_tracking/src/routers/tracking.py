from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from models import JobStatus, JobType, JobPriority
from usecases.tracking_service import TrackingService
from adapters.redis_adapter import RedisAdapter

router = APIRouter(prefix="/tracking", tags=["tracking"])


def get_tracking_service() -> TrackingService:
    """Dependency to get tracking service instance"""
    redis_adapter = RedisAdapter()
    return TrackingService(redis_adapter)


@router.get("/stats")
async def get_job_stats(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get overall job statistics"""
    try:
        stats = await tracking_service.get_job_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job stats: {str(e)}")


@router.get("/stats/by-status")
async def get_stats_by_status(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get job statistics grouped by status"""
    try:
        stats = await tracking_service.get_stats_by_status()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats by status: {str(e)}")


@router.get("/stats/by-type")
async def get_stats_by_type(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get job statistics grouped by type"""
    try:
        stats = await tracking_service.get_stats_by_type()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats by type: {str(e)}")


@router.get("/stats/by-priority")
async def get_stats_by_priority(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get job statistics grouped by priority"""
    try:
        stats = await tracking_service.get_stats_by_priority()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats by priority: {str(e)}")


@router.get("/performance")
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get performance metrics for the specified time period"""
    try:
        metrics = await tracking_service.get_performance_metrics(hours)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@router.get("/active-jobs")
async def get_active_jobs(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get all currently active (running) jobs"""
    try:
        jobs = await tracking_service.get_active_jobs()
        return {"active_jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active jobs: {str(e)}")


@router.get("/failed-jobs")
async def get_failed_jobs(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get failed jobs within the specified time period"""
    try:
        jobs = await tracking_service.get_failed_jobs(hours)
        return {"failed_jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get failed jobs: {str(e)}")


@router.get("/queue-depth")
async def get_queue_depth(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get the current queue depth (pending jobs)"""
    try:
        depth = await tracking_service.get_queue_depth()
        return {"queue_depth": depth}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue depth: {str(e)}")


@router.get("/throughput")
async def get_throughput(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get job throughput (completed jobs per hour) for the specified time period"""
    try:
        throughput = await tracking_service.get_throughput(hours)
        return throughput
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get throughput: {str(e)}")


@router.get("/worker-stats")
async def get_worker_stats(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get statistics about workers"""
    try:
        stats = await tracking_service.get_worker_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get worker stats: {str(e)}")


@router.get("/job-tree/{job_id}")
async def get_job_tree(
    job_id: str,
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get the complete job tree (parent and all sub-jobs) for a given job"""
    try:
        tree = await tracking_service.get_job_tree(job_id)
        if not tree:
            raise HTTPException(status_code=404, detail="Job not found")
        return tree
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job tree: {str(e)}")


@router.get("/health")
async def get_system_health(
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    """Get overall system health metrics"""
    try:
        health = await tracking_service.get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")
