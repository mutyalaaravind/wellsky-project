# Document Extraction Service Design

## Overview

This document details the hexagonal architecture implementation of the document extraction service, following Domain-Driven Design (DDD) principles.

## Project Structure

### Overall Organization

```
backend/services/
├── shared/                 # Shared library used across domain services
│   └── src/shared/
│       ├── domain/        # Common domain models and interfaces
│       │   ├── base.py    # Base classes for domain models
│       │   ├── events.py  # Domain event definitions
│       │   └── models.py  # Shared model abstractions
│       ├── application/   # Common application layer components
│       │   ├── commands.py       # Base command classes
│       │   ├── events.py        # Event handling infrastructure
│       │   └── ports/          # Common interface definitions
│       └── infrastructure/     # Shared infrastructure implementations
│           ├── persistence/    # Database and repository implementations
│           └── storage/        # Storage service implementations
└── document_extraction/   # Document extraction domain service
    └── src/docextract/
        ├── domain/       # Domain models and business logic
        ├── application/  # Application services and use cases
        ├── infrastructure/ # Technical implementations
        └── entrypoints/  # API and interface adapters
```

### Shared Library Components

#### Domain Layer

- Base domain models and aggregates
- Common value objects and types
- Domain event infrastructure
- Shared validation rules

#### Application Layer

- Command and event base classes
- Interface definitions (ports)
- Common application services
- Transaction handling abstractions

#### Infrastructure Layer

- Generic repository implementations
- Storage service adapters
- Database connection management
- Common infrastructure utilities

### Design Patterns and Best Practices

1. Domain-Driven Design

   - Aggregate roots with encapsulated state
   - Value objects for immutable concepts
   - Domain events for state changes
   - Rich domain models with behavior

2. Hexagonal Architecture

   - Clear separation of concerns
   - Port and adapter pattern
   - Dependency inversion
   - Technology-agnostic core

3. Command-Query Responsibility Segregation (CQRS)

   - Command handling infrastructure
   - Event sourcing support
   - Separate read and write models

4. Clean Architecture Principles
   - Dependency flow towards domain
   - Interface-driven development
   - Use case centered design
   - Infrastructure independence

## Shared Infrastructure Patterns

### 1. Unit of Work Pattern

- Location: `shared/src/shared/infrastructure/persistence/firestore/uow.py`
- Manages transaction boundaries and consistency
- Key features:
  ```python
  class FirestoreUnitOfWork(UnitOfWorkPort):
      async def __aenter__(self) -> 'FirestoreUnitOfWork'  # Start transaction
      async def commit(self) -> None                        # Commit changes
      def register_changes(self, changes: BaseChanges)      # Track modifications
  ```
- Responsibilities:
  - Transaction management with retry support
  - Change tracking (new/dirty/removed entities)
  - Event publishing within transaction boundary
  - Command/Event deduplication
  - Repository lifecycle management

### 2. Generic Repository Pattern

- Location: `shared/src/shared/infrastructure/persistence/firestore/repository.py`
- Type-safe generic repository implementation
- Key features:
  ```python
  class FirestoreRepository(Generic[T]):
      def stage_create(self, entity: T) -> None
      async def stage_update(self, entity: T) -> None
      def stage_delete(self, entity: T) -> None
  ```
- Capabilities:
  - Operation staging for transactions
  - Optimistic concurrency control
  - Entity mapping infrastructure
  - Subcollection support for events

### 3. Command/Event Infrastructure

- Locations:
  - `shared/src/shared/application/ports/command_handling.py`
  - `shared/src/shared/domain/events.py`
- Key patterns:
  ```python
  class ICommandHandlingPort(Protocol):
      async def handle_command(self, command: BaseCommand) -> Any
  ```
- Features:
  - Command validation and routing
  - Event storage and tracking
  - Idempotency handling
  - Event sourcing support

### 4. Repository Factory Pattern

- Location: `shared/src/shared/infrastructure/persistence/firestore/repository_factory.py`
- Dynamic repository creation and configuration
- Key features:
  ```python
  class FirestoreRepositoryFactory:
      def create_for(self, entity_type: Type[Versionable]) -> FirestoreRepository
  ```
- Benefits:
  - Centralized repository configuration
  - Type-safe repository instantiation
  - Dependency injection support

## Architecture Layers

### 1. API Layer (Entrypoints)

#### Routes

- Primary adapter implementing HTTP endpoints using FastAPI
- Located in `src/docextract/entrypoints/api/routes.py`
- Key endpoints:
  - POST `/documents`: Upload document endpoint
  - GET `/documents/health`: Health check endpoint

