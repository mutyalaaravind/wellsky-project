import json
import redis.asyncio as redis
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

import settings

logger = logging.getLogger(__name__)


class RedisAdapter:
    """Redis adapter for job storage and retrieval"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def set_job(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """Store a job in Redis"""
        try:
            job_key = f"job:{job_id}"
            serialized_data = json.dumps(job_data, default=str)
            await self.redis_client.set(job_key, serialized_data)
            
            # Add to various indexes
            await self._add_to_indexes(job_id, job_data)
            
            return True
        except Exception as e:
            logger.error(f"Failed to set job {job_id}: {e}")
            return False
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a job from Redis"""
        try:
            job_key = f"job:{job_id}"
            job_data = await self.redis_client.get(job_key)
            if job_data:
                return json.loads(job_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job from Redis"""
        try:
            job_key = f"job:{job_id}"
            
            # Get job data first to remove from indexes
            job_data = await self.get_job(job_id)
            if job_data:
                await self._remove_from_indexes(job_id, job_data)
            
            # Delete the job
            result = await self.redis_client.delete(job_key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    async def get_jobs_by_status(self, status: str) -> List[str]:
        """Get job IDs by status"""
        try:
            status_key = f"jobs:status:{status}"
            job_ids = await self.redis_client.smembers(status_key)
            return list(job_ids)
        except Exception as e:
            logger.error(f"Failed to get jobs by status {status}: {e}")
            return []
    
    async def get_jobs_by_type(self, job_type: str) -> List[str]:
        """Get job IDs by type"""
        try:
            type_key = f"jobs:type:{job_type}"
            job_ids = await self.redis_client.smembers(type_key)
            return list(job_ids)
        except Exception as e:
            logger.error(f"Failed to get jobs by type {job_type}: {e}")
            return []
    
    async def get_jobs_by_priority(self, priority: str) -> List[str]:
        """Get job IDs by priority"""
        try:
            priority_key = f"jobs:priority:{priority}"
            job_ids = await self.redis_client.smembers(priority_key)
            return list(job_ids)
        except Exception as e:
            logger.error(f"Failed to get jobs by priority {priority}: {e}")
            return []
    
    async def get_jobs_by_parent(self, parent_job_id: str) -> List[str]:
        """Get sub-job IDs by parent job ID"""
        try:
            parent_key = f"jobs:parent:{parent_job_id}"
            job_ids = await self.redis_client.smembers(parent_key)
            return list(job_ids)
        except Exception as e:
            logger.error(f"Failed to get jobs by parent {parent_job_id}: {e}")
            return []
    
    async def get_all_job_ids(self) -> List[str]:
        """Get all job IDs"""
        try:
            pattern = "job:*"
            keys = await self.redis_client.keys(pattern)
            # Extract job IDs from keys
            job_ids = [key.replace("job:", "") for key in keys]
            return job_ids
        except Exception as e:
            logger.error(f"Failed to get all job IDs: {e}")
            return []
    
    async def get_jobs_count_by_status(self) -> Dict[str, int]:
        """Get count of jobs by status"""
        try:
            statuses = ["pending", "running", "completed", "failed", "cancelled", "retrying"]
            counts = {}
            for status in statuses:
                status_key = f"jobs:status:{status}"
                count = await self.redis_client.scard(status_key)
                counts[status] = count
            return counts
        except Exception as e:
            logger.error(f"Failed to get jobs count by status: {e}")
            return {}
    
    async def get_jobs_count_by_type(self) -> Dict[str, int]:
        """Get count of jobs by type"""
        try:
            types = ["data_processing", "document_analysis", "entity_extraction", "medication_extraction", "custom"]
            counts = {}
            for job_type in types:
                type_key = f"jobs:type:{job_type}"
                count = await self.redis_client.scard(type_key)
                counts[job_type] = count
            return counts
        except Exception as e:
            logger.error(f"Failed to get jobs count by type: {e}")
            return {}
    
    async def get_jobs_count_by_priority(self) -> Dict[str, int]:
        """Get count of jobs by priority"""
        try:
            priorities = ["low", "normal", "high", "critical"]
            counts = {}
            for priority in priorities:
                priority_key = f"jobs:priority:{priority}"
                count = await self.redis_client.scard(priority_key)
                counts[priority] = count
            return counts
        except Exception as e:
            logger.error(f"Failed to get jobs count by priority: {e}")
            return {}
    
    async def _add_to_indexes(self, job_id: str, job_data: Dict[str, Any]):
        """Add job to various indexes"""
        try:
            # Status index
            status = job_data.get("status")
            if status:
                await self.redis_client.sadd(f"jobs:status:{status}", job_id)
            
            # Type index
            job_type = job_data.get("job_type")
            if job_type:
                await self.redis_client.sadd(f"jobs:type:{job_type}", job_id)
            
            # Priority index
            priority = job_data.get("priority")
            if priority:
                await self.redis_client.sadd(f"jobs:priority:{priority}", job_id)
            
            # Parent job index
            parent_job_id = job_data.get("parent_job_id")
            if parent_job_id:
                await self.redis_client.sadd(f"jobs:parent:{parent_job_id}", job_id)
            
            # Worker index
            worker_id = job_data.get("worker_id")
            if worker_id:
                await self.redis_client.sadd(f"jobs:worker:{worker_id}", job_id)
                
        except Exception as e:
            logger.error(f"Failed to add job {job_id} to indexes: {e}")
    
    async def _remove_from_indexes(self, job_id: str, job_data: Dict[str, Any]):
        """Remove job from various indexes"""
        try:
            # Status index
            status = job_data.get("status")
            if status:
                await self.redis_client.srem(f"jobs:status:{status}", job_id)
            
            # Type index
            job_type = job_data.get("job_type")
            if job_type:
                await self.redis_client.srem(f"jobs:type:{job_type}", job_id)
            
            # Priority index
            priority = job_data.get("priority")
            if priority:
                await self.redis_client.srem(f"jobs:priority:{priority}", job_id)
            
            # Parent job index
            parent_job_id = job_data.get("parent_job_id")
            if parent_job_id:
                await self.redis_client.srem(f"jobs:parent:{parent_job_id}", job_id)
            
            # Worker index
            worker_id = job_data.get("worker_id")
            if worker_id:
                await self.redis_client.srem(f"jobs:worker:{worker_id}", job_id)
                
        except Exception as e:
            logger.error(f"Failed to remove job {job_id} from indexes: {e}")
    
    async def update_job_status(self, job_id: str, old_status: str, new_status: str):
        """Update job status in indexes"""
        try:
            # Remove from old status index
            await self.redis_client.srem(f"jobs:status:{old_status}", job_id)
            # Add to new status index
            await self.redis_client.sadd(f"jobs:status:{new_status}", job_id)
        except Exception as e:
            logger.error(f"Failed to update job status indexes for {job_id}: {e}")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
