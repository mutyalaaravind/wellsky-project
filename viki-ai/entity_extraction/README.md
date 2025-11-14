# Entity Extraction Service

A simple FastAPI service for entity extraction, following the architectural patterns established by the medication_extraction service.

## Overview

This service provides a basic FastAPI application with health check and root endpoints. It's designed to be extended with entity extraction functionality while maintaining consistency with the existing project architecture.

## Features

- FastAPI web framework
- CORS middleware configuration
- Health check endpoint
- Docker containerization
- Docker Compose for local development
- UV package management
- Comprehensive testing setup

## Endpoints

- `GET /api/` - Welcome message
- `GET /api/health` - Health check endpoint
- `POST /api/pipeline/{scope}/{pipeline_key}/start` - Start a pipeline for the specified scope and pipeline
- `POST /api/pipeline/{scope}/{pipeline_key}/{task}/run` - Run a specific task within a pipeline scope
- `GET /api/config/{scope}/{pipeline_key}` - Retrieve a pipeline configuration from Firestore

## Development Setup

### Prerequisites

- Python 3.11+
- UV package manager
- Docker and Docker Compose

### Installation

1. Initialize dependencies:
```bash
make init
```

2. Install the package:
```bash
make install
```

### Running the Service

#### Using Docker Compose (Recommended)

```bash
make up
```

The service will be available at `http://localhost:18000`

#### Direct Python Execution

```bash
cd src
uv run uvicorn main:app --reload --host 0.0.0.0 --port 18000
```

### Testing

Run tests:
```bash
make test
```

Run tests with coverage:
```bash
make test-coverage
```

### Docker Commands

- Build Docker image: `make docker-build`
- Start services: `make up`
- Stop services: `make down`
- View logs: `make logs`
- Restart services: `make restart`

### Development Commands

- Clean cache files: `make clean`
- Format code: `make format`
- Lint code: `make lint`
- View all commands: `make help`

## Architecture

This service follows the same architectural patterns as the medication_extraction service:

- **FastAPI**: Modern, fast web framework for building APIs
- **UV**: Fast Python package installer and resolver
- **Docker**: Containerization for consistent deployment
- **Pytest**: Testing framework with async support
- **CORS**: Cross-origin resource sharing middleware

## Port Configuration

- Service runs on port 18000
- Docker Compose maps host port 18000 to container port 18000

## Environment Variables

- `PYTHONUNBUFFERED=1`: Ensures Python output is sent straight to terminal
- `SERVICE=entity_extraction`: Service identifier
- `STAGE=dev`: Environment stage
- `DEBUG=true`: Enable debug mode

## Future Extensions

This service is designed to be extended with:
- Entity extraction endpoints
- Request/response models
- Business logic services
- Database integration
- Authentication/authorization
- Logging and monitoring