#### Request Flow

1. Receives multipart form data with:

   - app_id: Application identifier
   - tenant_id: Tenant identifier
   - user_id: User identifier
   - file: Document file (UploadFile)

2. Data Transfer Objects (DTOs)

   - UploadDocumentRequest: Validates incoming request data
   - DocumentResponse: Structures response data
   - ErrorResponse: Standardizes error responses

3. Error Handling
   - 400 Bad Request: Validation errors, duplicate commands
   - 500 Internal Server Error: Storage errors, processing errors
   - Custom domain exceptions mapped to HTTP status codes

### 2. Domain Layer

#### Core Domain Model

##### Document (Aggregate Root)

- Location: `src/docextract/domain/models/document.py`
- Inherits from AggregateRoot (shared domain model)
- Key Properties:
  - document_id: Unique identifier
  - storage_path: Generated path for document storage
  - metadata: DocumentMetadata value object
  - app_id, tenant_id, user_id: Multi-tenancy support

##### Key Methods

1. Document Creation

   ```python
   @classmethod
   def create(cls, app_id, tenant_id, user_id, id, version, created_at, updated_at, metadata)
   ```

   - Factory method for creating new documents
   - Ensures all required fields are provided
   - Initializes with empty events list

2. Status Management

   ```python
   def update_status(self, status: DocumentStatus) -> Document
   ```

   - Immutable status updates
   - Creates new document instance with updated metadata
   - Increments version number

3. Path Generation
   ```python
   def file_path(self, filename: str) -> str
   ```
   - Generates hierarchical storage path
   - Format: app_id/tenant_id/user_id/document_id/filename

#### Value Objects

##### DocumentMetadata

- Location: `src/docextract/domain/models/document_metadata.py`
- Immutable value object (frozen=True)
- Properties:
  - content_type: MIME type (ContentType)
  - size_bytes: File size (ByteSize)
  - original_name: Original filename (Filename)
  - created_at: Creation timestamp
  - updated_at: Last update timestamp
  - status: Processing status (DocumentStatus)

##### Key Features

1. Validation

   - Filename validation: Must have extension and non-empty
   - Size validation: Must be greater than 0
   - Content type validation through custom type

2. Factory Method

   ```python
   @classmethod
   def create(cls, content_type, size_bytes, original_name)
   ```

   - Creates new metadata instances
   - Enforces validation rules
   - Sets default timestamps

3. Status Updates
   ```python
   def with_status(self, status: DocumentStatus) -> Self
   ```
   - Immutable status updates
   - Returns new instance with updated status
   - Preserves original metadata

#### Domain Types

Location: `src/docextract/domain/models/types.py`

##### Type Aliases

- ByteSize: Integer representing size in bytes
- Filename: String representing original filename

##### Enums

1. ContentType (str, Enum)

   - PDF = "application/pdf"
   - Extensible for additional document types

2. DocumentStatus (str, Enum)
   - PENDING: Initial state
   - PROCESSED: Successfully processed
   - FAILED: Processing failed

#### Domain Ports

##### Document Validation Port

- Location: `src/docextract/domain/ports/document_validation.py`
- Implements Protocol for runtime type checking
- Defines validation contract through DocumentValidatorPort

###### Validation Methods

1. Content Type Validation

   ```python
   def validate_content_type(self, content_type: ContentType) -> ContentType
   ```

   - Validates MIME type support
   - Ensures content type matches supported formats (e.g., PDF)
   - Raises DocumentValidationError for unsupported types

2. Size Validation

   ```python
   def validate_size(self, size: ByteSize) -> ByteSize
   ```

   - Validates document size constraints
   - Enforces minimum and maximum size limits
   - Raises DocumentValidationError for invalid sizes

3. Filename Validation

   ```python
   def validate_filename(self, filename: Filename) -> Filename
   ```

   - Validates filename format and extension
   - Checks for invalid characters
   - Ensures proper file extension
   - Raises DocumentValidationError for invalid filenames

4. Composite Validation
   ```python
   def validate_document(self, content_type, size, filename) -> tuple
   ```
   - Validates all document attributes together
   - Enables cross-field validation rules
   - Returns tuple of validated attributes
   - Allows for enforcing combined constraints

#### Domain Events

- Inherits event handling from shared domain events
- Events tracked in aggregate root for domain event publishing

### 3. Application Layer

#### Commands

- UploadDocumentCommand: Encapsulates document upload operation
- Command fields:
  - Basic fields: id, version, created_at, updated_at
  - Document fields: app_id, tenant_id, user_id
  - File fields: content_type, size_bytes, original_name, content

