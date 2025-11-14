"""
Distributed Job Tracking Port Interface - Shared Library

This port defines the interface for distributed job tracking operations
following hexagonal architecture principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Protocol
from shared.domain.models.djt_models import PipelineStatusUpdate


class DJTPort(Protocol):
    """
    Port interface for Distributed Job Tracking operations.
    
    This port defines the contract for interacting with the DJT service
    and can be implemented by different adapters (e.g., HTTP client, mock, etc.)
    """

    async def get_job_pipelines(self, run_id: str) -> Dict[str, Any]:
        """
        Get job pipeline status from the distributed job tracking service.
        
        Args:
            run_id: The job run ID to query
            
        Returns:
            Dictionary containing the job pipeline status response
            
        Raises:
            Exception: If there's an error communicating with the DJT service
        """
        ...

    async def pipeline_status_update(self, job_id: str, pipeline_id: str, pipeline_data: PipelineStatusUpdate) -> Dict[str, Any]:
        """
        Update pipeline status in the distributed job tracking service.
        
        Args:
            job_id: The job ID (used as run_id)
            pipeline_id: The pipeline ID to update
            pipeline_data: PipelineStatusUpdate model containing pipeline status update data
            
        Returns:
            Dictionary containing the pipeline status update response
            
        Raises:
            Exception: If there's an error communicating with the DJT service
        """
        ...

    async def create_job(self, job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job in the distributed job tracking service.
        
        Args:
            job_id: The job ID to create
            job_data: Dictionary containing job creation data
            
        Returns:
            Dictionary containing the job creation response
            
        Raises:
            Exception: If there's an error communicating with the DJT service
        """
        ...

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check against the DJT service.
        
        Returns:
            Dictionary containing health check response
            
        Raises:
            Exception: If the health check fails
        """
        ...