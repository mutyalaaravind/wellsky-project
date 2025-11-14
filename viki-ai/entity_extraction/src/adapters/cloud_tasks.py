import json
from datetime import datetime
from typing import Dict, Any, Optional, TYPE_CHECKING
from util.custom_logger import getLogger
from util.json_utils import JsonUtil
import settings

if TYPE_CHECKING:
    from models.general import TaskParameters

LOGGER = getLogger(__name__)


class CloudTaskAdapter:
    """
    Adapter for Google Cloud Tasks that automatically switches between
    the local emulator and real Cloud Tasks based on CLOUD_PROVIDER setting.
    """

    def __init__(self, project_id: str = None):
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self._emulator_client = None
        
    async def _get_emulator_client(self):
        """Get or create the emulator client."""
        if self._emulator_client is None:
            from adapters.cloudtask_emulator_client import CloudTaskEmulatorClient
            self._emulator_client = CloudTaskEmulatorClient(
                emulator_url=settings.CLOUDTASK_EMULATOR_URL
            )
        return self._emulator_client

    async def create_task(
        self,
        location: str,
        queue: str,
        url: str,
        payload: Dict[str, Any],
        task_name: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        headers: Optional[Dict[str, str]] = None,
        service_account_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a task using either the emulator or real Cloud Tasks.
        
        Args:
            location: GCP location (e.g., 'us-central1')
            queue: Queue name
            url: Target URL for the task
            payload: JSON payload to send
            task_name: Optional task name (auto-generated if None)
            schedule_time: When to execute the task (None for immediate)
            headers: Additional HTTP headers
            
        Returns:
            Task creation response
        """
        extra = {
            "project_id": self.project_id,
            "location": location,
            "queue": queue,
            "url": url,
            "payload": payload,
            "task_name": task_name,
            "schedule_time": schedule_time.isoformat() if schedule_time else None,
            "cloud_provider": settings.CLOUD_PROVIDER,
            "service_account_email": service_account_email
        }
        
        LOGGER.info(f"Creating task for queue: {queue}, url: {url}", extra=extra)

        if settings.CLOUD_PROVIDER == "local":
            return await self._create_task_emulator(
                location, queue, url, payload, task_name, schedule_time, headers, service_account_email
            )
        else:
            return await self._create_task_cloud(
                location, queue, url, payload, task_name, schedule_time, headers, service_account_email
            )

    async def _create_task_emulator(
        self,
        location: str,
        queue: str,
        url: str,
        payload: Dict[str, Any],
        task_name: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        headers: Optional[Dict[str, str]] = None,
        service_account_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a task using the local emulator."""
        try:
            client = await self._get_emulator_client()
            
            # Generate task name if not provided
            if task_name is None:
                import uuid
                task_name = f"task-{uuid.uuid4().hex[:8]}"
            
            # Get service account email - prioritize passed parameter over settings
            effective_service_account_email = service_account_email
            if not effective_service_account_email and hasattr(settings, 'SERVICE_ACCOUNT_EMAIL'):
                effective_service_account_email = settings.SERVICE_ACCOUNT_EMAIL
            
            response = await client.create_task(
                project=self.project_id,
                location=location,
                queue=queue,
                task_name=task_name,
                url=url,
                payload=payload,
                schedule_time=schedule_time,
                headers=headers,
                service_account_email=effective_service_account_email
            )
            
            extra = {
                "task_name": task_name,
                "service_account_email": effective_service_account_email,
                "url": url
            }
            LOGGER.debug(f"Created task via emulator: {task_name}", extra=extra)
            return response
            
        except Exception as e:
            LOGGER.error(f"Error creating task via emulator: {str(e)}")
            raise

    async def _create_task_cloud(
        self,
        location: str,
        queue: str,
        url: str,
        payload: Dict[str, Any],
        task_name: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        headers: Optional[Dict[str, str]] = None,
        service_account_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a task using real Google Cloud Tasks."""
        try:
            from google.cloud import tasks_v2
            from google.protobuf.timestamp_pb2 import Timestamp
            from proto.message import MessageToDict
            
            extra = {
                "project_id": self.project_id,
                "location": location,
                "queue": queue,
                "url": url,
                "task_name": task_name,
                "schedule_time": schedule_time.isoformat() if schedule_time else None,
                "service_account_email": service_account_email
            }
            
            LOGGER.info(f"Creating Cloud Task for queue: {queue}, url: {url}", extra=extra)
            
            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(self.project_id, location, queue)
            
            # Prepare headers
            task_headers = {
                "Content-Type": "application/json"
            }
            if headers:
                task_headers.update(headers)
            
            # Prepare HTTP request
            http_request = {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": task_headers,
                "body": JsonUtil.dumps(payload).encode()
            }
            
            # Add service account authentication if configured
            # Prioritize passed parameter over settings
            effective_service_account_email = service_account_email
            if not effective_service_account_email and hasattr(settings, 'SERVICE_ACCOUNT_EMAIL'):
                effective_service_account_email = settings.SERVICE_ACCOUNT_EMAIL
                
            if effective_service_account_email:
                http_request["oidc_token"] = {
                    "service_account_email": effective_service_account_email
                }
            
            # Prepare task
            task = {
                "http_request": http_request
            }
            
            # Add schedule time if provided
            if schedule_time:
                timestamp = Timestamp()
                timestamp.FromDatetime(schedule_time)
                task["schedule_time"] = timestamp
            
            # Create the task
            response = client.create_task(parent=parent, task=task)
            
            extra.update({
                "task_name": response.name,
                "response": MessageToDict(response._pb)
            })
            LOGGER.debug(f"Created task via Cloud Tasks: {response.name}", extra=extra)
            
            return MessageToDict(response._pb)
            
        except Exception as e:
            extra = {
                "project_id": self.project_id,
                "location": location,
                "queue": queue,
                "url": url,
                "error": str(e)
            }
            LOGGER.error(f"Error creating task via Cloud Tasks: {str(e)}", extra=extra)
            raise

    async def create_task_for_next_step(
        self,
        task_id: str,
        task_parameters: 'TaskParameters',
        location: str = None,
        queue: str = None,
        service_account_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method for creating tasks for next pipeline steps.
        
        Args:
            task_id: ID of the task to execute
            task_parameters: TaskParameters object
            location: GCP location (uses settings default if None)
            queue: Queue name (uses settings default if None)
            
        Returns:
            Task creation response
        """
        # Use default values from settings
        location = location or settings.GCP_LOCATION_2
        queue = queue or settings.DEFAULT_TASK_QUEUE
        
        # Build the target URL
        base_url = settings.SELF_API_URL
        url = f"{base_url}/api/pipeline/{task_parameters.pipeline_scope}/{task_parameters.pipeline_key}/{task_id}/run"
        
        # Generate unique task name
        import uuid
        task_name = f"{task_id}-{task_parameters.run_id}-{uuid.uuid4().hex[:8]}"

        LOGGER.debug(f"Creating task for next step: {task_id} with parameters: {task_parameters.dict()}", extra={
            "task_id": task_id,
            "task_parameters": task_parameters.dict(),
            "location": location,
            "queue": queue,
            "url": url,
            "task_name": task_name,
            "service_account_email": service_account_email
        })
        
        return await self.create_task(
            location=location,
            queue=queue,
            url=url,
            payload=task_parameters.dict(),
            task_name=task_name,
            service_account_email=service_account_email
        )

    # Queue Management Methods
    
    async def queue_exists(self, queue_name: str, location: str = None) -> bool:
        """
        Check if a queue exists.
        
        Args:
            queue_name: Name of the queue to check
            location: GCP location (uses settings default if None)
            
        Returns:
            True if queue exists, False otherwise
        """
        location = location or settings.GCP_LOCATION_2
        
        extra = {
            "operation": "queue_exists",
            "queue_name": queue_name,
            "location": location,
            "project_id": self.project_id
        }
        
        try:
            if settings.CLOUD_PROVIDER == "local":
                # Check with emulator
                client = await self._get_emulator_client()
                return await client.queue_exists(
                    project=self.project_id,
                    location=location,
                    queue=queue_name
                )
            else:
                # Check with real Cloud Tasks
                return await self._queue_exists_cloud(queue_name, location)
                
        except Exception as e:
            LOGGER.error(f"Error checking if queue exists: {str(e)}", extra=extra)
            return False
    
    async def create_queue(self, queue_name: str, location: str = None) -> bool:
        """
        Create a new queue.
        
        Args:
            queue_name: Name of the queue to create
            location: GCP location (uses settings default if None)
            
        Returns:
            True if queue was created successfully, False otherwise
        """
        location = location or settings.GCP_LOCATION_2
        
        extra = {
            "operation": "create_queue",
            "queue_name": queue_name,
            "location": location,
            "project_id": self.project_id
        }
        
        try:
            LOGGER.info(f"Creating queue: {queue_name}", extra=extra)
            
            if settings.CLOUD_PROVIDER == "local":
                # Create with emulator
                client = await self._get_emulator_client()
                return await client.create_queue(
                    project=self.project_id,
                    location=location,
                    queue=queue_name
                )
            else:
                # Create with real Cloud Tasks
                return await self._create_queue_cloud(queue_name, location)
                
        except Exception as e:
            LOGGER.error(f"Error creating queue: {str(e)}", extra=extra)
            return False
    
    async def list_queues(self, location: str = None) -> list[str]:
        """
        List all queues in the specified location.
        
        Args:
            location: GCP location (uses settings default if None)
            
        Returns:
            List of queue names
        """
        location = location or settings.GCP_LOCATION_2
        
        extra = {
            "operation": "list_queues",
            "location": location,
            "project_id": self.project_id
        }
        
        try:
            if settings.CLOUD_PROVIDER == "local":
                # List with emulator
                client = await self._get_emulator_client()
                return await client.list_queues(
                    project=self.project_id,
                    location=location
                )
            else:
                # List with real Cloud Tasks
                return await self._list_queues_cloud(location)
                
        except Exception as e:
            LOGGER.error(f"Error listing queues: {str(e)}", extra=extra)
            return []
    
    async def _queue_exists_cloud(self, queue_name: str, location: str) -> bool:
        """Check if queue exists using real Google Cloud Tasks."""
        try:
            from google.cloud import tasks_v2
            
            client = tasks_v2.CloudTasksClient()
            queue_path = client.queue_path(self.project_id, location, queue_name)
            
            try:
                client.get_queue(request={"name": queue_path})
                return True
            except Exception:
                return False
                
        except Exception as e:
            LOGGER.error(f"Error checking queue existence in cloud: {str(e)}")
            return False
    
    async def _create_queue_cloud(self, queue_name: str, location: str) -> bool:
        """Create queue using real Google Cloud Tasks."""
        try:
            from google.cloud import tasks_v2
            
            client = tasks_v2.CloudTasksClient()
            parent = client.location_path(self.project_id, location)
            
            queue = {
                "name": client.queue_path(self.project_id, location, queue_name),
                "rate_limits": {
                    "max_dispatches_per_second": 100
                },
                "retry_config": {
                    "max_attempts": 3
                }
            }
            
            client.create_queue(request={"parent": parent, "queue": queue})
            LOGGER.info(f"Successfully created queue in cloud: {queue_name}")
            return True
            
        except Exception as e:
            LOGGER.error(f"Error creating queue in cloud: {str(e)}")
            return False
    
    async def _list_queues_cloud(self, location: str) -> list[str]:
        """List queues using real Google Cloud Tasks."""
        try:
            from google.cloud import tasks_v2
            
            client = tasks_v2.CloudTasksClient()
            parent = client.location_path(self.project_id, location)
            
            queues = []
            for queue in client.list_queues(request={"parent": parent}):
                # Extract queue name from full path
                queue_name = queue.name.split('/')[-1]
                queues.append(queue_name)
            
            return queues
            
        except Exception as e:
            LOGGER.error(f"Error listing queues in cloud: {str(e)}")
            return []
    
    @property
    def location(self) -> str:
        """Get the default location for this adapter."""
        return getattr(settings, 'GCP_LOCATION_2', 'us-central1')

    async def close(self):
        """Close any open connections."""
        if self._emulator_client:
            await self._emulator_client.close()
            self._emulator_client = None
