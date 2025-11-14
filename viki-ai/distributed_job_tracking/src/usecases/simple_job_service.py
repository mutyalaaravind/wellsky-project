import json
from datetime import datetime
from typing import Optional
import redis.asyncio as redis
from models.simple_job import SimpleJob, SimpleJobCreate, SimpleJobUpdate
import settings
from util.custom_logger import getLogger, set_job_context


class SimpleJobService:
    """Service for handling simple job operations with Redis hash storage"""
    
    def __init__(self):
        # Test basic Python logging first
        import logging
        basic_logger = logging.getLogger(__name__)
        basic_logger.info("Basic Python logger test")
        print("Print statement test - SimpleJobService initializing...")
        
        self.logger = getLogger(__name__)
        print("Custom logger created")
        self.logger.info("SimpleJobService initialized with custom logger")
        print("After custom logger info call")
        
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    
    async def close(self):
        """Close Redis connection"""
        await self.redis_client.aclose()
    
    def _get_redis_key(self, run_id: str) -> str:
        """Generate Redis key for a job"""
        return f"djt::{run_id}"
    
    async def create_job(self, job_data: SimpleJobCreate) -> SimpleJob:
        """Create a new job and store in Redis"""
        # Set job context for logging
        set_job_context(run_id=job_data.run_id, job_type="simple_job", status="creating")
        
        self.logger.info("Creating new job with run_id: %s, name: %s", job_data.run_id, job_data.name)
        
        # Create job with timestamps
        job = SimpleJob(
            **job_data.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store in Redis as hash with key "djt::{run_id}" and hashkey "job"
        redis_key = self._get_redis_key(job.run_id)
        job_json = job.model_dump_json()
        
        await self.redis_client.hset(redis_key, "job", job_json)
        
        self.logger.info("Job created successfully using key '%s'", redis_key, extra={
            "run_id": job.run_id,
            "job_name": job.name,
            "operation": "create_job"
        })
        
        return job
    
    async def get_job(self, run_id: str) -> Optional[SimpleJob]:
        """Get a job by run_id"""
        set_job_context(run_id=run_id)
        
        self.logger.debug("Retrieving job", extra={
            "run_id": run_id,
            "operation": "get_job"
        })
        
        redis_key = self._get_redis_key(run_id)
        job_json = await self.redis_client.hget(redis_key, "job")
        
        if not job_json:
            self.logger.warning("Job not found", extra={
                "run_id": run_id,
                "operation": "get_job"
            })
            return None
        
        job_data = json.loads(job_json)
        job = SimpleJob(**job_data)
        
        self.logger.debug("Job retrieved successfully", extra={
            "run_id": run_id,
            "job_name": job.name,
            "operation": "get_job"
        })
        
        return job
    
    async def update_job(self, run_id: str, job_update: SimpleJobUpdate) -> Optional[SimpleJob]:
        """Update an existing job"""
        set_job_context(run_id=run_id)
        
        self.logger.info("Updating job", extra={
            "run_id": run_id,
            "operation": "update_job",
            "update_fields": list(job_update.model_dump(exclude_unset=True).keys())
        })
        
        # Get existing job
        existing_job = await self.get_job(run_id)
        if not existing_job:
            self.logger.warning("Cannot update job - job not found", extra={
                "run_id": run_id,
                "operation": "update_job"
            })
            return None
        
        # Update fields that are provided
        update_data = job_update.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now()
            
            # Create updated job
            updated_job_data = existing_job.model_dump()
            updated_job_data.update(update_data)
            updated_job = SimpleJob(**updated_job_data)
            
            # Store back to Redis
            redis_key = self._get_redis_key(run_id)
            job_json = updated_job.model_dump_json()
            await self.redis_client.hset(redis_key, "job", job_json)
            
            self.logger.info("Job updated successfully", extra={
                "run_id": run_id,
                "job_name": updated_job.name,
                "operation": "update_job",
                "updated_fields": list(update_data.keys())
            })
            
            return updated_job
        
        self.logger.debug("No updates provided for job", extra={
            "run_id": run_id,
            "operation": "update_job"
        })
        
        return existing_job
    
    async def delete_job(self, run_id: str) -> bool:
        """Delete a job by run_id"""
        set_job_context(run_id=run_id)
        
        self.logger.info("Deleting job", extra={
            "run_id": run_id,
            "operation": "delete_job"
        })
        
        redis_key = self._get_redis_key(run_id)
        result = await self.redis_client.delete(redis_key)
        
        if result > 0:
            self.logger.info("Job deleted successfully", extra={
                "run_id": run_id,
                "operation": "delete_job"
            })
        else:
            self.logger.warning("Job not found for deletion", extra={
                "run_id": run_id,
                "operation": "delete_job"
            })
        
        return result > 0
    
    async def job_exists(self, run_id: str) -> bool:
        """Check if a job exists"""
        redis_key = self._get_redis_key(run_id)
        return await self.redis_client.hexists(redis_key, "job")