#### Command Handling

- Uses command dispatcher pattern
- Dependencies injected through FastAPI dependency system
- Implements ICommandHandlingPort from shared library

### 4. Infrastructure Layer

#### Storage Implementation

- Location: `src/docextract/infrastructure/storage/document_storage.py`
- Implements adapter pattern wrapping shared storage implementation
- Uses dependency injection for configuration

##### DocumentStorageAdapter

- Implements IStoragePort interface from shared library
- Wraps base storage implementation (e.g., GCS)
- Configures storage with service-specific settings

###### Key Features

1. Location Management

   ```python
   def _get_location(self, path: str) -> StorageLocation
   ```

   - Creates storage locations with configured bucket
   - Encapsulates bucket configuration from settings

2. Document Upload

   ```python
   async def upload(self, location, content, content_type) -> None
   ```

   - Handles document content upload
   - Supports multiple content types (bytes, str, IO)
   - Uses configured storage bucket

3. Document Retrieval

   ```python
   async def get(self, location) -> Tuple[bytes, StorageMetadata]
   ```

   - Retrieves document content and metadata
   - Returns content as bytes with storage metadata

4. Existence Check
   ```python
   async def exists(self, location) -> bool
   ```
   - Verifies document existence in storage
   - Uses configured bucket settings

#### Persistence Implementation

- Location: `src/docextract/infrastructure/persistence/firestore_repository.py`
- Implements repository pattern using Firestore
- Inherits from shared FirestoreRepository implementation

##### DocumentRepository

- Implements generic repository for Document entities
- Uses Firestore collections for document storage
- Handles entity-document mapping

###### Key Features

1. Collection Management

   ```python
   COLLECTION_NAME = "documents"
   ENTITY_TYPE = Document
   ```

   - Configures Firestore collection for documents
   - Defines entity type for type safety

2. Entity Mapping

   ```python
   def _map_entity_to_doc(self, entity: Document) -> Dict[str, Any]
   ```

   - Maps domain entities to Firestore documents
   - Handles metadata serialization
   - Preserves all entity attributes

3. Document Mapping

   ```python
   def _map_doc_to_entity(self, data: Dict[str, Any]) -> Document
   ```

   - Maps Firestore documents to domain entities
   - Handles metadata deserialization
   - Reconstructs complete Document instances

4. Event Handling
   ```python
   def get_events_repository(self, document_id: str) -> EventRepository
   ```
   - Manages document event subcollections
   - Provides access to event history
   - Uses shared event repository implementation

### 5. Cross-Cutting Concerns

#### Dependency Injection

- Location: `src/docextract/infrastructure/dependencies.py`
- Uses FastAPI's dependency injection system
- Implements factory pattern for component creation

##### Key Components

1. Client Management

   ```python
   async def get_firestore_client() -> AsyncGenerator[firestore.AsyncClient, None]
   def get_storage_client(settings: Settings) -> storage.Client
   ```

   - Manages Firestore and Storage client lifecycles
   - Supports both production and emulator environments
   - Handles proper client cleanup

2. Repository Management

   ```python
   def get_repository_factory(client: firestore.AsyncClient) -> FirestoreRepositoryFactory
   ```

   - Creates and configures repository instances
   - Registers document repository with factory
   - Supports repository dependency resolution

3. Command/Event Infrastructure

   ```python
   def get_command_repository(client, command_factory) -> CommandRepository
   def get_event_repository(client) -> EventRepository
   ```

   - Sets up command and event persistence
   - Manages processed commands/events tracking
   - Configures collection names and factories

4. Unit of Work Management

   ```python
   def get_unit_of_work_manager(...) -> UnitOfWorkManagerPort
   ```

   - Coordinates transaction management
   - Integrates repositories and event tracking
   - Ensures data consistency

5. Service Dependencies

   ```python
   def get_storage_adapter(...) -> IStoragePort
   def get_document_validator() -> DocumentValidatorPort
   def get_upload_handler(...) -> UploadDocumentHandler
   ```

   - Configures service-specific components
   - Implements adapter pattern for external services
   - Manages component lifecycles

6. Command Handling
   ```python
   def get_command_dispatcher(...) -> ICommandHandlingPort
   ```
   - Sets up command handling infrastructure
   - Registers command handlers
   - Manages command routing

#### Configuration Management

- Uses Settings class for configuration
- Supports different environments (dev, qa, prod)
- Handles emulator configuration for local development

#### Error Handling

