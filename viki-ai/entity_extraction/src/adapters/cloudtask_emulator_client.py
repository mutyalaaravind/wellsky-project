import json
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from util.custom_logger import getLogger
from util.json_utils import DateTimeEncoder

LOGGER = getLogger(__name__)


class CloudTaskEmulatorClient:
    """
    Client for interacting with the Cloud Task Emulator via HTTP API.
    
    This client communicates with the emulator service running separately
    and does not require direct access to the emulator codebase.
    """
    
    def __init__(self, emulator_url: str):
        self.emulator_url = emulator_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def create_task(
        self,
        project: str,
        location: str,
        queue: str,
        task_name: str,
        url: str,
        payload: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        headers: Optional[Dict[str, str]] = None,
        service_account_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new task in the emulator.
        
        Args:
            project: GCP project ID
            location: GCP location
            queue: Queue name
            task_name: Unique task name
            url: Target URL for the task
            payload: JSON payload to send
            schedule_time: When to execute the task (None for immediate)
            headers: Additional HTTP headers
            service_account_email: Service account email for identity token generation
            
        Returns:
            Task creation response
        """
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
                "schedule_time": schedule_time.isoformat() if schedule_time else None,
                "service_account_email": service_account_email
            }
        }
        
        try:
            # Send to emulator
            response = await self.client.post(
                f"{self.emulator_url}/v2/projects/{project}/locations/{location}/queues/{queue}/tasks",
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
    
    async def list_tasks(
        self,
        project: str,
        location: str,
        queue: str
    ) -> Dict[str, Any]:
        """List tasks in a queue."""
        try:
            response = await self.client.get(
                f"{self.emulator_url}/v2/projects/{project}/locations/{location}/queues/{queue}/tasks"
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list tasks: {response.status_code} - {response.text}")
            
            return response.json()
            
        except httpx.ConnectError as e:
            LOGGER.error(f"Failed to connect to Cloud Task Emulator at {self.emulator_url}: {str(e)}")
            raise Exception(f"Cloud Task Emulator is not running at {self.emulator_url}")
        except Exception as e:
            LOGGER.error(f"Error listing tasks from emulator: {str(e)}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get emulator status."""
        try:
            response = await self.client.get(f"{self.emulator_url}/status")
            
            if response.status_code != 200:
                raise Exception(f"Failed to get status: {response.status_code} - {response.text}")
            
            return response.json()
            
        except httpx.ConnectError as e:
            LOGGER.error(f"Failed to connect to Cloud Task Emulator at {self.emulator_url}: {str(e)}")
            raise Exception(f"Cloud Task Emulator is not running at {self.emulator_url}")
        except Exception as e:
            LOGGER.error(f"Error getting status from emulator: {str(e)}")
            raise
    
    async def clear_tasks(self) -> Dict[str, Any]:
        """Clear all tasks (for testing)."""
        try:
            response = await self.client.delete(f"{self.emulator_url}/tasks")
            
            if response.status_code != 200:
                raise Exception(f"Failed to clear tasks: {response.status_code} - {response.text}")
            
            return response.json()
            
        except httpx.ConnectError as e:
            LOGGER.error(f"Failed to connect to Cloud Task Emulator at {self.emulator_url}: {str(e)}")
            raise Exception(f"Cloud Task Emulator is not running at {self.emulator_url}")
        except Exception as e:
            LOGGER.error(f"Error clearing tasks from emulator: {str(e)}")
            raise
    
    # Queue Management Methods
    
    async def queue_exists(self, project: str, location: str, queue: str) -> bool:
        """
        Check if a queue exists in the emulator.
        
        Args:
            project: GCP project ID
            location: GCP location
            queue: Queue name
            
        Returns:
            True if queue exists, False otherwise
        """
        try:
            response = await self.client.get(
                f"{self.emulator_url}/queues/{project}/{location}/{queue}"
            )
            
            return response.status_code == 200
            
        except httpx.ConnectError as e:
            LOGGER.error(f"Failed to connect to Cloud Task Emulator at {self.emulator_url}: {str(e)}")
            return False
        except Exception as e:
            LOGGER.error(f"Error checking queue existence in emulator: {str(e)}")
            return False
    
    async def create_queue(self, project: str, location: str, queue: str) -> bool:
        """
        Create a queue in the emulator.
        
        Args:
            project: GCP project ID
            location: GCP location
            queue: Queue name
            
        Returns:
            True if queue was created successfully, False otherwise
        """
        try:
            payload = {
                "project": project,
                "location": location,
                "queue": queue,
                "rate_limits": {
                    "max_dispatches_per_second": 100
                },
                "retry_config": {
                    "max_attempts": 3
                }
            }
            
            response = await self.client.post(
                f"{self.emulator_url}/queues",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                LOGGER.info(f"Successfully created queue in emulator: {queue}")
                return True
            else:
                LOGGER.error(f"Failed to create queue in emulator: {response.status_code} - {response.text}")
                return False
            
        except httpx.ConnectError as e:
            LOGGER.error(f"Failed to connect to Cloud Task Emulator at {self.emulator_url}: {str(e)}")
            return False
        except Exception as e:
            LOGGER.error(f"Error creating queue in emulator: {str(e)}")
            return False
    
    async def list_queues(self, project: str, location: str) -> list[str]:
        """
        List all queues in the emulator for a given project and location.
        
        Args:
            project: GCP project ID
            location: GCP location
            
        Returns:
            List of queue names
        """
        try:
            response = await self.client.get(
                f"{self.emulator_url}/queues/{project}/{location}"
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract queue names from response
                if isinstance(data, dict) and "queues" in data:
                    return [q.get("name", "") for q in data["queues"] if q.get("name")]
                elif isinstance(data, list):
                    return [q.get("name", "") for q in data if q.get("name")]
                else:
                    return []
            else:
                LOGGER.error(f"Failed to list queues from emulator: {response.status_code} - {response.text}")
                return []
            
        except httpx.ConnectError as e:
            LOGGER.error(f"Failed to connect to Cloud Task Emulator at {self.emulator_url}: {str(e)}")
            return []
        except Exception as e:
            LOGGER.error(f"Error listing queues from emulator: {str(e)}")
            return []
