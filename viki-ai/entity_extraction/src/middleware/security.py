"""
Security Middleware and Dependencies

This module provides FastAPI security dependencies for validating OIDC tokens
from Google Cloud Tasks and other Google services.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from util.oidc_validator import get_oidc_validator, OIDCValidationError
import settings

LOGGER = getLogger(__name__)

# FastAPI security scheme for Bearer tokens
security = HTTPBearer(auto_error=False)

async def require_service_account_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency that validates Google OIDC tokens from service accounts.
    
    This dependency only validates tokens when CLOUD_PROVIDER is not "local".
    In local development, it bypasses authentication for easier testing.
    
    Args:
        request: The FastAPI request object
        credentials: The HTTP Bearer credentials from the Authorization header
        
    Returns:
        Dict containing the validated token claims and authentication info
        
    Raises:
        HTTPException: 401 if authentication fails, 403 if forbidden
    """
    extra = {
        "function": "require_service_account_auth",
        "cloud_provider": settings.CLOUD_PROVIDER,
        "endpoint": str(request.url),
        "method": request.method
    }
    
    # Skip authentication in local development
    if settings.CLOUD_PROVIDER == "local":
        LOGGER.debug("Bypassing authentication for local development", extra=extra)
        return {
            "authenticated": False,
            "bypass_reason": "local_development",
            "cloud_provider": settings.CLOUD_PROVIDER
        }
    
    # Check if credentials are provided
    if not credentials:
        extra.update({
            "authentication_status": "missing_credentials",
            "error": "No Authorization header provided"
        })
        LOGGER.warning("Authentication failed: missing credentials", extra=extra)
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Validate the OIDC token
        validator = get_oidc_validator()
        authorization_header = f"Bearer {credentials.credentials}"
        
        LOGGER.debug("Validating OIDC token for service account authentication", extra=extra)
        
        token_claims = await validator.validate_token(authorization_header)
        
        # Extract relevant information from token claims
        auth_info = {
            "authenticated": True,
            "token_subject": token_claims.get("sub"),
            "token_email": token_claims.get("email"),
            "token_issuer": token_claims.get("iss"),
            "token_audience": token_claims.get("aud"),
            "service_account": token_claims.get("email"),
            "cloud_provider": settings.CLOUD_PROVIDER,
            "validation_time": token_claims.get("iat"),
            "expiration_time": token_claims.get("exp")
        }
        
        extra.update({
            "authentication_status": "success",
            "service_account": auth_info["service_account"]
        })
        LOGGER.info("Successfully authenticated service account request", extra=extra)
        
        return auth_info
        
    except OIDCValidationError as e:
        extra.update({
            "authentication_status": "validation_failed",
            "error": exceptionToMap(e)
        })
        LOGGER.warning("OIDC token validation failed", extra=extra)
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
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

def optional_service_account_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Optional authentication dependency that doesn't raise exceptions.
    
    This can be used for endpoints that support both authenticated and 
    unauthenticated access.
    
    Args:
        request: The FastAPI request object
        credentials: The HTTP Bearer credentials from the Authorization header
        
    Returns:
        Dict containing authentication info or indication of no auth
    """
    extra = {
        "function": "optional_service_account_auth",
        "cloud_provider": settings.CLOUD_PROVIDER,
        "endpoint": str(request.url),
        "method": request.method
    }
    
    # Skip authentication in local development
    if settings.CLOUD_PROVIDER == "local":
        LOGGER.debug("Bypassing optional authentication for local development", extra=extra)
        return {
            "authenticated": False,
            "bypass_reason": "local_development",
            "cloud_provider": settings.CLOUD_PROVIDER
        }
    
    # If no credentials provided, return unauthenticated
    if not credentials:
        LOGGER.debug("No credentials provided for optional authentication", extra=extra)
        return {
            "authenticated": False,
            "reason": "no_credentials_provided"
        }
    
    try:
        # Try to validate the token
        validator = get_oidc_validator()
        authorization_header = f"Bearer {credentials.credentials}"
        
        # Note: This is a synchronous call, would need async version for production
        # For now, we'll return unauthenticated if validation would be complex
        LOGGER.debug("Optional authentication not fully implemented", extra=extra)
        return {
            "authenticated": False,
            "reason": "optional_auth_not_implemented"
        }
        
    except Exception as e:
        extra.update({
            "authentication_status": "optional_auth_error",
            "error": exceptionToMap(e)
        })
        LOGGER.debug("Optional authentication failed, continuing without auth", extra=extra)
        return {
            "authenticated": False,
            "reason": "validation_failed",
            "error": str(e)
        }