- Custom domain exceptions for business rules
- Infrastructure exceptions for technical issues
- HTTP status code mapping in API layer

## Request Processing Flow

### Document Upload Flow

```python
# API Layer: Request Handling
routes.upload_document()
├── UploadDocumentRequest.model_validate()  # Validate request DTO
│   └── Pydantic validation rules applied
├── file.read()  # Read uploaded content
└── UploadDocumentCommand(  # Create command
    id=uuid4().hex,
    content=content,
    ...
)

# Application Layer: Command Processing
├── dependencies.get_command_dispatcher()
└── CommandDispatcher.handle_command(command)
    ├── ProcessedCommandRepository.get(command.id)  # Deduplication check
    └── UploadDocumentHandler.handle(command)
        # Domain Layer: Validation & Storage
        ├── DocumentValidator.validate_document(
        │   content_type, size, filename
        │)
        └── DocumentStorageAdapter.upload(
            location, content, content_type
        )
            └── GCSStorageAdapter._upload_to_bucket()

        # Domain Layer: Model Creation
        └── Document.create(
            app_id, tenant_id, user_id, metadata, ...
        )
            ├── DocumentMetadata.create(
            │   content_type, size_bytes, original_name
            │)
            └── Document instance with empty events

        # Infrastructure Layer: Transaction Management
        └── UnitOfWorkManager.start()
            └── FirestoreUnitOfWork.__aenter__()
                ├── transaction = client.transaction()
                └── repository_factory.create_for(Document)

                # Infrastructure Layer: Change Tracking
                ├── UnitOfWork.register_changes(changes)
                │   ├── FirestoreRepository.stage_create(document)
                │   │   └── _map_entity_to_doc(document)
                │   ├── EventRepository.stage_create(events)
                │   │   └── _map_event_to_doc(event)
                │   └── ProcessedCommandRepository.stage_create(command)
                │
                # Infrastructure Layer: Transaction Commit
                └── UnitOfWork.commit()
                    ├── _commit_staged_changes()
                    │   └── _save_event() for each event
                    ├── execute staged operations
                    └── transaction.commit()

# API Layer: Response Generation
└── DocumentResponse(  # Create response DTO
    document_id=document.document_id,
    storage_path=document.storage_path,
    ...
)
    └── FastAPI JSON response
```

DocumentResponse (DTO) created
↓
HTTP Response returned

````

### Key Interfaces By Layer

1. API Layer (Primary Adapters)
   ```python
   # FastAPI Route Handlers (Primary Adapter)
   @router.post("/documents")
   async def upload_document(
       request: UploadDocumentRequest,
       command_dispatcher: ICommandHandlingPort
   ) -> DocumentResponse: ...

   # Request/Response DTOs
   class UploadDocumentRequest(BaseModel):
       app_id: str
       tenant_id: str
       user_id: str
       file: UploadFile

   class DocumentResponse(BaseModel):
       document_id: str
       storage_path: str
       status: DocumentStatus
   ```

2. Domain Layer (Core Interfaces)
   ```python
   # Domain Model Interface
   class Document(AggregateRoot):
       @classmethod
       def create(cls, app_id, tenant_id, user_id, metadata) -> Document: ...
       def update_status(self, status: DocumentStatus) -> Document: ...
       def file_path(self, filename: str) -> str: ...

   # Domain Service Ports
   class DocumentValidatorPort(Protocol):
       def validate_content_type(self, content_type: ContentType) -> ContentType: ...
       def validate_size(self, size: ByteSize) -> ByteSize: ...
       def validate_filename(self, filename: Filename) -> Filename: ...
       def validate_document(self, content_type, size, filename) -> tuple: ...

   # Domain Events
   class DocumentCreated(DomainEvent):
       document_id: str
       app_id: str
       tenant_id: str
       metadata: DocumentMetadata

   class DocumentStatusUpdated(DomainEvent):
       document_id: str
       old_status: DocumentStatus
       new_status: DocumentStatus
   ```

3. Application Layer (Use Case Ports)
   ```python
   # Primary Ports (Use Case Interfaces)
   class ICommandHandlingPort(Protocol):
       async def handle_command(self, command: BaseCommand) -> Any: ...

   class ICommandHandler(Protocol[T]):
       async def handle(self, command: T) -> Any: ...

   # Commands
   class UploadDocumentCommand(BaseCommand):
       app_id: str
       tenant_id: str
       user_id: str
       content_type: ContentType
       size_bytes: ByteSize
       original_name: Filename
       content: bytes

   # Secondary Ports (Required by Use Cases)
   class UnitOfWorkManagerPort(Protocol):
       def start(self) -> UnitOfWorkPort: ...
       async def commit(self) -> None: ...
   ```

