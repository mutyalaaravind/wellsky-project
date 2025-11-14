import pytest
import asyncio
import uuid
from datetime import datetime
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from adapters.redis_adapter import RedisAdapter
from models.job import Job, JobStatus, JobType, JobPriority


@pytest.mark.integration
class TestRedisIntegration:
    """Integration tests for Redis adapter"""
    
    @pytest.fixture
    async def redis_adapter(self):
        """Create a Redis adapter for testing"""
        adapter = RedisAdapter()
        
        # Test connection
        is_connected = await adapter.ping()
        if not is_connected:
            pytest.skip("Redis is not available for integration testing")
        
        yield adapter
        
        # Cleanup
        await adapter.close()
    
    @pytest.mark.asyncio
    async def test_redis_connection(self, redis_adapter):
        """Test basic Redis connection"""
        # Test ping
        result = await redis_adapter.ping()
        assert result is True, "Redis connection should be successful"
    
    @pytest.mark.asyncio
    async def test_set_and_get_job(self, redis_adapter):
        """Test creating and retrieving a job from Redis"""
        # Create a test job
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "name": "Test Redis Job",
            "job_type": "data_processing",
            "status": "pending",
            "priority": "normal",
            "progress": 0.0,
            "payload": {"test": "data", "number": 42},
            "metadata": {"source": "integration_test"},
            "created_at": datetime.utcnow().isoformat(),
            "max_retries": 3,
            "retry_count": 0,
            "depends_on": [],
            "sub_job_ids": [],
            "is_parent_job": False
        }
        
        # Store the job in Redis
        success = await redis_adapter.set_job(job_id, job_data)
        assert success is True, "Job should be stored successfully"
        
        # Retrieve the job from Redis
        retrieved_job = await redis_adapter.get_job(job_id)
        assert retrieved_job is not None, "Job should be retrieved successfully"
        
        # Verify the data matches
        assert retrieved_job["id"] == job_id
        assert retrieved_job["name"] == "Test Redis Job"
        assert retrieved_job["job_type"] == "data_processing"
        assert retrieved_job["status"] == "pending"
        assert retrieved_job["priority"] == "normal"
        assert retrieved_job["payload"]["test"] == "data"
        assert retrieved_job["payload"]["number"] == 42
        assert retrieved_job["metadata"]["source"] == "integration_test"
        
        # Clean up
        await redis_adapter.delete_job(job_id)
    
    @pytest.mark.asyncio
    async def test_job_indexes(self, redis_adapter):
        """Test that jobs are properly indexed by status, type, and priority"""
        # Create multiple test jobs
        jobs = []
        for i in range(3):
            job_id = str(uuid.uuid4())
            job_data = {
                "id": job_id,
                "name": f"Test Job {i}",
                "job_type": "entity_extraction" if i % 2 == 0 else "document_analysis",
                "status": "pending" if i < 2 else "running",
                "priority": "high" if i == 0 else "normal",
                "progress": 0.0,
                "payload": {"test": f"data_{i}"},
                "metadata": {},
                "created_at": datetime.utcnow().isoformat(),
                "max_retries": 3,
                "retry_count": 0,
                "depends_on": [],
                "sub_job_ids": [],
                "is_parent_job": False
            }
            jobs.append((job_id, job_data))
            
            # Store the job
            success = await redis_adapter.set_job(job_id, job_data)
            assert success is True
        
        # Test status index
        pending_jobs = await redis_adapter.get_jobs_by_status("pending")
        running_jobs = await redis_adapter.get_jobs_by_status("running")
        
        assert len(pending_jobs) >= 2, "Should have at least 2 pending jobs"
        assert len(running_jobs) >= 1, "Should have at least 1 running job"
        
        # Test type index
        entity_jobs = await redis_adapter.get_jobs_by_type("entity_extraction")
        doc_jobs = await redis_adapter.get_jobs_by_type("document_analysis")
        
        assert len(entity_jobs) >= 2, "Should have at least 2 entity extraction jobs"
        assert len(doc_jobs) >= 1, "Should have at least 1 document analysis job"
        
        # Test priority index
        high_priority_jobs = await redis_adapter.get_jobs_by_priority("high")
        normal_priority_jobs = await redis_adapter.get_jobs_by_priority("normal")
        
        assert len(high_priority_jobs) >= 1, "Should have at least 1 high priority job"
        assert len(normal_priority_jobs) >= 2, "Should have at least 2 normal priority jobs"
        
        # Clean up
        for job_id, _ in jobs:
            await redis_adapter.delete_job(job_id)
    
    @pytest.mark.asyncio
    async def test_job_counts(self, redis_adapter):
        """Test job count statistics"""
        # Create test jobs with different statuses
        test_jobs = []
        statuses = ["pending", "running", "completed", "failed"]
        
        for i, status in enumerate(statuses):
            job_id = str(uuid.uuid4())
            job_data = {
                "id": job_id,
                "name": f"Count Test Job {i}",
                "job_type": "custom",
                "status": status,
                "priority": "normal",
                "progress": 100.0 if status == "completed" else 0.0,
                "payload": {},
                "metadata": {},
                "created_at": datetime.utcnow().isoformat(),
                "max_retries": 3,
                "retry_count": 0,
                "depends_on": [],
                "sub_job_ids": [],
                "is_parent_job": False
            }
            test_jobs.append((job_id, job_data))
            
            # Store the job
            success = await redis_adapter.set_job(job_id, job_data)
            assert success is True
        
        # Get counts by status
        status_counts = await redis_adapter.get_jobs_count_by_status()
        
        # Verify counts (should be at least 1 for each status we created)
        assert status_counts.get("pending", 0) >= 1
        assert status_counts.get("running", 0) >= 1
        assert status_counts.get("completed", 0) >= 1
        assert status_counts.get("failed", 0) >= 1
        
        # Clean up
        for job_id, _ in test_jobs:
            await redis_adapter.delete_job(job_id)
    
    @pytest.mark.asyncio
    async def test_parent_child_jobs(self, redis_adapter):
        """Test parent-child job relationships"""
        # Create parent job
        parent_job_id = str(uuid.uuid4())
        parent_job_data = {
            "id": parent_job_id,
            "name": "Parent Job",
            "job_type": "document_analysis",
            "status": "pending",
            "priority": "normal",
            "progress": 0.0,
            "payload": {"document_id": "doc123"},
            "metadata": {},
            "created_at": datetime.utcnow().isoformat(),
            "max_retries": 3,
            "retry_count": 0,
            "depends_on": [],
            "sub_job_ids": [],
            "is_parent_job": True
        }
        
        # Create child jobs
        child_job_ids = []
        for i in range(2):
            child_job_id = str(uuid.uuid4())
            child_job_data = {
                "id": child_job_id,
                "name": f"Child Job {i}",
                "job_type": "entity_extraction",
                "status": "pending",
                "priority": "normal",
                "progress": 0.0,
                "payload": {"parent_doc": "doc123"},
                "metadata": {},
                "created_at": datetime.utcnow().isoformat(),
                "max_retries": 3,
                "retry_count": 0,
                "depends_on": [],
                "parent_job_id": parent_job_id,
                "sub_job_ids": [],
                "is_parent_job": False
            }
            child_job_ids.append(child_job_id)
            
            # Store child job
            success = await redis_adapter.set_job(child_job_id, child_job_data)
            assert success is True
        
        # Update parent job with child IDs
        parent_job_data["sub_job_ids"] = child_job_ids
        success = await redis_adapter.set_job(parent_job_id, parent_job_data)
        assert success is True
        
        # Test retrieving children by parent
        children = await redis_adapter.get_jobs_by_parent(parent_job_id)
        assert len(children) == 2, "Should have 2 child jobs"
        assert all(child_id in children for child_id in child_job_ids)
        
        # Clean up
        await redis_adapter.delete_job(parent_job_id)
        for child_job_id in child_job_ids:
            await redis_adapter.delete_job(child_job_id)
    
    @pytest.mark.asyncio
    async def test_job_update_status_indexes(self, redis_adapter):
        """Test that status indexes are updated when job status changes"""
        # Create a job
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "name": "Status Update Test Job",
            "job_type": "data_processing",
            "status": "pending",
            "priority": "normal",
            "progress": 0.0,
            "payload": {},
            "metadata": {},
            "created_at": datetime.utcnow().isoformat(),
            "max_retries": 3,
            "retry_count": 0,
            "depends_on": [],
            "sub_job_ids": [],
            "is_parent_job": False
        }
        
        # Store the job
        success = await redis_adapter.set_job(job_id, job_data)
        assert success is True
        
        # Verify it's in pending index
        pending_jobs = await redis_adapter.get_jobs_by_status("pending")
        assert job_id in pending_jobs
        
        # Update status to running
        await redis_adapter.update_job_status(job_id, "pending", "running")
        
        # Verify it's moved to running index
        pending_jobs = await redis_adapter.get_jobs_by_status("pending")
        running_jobs = await redis_adapter.get_jobs_by_status("running")
        
        assert job_id not in pending_jobs, "Job should be removed from pending index"
        assert job_id in running_jobs, "Job should be added to running index"
        
        # Clean up
        await redis_adapter.delete_job(job_id)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-m", "integration"])
