"""
Distributed Job Tracking (DJT) Client Adapter - Shared Library

This adapter handles communication with the distributed job tracking service,
including authentication for cloud environments. This is a shared implementation
that can be used across all services.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from shared.domain.models.djt_models import PipelineStatusUpdate
from shared.application.ports.djt_port import DJTPort
from shared.infrastructure.utils.exception import exceptionToMap
from viki_shared.utils.gcp_auth import get_service_account_identity_token

logger = logging.getLogger(__name__)

class DistributedJobTracking(DJTPort):
    """Adapter for interacting with the Distributed Job Tracking service."""
    
    def __init__(self, base_url: str, cloud_provider: str, timeout: float = 30.0):
        """
        Initialize the DJT client adapter.
        
        Args:
            base_url: Base URL for the DJT service
            cloud_provider: Cloud provider identifier (for auth)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.cloud_provider = cloud_provider
        self.timeout = timeout
    
    async def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for DJT API requests with authentication.

        For cloud environments (cloud_provider != "local"), adds service account
        identity token for authenticated service-to-service communication.

        Returns:
            Dictionary of HTTP headers with optional authentication token
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # In cloud environments (non-local), add authentication token
        if self.cloud_provider != "local":
            try:
                token = await get_service_account_identity_token(
                    target_audience=self.base_url
                )
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    logger.debug(f"Added authentication header for DJT API request (cloud_provider: {self.cloud_provider})")
            except Exception as e:
                logger.warning(f"Failed to get authentication token for DJT: {e}. Proceeding without auth.")
        else:
            logger.debug(f"Skipping authentication for local development (cloud_provider: {self.cloud_provider})")

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
            
            logger.info(f"Fetching job pipelines for run_id: {run_id} from DJT API", extra=extra)
            
            # Get headers with conditional authentication
            headers = await self._get_headers()
            
            # Make HTTP request to distributed job tracking service
            timeout = httpx.Timeout(self.timeout, read=self.timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                
                # Check for successful response
                if response.status_code == 200:
                    try:
                        result = await response.json()
                    except TypeError:
                        # Handle case where json() returns dict directly instead of coroutine
                        result = response.json()
                    logger.debug(f"Successfully retrieved job pipelines for run_id: {run_id}", extra)
                    return result
                else:
                    # Log the error and raise an exception with the status code
                    error_detail = f"DJT API returned status {response.status_code}: {response.text}"
                    extra.update({"status_code": response.status_code, "response_text": response.text})
                    logger.warning(f"DJT API error for run_id: {run_id}", extra)
                    
                    # Create an exception that preserves the original status code
                    error = Exception(error_detail)
                    error.status_code = response.status_code
                    error.response_text = response.text
                    raise error
                    
        except httpx.RequestError as e:
            extra.update({"error": exceptionToMap(e)})
            logger.error(f"Network error when calling DJT API for run_id: {run_id}", extra)
            raise Exception(f"Unable to connect to distributed job tracking service: {str(e)}")
        except Exception as e:
            # If it's already our custom exception with status_code, re-raise it
            if hasattr(e, 'status_code'):
                raise e
            
            # Otherwise, log and wrap as a generic error
            extra.update({"error": exceptionToMap(e)})
            logger.error(f"Unexpected error calling DJT API for run_id: {run_id}", extra)
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
            
            logger.info(f"Updating pipeline status for job_id: {job_id}, pipeline_id: {pipeline_id}", extra)
            
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
            timeout = httpx.Timeout(self.timeout, read=self.timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                import json
                logger.debug(f"Sending pipeline status update for job_id: {job_id}, pipeline_id: {pipeline_id}: {json.dumps(extra, indent=2)}", extra=extra)

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
                    logger.debug(f"Successfully updated pipeline status for job_id: {job_id}, pipeline_id: {pipeline_id}", extra)
                    return result
                else:
                    # Log the error and raise an exception with the status code
                    error_detail = f"DJT API returned status {response.status_code}: {response.text}"
                    extra.update({"status_code": response.status_code, "response_text": response.text})
                    logger.warning(f"DJT API error for pipeline status update: job_id: {job_id}, pipeline_id: {pipeline_id}", extra=extra)
                    
                    # Create an exception that preserves the original status code
                    error = Exception(error_detail)
                    error.status_code = response.status_code
                    error.response_text = response.text
                    raise error
                    
        except httpx.RequestError as e:
            extra.update({"error": exceptionToMap(e)})
            logger.error(f"Network error when calling DJT API for pipeline status update: job_id: {job_id}, pipeline_id: {pipeline_id}", extra)
            raise Exception(f"Unable to connect to distributed job tracking service: {str(e)}")
        except Exception as e:
            # If it's already our custom exception with status_code, re-raise it
            if hasattr(e, 'status_code'):
                raise e
            
            # Otherwise, log and wrap as a generic error
            extra.update({"error": exceptionToMap(e)})
            logger.error(f"Unexpected error calling DJT API for pipeline status update: job_id: {job_id}, pipeline_id: {pipeline_id}", extra)
            raise Exception(f"Error communicating with distributed job tracking service: {str(e)}")

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
        extra = {
            "job_id": job_id,
            "djt_base_url": self.base_url,
            "cloud_provider": self.cloud_provider,            
        }
        
        try:            
            # Construct the URL for the DJT API
            url = f"{self.base_url}/api/v1/jobs/"
            
            logger.info(f"Creating job for job_id: {job_id}", extra)
            
            # Get headers with conditional authentication
            headers = await self._get_headers()

            # Add job_id to the job data
            body = {**job_data, "id": job_id}

            extra.update({                
                "http_request": {
                    "method": "POST",
                    "url": url,
                    "headers": headers,
                    "body": body
                }
            })
            
            # Make HTTP request to distributed job tracking service
            timeout = httpx.Timeout(self.timeout, read=self.timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.debug(f"Creating job for job_id: {job_id}", extra=extra)

                response = await client.post(url, headers=headers, json=body)

                extra.update({
                    "http_response": {
                        "status_code": response.status_code,
                        "response_text": response.text
                    }
                })
                
                # Check for successful response
                if response.status_code in [200, 201]:
                    try:
                        result = await response.json()
                    except TypeError:
                        # Handle case where json() returns dict directly instead of coroutine
                        result = response.json()
                    logger.debug(f"Successfully created job for job_id: {job_id}", extra)
                    return result
                else:
                    # Log the error and raise an exception with the status code
                    error_detail = f"DJT API returned status {response.status_code}: {response.text}"
                    extra.update({"status_code": response.status_code, "response_text": response.text})
                    logger.warning(f"DJT API error for job creation: job_id: {job_id}", extra=extra)
                    
                    # Create an exception that preserves the original status code
                    error = Exception(error_detail)
                    error.status_code = response.status_code
                    error.response_text = response.text
                    raise error
                    
        except httpx.RequestError as e:
            extra.update({"error": exceptionToMap(e)})
            logger.error(f"Network error when calling DJT API for job creation: job_id: {job_id}", extra=extra)
            raise Exception(f"Unable to connect to distributed job tracking service: {str(e)}")
        except Exception as e:
            # If it's already our custom exception with status_code, re-raise it
            if hasattr(e, 'status_code'):
                raise e
            
            # Otherwise, log and wrap as a generic error
            extra.update({"error": exceptionToMap(e)})
            logger.error(f"Unexpected error calling DJT API for job creation: job_id: {job_id}", extra=extra)
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
            
            logger.debug("Performing DJT service health check", extra)
            
            # Get headers with conditional authentication
            headers = await self._get_headers()
            
            # Make HTTP request
            timeout = httpx.Timeout(self.timeout, read=self.timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    try:
                        result = await response.json()
                    except TypeError:
                        # Handle case where json() returns dict directly instead of coroutine
                        result = response.json()
                    logger.debug("DJT service health check successful", extra)
                    return result
                else:
                    error_detail = f"DJT health check failed with status {response.status_code}: {response.text}"
                    extra.update({"status_code": response.status_code, "response_text": response.text})
                    logger.warning("DJT service health check failed", extra)
                    
                    error = Exception(error_detail)
                    error.status_code = response.status_code
                    error.response_text = response.text
                    raise error
                    
        except httpx.RequestError as e:
            extra.update({"error": exceptionToMap(e)})
            logger.error("Network error during DJT health check", extra)
            raise Exception(f"Unable to connect to distributed job tracking service for health check: {str(e)}")
        except Exception as e:
            if hasattr(e, 'status_code'):
                raise e
            
            extra.update({"error": exceptionToMap(e)})
            logger.error("Unexpected error during DJT health check", extra)
            raise Exception(f"Error during DJT service health check: {str(e)}")


# Factory function for easy instantiation
def get_djt_client(base_url: str, cloud_provider: str, timeout: float = 30.0) -> DistributedJobTracking:
    """
    Get an instance of the DistributedJobTracking client.
    
    Args:
        base_url: DJT service base URL
        cloud_provider: Cloud provider identifier
        timeout: Request timeout in seconds
        
    Returns:
        DistributedJobTracking instance
    """
    return DistributedJobTracking(base_url=base_url, cloud_provider=cloud_provider, timeout=timeout)