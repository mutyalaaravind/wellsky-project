import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel

class CloudTaskEmulatorClient:
    """
    Client for interacting with the Cloud Task Emulator.
    
    This client provides the same interface as Google Cloud Tasks
    but routes requests to the local emulator for development.
    """
    
    def __init__(self, emulator_url: str = "http://localhost:30001"):
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
        headers: Optional[Dict[str, str]] = None
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
                    "body": json.dumps(payload)
                },
                "schedule_time": schedule_time.isoformat() if schedule_time else None
            }
        }
        
        # Send to emulator
        response = await self.client.post(
            f"{self.emulator_url}/v2/projects/{project}/locations/{location}/queues/{queue}/tasks",
            json=task_request
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to create task: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def list_tasks(
        self,
        project: str,
        location: str,
        queue: str
    ) -> Dict[str, Any]:
        """List tasks in a queue."""
        response = await self.client.get(
            f"{self.emulator_url}/v2/projects/{project}/locations/{location}/queues/{queue}/tasks"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to list tasks: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get emulator status."""
        response = await self.client.get(f"{self.emulator_url}/status")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get status: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def clear_tasks(self) -> Dict[str, Any]:
        """Clear all tasks (for testing)."""
        response = await self.client.delete(f"{self.emulator_url}/tasks")
        
        if response.status_code != 200:
            raise Exception(f"Failed to clear tasks: {response.status_code} - {response.text}")
        
        return response.json()


class CloudTaskAdapter:
    """
    Adapter that provides a unified interface for both real Cloud Tasks
    and the local emulator based on environment configuration.
    """
    
    def __init__(self, use_emulator: bool = True, emulator_url: str = "http://localhost:30001"):
        self.use_emulator = use_emulator
        
        if use_emulator:
            self.client = CloudTaskEmulatorClient(emulator_url)
        else:
            # In production, this would initialize the real Google Cloud Tasks client
            raise NotImplementedError("Real Cloud Tasks client not implemented yet")
    
    async def create_task(
        self,
        project: str,
        location: str,
        queue: str,
        task_name: str,
        url: str,
        payload: Dict[str, Any],
        schedule_time: Optional[datetime] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a task using either emulator or real Cloud Tasks."""
        if self.use_emulator:
            return await self.client.create_task(
                project, location, queue, task_name, url, payload, schedule_time, headers
            )
        else:
            # Real Cloud Tasks implementation would go here
            raise NotImplementedError("Real Cloud Tasks not implemented")
    
    async def close(self):
        """Close the underlying client."""
        if hasattr(self.client, 'close'):
            await self.client.close()
