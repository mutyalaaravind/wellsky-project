# Distributed Job Tracking Service

A FastAPI-based microservice for tracking and managing distributed jobs with support for hierarchical job structures (parent jobs with sub-jobs).

## Features

- **Job Management**: Create, update, delete, and monitor jobs
- **Hierarchical Jobs**: Support for parent jobs with sub-jobs
- **Job Tracking**: Real-time tracking of job status, progress, and performance
- **Redis Backend**: Fast, scalable storage using Redis
- **RESTful API**: Clean REST API with automatic OpenAPI documentation
- **Docker Support**: Containerized deployment with Docker Compose
- **Health Monitoring**: Built-in health checks and system monitoring

## Job Types

- Data Processing
- Document Analysis
- Entity Extraction
- Medication Extraction
- Custom

## Job Statuses

- Pending
- Running
- Completed
- Failed
- Cancelled
- Retrying

## API Endpoints

### Job Management

- `POST /api/jobs/` - Create a new job
- `POST /api/jobs/with-subjobs` - Create a job with sub-jobs
- `GET /api/jobs/` - List jobs with filtering and pagination
- `GET /api/jobs/{job_id}` - Get a specific job
- `GET /api/jobs/{job_id}/with-subjobs` - Get a job with all its sub-jobs
- `PUT /api/jobs/{job_id}` - Update a job
- `DELETE /api/jobs/{job_id}` - Delete a job
- `POST /api/jobs/{job_id}/start` - Start a job
- `POST /api/jobs/{job_id}/cancel` - Cancel a job
- `POST /api/jobs/{job_id}/retry` - Retry a failed job

### Job Tracking

- `GET /api/tracking/stats` - Get overall job statistics
- `GET /api/tracking/stats/by-status` - Get stats grouped by status
- `GET /api/tracking/stats/by-type` - Get stats grouped by type
- `GET /api/tracking/stats/by-priority` - Get stats grouped by priority
- `GET /api/tracking/performance` - Get performance metrics
- `GET /api/tracking/active-jobs` - Get currently running jobs
- `GET /api/tracking/failed-jobs` - Get recent failed jobs
- `GET /api/tracking/queue-depth` - Get pending jobs count
- `GET /api/tracking/throughput` - Get job throughput metrics
- `GET /api/tracking/worker-stats` - Get worker statistics
- `GET /api/tracking/job-tree/{job_id}` - Get complete job tree
- `GET /api/tracking/health` - Get system health status

### Health Check

- `GET /api/health` - Service health check

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- uv (Python package manager)

### Running with Docker Compose

1. Clone the repository and navigate to the service directory:
```bash
cd distributed_job_tracking
```

2. Build and run the service:
```bash
make build
make run
```

3. The service will be available at `http://localhost:19000`

4. View the API documentation at `http://localhost:19000/docs`

### Local Development

1. Install dependencies:
```bash
make install
```

2. Run the service locally:
```bash
cd src
uv run uvicorn main:app --reload --host 0.0.0.0 --port 19000
```

## Configuration

The service can be configured using environment variables:

### Core Settings
- `SERVICE_NAME`: Service name (default: "distributed_job_tracking")
- `DEBUG`: Enable debug mode (default: False)
- `API_HOST`: API host (default: "0.0.0.0")
- `API_PORT`: API port (default: 19000)

### Redis Settings
- `REDIS_URL`: Redis connection URL (default: "redis://localhost:6379")
- `REDIS_DB`: Redis database number (default: 0)

### Google Cloud Settings
- `GCP_PROJECT_ID`: Google Cloud project ID
- `GCP_LOCATION`: Primary GCP location
- `FIRESTORE_EMULATOR_HOST`: Firestore emulator host
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name

## Usage Examples

### Creating a Simple Job

```bash
curl -X POST "http://localhost:19000/api/jobs/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Process Document",
    "job_type": "document_analysis",
    "priority": "normal",
    "payload": {
      "document_id": "doc123",
      "analysis_type": "full"
    }
  }'
```

### Creating a Job with Sub-jobs

```bash
curl -X POST "http://localhost:19000/api/jobs/with-subjobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Complex Document Processing",
    "job_type": "document_analysis",
    "priority": "high",
    "payload": {
      "document_id": "doc456"
    },
    "sub_jobs": [
      {
        "name": "Extract Entities",
        "job_type": "entity_extraction",
        "payload": {"document_id": "doc456"}
      },
      {
        "name": "Extract Medications",
        "job_type": "medication_extraction",
        "payload": {"document_id": "doc456"}
      }
    ]
  }'
```

### Getting Job Statistics

```bash
curl "http://localhost:19000/api/tracking/stats"
```

### Listing Jobs with Filters

```bash
# Get all pending jobs
curl "http://localhost:19000/api/jobs/?status=pending"

# Get jobs by type
curl "http://localhost:19000/api/jobs/?job_type=entity_extraction"

# Get jobs with pagination
curl "http://localhost:19000/api/jobs/?page=1&page_size=10"
```

## Development

### Available Make Commands

- `make help` - Show available commands
- `make build` - Build Docker image
- `make run` - Run service in background
- `make dev` - Run service in foreground with logs
- `make stop` - Stop the service
- `make clean` - Clean up containers and volumes
- `make logs` - Show service logs
- `make test` - Run tests
- `make lint` - Run code linting
- `make format` - Format code
- `make install` - Install dependencies

### Project Structure

```
distributed_job_tracking/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── settings.py             # Configuration settings
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   └── job.py             # Job models
│   ├── routers/               # API route handlers
│   │   ├── __init__.py
│   │   ├── jobs.py            # Job management endpoints
│   │   └── tracking.py        # Job tracking endpoints
│   ├── usecases/              # Business logic
│   │   ├── __init__.py
│   │   ├── job_service.py     # Job management service
│   │   └── tracking_service.py # Job tracking service
│   ├── adapters/              # External service adapters
│   │   ├── __init__.py
│   │   └── redis_adapter.py   # Redis storage adapter
│   ├── middleware/            # Custom middleware
│   │   ├── __init__.py
│   │   └── auto_headers.py    # Request/response headers
│   └── util/                  # Utility functions
├── tests/                     # Test files
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── Makefile                   # Development commands
├── pyproject.toml            # Python project configuration
└── README.md                 # This file
```

## Testing

Run the test suite:

```bash
make test
```

## Monitoring

The service provides comprehensive monitoring capabilities:

- **Health Checks**: Built-in health endpoints for container orchestration
- **Metrics**: Performance metrics and job statistics
- **Logging**: Structured logging with request tracing
- **Redis Monitoring**: Connection health and performance tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is part of the Viki AI platform.
