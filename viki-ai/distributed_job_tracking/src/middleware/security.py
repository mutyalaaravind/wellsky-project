"""
Security Middleware for DJT Service

This module provides FastAPI security dependencies for validating OIDC tokens
from Cloud Tasks and other Google Cloud services.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from util.oidc_validator import get_oidc_validator, OIDCValidationError
from util.custom_logger import getLogger
from util.exception import exceptionToMap
import settings

LOGGER = getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)

async def require_service_account_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency that validates OIDC tokens for service account authentication.
    
    This dependency:
    - Bypasses authentication when CLOUD_PROVIDER is "local" for development
    - Validates OIDC tokens in cloud environments
    - Returns authentication information for logging and auditing
    
    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials from Authorization header
        
    Returns:
        Dict containing authentication information
        
    Raises:
        HTTPException: 401 if authentication fails, 500 for unexpected errors
    """
    extra = {
        "function": "require_service_account_auth",
        "cloud_provider": settings.CLOUD_PROVIDER,
        "endpoint": str(request.url),
        "method": request.method
    }
    
    try:
        # Bypass authentication in local development
        if settings.CLOUD_PROVIDER == "local":
            LOGGER.debug("Bypassing authentication for local development", extra=extra)
            return {
                "authenticated": False,
                "bypass_reason": "local_development",
                "cloud_provider": settings.CLOUD_PROVIDER,
                "endpoint": str(request.url),
                "method": request.method
            }
        
        # Require credentials in cloud environments
        if not credentials:
            extra.update({"authentication_status": "missing_credentials"})
            LOGGER.warning("Authentication required but no credentials provided", extra=extra)
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Please provide a valid Bearer token."
            )
        
        # Validate the OIDC token
        validator = get_oidc_validator()
        authorization_header = f"{credentials.scheme} {credentials.credentials}"
        
        extra.update({"authentication_status": "validating"})
        LOGGER.debug("Validating OIDC token", extra=extra)
        
        token_claims = await validator.validate_token(authorization_header)
        
        # Extract service account information
        service_account = token_claims.get("email") or token_claims.get("sub")
        
        auth_info = {
            "authenticated": True,
            "service_account": service_account,
            "token_subject": token_claims.get("sub"),
            "token_issuer": token_claims.get("iss"),
            "token_audience": token_claims.get("aud"),
            "cloud_provider": settings.CLOUD_PROVIDER,
            "endpoint": str(request.url),
            "method": request.method
        }
        
        extra.update({
            "authentication_status": "success",
            "service_account": service_account
        })
        LOGGER.info("Successfully authenticated service account", extra=extra)
        
        return auth_info
        
    except OIDCValidationError as e:
        extra.update({
            "authentication_status": "failed",
            "error": exceptionToMap(e)
        })
        LOGGER.warning("OIDC token validation failed", extra=extra)
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions without modification
        raise e
    except Exception as e:
        extra.update({
            "authentication_status": "error",
            "error": exceptionToMap(e)
        })
        LOGGER.error("Unexpected error during authentication", extra=extra)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during authentication"
        )
