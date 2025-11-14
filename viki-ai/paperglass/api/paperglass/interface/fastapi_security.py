"""
FastAPI security dependencies for paperglass API endpoints.
Provides unified authentication supporting both GCP OIDC tokens and Okta OAuth tokens.
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from paperglass.interface.utils import (
    verify_okta_token, 
    _validate_gcp_identity_token,
    extract_elements_from_token,
    is_valid_issuer_url
)
from paperglass.domain.utils.exception_utils import UnAuthorizedException
from paperglass.settings import (
    OKTA_SERVICE_ISSUER_URL, 
    OKTA_TOKEN_ISSUER_URL,
    OKTA_SERVICE_AUDIENCE,
    OKTA_AUDIENCE,
    OKTA_CLIENT_ID
)

# FastAPI security scheme
security = HTTPBearer()


async def validate_any_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    FastAPI dependency that validates either GCP OIDC tokens or Okta OAuth tokens.
    Returns the validated token string.
    """
    from paperglass.log import getLogger
    logger = getLogger(__name__)
    
    token = credentials.credentials
    
    # Try GCP service account OIDC token validation first
    try:
        is_valid_gcp = await _validate_gcp_identity_token(token)
        if is_valid_gcp:
            logger.debug("Authentication successful: GCP service account OIDC token")
            return token
    except Exception as e:
        logger.debug(f"GCP OIDC token validation failed: {e}")
    
    # Try Okta OAuth token validation
    try:
        # Extract token claims to determine validation approach
        claims = extract_elements_from_token(token)
        issuer_url = claims.get("iss")
        
        # Skip Okta validation if this is a Google token (already tried GCP validation above)
        if issuer_url in ['https://accounts.google.com', 'accounts.google.com']:
            logger.debug(f"Skipping Okta validation for Google issuer: {issuer_url}")
            raise Exception("Google token, skip Okta validation")
        
        if not issuer_url or not is_valid_issuer_url(issuer_url):
            logger.warning(f"Authentication failed: Invalid or missing issuer URL: {issuer_url}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token issuer"
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
            raise HTTPException(
                status_code=401, 
                detail="Unrecognized token issuer"
            )
        
        # If we get here, Okta validation succeeded
        return token
        
    except UnAuthorizedException as e:
        logger.warning(f"Okta OAuth token validation failed: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.debug(f"Okta OAuth token validation failed: {e}")
    
    # If all validation attempts failed
    logger.warning("Authentication failed: All token validation attempts failed")
    raise HTTPException(
        status_code=401, 
        detail="Invalid authentication token"
    )


async def validate_service_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    FastAPI dependency that validates either GCP service account OIDC tokens or Okta service OAuth tokens.
    This is for service-to-service communication.
    """
    from paperglass.log import getLogger
    logger = getLogger(__name__)
    
    token = credentials.credentials
    
    # Try GCP service account OIDC token validation first
    try:
        is_valid_gcp = await _validate_gcp_identity_token(token)
        if is_valid_gcp:
            logger.debug("Authentication successful: GCP service account OIDC token")
            return token
    except Exception as e:
        logger.debug(f"GCP OIDC token validation failed: {e}")
    
    # Try Okta service OAuth token validation
    try:
        # Extract token claims to determine validation approach
        claims = extract_elements_from_token(token)
        issuer_url = claims.get("iss")
        
        if issuer_url != OKTA_SERVICE_ISSUER_URL:
            logger.warning(f"Service authentication failed: Invalid issuer URL for service token: {issuer_url}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid service token issuer"
            )
        
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
        return token
        
    except UnAuthorizedException as e:
        logger.warning(f"Okta service OAuth token validation failed: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.debug(f"Okta service OAuth token validation failed: {e}")
    
    # If all validation attempts failed
    logger.warning("Service authentication failed: All token validation attempts failed")
    raise HTTPException(
        status_code=401, 
        detail="Invalid service authentication token"
    )


async def validate_user_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    FastAPI dependency that validates Okta user OAuth tokens.
    This is for user-facing endpoints.
    """
    from paperglass.log import getLogger
    logger = getLogger(__name__)
    
    token = credentials.credentials
    
    # Try Okta user OAuth token validation
    try:
        # Extract token claims to determine validation approach
        claims = extract_elements_from_token(token)
        issuer_url = claims.get("iss")
        
        if issuer_url != OKTA_TOKEN_ISSUER_URL.replace("/v1/token", ""):
            logger.warning(f"User authentication failed: Invalid issuer URL for user token: {issuer_url}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid user token issuer"
            )
        
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
        return token
        
    except UnAuthorizedException as e:
        logger.warning(f"Okta user OAuth token validation failed: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.debug(f"Okta user OAuth token validation failed: {e}")
    
    # If validation failed
    logger.warning("User authentication failed: Token validation failed")
    raise HTTPException(
        status_code=401, 
        detail="Invalid user authentication token"
    )


# Convenience dependencies for different authentication requirements
RequireAnyAuth = Depends(validate_any_auth_token)
RequireServiceAuth = Depends(validate_service_auth_token)
RequireUserAuth = Depends(validate_user_auth_token)
