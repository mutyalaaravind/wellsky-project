import json
from datetime import datetime
from typing import Dict, Any, Optional
from util.custom_logger import getLogger
import settings

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
            service_account_email: Service account email for OIDC authentication
            
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
            
            response = await client.create_task(
                project=self.project_id,
                location=location,
                queue=queue,
                task_name=task_name,
                url=url,
                payload=payload,
                schedule_time=schedule_time,
                headers=headers
            )
            
            LOGGER.debug(f"Created task via emulator: {task_name}")
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
                "body": json.dumps(payload).encode()
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

    async def close(self):
        """Close any open connections."""
        if self._emulator_client:
            await self._emulator_client.close()
            self._emulator_client = None
