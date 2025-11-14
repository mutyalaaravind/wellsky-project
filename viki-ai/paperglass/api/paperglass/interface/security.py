"""
Comprehensive security module for paperglass API endpoints.
Provides unified authentication supporting both GCP OIDC tokens and Okta OAuth tokens.
"""

import asyncio
from functools import wraps
from typing import Optional, Union
from starlette.responses import JSONResponse
from paperglass.interface.utils import (
    verify_okta_token, 
    _validate_gcp_identity_token,
    extract_elements_from_token,
    is_valid_issuer_url,
    decode_token
)
from paperglass.domain.utils.exception_utils import UnAuthorizedException
from paperglass.settings import (
    OKTA_SERVICE_ISSUER_URL, 
    OKTA_TOKEN_ISSUER_URL,
    OKTA_SERVICE_AUDIENCE,
    OKTA_AUDIENCE,
    OKTA_CLIENT_ID
)


def require_auth(allow_service_accounts: bool = True, allow_user_tokens: bool = True):
    """
    Comprehensive authentication decorator that supports both GCP OIDC tokens and Okta OAuth tokens.
    
    Args:
        allow_service_accounts: Whether to allow GCP service account OIDC tokens
        allow_user_tokens: Whether to allow Okta user OAuth tokens
    
    This decorator will:
    1. First try to validate as a GCP service account OIDC token
    2. If that fails, try to validate as an Okta OAuth token (service or user)
    3. If both fail, return 401 Unauthorized
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(starlette, request, *args, **kwargs):
            from paperglass.log import getLogger
            logger = getLogger(__name__)
            
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                logger.warning("Authentication failed: Authorization header missing")
                return JSONResponse(
                    status_code=401, 
                    content={"error": "Authorization header required"}
                )
            
            # Extract Bearer token
            if not auth_header.startswith('Bearer '):
                logger.warning("Authentication failed: Invalid Authorization header format")
                return JSONResponse(
                    status_code=401, 
                    content={"error": "Invalid Authorization header format"}
                )
            
            token = auth_header.split(' ')[1]
            if not token:
                logger.warning("Authentication failed: Empty token")
                return JSONResponse(
                    status_code=401, 
                    content={"error": "Empty token"}
                )
            
            # Try GCP service account OIDC token validation first
            if allow_service_accounts:
                try:
                    is_valid_gcp = await _validate_gcp_identity_token(token)
                    if is_valid_gcp:
                        logger.debug("Authentication successful: GCP service account OIDC token")
                        return await view_func(starlette, request, *args, **kwargs)
                except Exception as e:
                    logger.debug(f"GCP OIDC token validation failed: {e}")
            
            # Try Okta OAuth token validation
            if allow_user_tokens:
                try:
                    # Extract token claims to determine validation approach
                    claims = extract_elements_from_token(token)
                    issuer_url = claims.get("iss")
                    
                    if not issuer_url or not is_valid_issuer_url(issuer_url):
                        logger.warning(f"Authentication failed: Invalid or missing issuer URL: {issuer_url}")
                        return JSONResponse(
                            status_code=401, 
                            content={"error": "Invalid token issuer"}
                        )
                    
                    # Determine if this is a service token or user token based on issuer
                    if issuer_url == OKTA_SERVICE_ISSUER_URL:
                        # Service token validation
                        client_id = claims.get("cid")
                        audience = claims.get("aud")
                        
                        await verify_okta_token(
                            token,
                            issuer_url,
                            client_id,
                            audience
                        )
                        logger.debug("Authentication successful: Okta service OAuth token")
                        
                    elif issuer_url == OKTA_TOKEN_ISSUER_URL.replace("/v1/token", ""):
                        # User token validation
                        client_id = OKTA_CLIENT_ID
                        audience = OKTA_AUDIENCE
                        
                        await verify_okta_token(
                            token,
                            issuer_url,
                            client_id,
                            audience
                        )
                        logger.debug("Authentication successful: Okta user OAuth token")
                        
                    else:
                        logger.warning(f"Authentication failed: Unrecognized issuer URL: {issuer_url}")
                        return JSONResponse(
                            status_code=401, 
                            content={"error": "Unrecognized token issuer"}
                        )
                    
                    # If we get here, Okta validation succeeded
                    return await view_func(starlette, request, *args, **kwargs)
                    
                except UnAuthorizedException as e:
                    logger.warning(f"Okta OAuth token validation failed: {e}")
                except Exception as e:
                    logger.debug(f"Okta OAuth token validation failed: {e}")
            
            # If all validation attempts failed
            logger.warning("Authentication failed: All token validation attempts failed")
            return JSONResponse(
                status_code=401, 
                content={"error": "Invalid authentication token"}
            )
        
        return wrapper
    return decorator


def require_service_auth(view_func):
    """
    Decorator that requires either GCP service account OIDC token or Okta service OAuth token.
    This is for service-to-service communication.
    In local development (CLOUD_PROVIDER=local), authentication is bypassed for easier testing.
    """
    @wraps(view_func)
    async def wrapper(starlette, request, *args, **kwargs):
        from paperglass.settings import CLOUD_PROVIDER
        from paperglass.log import getLogger
        logger = getLogger(__name__)
        
        # Bypass authentication in local development
        if CLOUD_PROVIDER == "local":
            logger.debug("Authentication bypassed for local development (CLOUD_PROVIDER=local)")
            return await view_func(starlette, request, *args, **kwargs)
        
        # Use normal authentication for non-local environments
        auth_decorator = require_auth(allow_service_accounts=True, allow_user_tokens=False)
        return await auth_decorator(view_func)(starlette, request, *args, **kwargs)
    
    return wrapper


def require_user_auth(view_func):
    """
    Decorator that requires Okta user OAuth token.
    This is for user-facing endpoints.
    """
    return require_auth(allow_service_accounts=False, allow_user_tokens=True)(view_func)


def require_any_auth(view_func):
    """
    Decorator that accepts any valid authentication token (GCP OIDC or Okta OAuth).
    This is the most permissive option.
    """
    return require_auth(allow_service_accounts=True, allow_user_tokens=True)(view_func)


# Backward compatibility aliases
verify_service_okta_or_gcp = require_service_auth
verify_okta_or_gcp = require_any_auth
