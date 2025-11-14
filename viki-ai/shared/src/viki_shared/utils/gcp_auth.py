"""
Google Cloud Platform Authentication Utilities

This module provides utilities for authenticating service-to-service calls
in Google Cloud environments.
"""

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import service_account
import google.auth
from viki_shared.utils.logger import getLogger
import aiocache


logger = getLogger(__name__)

@aiocache.cached(ttl=300)
async def get_service_account_identity_token(target_audience: str) -> str:
    """
    Get a service account identity token for service-to-service communication.

    This function generates a proper JWT identity token with the target audience claim,
    which is required for secure service-to-service authentication.

    Works in various environments:
    - Cloud Run: Uses the service account attached to the Cloud Run service
    - Local development: Uses gcloud auth application-default login credentials
    - Compute Engine: Uses the default service account

    The token is cached for 900 seconds (15 minutes) to avoid unnecessary API calls.

    Args:
        target_audience: The target audience for the identity token (typically the service URL)

    Returns:
        str: A valid JWT identity token with audience claim

    Raises:
        Exception: If authentication fails
    """
    try:
        # Get default credentials to identify the service account
        credentials, project = google.auth.default()

        # Always use IAM API to generate identity tokens for maximum compatibility
        import requests as http_requests

        # Detect impersonated credentials and handle them differently
        is_impersonated = (hasattr(credentials, '_target_principal') or
                          credentials.__class__.__name__ == 'ImpersonatedCredentials')

        logger.warning(f"[DEBUG_TOKEN_GEN_v2] Credentials type: {credentials.__class__.__name__}, is_impersonated: {is_impersonated}")

        if is_impersonated:
            # For impersonated credentials, try metadata service first (works in cloud)
            # Then fall back to using user credentials to get access token
            access_token = None

            # Try metadata service first
            try:
                metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
                headers = {"Metadata-Flavor": "Google"}
                import requests
                response = requests.get(metadata_url, headers=headers, timeout=2)
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get('access_token')
                    logger.debug("Got access token from metadata service")
            except Exception:
                logger.debug("Metadata service not available (local development)")

            # If metadata fails, get the underlying user credentials to make IAM call
            if not access_token:
                try:
                    # For impersonated credentials, get the source credentials to make IAM API call
                    source_credentials = getattr(credentials, '_source_credentials', None)
                    if source_credentials:
                        auth_req = GoogleRequest()
                        source_credentials.refresh(auth_req)
                        access_token = source_credentials.token
                        logger.debug("Got access token from source credentials for IAM API")
                    else:
                        raise Exception("Could not find source credentials for impersonated credentials")
                except Exception as source_creds_error:
                    raise Exception(f"Could not get access token for IAM API call: {source_creds_error}")
        else:
            # Regular service account credentials
            auth_req = GoogleRequest()
            credentials.refresh(auth_req)
            access_token = credentials.token
            logger.debug("Got access token from service account credentials")

        # Determine the service account email
        service_account_email = getattr(credentials, 'service_account_email', None)

        if not service_account_email:
            # For impersonated credentials, the service account email might be in _target_principal
            service_account_email = getattr(credentials, '_target_principal', None)

        if not service_account_email:
            # Try to get service account email from token info
            token_info_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
            token_response = http_requests.get(token_info_url, timeout=10)
            if token_response.status_code == 200:
                token_data = token_response.json()
                service_account_email = token_data.get('email')

        if not service_account_email or not service_account_email.endswith('.gserviceaccount.com'):
            raise Exception(f"Unable to determine service account email from credentials. Got: {service_account_email}")

        # Generate identity token using IAM Credentials API
        iam_url = f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{service_account_email}:generateIdToken"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "audience": target_audience,
            "includeEmail": True
        }

        logger.debug(f"Generating identity token for {service_account_email} with audience {target_audience}")

        iam_response = http_requests.post(iam_url, headers=headers, json=payload, timeout=10)
        if iam_response.status_code == 200:
            response_data = iam_response.json()
            token = response_data.get('token')
            if token:
                logger.debug(f"Successfully generated identity token via IAM API for {service_account_email}")
                return token
            else:
                raise Exception("IAM API response did not contain token")
        else:
            error_detail = iam_response.text
            raise Exception(f"IAM API returned status {iam_response.status_code}: {error_detail}")

    except Exception as e:
        logger.error(f"Failed to get service account identity token: {str(e)}")
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
        logger.error(f"Failed to get authentication headers: {str(e)}")
        raise Exception(f"Failed to authenticate for service-to-service communication: {str(e)}")