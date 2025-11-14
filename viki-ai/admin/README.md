# Admin Project

This project contains the admin interface for managing system administration tasks, including entity schemas, pipelines, and system settings.

## Structure

- `api/` - FastAPI backend service
- `ui/` - React frontend application

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local UI development)
- Python 3.11+ with uv (for local API development)

### Development

1. **Start all services:**
   ```bash
   make up
   ```

2. **Access the applications:**
   - API: http://localhost:14000
   - UI: http://localhost:14001

### Individual Services

#### API Development
```bash
cd api
make init    # Initialize dependencies
make test    # Run tests
```

#### UI Development
```bash
cd ui
npm ci       # Install dependencies
npm start    # Start development server (PORT=14001)
```

## Available Commands

- `make help` - Show available commands
- `make build` - Build both API and UI
- `make up` - Start services with Docker Compose
- `make down` - Stop services
- `make logs` - View logs
- `make clean` - Clean build artifacts

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /admin/` - Admin status
- `GET /admin/users` - List users
- `GET /admin/system/health` - System health check

## Features

- **Home Dashboard** - Overview and quick actions
- **Entity Schema Management** - Configure data extraction schemas
- **Pipeline Management** - Create and manage extraction pipelines
- **Settings** - System configuration and preferences