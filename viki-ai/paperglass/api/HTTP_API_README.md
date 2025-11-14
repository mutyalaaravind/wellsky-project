# Paperglass HTTP API

This document describes the new FastAPI-based HTTP API entrypoint for the paperglass service.

## Overview

The HTTP API provides a modern FastAPI-based interface for other services to call paperglass endpoints. It's designed to be a clean, well-documented API that can be easily consumed by external services.

## Architecture

- **Framework**: FastAPI (built on Starlette and Pydantic)
- **Router**: Located in `paperglass/interface/adapters/api.py`
- **Entrypoint**: Located in `paperglass/entrypoints/http_api.py`
- **Port**: 15003 (configurable)

## Endpoints

### Root Endpoints

- `GET /` - Service information and available endpoints
- `GET /health` - Simple health check for load balancers

### API Endpoints (under `/api` prefix)

- `GET /api/health` - Detailed health check with service information
- `GET /api/status` - Basic status endpoint

### Documentation (Debug Mode Only)

- `GET /docs` - Interactive Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Running the Service

### Using Docker Compose

The HTTP API service is included in the docker-compose.yml configuration:

```bash
# Start all services including the new HTTP API
docker-compose up

# Start only the HTTP API service
docker-compose up http-api
```

The service will be available at: http://localhost:15003

### Running Directly

```bash
# From the paperglass/api directory
python -m paperglass.entrypoints.http_api

# Or using uvicorn directly
uvicorn paperglass.entrypoints.http_api:app --host 0.0.0.0 --port 15003 --reload
```

## Configuration

The HTTP API uses the same environment variables and configuration as the main paperglass service. Key settings:

- `DEBUG`: Enables/disables API documentation endpoints
- `STAGE`: Environment stage (dev, qa, prod)
- `VERSION`: Service version
- All other paperglass environment variables are available

## Testing

Test files are available in `paperglass/tests/http_api.rest` for testing the endpoints using REST client tools.

### Example Requests

```bash
# Health check
curl http://localhost:15003/health

# API health check
curl http://localhost:15003/api/health

# Service information
curl http://localhost:15003/
```

## Adding New Endpoints

To add new endpoints to the HTTP API:

1. Add your endpoint functions to `paperglass/interface/adapters/api.py`
2. Use FastAPI decorators and Pydantic models for request/response validation
3. Follow the existing patterns for error handling and logging
4. Add tests to the REST file

Example:

```python
from fastapi import APIRouter
from pydantic import BaseModel

class MyRequest(BaseModel):
    name: str
    value: int

class MyResponse(BaseModel):
    result: str
    processed: bool

@api_router.post("/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest) -> MyResponse:
    # Your logic here
    return MyResponse(result=f"Processed {request.name}", processed=True)
```

## Features

- **Automatic Documentation**: FastAPI generates interactive API docs
- **Request/Response Validation**: Pydantic models ensure type safety
- **CORS Support**: Configured for cross-origin requests
- **Logging**: Integrated with paperglass logging system
- **Health Checks**: Multiple health check endpoints for monitoring
- **Development Mode**: Auto-reload and debug features when DEBUG=true

## Future Enhancements

This is the initial implementation with basic health endpoints. Future enhancements will include:

- Authentication and authorization
- Additional business logic endpoints
- Rate limiting
- Metrics and monitoring
- API versioning
- More comprehensive error handling

## Docker Compose Service

The new service is configured in docker-compose.yml as:

```yaml
http-api:
  image: paperglass-api
  build: *build
  ports:
    - '15003:15003'
  tty: true
  environment: *env
  volumes: *volumes
  command: uvicorn paperglass.entrypoints.http_api:app --host 0.0.0.0 --port 15003 --reload
```

This service shares the same image and configuration as the main API service but runs the FastAPI application instead.
