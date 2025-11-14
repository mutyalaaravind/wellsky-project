import asyncio
import json
import logging
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import uvicorn
from contextlib import asynccontextmanager
import aiocache
import settings
from utils.json_utils import DateTimeEncoder
from utils.custom_logger import CustomLogger
from utils.exception import exceptionToMap

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = CustomLogger(__name__)

# Google Auth imports for identity token generation
try:
    from google.auth import impersonated_credentials
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    import google.auth
    has_google_auth = True
except ImportError:
    logger.warning("Google Auth library not available. Identity tokens will not be generated.")
    has_google_auth = False

# Task models
class TaskPayload(BaseModel):
    url: str
    method: str = "POST"
    headers: Dict[str, str] = {}
    body: str = ""

class Task(BaseModel):
    name: str
    payload: TaskPayload
    schedule_time: Optional[datetime] = None
    dispatch_deadline: Optional[timedelta] = None
    response_count: int = 0
    first_attempt_time: Optional[datetime] = None
    last_attempt_time: Optional[datetime] = None
    service_account_email: Optional[str] = None  # For generating identity tokens

class CreateTaskRequest(BaseModel):
    task: Task

# Global task storage (in production, this would be Redis or a database)
task_queue: List[Task] = []
task_history: List[Dict[str, Any]] = []

