from typing import Dict, Any, Optional, List
from google.cloud import tasks_v2
from google.protobuf.duration_pb2 import Duration
from proto.message import MessageToDict

from util.custom_logger import getLogger
import settings

LOGGER = getLogger(__name__)


class CloudTaskAdapter:
    """
    Adapter for Google Cloud Tasks that can create and manage Cloud Task queues dynamically.
    This adapter provides functionality to provision new queues on the fly instead of 
    requiring Terraform configuration.
    """

    def __init__(self, project_id: Optional[str] = None, location: Optional[str] = None):
        """
        Initialize the CloudTaskAdapter.
        
        Args:
            project_id: Google Cloud project ID. If None, uses settings value.
            location: GCP location. If None, uses settings value.
        """
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self.location = location or settings.GCP_LOCATION_2
        self._client = None
        
    def _get_client(self) -> tasks_v2.CloudTasksClient:
        """Get or create the Cloud Tasks client."""
        if self._client is None:
            self._client = tasks_v2.CloudTasksClient()
        return self._client

    async def create_queue(
        self,
        queue_name: str,
        location: Optional[str] = None,
        max_concurrent_dispatches: Optional[int] = None,
        max_dispatches_per_second: Optional[float] = None,
        max_retry_duration_seconds: Optional[int] = None,
        min_backoff_seconds: Optional[int] = None,
        max_backoff_seconds: Optional[int] = None,
        max_attempts: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new Cloud Task queue.
        
        Args:
            queue_name: Name of the queue to create
            location: GCP location (uses instance default if None)
            max_concurrent_dispatches: Maximum number of concurrent dispatches
            max_dispatches_per_second: Maximum dispatches per second
            max_retry_duration_seconds: Maximum retry duration in seconds
            min_backoff_seconds: Minimum backoff duration in seconds
            max_backoff_seconds: Maximum backoff duration in seconds
            max_attempts: Maximum number of retry attempts
            
        Returns:
            Queue creation response as dictionary
            
        Raises:
            Exception: If there's an error creating the queue
        """
        effective_location = location or self.location
        
        extra = {
            "project_id": self.project_id,
            "location": effective_location,
            "queue_name": queue_name,
            "max_concurrent_dispatches": max_concurrent_dispatches,
            "max_dispatches_per_second": max_dispatches_per_second,
            "max_retry_duration_seconds": max_retry_duration_seconds,
            "min_backoff_seconds": min_backoff_seconds,
            "max_backoff_seconds": max_backoff_seconds,
            "max_attempts": max_attempts
        }
        
        LOGGER.info(f"Creating Cloud Task queue: {queue_name} in location: {effective_location}", extra=extra)
        
        try:
            client = self._get_client()
            parent = f"projects/{self.project_id}/locations/{effective_location}"
            
            # Build queue configuration
            queue = {
                "name": f"projects/{self.project_id}/locations/{effective_location}/queues/{queue_name}"
            }
            
            
            # Configure rate limits if provided
            rate_limits = {}
            if max_concurrent_dispatches is not None:
                rate_limits["max_concurrent_dispatches"] = max_concurrent_dispatches
            if max_dispatches_per_second is not None:
                rate_limits["max_dispatches_per_second"] = max_dispatches_per_second
                
            if rate_limits:
                queue["rate_limits"] = rate_limits
            
            # Configure retry settings if provided
            retry_config = {}
            if max_retry_duration_seconds is not None:
                retry_config["max_retry_duration"] = Duration(seconds=max_retry_duration_seconds)
            if min_backoff_seconds is not None:
                retry_config["min_backoff"] = Duration(seconds=min_backoff_seconds)
            if max_backoff_seconds is not None:
                retry_config["max_backoff"] = Duration(seconds=max_backoff_seconds)
            if max_attempts is not None:
                retry_config["max_attempts"] = max_attempts
                
            if retry_config:
                queue["retry_config"] = retry_config
            
            # Create the queue
            response = client.create_queue(parent=parent, queue=queue)
            
            extra.update({
                "created_queue_name": response.name,
                "queue_state": response.state.name if response.state else "UNKNOWN"
            })
            LOGGER.info(f"Successfully created Cloud Task queue: {response.name}", extra=extra)
            
            return MessageToDict(response._pb)
            
        except Exception as e:
            extra.update({"error": str(e)})
            LOGGER.error(f"Error creating Cloud Task queue {queue_name}: {str(e)}", extra=extra)
            raise Exception(f"Error creating Cloud Task queue {queue_name}: {str(e)}")

    async def get_queue(self, queue_name: str, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific queue.
        
        Args:
            queue_name: Name of the queue
            location: GCP location (uses instance default if None)
            
        Returns:
            Queue information as dictionary, None if not found
        """
        effective_location = location or self.location
        
        try:
            client = self._get_client()
            queue_path = f"projects/{self.project_id}/locations/{effective_location}/queues/{queue_name}"
            
            response = client.get_queue(name=queue_path)
            return MessageToDict(response._pb)
            
        except Exception as e:
            if "not found" in str(e).lower():
                return None
            LOGGER.error(f"Error getting queue {queue_name}: {str(e)}")
            raise Exception(f"Error getting queue {queue_name}: {str(e)}")

    async def list_queues(self, location: Optional[str] = None, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        List all queues in the specified location.
        
        Args:
            location: GCP location (uses instance default if None)
            page_size: Maximum number of queues to return
            
        Returns:
            List of queue information dictionaries
        """
        effective_location = location or self.location
        
        try:
            client = self._get_client()
            parent = f"projects/{self.project_id}/locations/{effective_location}"
            
            request = tasks_v2.ListQueuesRequest(
                parent=parent,
                page_size=page_size
            )
            
            page_result = client.list_queues(request=request)
            queues = []
            
            for response in page_result:
                queues.append(MessageToDict(response._pb))
                
            return queues
            
        except Exception as e:
            LOGGER.error(f"Error listing queues in location {effective_location}: {str(e)}")
            raise Exception(f"Error listing queues in location {effective_location}: {str(e)}")

    async def update_queue(
        self,
        queue_name: str,
        location: Optional[str] = None,
        max_concurrent_dispatches: Optional[int] = None,
        max_dispatches_per_second: Optional[float] = None,
        max_retry_duration_seconds: Optional[int] = None,
        min_backoff_seconds: Optional[int] = None,
        max_backoff_seconds: Optional[int] = None,
        max_attempts: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update an existing Cloud Task queue configuration.
        
        Args:
            queue_name: Name of the queue to update
            location: GCP location (uses instance default if None)
            max_concurrent_dispatches: Maximum number of concurrent dispatches
            max_dispatches_per_second: Maximum dispatches per second
            max_retry_duration_seconds: Maximum retry duration in seconds
            min_backoff_seconds: Minimum backoff duration in seconds
            max_backoff_seconds: Maximum backoff duration in seconds
            max_attempts: Maximum number of retry attempts
            
        Returns:
            Queue update response as dictionary
        """
        effective_location = location or self.location
        
        extra = {
            "project_id": self.project_id,
            "location": effective_location,
            "queue_name": queue_name
        }
        
        LOGGER.info(f"Updating Cloud Task queue: {queue_name}", extra=extra)
        
        try:
            client = self._get_client()
            queue_path = f"projects/{self.project_id}/locations/{effective_location}/queues/{queue_name}"
            
            # Get current queue configuration
            current_queue = client.get_queue(name=queue_path)
            
            # Update rate limits if provided
            if max_concurrent_dispatches is not None or max_dispatches_per_second is not None:
                if not current_queue.rate_limits:
                    current_queue.rate_limits = tasks_v2.RateLimits()
                
                if max_concurrent_dispatches is not None:
                    current_queue.rate_limits.max_concurrent_dispatches = max_concurrent_dispatches
                if max_dispatches_per_second is not None:
                    current_queue.rate_limits.max_dispatches_per_second = max_dispatches_per_second
            
            # Update retry configuration if provided
            if any([max_retry_duration_seconds, min_backoff_seconds, max_backoff_seconds, max_attempts]):
                if not current_queue.retry_config:
                    current_queue.retry_config = tasks_v2.RetryConfig()
                
                if max_retry_duration_seconds is not None:
                    current_queue.retry_config.max_retry_duration = Duration(seconds=max_retry_duration_seconds)
                if min_backoff_seconds is not None:
                    current_queue.retry_config.min_backoff = Duration(seconds=min_backoff_seconds)
                if max_backoff_seconds is not None:
                    current_queue.retry_config.max_backoff = Duration(seconds=max_backoff_seconds)
                if max_attempts is not None:
                    current_queue.retry_config.max_attempts = max_attempts
            
            # Update the queue
            response = client.update_queue(queue=current_queue)
            
            extra.update({
                "updated_queue_name": response.name,
                "queue_state": response.state.name if response.state else "UNKNOWN"
            })
            LOGGER.info(f"Successfully updated Cloud Task queue: {response.name}", extra=extra)
            
            return MessageToDict(response._pb)
            
        except Exception as e:
            extra.update({"error": str(e)})
            LOGGER.error(f"Error updating Cloud Task queue {queue_name}: {str(e)}", extra=extra)
            raise Exception(f"Error updating Cloud Task queue {queue_name}: {str(e)}")

    async def delete_queue(self, queue_name: str, location: Optional[str] = None) -> bool:
        """
        Delete a Cloud Task queue.
        
        Args:
            queue_name: Name of the queue to delete
            location: GCP location (uses instance default if None)
            
        Returns:
            True if queue was deleted, False if not found
        """
        effective_location = location or self.location
        
        extra = {
            "project_id": self.project_id,
            "location": effective_location,
            "queue_name": queue_name
        }
        
        LOGGER.info(f"Deleting Cloud Task queue: {queue_name}", extra=extra)
        
        try:
            client = self._get_client()
            queue_path = f"projects/{self.project_id}/locations/{effective_location}/queues/{queue_name}"
            
            client.delete_queue(name=queue_path)
            LOGGER.info(f"Successfully deleted Cloud Task queue: {queue_name}", extra=extra)
            return True
            
        except Exception as e:
            if "not found" in str(e).lower():
                LOGGER.warning(f"Queue {queue_name} not found for deletion", extra=extra)
                return False
            extra.update({"error": str(e)})
            LOGGER.error(f"Error deleting Cloud Task queue {queue_name}: {str(e)}", extra=extra)
            raise Exception(f"Error deleting Cloud Task queue {queue_name}: {str(e)}")

    async def pause_queue(self, queue_name: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Pause a Cloud Task queue.
        
        Args:
            queue_name: Name of the queue to pause
            location: GCP location (uses instance default if None)
            
        Returns:
            Queue pause response as dictionary
        """
        effective_location = location or self.location
        
        try:
            client = self._get_client()
            queue_path = f"projects/{self.project_id}/locations/{effective_location}/queues/{queue_name}"
            
            response = client.pause_queue(name=queue_path)
            LOGGER.info(f"Successfully paused Cloud Task queue: {queue_name}")
            
            return MessageToDict(response._pb)
            
        except Exception as e:
            LOGGER.error(f"Error pausing Cloud Task queue {queue_name}: {str(e)}")
            raise Exception(f"Error pausing Cloud Task queue {queue_name}: {str(e)}")

    async def resume_queue(self, queue_name: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Resume a paused Cloud Task queue.
        
        Args:
            queue_name: Name of the queue to resume
            location: GCP location (uses instance default if None)
            
        Returns:
            Queue resume response as dictionary
        """
        effective_location = location or self.location
        
        try:
            client = self._get_client()
            queue_path = f"projects/{self.project_id}/locations/{effective_location}/queues/{queue_name}"
            
            response = client.resume_queue(name=queue_path)
            LOGGER.info(f"Successfully resumed Cloud Task queue: {queue_name}")
            
            return MessageToDict(response._pb)
            
        except Exception as e:
            LOGGER.error(f"Error resuming Cloud Task queue {queue_name}: {str(e)}")
            raise Exception(f"Error resuming Cloud Task queue {queue_name}: {str(e)}")

    async def queue_exists(self, queue_name: str, location: Optional[str] = None) -> bool:
        """
        Check if a queue exists.
        
        Args:
            queue_name: Name of the queue to check
            location: GCP location (uses instance default if None)
            
        Returns:
            True if queue exists, False otherwise
        """
        queue_info = await self.get_queue(queue_name, location)
        return queue_info is not None

    async def create_queue_if_not_exists(
        self,
        queue_name: str,
        location: Optional[str] = None,
        max_concurrent_dispatches: Optional[int] = None,
        max_dispatches_per_second: Optional[float] = None,
        max_retry_duration_seconds: Optional[int] = None,
        min_backoff_seconds: Optional[int] = None,
        max_backoff_seconds: Optional[int] = None,
        max_attempts: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a queue only if it doesn't already exist.
        
        Args:
            queue_name: Name of the queue to create
            location: GCP location (uses instance default if None)
            max_concurrent_dispatches: Maximum number of concurrent dispatches
            max_dispatches_per_second: Maximum dispatches per second
            max_retry_duration_seconds: Maximum retry duration in seconds
            min_backoff_seconds: Minimum backoff duration in seconds
            max_backoff_seconds: Maximum backoff duration in seconds
            max_attempts: Maximum number of retry attempts
            
        Returns:
            Queue information as dictionary (either existing or newly created)
        """
        # Check if queue already exists
        existing_queue = await self.get_queue(queue_name, location)
        if existing_queue:
            LOGGER.info(f"Queue {queue_name} already exists, returning existing queue info")
            return existing_queue
        
        # Create the queue since it doesn't exist
        return await self.create_queue(
            queue_name=queue_name,
            location=location,
            max_concurrent_dispatches=max_concurrent_dispatches,
            max_dispatches_per_second=max_dispatches_per_second,
            max_retry_duration_seconds=max_retry_duration_seconds,
            min_backoff_seconds=min_backoff_seconds,
            max_backoff_seconds=max_backoff_seconds,
            max_attempts=max_attempts
        )

    def close(self):
        """Close the client connection."""
        if self._client:
            self._client.transport.close()
            self._client = None


# Convenience functions for easy usage
async def create_cloud_task_queue(
    queue_name: str,
    location: Optional[str] = None,
    project_id: Optional[str] = None,
    max_concurrent_dispatches: Optional[int] = None,
    max_dispatches_per_second: Optional[float] = None,
    max_retry_duration_seconds: Optional[int] = None,
    min_backoff_seconds: Optional[int] = None,
    max_backoff_seconds: Optional[int] = None,
    max_attempts: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function to create a Cloud Task queue.
    
    Args:
        queue_name: Name of the queue to create
        location: GCP location
        project_id: Google Cloud project ID
        max_concurrent_dispatches: Maximum number of concurrent dispatches
        max_dispatches_per_second: Maximum dispatches per second
        max_retry_duration_seconds: Maximum retry duration in seconds
        min_backoff_seconds: Minimum backoff duration in seconds
        max_backoff_seconds: Maximum backoff duration in seconds
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Queue creation response as dictionary
    """
    adapter = CloudTaskAdapter(project_id=project_id, location=location)
    try:
        return await adapter.create_queue(
            queue_name=queue_name,
            location=location,
            max_concurrent_dispatches=max_concurrent_dispatches,
            max_dispatches_per_second=max_dispatches_per_second,
            max_retry_duration_seconds=max_retry_duration_seconds,
            min_backoff_seconds=min_backoff_seconds,
            max_backoff_seconds=max_backoff_seconds,
            max_attempts=max_attempts
        )
    finally:
        adapter.close()


async def ensure_cloud_task_queue_exists(
    queue_name: str,
    location: Optional[str] = None,
    project_id: Optional[str] = None,
    max_concurrent_dispatches: Optional[int] = None,
    max_dispatches_per_second: Optional[float] = None,
    max_retry_duration_seconds: Optional[int] = None,
    min_backoff_seconds: Optional[int] = None,
    max_backoff_seconds: Optional[int] = None,
    max_attempts: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function to ensure a Cloud Task queue exists (create if it doesn't).
    
    Args:
        queue_name: Name of the queue
        location: GCP location
        project_id: Google Cloud project ID
        max_concurrent_dispatches: Maximum number of concurrent dispatches
        max_dispatches_per_second: Maximum dispatches per second
        max_retry_duration_seconds: Maximum retry duration in seconds
        min_backoff_seconds: Minimum backoff duration in seconds
        max_backoff_seconds: Maximum backoff duration in seconds
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Queue information as dictionary
    """
    adapter = CloudTaskAdapter(project_id=project_id, location=location)
    try:
        return await adapter.create_queue_if_not_exists(
            queue_name=queue_name,
            location=location,
            max_concurrent_dispatches=max_concurrent_dispatches,
            max_dispatches_per_second=max_dispatches_per_second,
            max_retry_duration_seconds=max_retry_duration_seconds,
            min_backoff_seconds=min_backoff_seconds,
            max_backoff_seconds=max_backoff_seconds,
            max_attempts=max_attempts
        )
    finally:
        adapter.close()