from datetime import datetime
from typing import List, Optional
import logging

from models import (
    Job,
    JobCreate,
    JobUpdate,
    JobStatus,
    JobPriority,
    JobType,
    JobWithSubJobs,
    JobListResponse,
)
from adapters.redis_adapter import RedisAdapter

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing jobs"""
    
    def __init__(self, redis_adapter: RedisAdapter):
        self.redis_adapter = redis_adapter
    
    async def create_job(self, job_data: JobCreate) -> Job:
        """Create a new job"""
        try:
            # Create job instance
            job = Job(
                name=job_data.name,
                job_type=job_data.job_type,
                priority=job_data.priority,
                payload=job_data.payload,
                metadata=job_data.metadata,
                max_retries=job_data.max_retries,
                timeout_seconds=job_data.timeout_seconds,
                scheduled_at=job_data.scheduled_at,
                depends_on=job_data.depends_on,
                parent_job_id=job_data.parent_job_id,
            )
            
            # Store in Redis
            job_dict = job.dict()
            success = await self.redis_adapter.set_job(job.id, job_dict)
            
            if not success:
                raise Exception("Failed to store job in Redis")
            
            logger.info(f"Created job {job.id}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise
    
    async def create_job_with_subjobs(self, job_data: JobCreate) -> JobWithSubJobs:
        """Create a job with sub-jobs"""
        try:
            # Create parent job
            parent_job = await self.create_job(job_data)
            
            # Mark as parent job if it has sub-jobs
            if job_data.sub_jobs:
                parent_job.is_parent_job = True
                await self.update_job(parent_job.id, JobUpdate(metadata={"is_parent_job": True}))
            
            # Create sub-jobs
            sub_jobs = []
            for sub_job_data in job_data.sub_jobs:
                # Set parent job ID
                sub_job_data.parent_job_id = parent_job.id
                sub_job = await self.create_job(sub_job_data)
                sub_jobs.append(sub_job)
                
                # Add to parent's sub_job_ids
                parent_job.sub_job_ids.append(sub_job.id)
            
            # Update parent job with sub-job IDs
            if sub_jobs:
                await self.update_job(
                    parent_job.id,
                    JobUpdate(metadata={**parent_job.metadata, "sub_job_ids": parent_job.sub_job_ids})
                )
            
            return JobWithSubJobs(job=parent_job, sub_jobs=sub_jobs)
            
        except Exception as e:
            logger.error(f"Failed to create job with sub-jobs: {e}")
            raise
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID"""
        try:
            job_data = await self.redis_adapter.get_job(job_id)
            if job_data:
                return Job(**job_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    async def get_job_with_subjobs(self, job_id: str) -> Optional[JobWithSubJobs]:
        """Get a job with all its sub-jobs"""
        try:
            job = await self.get_job(job_id)
            if not job:
                return None
            
            # Get sub-jobs
            sub_jobs = []
            if job.sub_job_ids:
                for sub_job_id in job.sub_job_ids:
                    sub_job = await self.get_job(sub_job_id)
                    if sub_job:
                        sub_jobs.append(sub_job)
            
            return JobWithSubJobs(job=job, sub_jobs=sub_jobs)
            
        except Exception as e:
            logger.error(f"Failed to get job with sub-jobs {job_id}: {e}")
            return None
    
    async def update_job(self, job_id: str, job_update: JobUpdate) -> Optional[Job]:
        """Update a job"""
        try:
            # Get existing job
            job = await self.get_job(job_id)
            if not job:
                return None
            
            # Track old status for index updates
            old_status = job.status
            
            # Update fields
            update_data = job_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(job, field):
                    setattr(job, field, value)
            
            # Update timestamps based on status changes
            if job_update.status:
                if job_update.status == JobStatus.RUNNING and not job.started_at:
                    job.started_at = datetime.utcnow()
                elif job_update.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    if not job.completed_at:
                        job.completed_at = datetime.utcnow()
            
            # Store updated job
            job_dict = job.dict()
            success = await self.redis_adapter.set_job(job_id, job_dict)
            
            if not success:
                raise Exception("Failed to update job in Redis")
            
            # Update status indexes if status changed
            if job_update.status and old_status != job_update.status:
                await self.redis_adapter.update_job_status(job_id, old_status, job_update.status)
            
            logger.info(f"Updated job {job_id}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            raise
    
    async def delete_job(self, job_id: str, cascade: bool = False) -> bool:
        """Delete a job"""
        try:
            job = await self.get_job(job_id)
            if not job:
                return False
            
            # If cascade is True, delete sub-jobs first
            if cascade and job.sub_job_ids:
                for sub_job_id in job.sub_job_ids:
                    await self.delete_job(sub_job_id, cascade=False)
            
            # Delete the job
            success = await self.redis_adapter.delete_job(job_id)
            
            if success:
                logger.info(f"Deleted job {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    async def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[JobType] = None,
        priority: Optional[JobPriority] = None,
        parent_job_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> JobListResponse:
        """List jobs with filtering and pagination"""
        try:
            job_ids = []
            
            # Apply filters
            if status:
                job_ids = await self.redis_adapter.get_jobs_by_status(status.value)
            elif job_type:
                job_ids = await self.redis_adapter.get_jobs_by_type(job_type.value)
            elif priority:
                job_ids = await self.redis_adapter.get_jobs_by_priority(priority.value)
            elif parent_job_id:
                job_ids = await self.redis_adapter.get_jobs_by_parent(parent_job_id)
            else:
                job_ids = await self.redis_adapter.get_all_job_ids()
            
            # Apply pagination
            total = len(job_ids)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_job_ids = job_ids[start_idx:end_idx]
            
            # Get job objects
            jobs = []
            for job_id in paginated_job_ids:
                job = await self.get_job(job_id)
                if job:
                    jobs.append(job)
            
            # Calculate pagination info
            has_next = end_idx < total
            has_prev = page > 1
            
            return JobListResponse(
                jobs=jobs,
                total=total,
                page=page,
                page_size=page_size,
                has_next=has_next,
                has_prev=has_prev
            )
            
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            raise
    
    async def start_job(self, job_id: str) -> Optional[Job]:
        """Start a job"""
        try:
            job_update = JobUpdate(
                status=JobStatus.RUNNING,
                metadata={"started_by": "api"}
            )
            return await self.update_job(job_id, job_update)
        except Exception as e:
            logger.error(f"Failed to start job {job_id}: {e}")
            raise
    
    async def cancel_job(self, job_id: str) -> Optional[Job]:
        """Cancel a job"""
        try:
            job_update = JobUpdate(
                status=JobStatus.CANCELLED,
                metadata={"cancelled_by": "api"}
            )
            return await self.update_job(job_id, job_update)
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            raise
    
    async def retry_job(self, job_id: str) -> Optional[Job]:
        """Retry a failed job"""
        try:
            job = await self.get_job(job_id)
            if not job:
                return None
            
            if job.status != JobStatus.FAILED:
                raise Exception("Only failed jobs can be retried")
            
            if job.retry_count >= job.max_retries:
                raise Exception("Maximum retry count exceeded")
            
            job_update = JobUpdate(
                status=JobStatus.RETRYING,
                metadata={**job.metadata, "retry_initiated_by": "api"}
            )
            
            # Increment retry count
            updated_job = await self.update_job(job_id, job_update)
            if updated_job:
                updated_job.retry_count += 1
                await self.redis_adapter.set_job(job_id, updated_job.dict())
            
            return updated_job
            
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            raise
