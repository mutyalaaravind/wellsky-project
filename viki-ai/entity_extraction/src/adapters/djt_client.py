"""
Distributed Job Tracking (DJT) Client Adapter

This adapter handles communication with the distributed job tracking service,
including authentication for cloud environments.
"""

import httpx
from typing import Dict, Any, Optional
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from util.google_oidc_auth import get_oidc_headers
from models.djt_models import PipelineStatusUpdate
import settings

LOGGER = getLogger(__name__)

class DistributedJobTracking:
    """Adapter for interacting with the Distributed Job Tracking service."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the DJT client adapter.
        
        Args:
            base_url: Base URL for the DJT service. If None, uses settings value.
        """
        self.base_url = base_url or settings.DJT_API_URL
        self.cloud_provider = settings.CLOUD_PROVIDER
    
    async def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for DJT API requests.
        
        Returns:
            Dictionary of HTTP headers, including authentication for cloud environments
        """
        # Use OIDC headers which handle conditional authentication based on CLOUD_PROVIDER
        headers = await get_oidc_headers(target_audience=self.base_url)
        LOGGER.debug(f"Got headers for DJT API request (cloud_provider: {self.cloud_provider})")
        return headers
    
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
        try:
            extra = {
                "run_id": run_id,
                "djt_base_url": self.base_url,
                "cloud_provider": self.cloud_provider
            }
            
            # Construct the URL for the DJT API
            url = f"{self.base_url}/api/v1/jobs/{run_id}/pipelines"
            
            LOGGER.info(f"Fetching job pipelines for run_id: {run_id} from DJT API", extra=extra)
            
            # Get headers with conditional authentication
            headers = await self._get_headers()
            
            # Make HTTP request to distributed job tracking service
            # Set timeout from settings
            timeout = httpx.Timeout(settings.DJT_API_TIMEOUT, read=settings.DJT_API_TIMEOUT)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                
                # Check for successful response
                if response.status_code == 200:
                    try:
                        result = await response.json()
                    except TypeError:
                        # Handle case where json() returns dict directly instead of coroutine
                        result = response.json()
                    LOGGER.debug(f"Successfully retrieved job pipelines for run_id: {run_id}", extra)
                    return result
                else:
                    # Log the error and raise an exception with the status code
                    error_detail = f"DJT API returned status {response.status_code}: {response.text}"
                    extra.update({"status_code": response.status_code, "response_text": response.text})
                    LOGGER.warning(f"DJT API error for run_id: {run_id}", extra)
                    
                    # Create an exception that preserves the original status code
                    error = Exception(error_detail)
                    error.status_code = response.status_code
                    error.response_text = response.text
                    raise error
                    
        except httpx.RequestError as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Network error when calling DJT API for run_id: {run_id}", extra)
            raise Exception(f"Unable to connect to distributed job tracking service: {str(e)}")
        except Exception as e:
            # If it's already our custom exception with status_code, re-raise it
            if hasattr(e, 'status_code'):
                raise e
            
            # Otherwise, log and wrap as a generic error
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Unexpected error calling DJT API for run_id: {run_id}", extra)
            raise Exception(f"Error communicating with distributed job tracking service: {str(e)}")
    
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
        extra = {
            "job_id": job_id,
            "pipeline_id": pipeline_id,
            "djt_base_url": self.base_url,
            "cloud_provider": self.cloud_provider,            
        }
        
        try:            
            # Construct the URL for the DJT API
            url = f"{self.base_url}/api/v1/jobs/{job_id}/pipelines/{pipeline_id}/status"
            
            LOGGER.info(f"Updating pipeline status for job_id: {job_id}, pipeline_id: {pipeline_id}", extra)
            
            # Get headers with conditional authentication
            headers = await self._get_headers()

            body = pipeline_data.model_dump()

            extra.update({                
                "http_request": {
                    "method": "POST",
                    "url": url,
                    "headers": headers,
                    "body": body
                }
            })
            
            # Make HTTP request to distributed job tracking service
            # Set timeout from settings
            timeout = httpx.Timeout(settings.DJT_API_TIMEOUT, read=settings.DJT_API_TIMEOUT)
            async with httpx.AsyncClient(timeout=timeout) as client:
                import json
                LOGGER.debug(f"Sending pipeline status update for job_id: {job_id}, pipeline_id: {pipeline_id}: {json.dumps(extra, indent=2)}", extra=extra)

                response = await client.post(url, headers=headers, json=body)

                extra.update({
                    "http_response": {
                        "status_code": response.status_code,
                        "response_text": response.text
                    }
                })
                
                # Check for successful response
                if response.status_code == 200:
                    try:
                        result = await response.json()
                    except TypeError:
                        # Handle case where json() returns dict directly instead of coroutine
                        result = response.json()
                    LOGGER.debug(f"Successfully updated pipeline status for job_id: {job_id}, pipeline_id: {pipeline_id}", extra)
                    return result
                else:
                    # Log the error and raise an exception with the status code
                    error_detail = f"DJT API returned status {response.status_code}: {response.text}"
                    extra.update({"status_code": response.status_code, "response_text": response.text})
                    LOGGER.warning(f"DJT API error for pipeline status update: job_id: {job_id}, pipeline_id: {pipeline_id}", extra=extra)
                    
                    # Create an exception that preserves the original status code
                    error = Exception(error_detail)
                    error.status_code = response.status_code
                    error.response_text = response.text
                    raise error
                    
        except httpx.RequestError as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Network error when calling DJT API for pipeline status update: job_id: {job_id}, pipeline_id: {pipeline_id}", extra=extra)
            raise Exception(f"Unable to connect to distributed job tracking service: {str(e)}")
        except Exception as e:
            # If it's already our custom exception with status_code, re-raise it
            if hasattr(e, 'status_code'):
                raise e
            
            # Otherwise, log and wrap as a generic error
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Unexpected error calling DJT API for pipeline status update: job_id: {job_id}, pipeline_id: {pipeline_id}", extra=extra)
            raise Exception(f"Error communicating with distributed job tracking service: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check against the DJT service.
        
        Returns:
            Dictionary containing health check response
            
        Raises:
            Exception: If the health check fails
        """
        try:
            extra = {
                "djt_base_url": self.base_url,
                "cloud_provider": self.cloud_provider
            }
            
            # Construct the health check URL
            url = f"{self.base_url}/health"
            
            LOGGER.debug("Performing DJT service health check", extra)
            
            # Get headers with conditional authentication
            headers = await self._get_headers()
            
            # Make HTTP request
            # Set timeout from settings
            timeout = httpx.Timeout(settings.DJT_API_TIMEOUT, read=settings.DJT_API_TIMEOUT)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    try:
                        result = await response.json()
                    except TypeError:
                        # Handle case where json() returns dict directly instead of coroutine
                        result = response.json()
                    LOGGER.debug("DJT service health check successful", extra)
                    return result
                else:
                    error_detail = f"DJT health check failed with status {response.status_code}: {response.text}"
                    extra.update({"status_code": response.status_code, "response_text": response.text})
                    LOGGER.warning("DJT service health check failed", extra)
                    
                    error = Exception(error_detail)
                    error.status_code = response.status_code
                    error.response_text = response.text
                    raise error
                    
        except httpx.RequestError as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error("Network error during DJT health check", extra)
            raise Exception(f"Unable to connect to distributed job tracking service for health check: {str(e)}")
        except Exception as e:
            if hasattr(e, 'status_code'):
                raise e
            
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error("Unexpected error during DJT health check", extra)
            raise Exception(f"Error during DJT service health check: {str(e)}")


# Factory function for easy instantiation
def get_djt_client(base_url: Optional[str] = None) -> DistributedJobTracking:
    """
    Get an instance of the DistributedJobTracking client.
    
    Args:
        base_url: Optional base URL override
        
    Returns:
        DistributedJobTracking instance
    """
    return DistributedJobTracking(base_url=base_url)
