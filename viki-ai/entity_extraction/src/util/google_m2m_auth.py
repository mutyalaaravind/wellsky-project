"""
Google Machine-to-Machine Authentication Utilities

This module provides utilities for authenticating service-to-service calls
in Google Cloud environments.
"""

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import service_account
import google.auth
from util.custom_logger import getLogger
import aiocache


LOGGER = getLogger(__name__)

@aiocache.cached(ttl=900)
async def get_auth_token() -> str:
    """
    Get an authentication token for service-to-service communication.
    
    This function uses Google's default credentials which work in various environments:
    - Cloud Run: Uses the service account attached to the Cloud Run service
    - Local development: Uses gcloud auth application-default login credentials
    - Compute Engine: Uses the default service account
    
    The token is cached for 900 seconds (15 minutes) to avoid unnecessary API calls.
    
    Returns:
        str: A valid OAuth2 access token
        
    Raises:
        Exception: If authentication fails
    """
    try:
        # Get default credentials (works in Cloud Run, local development with gcloud auth)
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Refresh the credentials to get a valid token
        auth_req = GoogleRequest()
        credentials.refresh(auth_req)
        
        LOGGER.debug("Successfully obtained authentication token for service-to-service communication")
        return credentials.token
        
    except Exception as e:
        LOGGER.error(f"Failed to get authentication token: {str(e)}")
        raise Exception(f"Failed to authenticate for service-to-service communication: {str(e)}")

def get_auth_headers() -> dict:
    """
    Get HTTP headers with authentication for service-to-service calls.
    
    Returns:
        dict: Headers dictionary with Authorization bearer token
        
    Raises:
        Exception: If authentication fails
    """
    try:
        # This is a synchronous version for cases where async is not needed
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        auth_req = GoogleRequest()
        credentials.refresh(auth_req)
        
        return {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json"
        }
        
    except Exception as e:
        LOGGER.error(f"Failed to get authentication headers: {str(e)}")
        raise Exception(f"Failed to authenticate for service-to-service communication: {str(e)}")
