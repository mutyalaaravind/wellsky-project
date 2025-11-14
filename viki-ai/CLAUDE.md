# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Building and Running
- `make run` - Run all applications using Docker Compose with proper networking
- `make login` - Authenticate with GCP and set up database tunneling for development
- `make configure` - Initialize settings and copy .npmrc files to all subdirectories

### Frontend Applications (React/TypeScript/Vite)
- **Admin UI**: `cd admin/ui && npm run dev` (port 14001)
- **Demo Dashboard**: `cd demo/dashboard && npm start` (port 13001)
- **AutoScribe Widget**: `cd autoscribe/widget && npm start` (port 11001)
- **Extract-and-Fill Widget**: `cd extract-and-fill/widget && npm start` (port 12001)
- **PaperGlass Widget**: `cd paperglass/widget && npm start` (port 15001)

### Python APIs (FastAPI/uv)
All Python services use pyproject.toml with uv dependency management:
- Run tests: `uv run pytest` or `pytest --cov=src`
- Run with coverage: `pytest --cov=src --cov-report=term-missing`
- Start development server: `uv run uvicorn main:app --reload`

### Key Services and Ports
- **AutoScribe API**: port 11000 (speech-to-text)
- **Extract-and-Fill API**: port 12000 (form extraction)
- **Demo API**: port 13000 (demo backend)
- **PaperGlass API**: port 15000 (document search)
- **Entity Extraction API**: port 17000 (AI entity extraction)
- **Medication Extraction API**: port 17000 (medication parsing)
- **Admin API**: port 14000 (admin operations)

## Architecture Overview

### Monorepo Structure
VIKI is a monorepo containing multiple loosely coupled applications, each consisting of:
- **Backend**: FastAPI microservice with hexagonal architecture
- **Frontend**: React microfrontend (widget) or admin dashboard
- **Shared Infrastructure**: Firebase emulators, Docker containers

### Backend Architecture (Hexagonal)
All Python APIs follow hexagonal architecture with:

**Domain Layer**:
- Models and aggregates (e.g., `Document`, `Pipeline`)
- Value objects (e.g., `DocumentMetadata`, `ContentType`)
- Domain events and business rules
- Domain ports/interfaces

**Application Layer**:
- Commands and command handlers
- Use cases and application services
- Application ports (e.g., `ICommandHandlingPort`)

**Infrastructure Layer**:
- Adapters for external services (Firestore, GCS, LLM APIs)
- Repository implementations
- FastAPI route handlers
- Dependency injection configuration

**Key Patterns**:
- Unit of Work for transaction management
- Repository pattern with generic implementations
- Command/Event sourcing with deduplication
- Dependency injection using FastAPI's DI system

### Frontend Architecture
- **React 18** with TypeScript
- **Chakra UI** for most components (admin UI uses Chakra, demo uses both Chakra and Ant Design)
- **Vite** build tool for modern apps
- **React Router** for navigation
- Custom hooks for API integration (e.g., `useApps`, `useLLMModels`)

### Service Integration
- **Firebase Emulators**: Firestore, Cloud Functions, Pub/Sub for local development
- **Cloud Tasks Emulator**: For async job processing
- **Docker Compose**: Orchestrates all services with proper networking
- **GCP Services**: Firestore, Cloud Storage, Cloud Tasks, LLM APIs (Vertex AI)

## Development Workflow

### Prerequisites
- Docker and docker-compose 2.x.x
- Access to `viki-dev-app-wsky` GCP project
- `.envrc` file in repo root (ask teammate)

### Local Development Setup
1. `gcloud config set project viki-dev-app-wsky`
2. `make configure` - Copy .npmrc files
3. `make login` - GCP auth + AlloyDB tunneling
4. `make run` - Start all services

### Testing Strategy
**Python Services**:
- Unit tests: Domain and application layer logic
- Integration tests: Repository and adapter implementations
- Pytest with asyncio support and coverage reporting
- Mark integration tests with `@pytest.mark.integration`

**Frontend**:
- React Testing Library for component tests
- Jest for unit tests
- End-to-end tests using Playwright (see `e2e/` directory)

### Dependencies Management
**Python**: All services use `uv` with `pyproject.toml`
- Add dependency: Edit `pyproject.toml` dependencies array
- Install: `uv sync`
- Shared library: `viki-shared` package used across services

**Node.js**: Standard npm with `package.json`
- Install: `npm install`
- Each frontend has its own dependencies

## Key Implementation Patterns

### Python API Structure
```
api/
├── src/
│   ├── domain/          # Business logic and models
│   ├── application/     # Use cases and commands
│   ├── infrastructure/  # External service adapters
│   ├── main.py         # FastAPI app entry point
│   └── settings.py     # Configuration
├── tests/
│   ├── unit/           # Domain/application tests
│   └── integration/    # Infrastructure tests
└── pyproject.toml      # Dependencies and config
```

### Command Pattern Implementation
- Commands are immutable dataclasses with validation
- Command handlers implement single responsibility
- Unit of Work manages transactions and event publishing
- Processed commands tracked for idempotency

### Repository Pattern
- Generic repositories with type safety
- Firestore-based implementations
- Change tracking for efficient transactions
- Event sourcing support with subcollections

### Frontend Service Integration
- Custom hooks abstract API calls (e.g., `useApps`, `usePipelines`)
- Services handle HTTP requests and error handling
- TypeScript interfaces define API contracts
- Environment-specific configuration via `env.json`

### Edicts
- Refrain from leaving mock data in code unless explicitly requested

## Security and Compliance

### Authentication
- OIDC-based authentication for APIs
- JWT token validation
- Service account impersonation for development
- Multi-tenant isolation (app_id, tenant_id, user_id)

### Data Handling
- Document storage in Google Cloud Storage
- Metadata in Firestore with proper indexing
- PII handling follows healthcare compliance requirements
- Audit trails via domain events

## Common Troubleshooting

### Docker Issues
- On macOS: Use Colima instead of Docker Desktop
- Mount path issues: Ensure full paths in docker-compose
- Port conflicts: Check if services are already running

### GCP Authentication
- Run `make login` for proper service account setup
- AlloyDB requires proxy tunnel for local development
- Emulator endpoints configured in `.envrc`

### Development Environment
- Firebase emulators must be running for local development
- Cloud Tasks emulator needed for async processing
- All services expect common Firebase project configuration

### 🗺️ Key Documentation References
- **Architecture**: `requirements/architecture/ARCHITECTURE_GUIDELINES.md`
- **UX GUIDELINES**: `requirements/ux/UX_GUIDELINES.md`