4. Infrastructure Layer (Secondary Adapters)
   ```python
   # Storage Port
   class IStoragePort(Protocol):
       async def upload(self, location: StorageLocation, content: bytes) -> None: ...
       async def get(self, location: StorageLocation) -> Tuple[bytes, StorageMetadata]: ...
       async def exists(self, location: StorageLocation) -> bool: ...

   # Repository Port
   class RepositoryPort(Protocol[T]):
       async def get(self, id: str) -> T: ...
       async def save(self, entity: T) -> None: ...
       async def delete(self, id: str) -> None: ...

   # Event Repository Port
   class EventRepositoryPort(Protocol):
       async def save(self, event: DomainEvent) -> None: ...
       async def get_for_aggregate(self, aggregate_id: str) -> List[DomainEvent]: ...

   # Command Repository Port
   class CommandRepositoryPort(Protocol):
       async def save(self, command: BaseCommand) -> None: ...
       async def get(self, command_id: str) -> BaseCommand: ...
       def stage_create(self, command: BaseCommand) -> None: ...

   # Unit of Work Port
   class UnitOfWorkPort(Protocol):
       async def __aenter__(self) -> 'UnitOfWorkPort': ...
       async def commit(self) -> None: ...
       def register_changes(self, changes: BaseChanges) -> None: ...
       async def start_command_processing(self, command: BaseCommand) -> bool: ...
       def finish_command_processing(self, command: BaseCommand) -> None: ...
   ```

### Key Component Interactions

1. Command Processing Chain
   ```python
   get_command_dispatcher(uowm, upload_handler) -> CommandDispatcher
   ├── Injects: UnitOfWorkManager
   ├── Injects: UploadDocumentHandler
   └── Used by: API routes for command handling

   get_upload_handler(validator, storage) -> UploadDocumentHandler
   ├── Injects: DocumentValidator
   ├── Injects: DocumentStorageAdapter
   └── Used by: CommandDispatcher for document uploads
````

2. Storage Chain

   ```python
   get_storage_adapter(client, settings) -> DocumentStorageAdapter
   ├── Injects: GCSStorageAdapter
   ├── Injects: Settings (bucket configuration)
   └── Used by: UploadDocumentHandler for file storage

   get_document_validator() -> DocumentValidator
   ├── Injects: None (stateless validation)
   └── Used by: UploadDocumentHandler for validation
   ```

3. Repository Chain

   ```python
   get_repository_factory(client) -> FirestoreRepositoryFactory
   ├── Injects: FirestoreClient
   ├── Registers: DocumentRepository
   └── Used by: UnitOfWorkManager for repository creation

   get_command_repository(client, command_factory) -> CommandRepository
   ├── Injects: FirestoreClient
   ├── Injects: DocumentCommandFactory
   └── Used by: UnitOfWorkManager for command tracking

   get_event_repository(client) -> EventRepository
   ├── Injects: FirestoreClient
   └── Used by: UnitOfWorkManager for event publishing
   ```

4. Transaction Chain

   ```python
   get_unit_of_work_manager(...) -> UnitOfWorkManager
   ├── Injects: RepositoryFactory
   ├── Injects: CommandRepository
   ├── Injects: EventRepository
   ├── Injects: ProcessedCommandRepository
   ├── Injects: ProcessedEventRepository
   └── Used by: CommandDispatcher for transactions

   FirestoreUnitOfWork
   ├── Manages: Transaction lifecycle
   ├── Manages: Repository operations
   ├── Manages: Event publishing
   └── Used by: UnitOfWorkManager for atomic operations
   ```

- Infrastructure exceptions for technical issues
- Transaction rollback on errors
- HTTP status code mapping

## Next Steps

- [ ] Review complete documentation with stakeholders
- [ ] Add sequence diagrams for key flows:
- Document upload flow
- Command/Event handling flow
- Storage and persistence flow
- [ ] Document testing strategy and examples:
- Unit test coverage
- Integration test scenarios
- End-to-end test cases
- [ ] Create onboarding guide for new developers:
- Setup instructions
- Development workflow
- Common debugging scenarios

## Implementation Notes

- Uses shared library implementations for persistence and storage
- Follows functional programming principles
- Implements clean architecture patterns
- Uses dependency injection for loose coupling
- Implements immutable domain models with version tracking
- Uses Pydantic for validation and data modeling
- Strong typing with custom domain types

```

```
