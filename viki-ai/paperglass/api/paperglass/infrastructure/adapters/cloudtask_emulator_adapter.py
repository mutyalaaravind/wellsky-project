import json
import uuid
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from paperglass.log import getLogger
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils
from paperglass.infrastructure.ports import ICloudTaskPort

LOGGER = getLogger(__name__)


class CloudTaskEmulatorAdapter(ICloudTaskPort):
    """
    Adapter for Cloud Task Emulator that implements the same interface as CloudTaskAdapter.
    This can be used as a drop-in replacement for local development.
    """

    def __init__(self, project_id: str, emulator_url: str):
        self.project_id = project_id
        self.emulator_url = emulator_url.rstrip('/')
        self._http_client = None

        self.SPAN_BASE: str = "INFRA:CloudTaskEmulatorAdapter:"
        self.opentelemetry = OpenTelemetryUtils(self.SPAN_BASE)

    async def _get_http_client(self):
        """Get or create the HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def _create_emulator_task(
        self,
        location: str,
        queue: str,
        task_name: str,
        url: str,
        payload: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a task in the emulator."""
        if headers is None:
            headers = {}
        
        # Prepare task request
        task_request = {
            "task": {
                "name": task_name,
                "payload": {
                    "url": url,
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json",
                        **headers
                    },
                    "body": json.dumps(payload, cls=DateTimeEncoder)
                },
                "schedule_time": schedule_time.isoformat() if schedule_time else None
            }
        }
        
        try:
            client = await self._get_http_client()
            # Send to emulator
            response = await client.post(
                f"{self.emulator_url}/v2/projects/{self.project_id}/locations/{location}/queues/{queue}/tasks",
                json=task_request
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to create task: {response.status_code} - {response.text}")
            
            return response.json()
            
        except httpx.ConnectError as e:
            LOGGER.error(f"Failed to connect to Cloud Task Emulator at {self.emulator_url}: {str(e)}")
            raise Exception(f"Cloud Task Emulator is not running at {self.emulator_url}. Please start the emulator service.")
        except Exception as e:
            LOGGER.error(f"Error creating task in emulator: {str(e)}")
            raise

    async def create_task(self, token, location, service_account_email, queue, url, payload):
        """Legacy create_task method for backward compatibility."""
        extra = {
            "project_id": self.project_id,
            "location": location,
            "queue": queue,
            "url": url,
            "payload": payload,
            "emulator_url": self.emulator_url
        }
        
        LOGGER.info(f"Creating task via emulator for queue: {queue}, url: {url}", extra=extra)

        try:
            # Generate task name
            task_name = f"task-{uuid.uuid4().hex[:8]}"
            
            # Prepare headers
            headers = {}
            if token:
                headers["Authorization2"] = f"Bearer {token}"
            
            response = await self._create_emulator_task(
                location=location,
                queue=queue,
                task_name=task_name,
                url=url,
                payload=payload,
                headers=headers
            )
            
            LOGGER.debug(f"Created task via emulator: {task_name}")
            return response
            
        except Exception as e:
            LOGGER.error(f"Error creating task via emulator: {str(e)}")
            raise

    async def create_task_v2(self, location, service_account_email, queue, url, payload, http_headers: Dict[str, str] = {}, token: str = None, schedule_time: datetime = None):
        """Enhanced create_task_v2 method with full emulator support."""
        extra = {
            "project_id": self.project_id,
            "location": location,
            "queue": queue,
            "url": url,
            "payload": payload,
            "schedule_time": schedule_time.isoformat() if schedule_time else None,
            "emulator_url": self.emulator_url
        }
        
        LOGGER.info(f"Creating task (v2) via emulator for queue: {queue}, url: {url}", extra=extra)

        try:
            # Generate task name
            task_name = f"task-v2-{uuid.uuid4().hex[:8]}"
            
            # Merge headers
            headers = http_headers.copy() if http_headers else {}
            if token:
                headers["Authorization2"] = f"Bearer {token}"
            
            response = await self._create_emulator_task(
                location=location,
                queue=queue,
                task_name=task_name,
                url=url,
                payload=payload,
                schedule_time=schedule_time,
                headers=headers
            )
            
            LOGGER.debug(f"Created task (v2) via emulator: {task_name}")
            return response
            
        except Exception as e:
            LOGGER.error(f"Error creating task (v2) via emulator: {str(e)}")
            raise
