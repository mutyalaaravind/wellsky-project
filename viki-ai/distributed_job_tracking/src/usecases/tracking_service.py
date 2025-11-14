from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from models import Job, JobStatus, JobType, JobPriority
from adapters.redis_adapter import RedisAdapter

logger = logging.getLogger(__name__)


class TrackingService:
    """Service for tracking and monitoring jobs"""
    
    def __init__(self, redis_adapter: RedisAdapter):
        self.redis_adapter = redis_adapter
    
    async def get_job_stats(self) -> Dict[str, Any]:
        """Get overall job statistics"""
        try:
            # Get counts by status
            status_counts = await self.redis_adapter.get_jobs_count_by_status()
            
            # Get counts by type
            type_counts = await self.redis_adapter.get_jobs_count_by_type()
            
            # Get counts by priority
            priority_counts = await self.redis_adapter.get_jobs_count_by_priority()
            
            # Calculate totals
            total_jobs = sum(status_counts.values())
            active_jobs = status_counts.get("running", 0)
            pending_jobs = status_counts.get("pending", 0)
            completed_jobs = status_counts.get("completed", 0)
            failed_jobs = status_counts.get("failed", 0)
            
            return {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "pending_jobs": pending_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
                "status_breakdown": status_counts,
                "type_breakdown": type_counts,
                "priority_breakdown": priority_counts,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get job stats: {e}")
            raise
    
    async def get_stats_by_status(self) -> Dict[str, int]:
        """Get job statistics grouped by status"""
        try:
            return await self.redis_adapter.get_jobs_count_by_status()
        except Exception as e:
            logger.error(f"Failed to get stats by status: {e}")
            raise
    
    async def get_stats_by_type(self) -> Dict[str, int]:
        """Get job statistics grouped by type"""
        try:
            return await self.redis_adapter.get_jobs_count_by_type()
        except Exception as e:
            logger.error(f"Failed to get stats by type: {e}")
            raise
    
    async def get_stats_by_priority(self) -> Dict[str, int]:
        """Get job statistics grouped by priority"""
        try:
            return await self.redis_adapter.get_jobs_count_by_priority()
        except Exception as e:
            logger.error(f"Failed to get stats by priority: {e}")
            raise
    
    async def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for the specified time period"""
        try:
            # Get all jobs
            all_job_ids = await self.redis_adapter.get_all_job_ids()
            
            # Filter jobs by time period
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_jobs = []
            
            for job_id in all_job_ids:
                job_data = await self.redis_adapter.get_job(job_id)
                if job_data:
                    created_at = datetime.fromisoformat(job_data.get("created_at", ""))
                    if created_at >= cutoff_time:
                        recent_jobs.append(job_data)
            
            # Calculate metrics
            total_jobs = len(recent_jobs)
            completed_jobs = [j for j in recent_jobs if j.get("status") == "completed"]
            failed_jobs = [j for j in recent_jobs if j.get("status") == "failed"]
            
            # Calculate average execution time for completed jobs
            execution_times = []
            for job in completed_jobs:
                started_at = job.get("started_at")
                completed_at = job.get("completed_at")
                if started_at and completed_at:
                    start_time = datetime.fromisoformat(started_at)
                    end_time = datetime.fromisoformat(completed_at)
                    execution_time = (end_time - start_time).total_seconds()
                    execution_times.append(execution_time)
            
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            # Calculate success rate
            success_rate = len(completed_jobs) / total_jobs * 100 if total_jobs > 0 else 0
            
            # Calculate throughput (jobs per hour)
            throughput = total_jobs / hours if hours > 0 else 0
            
            return {
                "time_period_hours": hours,
                "total_jobs": total_jobs,
                "completed_jobs": len(completed_jobs),
                "failed_jobs": len(failed_jobs),
                "success_rate_percent": round(success_rate, 2),
                "average_execution_time_seconds": round(avg_execution_time, 2),
                "throughput_jobs_per_hour": round(throughput, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            raise
    
    async def get_active_jobs(self) -> List[Dict[str, Any]]:
        """Get all currently active (running) jobs"""
        try:
            running_job_ids = await self.redis_adapter.get_jobs_by_status("running")
            
            active_jobs = []
            for job_id in running_job_ids:
                job_data = await self.redis_adapter.get_job(job_id)
                if job_data:
                    active_jobs.append(job_data)
            
            return active_jobs
            
        except Exception as e:
            logger.error(f"Failed to get active jobs: {e}")
            raise
    
    async def get_failed_jobs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed jobs within the specified time period"""
        try:
            failed_job_ids = await self.redis_adapter.get_jobs_by_status("failed")
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_failed_jobs = []
            
            for job_id in failed_job_ids:
                job_data = await self.redis_adapter.get_job(job_id)
                if job_data:
                    created_at = datetime.fromisoformat(job_data.get("created_at", ""))
                    if created_at >= cutoff_time:
                        recent_failed_jobs.append(job_data)
            
            return recent_failed_jobs
            
        except Exception as e:
            logger.error(f"Failed to get failed jobs: {e}")
            raise
    
    async def get_queue_depth(self) -> int:
        """Get the current queue depth (pending jobs)"""
        try:
            pending_job_ids = await self.redis_adapter.get_jobs_by_status("pending")
            return len(pending_job_ids)
        except Exception as e:
            logger.error(f"Failed to get queue depth: {e}")
            raise
    
    async def get_throughput(self, hours: int = 24) -> Dict[str, Any]:
        """Get job throughput for the specified time period"""
        try:
            completed_job_ids = await self.redis_adapter.get_jobs_by_status("completed")
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_completed_jobs = []
            
            for job_id in completed_job_ids:
                job_data = await self.redis_adapter.get_job(job_id)
                if job_data:
                    completed_at = job_data.get("completed_at")
                    if completed_at:
                        completion_time = datetime.fromisoformat(completed_at)
                        if completion_time >= cutoff_time:
                            recent_completed_jobs.append(job_data)
            
            total_completed = len(recent_completed_jobs)
            throughput_per_hour = total_completed / hours if hours > 0 else 0
            
            return {
                "time_period_hours": hours,
                "completed_jobs": total_completed,
                "throughput_jobs_per_hour": round(throughput_per_hour, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get throughput: {e}")
            raise
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get statistics about workers"""
        try:
            # Get all running jobs to see active workers
            running_job_ids = await self.redis_adapter.get_jobs_by_status("running")
            
            worker_jobs = {}
            active_workers = set()
            
            for job_id in running_job_ids:
                job_data = await self.redis_adapter.get_job(job_id)
                if job_data:
                    worker_id = job_data.get("worker_id")
                    if worker_id:
                        active_workers.add(worker_id)
                        if worker_id not in worker_jobs:
                            worker_jobs[worker_id] = []
                        worker_jobs[worker_id].append(job_data)
            
            return {
                "active_workers": len(active_workers),
                "worker_job_distribution": {
                    worker_id: len(jobs) for worker_id, jobs in worker_jobs.items()
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker stats: {e}")
            raise
    
    async def get_job_tree(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the complete job tree for a given job"""
        try:
            job_data = await self.redis_adapter.get_job(job_id)
            if not job_data:
                return None
            
            # If this is a sub-job, get the parent first
            parent_job_id = job_data.get("parent_job_id")
            if parent_job_id:
                return await self.get_job_tree(parent_job_id)
            
            # This is a parent job, get all sub-jobs
            sub_job_ids = job_data.get("sub_job_ids", [])
            sub_jobs = []
            
            for sub_job_id in sub_job_ids:
                sub_job_data = await self.redis_adapter.get_job(sub_job_id)
                if sub_job_data:
                    sub_jobs.append(sub_job_data)
            
            return {
                "parent_job": job_data,
                "sub_jobs": sub_jobs,
                "total_sub_jobs": len(sub_jobs),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get job tree for {job_id}: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # Test Redis connection
            redis_healthy = await self.redis_adapter.ping()
            
            # Get basic stats
            stats = await self.get_job_stats()
            
            # Calculate health indicators
            total_jobs = stats["total_jobs"]
            failed_jobs = stats["failed_jobs"]
            active_jobs = stats["active_jobs"]
            
            # Calculate failure rate
            failure_rate = (failed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            # Determine overall health status
            if not redis_healthy:
                health_status = "critical"
            elif failure_rate > 20:
                health_status = "degraded"
            elif active_jobs > 100:  # Arbitrary threshold
                health_status = "busy"
            else:
                health_status = "healthy"
            
            return {
                "status": health_status,
                "redis_connection": "healthy" if redis_healthy else "failed",
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "failed_jobs": failed_jobs,
                "failure_rate_percent": round(failure_rate, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
