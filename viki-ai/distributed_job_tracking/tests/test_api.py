import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

# Mock the Redis adapter before importing the main app
import sys
from unittest.mock import patch

# Mock the RedisAdapter
mock_redis_adapter = MagicMock()
mock_redis_adapter.ping = AsyncMock(return_value=True)
mock_redis_adapter.set_job = AsyncMock(return_value=True)
mock_redis_adapter.get_job = AsyncMock(return_value=None)

with patch('adapters.redis_adapter.RedisAdapter', return_value=mock_redis_adapter):
    from main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Distributed Job Tracking API"}


def test_create_job():
    """Test creating a job"""
    job_data = {
        "name": "Test Job",
        "job_type": "data_processing",
        "priority": "normal",
        "payload": {"test": "data"}
    }
    
    with patch('usecases.job_service.JobService.create_job') as mock_create:
        # Mock the job creation
        from models import Job
        mock_job = Job(
            name="Test Job",
            job_type="data_processing",
            priority="normal",
            payload={"test": "data"}
        )
        mock_create.return_value = mock_job
        
        response = client.post("/api/jobs/", json=job_data)
        assert response.status_code == 200
        assert "job" in response.json()
        assert response.json()["message"] == "Job created successfully"


def test_list_jobs():
    """Test listing jobs"""
    with patch('usecases.job_service.JobService.list_jobs') as mock_list:
        from models import JobListResponse
        mock_list.return_value = JobListResponse(
            jobs=[],
            total=0,
            page=1,
            page_size=50,
            has_next=False,
            has_prev=False
        )
        
        response = client.get("/api/jobs/")
        assert response.status_code == 200
        assert "jobs" in response.json()
        assert response.json()["total"] == 0


def test_get_job_stats():
    """Test getting job statistics"""
    with patch('usecases.tracking_service.TrackingService.get_job_stats') as mock_stats:
        mock_stats.return_value = {
            "total_jobs": 0,
            "active_jobs": 0,
            "pending_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0
        }
        
        response = client.get("/api/tracking/stats")
        assert response.status_code == 200
        assert "total_jobs" in response.json()


if __name__ == "__main__":
    pytest.main([__file__])
