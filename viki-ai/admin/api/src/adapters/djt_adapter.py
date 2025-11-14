"""
Distributed Job Tracking Adapter for Admin API

This adapter implements the DJT port using the shared DJT client,
following the adapter pattern in hexagonal architecture.
"""

from typing import Dict, Any
from viki_shared.utils.logger import getLogger
from shared.infrastructure.adapters.djt_client import get_djt_client
from shared.domain.models.djt_models import PipelineStatusUpdate
from contracts.djt_contracts import DJTPort
from settings import Settings

logger = getLogger(__name__)


class DJTAdapter(DJTPort):
    """
    Adapter for Distributed Job Tracking operations using the shared DJT client.
    
    This adapter implements the DJT port interface and uses the shared
    DJT client infrastructure to communicate with the DJT service.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the DJT adapter.
        
        Args:
            settings: Application settings containing DJT configuration
        """
        self.settings = settings
        self._client = get_djt_client(
            base_url=settings.DJT_API_URL,
            cloud_provider=settings.CLOUD_PROVIDER,
            timeout=30.0
        )
        logger.info(f"DJT Adapter initialized with base_url: {settings.DJT_API_URL}")

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
        logger.info(f"Getting job pipelines for run_id: {run_id}")
        return await self._client.get_job_pipelines(run_id)

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
        logger.info(f"Updating pipeline status for job_id: {job_id}, pipeline_id: {pipeline_id}")
        return await self._client.pipeline_status_update(job_id, pipeline_id, pipeline_data)

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
        logger.info(f"Creating job for job_id: {job_id}")
        return await self._client.create_job(job_id, job_data)

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check against the DJT service.
        
        Returns:
            Dictionary containing health check response
            
        Raises:
            Exception: If the health check fails
        """
        logger.debug("Performing DJT health check")
        return await self._client.health_check()