# Cloud Task Emulator

A local emulator for Google Cloud Tasks that provides the same API interface for development and testing environments.

## Features

- **Asynchronous Task Execution**: Tasks are executed asynchronously in separate threads
- **Task Scheduling**: Support for delayed task execution
- **Retry Logic**: Automatic retry with exponential backoff for failed tasks
- **Queue Management**: Multiple queue support with task isolation
- **HTTP Task Execution**: Execute HTTP requests to target endpoints
- **Monitoring**: Real-time status and task history tracking
- **Cloud Tasks API Compatibility**: Same API endpoints as Google Cloud Tasks

## Quick Start

### 1. Install Dependencies

```bash
cd cloudtask-emulator
pip install -e .
```

### 2. Start the Emulator

```bash
python src/main.py
```

The emulator will start on `http://localhost:30001`

### 3. Use the Client

```python
from cloudtask_emulator.client import CloudTaskEmulatorClient

client = CloudTaskEmulatorClient("http://localhost:30001")

# Create a task
await client.create_task(
    project="my-project",
    location="us-central1", 
    queue="my-queue",
    task_name="task-123",
    url="http://localhost:8080/api/process",
    payload={"data": "example"}
)
```

## API Endpoints

### Create Task
```
POST /v2/projects/{project}/locations/{location}/queues/{queue}/tasks
```

### List Tasks
```
GET /v2/projects/{project}/locations/{location}/queues/{queue}/tasks
```

### Get Status
```
GET /status
```

### Clear Tasks (Testing)
```
DELETE /tasks
```

## Configuration

The emulator can be configured through environment variables:

- `CLOUDTASK_EMULATOR_PORT`: Port to run on (default: 30001)
- `CLOUDTASK_EMULATOR_HOST`: Host to bind to (default: 0.0.0.0)
- `CLOUDTASK_MAX_RETRIES`: Maximum retry attempts (default: 3)
- `CLOUDTASK_RETRY_BASE_DELAY`: Base retry delay in seconds (default: 2)
- `CLOUDTASK_MAX_RETRY_DELAY`: Maximum retry delay in seconds (default: 60)
- `CLOUDTASK_LOG_LEVEL`: Logging level (default: INFO)

## Integration with Entity Extraction

The emulator is designed to work seamlessly with the entity extraction TaskOrchestrator:

```python
# In TaskOrchestrator.invoke()
if settings.CLOUD_PROVIDER == "local":
    # Use emulator
    client = CloudTaskEmulatorClient()
    await client.create_task(...)
else:
    # Use real Cloud Tasks
    # ... real implementation
```

## Development

### Running Tests

```bash
pytest
```

### Running with Docker

```bash
docker build -t cloudtask-emulator .
docker run -p 8081:8081 cloudtask-emulator
```

## Architecture

The emulator consists of:

1. **FastAPI Server**: Provides Cloud Tasks compatible API
2. **Task Queue**: In-memory task storage (Redis in production)
3. **Worker Loop**: Asynchronous task processor
4. **HTTP Client**: Executes HTTP requests to target endpoints
5. **Retry Logic**: Handles task failures with exponential backoff

## Benefits

- **No Serial Execution**: Tasks run asynchronously, preventing blocking
- **Proper Task Isolation**: Each task runs independently
- **Realistic Behavior**: Mimics Cloud Tasks retry and scheduling behavior
- **Easy Testing**: Clear tasks and inspect queue state
- **Development Speed**: No need for real Cloud Tasks setup locally