class CloudTaskEmulator:
    """
    Emulates Google Cloud Tasks behavior for local development.
    
    Features:
    - Asynchronous task execution
    - Task scheduling with delays
    - Retry logic with exponential backoff
    - Task queue management
    - HTTP task execution
    """
    
    def __init__(self):
        self.running = False
        self.worker_task = None
        self.http_client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT)
    
    @aiocache.cached(ttl=900)
    async def _generate_identity_token(self, service_account_email: str, target_audience: str) -> Optional[str]:
        """
        Generate an identity token for the specified service account.
        Uses Google Auth library to create real identity tokens.
        """
        if not has_google_auth:
            logger.warning("Google Auth library not available. Cannot generate identity token.")
            return None
        
        try:
            # Get default credentials
            credentials, project = google.auth.default()
            
            # Create impersonated credentials for the service account
            target_credentials = impersonated_credentials.Credentials(
                source_credentials=credentials,
                target_principal=service_account_email,
                target_scopes=[],  # Identity tokens don't need scopes
                delegates=[]
            )
            
            # Generate identity token
            request = Request()
            target_credentials.refresh(request)
            
            # Create identity token with target audience
            identity_token = target_credentials.token
            
            logger.debug(f"Generated identity token for {service_account_email} with audience {target_audience}")
            return identity_token
            
        except Exception as e:
            logger.error(f"Failed to generate identity token for {service_account_email}: {e}")
            return None
    
    async def start(self):
        """Start the task worker."""
        if not self.running:
            self.running = True
            self.worker_task = asyncio.create_task(self._worker_loop())
            logger.info("Cloud Task Emulator started")
    
    async def stop(self):
        """Stop the task worker."""
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        await self.http_client.aclose()
        logger.info("Cloud Task Emulator stopped")
    
    async def _worker_loop(self):
        """Main worker loop that processes tasks."""
        while self.running:
            try:
                await self._process_pending_tasks()
                await asyncio.sleep(settings.WORKER_CHECK_INTERVAL)  # Check for tasks every second
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(settings.WORKER_ERROR_DELAY)  # Wait longer on error
    
    async def _process_pending_tasks(self):
        """Process all pending tasks that are ready to execute."""
        current_time = datetime.utcnow()
        tasks_to_execute = []
        
        # Find tasks ready for execution
        for i, task in enumerate(task_queue):
            if task.schedule_time is None or task.schedule_time <= current_time:
                tasks_to_execute.append((i, task))
        
        # Execute tasks (remove from queue first to avoid duplicate execution)
        for i, task in reversed(tasks_to_execute):  # Reverse to maintain indices
            task_queue.pop(i)
            asyncio.create_task(self._execute_task(task))
    
    async def _execute_task(self, task: Task):
        """Execute a single task."""
        execution_start = datetime.utcnow()
        
        extra = {
            "task_name": task.name,
            "attempt_count": task.response_count + 1,
            "http_request": {
                "url": task.payload.url,
                "method": task.payload.method,
                "headers": task.payload.headers,
                "body": task.payload.body[:5000] if task.payload.body else None                
            },
            "service_account_email": task.service_account_email
        }
        
        try:
            
            logger.info(f"Executing task: {task.name}", extra=extra)
            
            # Update task metadata
            task.response_count += 1
            task.last_attempt_time = execution_start
            if task.first_attempt_time is None:
                task.first_attempt_time = execution_start
            
            # Prepare HTTP request
            headers = task.payload.headers.copy()
            if 'Content-Type' not in headers and task.payload.body:
                headers['Content-Type'] = 'application/json'
            
            # Generate and add identity token if service account email is provided
            if task.service_account_email:
                logger.debug(f"Service account email found: {task.service_account_email}, generating identity token", extra=extra)
                identity_token = await self._generate_identity_token(
                    service_account_email=task.service_account_email,
                    target_audience=task.payload.url
                )
                if identity_token:
                    headers['Authorization'] = f'Bearer {identity_token}'
                    extra.update({
                        "service_account_email": task.service_account_email,
                        "identity_token_generated": True
                    })
                    logger.info(f"Added identity token for service account {task.service_account_email}", extra=extra)
                else:
                    extra.update({
                        "service_account_email": task.service_account_email,
                        "identity_token_generated": False
                    })
                    logger.warning(f"Failed to generate identity token for service account {task.service_account_email}", extra=extra)
            else:
                logger.warning(f"No service account email provided for task {task.name}. Authorization header will not be added.", extra=extra)

            extra.get("http_request", {}).update({
                "headers": {k: v if k != 'Authorization' else 'Bearer [REDACTED]' for k, v in headers.items()},  # Redact token in logs
                "body": task.payload.body[:5000] if task.payload.body else None  # Truncate for logging
            })

            logger.debug(f"Task {task.name} HTTP request headers prepared", extra=extra)
            
            # Execute HTTP request
            response = await self.http_client.request(
                method=task.payload.method,
                url=task.payload.url,
                headers=headers,
                content=task.payload.body
            )
            
            execution_end = datetime.utcnow()
            execution_time = (execution_end - execution_start).total_seconds()
            
            # Log result
            if response.status_code < 400:
                extra.update({
                    "task_name": task.name,
                    "http_response": {
                        "status_code": response.status_code
                    },
                    "execution_time": execution_time,
                    "attempt_count": task.response_count
                })
                logger.info(f"Task {task.name} completed successfully in {execution_time:.2f}s (status: {response.status_code})", extra=extra)
                
                # Record successful execution
                task_history.append({
                    "task_name": task.name,
                    "status": "success",
                    "status_code": response.status_code,
                    "execution_time": execution_time,
                    "attempt_count": task.response_count,
                    "executed_at": execution_start.isoformat(),
                    "response_body": response.text[:1000] if response.text else None  # Truncate for storage
                })
            else:
                extra.update({
                    "task_name": task.name,
                    "http_response": {
                        "status_code": response.status_code,
                        "body": response.text[:500] if response.text else None
                    },                    
                    "attempt_count": task.response_count                    
                })
                logger.warning(f"Task {task.name} failed with status {response.status_code}", extra=extra)
                await self._handle_task_failure(task, response.status_code, response.text)
                
        except Exception as e:
            execution_end = datetime.utcnow()
            execution_time = (execution_end - execution_start).total_seconds()

            extra.update({"error": exceptionToMap(e)})
            
            logger.error(f"Task {task.name} failed with exception: {e}", extra=extra)
            logger.error("Execution task: %s", json.dumps(task.model_dump(), indent=2, cls=DateTimeEncoder), extra=extra)
            await self._handle_task_failure(task, 0, str(e))
    
    async def _handle_task_failure(self, task: Task, status_code: int, error_message: str):
        """Handle task failure with retry logic."""
        max_retries = settings.MAX_RETRIES
        
        if task.response_count < max_retries:
            # Calculate exponential backoff delay
            delay_seconds = min(settings.RETRY_BASE_DELAY ** task.response_count, settings.MAX_RETRY_DELAY)
            retry_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
            
            # Reschedule task
            task.schedule_time = retry_time
            task_queue.append(task)
            
            logger.info(f"Task {task.name} scheduled for retry {task.response_count}/{max_retries} in {delay_seconds}s")
        else:
            logger.error(f"Task {task.name} failed permanently after {max_retries} attempts")
            
            # Record permanent failure
            task_history.append({
                "task_name": task.name,
                "status": "failed",
                "status_code": status_code,
                "error_message": error_message,
                "attempt_count": task.response_count,
                "failed_at": datetime.utcnow().isoformat()
            })

