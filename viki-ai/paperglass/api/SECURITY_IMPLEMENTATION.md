# Paperglass API Security Implementation

## Overview

This document describes the comprehensive security implementation for the paperglass API that ensures all endpoints require either OIDC tokens (GCP service accounts) or OAuth tokens (Okta).

## Security Architecture

### Authentication Methods Supported

1. **GCP Service Account OIDC Tokens** - For service-to-service communication
2. **Okta OAuth Tokens** - For both user authentication and service authentication
   - User tokens: For user-facing endpoints
   - Service tokens: For service-to-service communication

### Security Modules

#### 1. `paperglass/interface/security.py`
Provides Starlette-compatible security decorators for the REST adapter:

- `@require_any_auth` - Accepts any valid authentication token (GCP OIDC or Okta OAuth)
- `@require_service_auth` - Requires either GCP service account OIDC or Okta service OAuth tokens
- `@require_user_auth` - Requires Okta user OAuth tokens only

#### 2. `paperglass/interface/fastapi_security.py`
Provides FastAPI-compatible security dependencies for the API router:

- `RequireAnyAuth` - FastAPI dependency for any valid authentication
- `RequireServiceAuth` - FastAPI dependency for service authentication
- `RequireUserAuth` - FastAPI dependency for user authentication

### Token Validation Flow

1. **Authorization Header Check**: Validates presence of `Authorization: Bearer <token>` header
2. **GCP OIDC Validation**: First attempts to validate as GCP service account identity token
3. **Okta OAuth Validation**: If GCP validation fails, attempts Okta OAuth validation
4. **Issuer-based Routing**: Determines token type based on issuer claim:
   - `OKTA_SERVICE_ISSUER_URL` → Service token validation
   - `OKTA_TOKEN_ISSUER_URL` → User token validation
5. **Token Verification**: Uses appropriate client ID and audience for validation

## Secured Endpoints

### FastAPI Endpoints (`api.py`)

The FastAPI router includes both secured and public endpoints:

#### Public Endpoints (No Authentication Required)
1. **GET `/health`** - Health check endpoint
2. **GET `/api/health`** - API health check endpoint

#### Secured Endpoints (Authentication Required)
1. **GET `/api/v1/documents/status`** - `RequireAnyAuth`
   - Allows both user and service tokens
   - Used for document status queries

2. **POST `/api/v1/documents/external/create`** - `RequireServiceAuth`
   - Requires service tokens only (GCP OIDC or Okta service OAuth)
   - Used for external document creation (service-to-service)

3. **POST `/api/v1/entities/search`** - `RequireAnyAuth`
   - Allows both user and service tokens
   - Used for entity search functionality

### REST Adapter Endpoints (`rest.py`)

The existing REST adapter endpoints maintain their current security decorators:
- `@verify_okta` - For user-facing endpoints
- `@verify_service_okta` - For service-to-service endpoints
- `@decode_token` - For token decoding and validation

## Security Configuration

### Required Settings

The following settings must be configured in `paperglass/settings.py`:

```python
# Okta Configuration
OKTA_SERVICE_ISSUER_URL = "https://your-okta-domain/oauth2/default"
OKTA_TOKEN_ISSUER_URL = "https://your-okta-domain/oauth2/default/v1/token"
OKTA_SERVICE_AUDIENCE = "api://your-service-audience"
OKTA_AUDIENCE = "api://your-user-audience"
OKTA_CLIENT_ID = "your-client-id"
OKTA_VERIFY = True  # Enable/disable Okta verification
```

### Token Requirements

#### GCP Service Account OIDC Tokens
- Must be valid Google Cloud identity tokens
- Issued by `https://accounts.google.com` or `accounts.google.com`
- Must contain valid `email` claim ending in `.gserviceaccount.com`

#### Okta OAuth Tokens
- Must be valid JWT tokens with proper signature
- Must contain valid `iss` (issuer), `cid` (client ID), and `aud` (audience) claims
- Must not be expired

## Error Handling

### HTTP Status Codes
- `401 Unauthorized` - Invalid or missing authentication token
- `403 Forbidden` - Valid token but insufficient permissions
- `500 Internal Server Error` - Authentication system error

### Error Response Format
```json
{
  "error": "Error description",
  "detail": "Detailed error message"
}
```

## Usage Examples

### Calling Secured Endpoints

#### With GCP Service Account Token
```bash
curl -H "Authorization: Bearer <gcp-identity-token>" \
     https://api.example.com/api/v1/documents/status?host_attachment_id=123&app_id=app&tenant_id=tenant&patient_id=patient
```

#### With Okta OAuth Token
```bash
curl -H "Authorization: Bearer <okta-oauth-token>" \
     https://api.example.com/api/v1/entities/search \
     -d '{"appId":"app","tenantId":"tenant","patientId":"patient"}'
```

## Implementation Benefits

1. **Unified Security**: Single security implementation supporting multiple token types
2. **Flexible Authentication**: Supports both user and service authentication patterns
3. **Backward Compatibility**: Existing REST endpoints maintain current security
4. **Comprehensive Coverage**: All API endpoints now require authentication
5. **Clear Separation**: Different security levels for different endpoint types
6. **Robust Validation**: Multi-step token validation with fallback mechanisms

## Migration Notes

### For API Consumers
- All endpoints now require valid authentication tokens
- Ensure proper `Authorization: Bearer <token>` headers are included
- Service-to-service calls should use GCP OIDC or Okta service tokens
- User-facing calls should use Okta user tokens

### For Developers
- Use appropriate security decorators/dependencies based on endpoint type
- Test with both GCP OIDC and Okta OAuth tokens
- Monitor authentication logs for validation issues
- Update API documentation to reflect authentication requirements

## Testing

### Security Testing Checklist
- [ ] Test with valid GCP service account OIDC tokens
- [ ] Test with valid Okta user OAuth tokens  
- [ ] Test with valid Okta service OAuth tokens
- [ ] Test with invalid/expired tokens (should return 401)
- [ ] Test with missing Authorization header (should return 401)
- [ ] Test with malformed tokens (should return 401)
- [ ] Verify appropriate security level for each endpoint type

### Test Token Generation
- GCP OIDC: Use `gcloud auth print-identity-token`
- Okta OAuth: Use Okta API or SDK to generate tokens

## Monitoring and Logging

The security implementation includes comprehensive logging:
- Authentication attempts (success/failure)
- Token validation steps
- Error conditions and reasons
- Performance metrics for token validation

Monitor these logs to ensure proper security operation and identify potential issues.
