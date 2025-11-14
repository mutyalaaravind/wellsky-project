"""
Google OIDC Authentication Utilities

This module provides utilities for obtaining OIDC tokens for service-to-service
authentication, similar to what Cloud Tasks does automatically.
"""

import json
import time
from typing import Optional
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import service_account
import google.auth
from util.custom_logger import getLogger
import aiocache
import httpx
import settings

LOGGER = getLogger(__name__)

@aiocache.cached(ttl=900, key_builder=lambda func, target_audience=None: f"oidc_token:{hash(target_audience or 'default')}")
async def get_oidc_token(target_audience: Optional[str] = None) -> str:
    """
    Get an OIDC identity token for service-to-service communication.
    
    This function obtains an OIDC token that can be used for authenticating
    with services that expect OIDC tokens (like the DJT service).
    
    Args:
        target_audience: The target audience for the token. If None, uses DJT_API_URL.
        
    Returns:
        str: A valid OIDC identity token
        
    Raises:
        Exception: If authentication fails
    """
    try:
        # Use DJT API URL as default audience
        audience = target_audience or settings.DJT_API_URL
        
        LOGGER.debug(f"Obtaining OIDC token for audience: {audience} (cache miss)")
        
        if settings.CLOUD_PROVIDER == "local":
            # In local development, we can't get real OIDC tokens
            # Return a mock token that will be bypassed by the security middleware
            LOGGER.debug("Local environment detected, returning mock OIDC token")
            return "mock-oidc-token-for-local-development"
        
        # Get default credentials
        credentials, project = google.auth.default()
        
        # Check if we have service account credentials
        if isinstance(credentials, service_account.Credentials):
            # Use service account to create OIDC token
            return await _get_oidc_token_from_service_account(credentials, audience)
        else:
            # Use metadata server to get OIDC token (for Cloud Run, Compute Engine)
            return await _get_oidc_token_from_metadata_server(audience)
            
    except Exception as e:
        LOGGER.error(f"Failed to get OIDC token: {str(e)}")
        raise Exception(f"Failed to obtain OIDC token for service-to-service communication: {str(e)}")

async def _get_oidc_token_from_service_account(
    credentials: service_account.Credentials, 
    audience: str
) -> str:
    """
    Get OIDC token using service account credentials.
    
    Args:
        credentials: Service account credentials
        audience: Target audience for the token
        
    Returns:
        str: OIDC identity token
    """
    try:
        # Create a new credentials object with the target audience
        oidc_credentials = credentials.with_claims(
            additional_claims={
                "target_audience": audience
            }
        )
        
        # Create the JWT token
        now = int(time.time())
        payload = {
            "iss": credentials.service_account_email,
            "sub": credentials.service_account_email,
            "aud": audience,
            "iat": now,
            "exp": now + 3600,  # 1 hour expiration
        }
        
        # Sign the token
        import jwt
        token = jwt.encode(
            payload,
            credentials.signer.key_id,
            algorithm="RS256",
            headers={"kid": credentials.signer.key_id}
        )
        
        LOGGER.debug("Successfully created OIDC token using service account")
        return token
        
    except Exception as e:
        LOGGER.error(f"Failed to create OIDC token from service account: {str(e)}")
        raise

async def _get_oidc_token_from_metadata_server(audience: str) -> str:
    """
    Get OIDC token from Google Cloud metadata server.
    
    This works in Cloud Run, Compute Engine, and other Google Cloud environments.
    
    Args:
        audience: Target audience for the token
        
    Returns:
        str: OIDC identity token
    """
    try:
        metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity"
        
        headers = {
            "Metadata-Flavor": "Google"
        }
        
        params = {
            "audience": audience,
            "format": "full",
            "include_email": "true"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                metadata_url,
                headers=headers,
                params=params,
                timeout=10.0
            )
            
            if response.status_code == 200:
                token = response.text.strip()
                LOGGER.debug("Successfully obtained OIDC token from metadata server")
                return token
            else:
                raise Exception(f"Metadata server returned status {response.status_code}: {response.text}")
                
    except Exception as e:
        LOGGER.error(f"Failed to get OIDC token from metadata server: {str(e)}")
        raise

async def get_oidc_headers(target_audience: Optional[str] = None) -> dict:
    """
    Get HTTP headers with OIDC authentication for service-to-service calls.
    
    Args:
        target_audience: The target audience for the token. If None, uses DJT_API_URL.
        
    Returns:
        dict: Headers dictionary with Authorization bearer token
        
    Raises:
        Exception: If authentication fails
    """
    try:
        if settings.CLOUD_PROVIDER == "local":
            # In local development, return headers without authentication
            LOGGER.debug("Local environment detected, returning headers without authentication")
            return {
                "Content-Type": "application/json"
            }
        
        token = await get_oidc_token(target_audience)
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    except Exception as e:
        LOGGER.error(f"Failed to get OIDC authentication headers: {str(e)}")
        raise Exception(f"Failed to create authenticated headers for service-to-service communication: {str(e)}")