# Global emulator instance
emulator = CloudTaskEmulator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifecycle of the emulator."""
    await emulator.start()
    yield
    await emulator.stop()

# FastAPI app
app = FastAPI(
    title="Cloud Task Emulator",
    description="Local emulator for Google Cloud Tasks",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "Cloud Task Emulator",
        "status": "running" if emulator.running else "stopped",
        "queue_size": len(task_queue),
        "completed_tasks": len(task_history)
    }

@app.post("/v2/projects/{project}/locations/{location}/queues/{queue}/tasks")
async def create_task(
    project: str,
    location: str, 
    queue: str,
    request: CreateTaskRequest
):
    """Create a new task (emulates Cloud Tasks API)."""
    try:
        task = request.task
        
        # Set default schedule time if not provided
        if task.schedule_time is None:
            task.schedule_time = datetime.utcnow()
        
        # Log the complete task data for debugging
        task_debug_extra = {
            "task_data": task.model_dump(),
            "service_account_email": task.service_account_email,
            "has_service_account": task.service_account_email is not None
        }
        logger.debug(f"Creating task with data: {json.dumps(task.model_dump(), indent=2, cls=DateTimeEncoder)}", extra=task_debug_extra)
        
        # Add to queue
        task_queue.append(task)
        
        create_extra = {
            "task_name": task.name,
            "queue": queue,
            "project": project,
            "location": location,
            "schedule_time": task.schedule_time.isoformat() if task.schedule_time else None,
            "url": task.payload.url,
            "method": task.payload.method,
            "service_account_email": task.service_account_email
        }
        logger.info(f"Task {task.name} added to queue {queue} (scheduled for {task.schedule_time})", extra=create_extra)
        
        return {
            "name": f"projects/{project}/locations/{location}/queues/{queue}/tasks/{task.name}",
            "scheduleTime": task.schedule_time.isoformat() if task.schedule_time else None,
            "createTime": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v2/projects/{project}/locations/{location}/queues/{queue}/tasks")
async def list_tasks(project: str, location: str, queue: str):
    """List tasks in queue."""
    return {
        "tasks": [
            {
                "name": f"projects/{project}/locations/{location}/queues/{queue}/tasks/{task.name}",
                "scheduleTime": task.schedule_time.isoformat() if task.schedule_time else None,
                "responseCount": task.response_count,
                "firstAttemptTime": task.first_attempt_time.isoformat() if task.first_attempt_time else None,
                "lastAttemptTime": task.last_attempt_time.isoformat() if task.last_attempt_time else None
            }
            for task in task_queue
        ]
    }

@app.get("/status")
async def get_status():
    """Get emulator status and statistics."""
    return {
        "running": emulator.running,
        "queue_size": len(task_queue),
        "completed_tasks": len(task_history),
        "recent_history": task_history[-10:] if task_history else []
    }

@app.delete("/tasks")
async def clear_tasks():
    """Clear all tasks (for testing)."""
    task_queue.clear()
    task_history.clear()
    return {"message": "All tasks cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.CLOUDTASK_EMULATOR_HOST, port=settings.CLOUDTASK_EMULATOR_PORT)
