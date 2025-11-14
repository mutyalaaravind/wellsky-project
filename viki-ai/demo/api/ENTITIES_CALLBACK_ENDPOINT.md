# Document Processing Complete Callback Endpoint

## Overview

This document describes the new POST /api/entities endpoint that has been added to the demo API to handle callbacks from the `invoke_document_processing_complete()` function in the paperglass system.

## Endpoint Details

**URL:** `POST /api/entities`  
**Content-Type:** `application/json`

## Request Payload

The endpoint accepts the exact payload structure sent by the `invoke_document_processing_complete()` callback:

```json
{
  "app_id": "string",
  "tenant_id": "string",
  "patient_id": "string",
  "document_id": "string",
  "source_id": "string (optional)",
  "status": "string",
  "timestamp": "string (ISO format)",
  "run_id": "string",
  "metadata": {
    // Optional metadata object
  },
  "data": [
    // Optional array of entity objects
  ]
}
```

## Functionality

1. **Validates** the incoming callback payload using Pydantic models
2. **Logs** the received callback data for audit purposes
3. **Persists entities** if they exist in the `data` field:
   - Uses the existing `save_entities` usecase
   - Generates a unique `entity_id` based on `document_id` and `run_id`
   - Uses a default `entity_schema_id` of "document_processing_callback"
   - Saves entities to Firestore collections
4. **Returns** a comprehensive response with processing status

## Response Format

### Success Response (200 OK)
```json
{
  "app_id": "demo_app",
  "tenant_id": "54321",
  "patient_id": "9e01906eccfa4e8db14171b1f7ccc914",
  "document_id": "doc_callback_test_12345",
  "source_id": "host_doc_12345",
  "status": "processed",
  "message": "Document processing complete callback processed successfully",
  "document_status": "completed",
  "run_id": "run_callback_test_12345",
  "timestamp": "2025-07-28T15:45:00.000Z",
  "entities_received": 3,
  "entities_saved": 3,
  "entity_document_ids": ["doc1", "doc2", "doc3"]
}
```

### Error Responses

**400 Bad Request** - Validation Error:
```json
{
  "messageType": "VALIDATION_ERROR",
  "message": "Invalid callback payload: ...",
  "relatedToKeys": []
}
```

**500 Internal Server Error** - Processing Error:
```json
{
  "messageType": "ERROR",
  "message": "Failed to process callback: ...",
  "relatedToKeys": []
}
```

## Implementation Details

### Files Modified

1. **`demo/api/main/interface/adapters/rest.py`**:
   - Added `DocumentProcessingCompleteRequest` Pydantic model
   - Added new route: `Route('/entities', self.process_document_complete_callback, methods=['POST'])`
   - Implemented `process_document_complete_callback()` method

2. **`demo/tests/demo.rest`**:
   - Added comprehensive test cases for the new endpoint
   - Tests include scenarios with entities, empty entities, and null data

### Key Features

- **Robust Error Handling**: Continues processing even if entity saving fails
- **Comprehensive Logging**: Logs all callback data for debugging and audit
- **Flexible Entity Handling**: Handles cases where no entities are present
- **Reuses Existing Infrastructure**: Leverages the existing `save_entities` usecase and entity repository

## Testing

The endpoint can be tested using the provided REST client tests in `demo/tests/demo.rest`. Three test scenarios are included:

1. **Full callback with entities**: Tests normal operation with multiple entities
2. **Empty entities array**: Tests handling when no entities are extracted
3. **Null data field**: Tests handling when data field is null

## Usage in Production

To use this endpoint as a callback destination:

1. Configure the paperglass integration callback endpoint to point to: `{base_url}/api/entities`
2. Ensure the demo API is running and accessible
3. The callback will automatically persist any entities included in the document processing results

## Entity Storage

Entities are stored in Firestore collections with the naming pattern:
- Collection: `demo_entity_{entity_id}`
- Where `entity_id` = `{document_id}_{run_id}`

Each entity document includes:
- All original entity data from the callback
- Additional metadata: `app_id`, `tenant_id`, `patient_id`, `document_id`, `source_id`, `entity_schema_id`, `run_id`

### Document ID vs Source ID
- **`document_id`**: PaperGlass internal document UUID (auto-generated)
- **`source_id`**: Original identifier from the host system that submitted the document (optional)

This allows host systems to maintain traceability between their original documents and the processed entities.
