from typing import Dict, Any, Optional
import google.auth
import google.auth.transport.requests
import aiocache
from paperglass.infrastructure.adapters.http_rest_client import HttpRestClient
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.log import getLogger
import paperglass.settings as settings

LOGGER = getLogger(__name__)


@aiocache.cached(ttl=900, key_builder=lambda func, target_audience: f"oidc_token:{hash(target_audience)}")  # Cache for 15 minutes
async def _get_cached_oidc_token(target_audience: str) -> Optional[str]:
    """
    Get a cached OIDC identity token for service-to-service authentication.
    
    Args:
        target_audience: The target audience for the token (entity extraction service URL)
        
    Returns:
        str: A valid OIDC identity token, or None if in local environment or if auth fails
    """
    # Check if we're in local development mode first
    if hasattr(settings, 'CLOUD_PROVIDER') and settings.CLOUD_PROVIDER == "local":
        LOGGER.debug("Local environment detected (CLOUD_PROVIDER=local), skipping OIDC token generation for entity extraction")
        return None
    
    try:
        LOGGER.info("Cloud environment detected, generating OIDC token for entity extraction service authentication (cache miss)")
        
        # Use Google Cloud metadata server to get OIDC token
        import httpx
        metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity"
        
        headers = {
            "Metadata-Flavor": "Google"
        }
        
        params = {
            "audience": target_audience,
            "format": "full",
            "include_email": "true"
        }
        
        LOGGER.debug(f"Requesting OIDC token from metadata server for audience: {target_audience}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                metadata_url,
                headers=headers,
                params=params,
                timeout=10.0
            )
            
            if response.status_code == 200:
                token = response.text.strip()
                # Log token length for verification without exposing the actual token
                LOGGER.info(f"Successfully obtained OIDC token for entity extraction service (length: {len(token)} chars)")
                return token
            else:
                error_msg = f"Metadata server returned status {response.status_code}: {response.text}"
                LOGGER.error(f"Failed to get OIDC token from metadata server: {error_msg}")
                raise Exception(error_msg)
                
    except Exception as e:
        LOGGER.error(f"Failed to get OIDC token for entity extraction service: {str(e)}")
        # In case of failure, return None and let the request proceed without auth
        # This allows for graceful degradation in development environments
        return None


class EntityExtractionClient:
    """
    Client adapter for communicating with the Entity Extraction API.
    """

    def __init__(self, http_client: Optional[HttpRestClient] = None):
        """
        Initialize the EntityExtractionClient.
        
        Args:
            http_client: Optional HTTP client for dependency injection. If not provided,
                        a new HttpRestClient instance will be created.
        """
        self.http_client = http_client or HttpRestClient()
        self.base_url = settings.ENTITY_EXTRACTION_API_URL.rstrip('/')

    async def _get_oidc_token(self, target_audience: str) -> Optional[str]:
        """
        Get a cached OIDC identity token for service-to-service authentication.
        
        Args:
            target_audience: The target audience for the token (entity extraction service URL)
            
        Returns:
            str: A valid OIDC identity token, or None if in local environment or if auth fails
        """
        return await _get_cached_oidc_token(target_audience)

    async def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for entity extraction API requests.
        
        Returns:
            Dictionary of HTTP headers, including authentication for cloud environments
        """
        headers = {"Content-Type": "application/json"}
        
        # Get OIDC token for authentication (with caching)
        oidc_token = await self._get_oidc_token(self.base_url)
        if oidc_token:
            headers["Authorization"] = f"Bearer {oidc_token}"
            LOGGER.debug("Added cached OIDC authentication header for entity extraction request")
        else:
            LOGGER.debug("No OIDC token available, proceeding without authentication")
        
        return headers

    async def get_status(self, run_id: str) -> Dict[str, Any]:
        """
        Get the status of an entity extraction job by run_id.
        
        Args:
            run_id: The unique identifier for the extraction job.
            
        Returns:
            Dict containing the job status and pipeline information.
            
        Raises:
            Exception: If the request fails or returns an error status.
        """
        url = f"{self.base_url}/api/status/{run_id}"
        
        # Get headers with conditional OIDC authentication
        headers = await self._get_headers()
        
        # Use longer timeouts for local development to handle slower container startup
        connection_timeout = settings.EXTERNAL_API_CONNECT_TIMEOUT_SECONDS
        response_timeout = settings.EXTERNAL_API_SOCKET_READ_TIMEOUT_SECONDS
        
        # Prepare comprehensive request context for logging
        http_request = {
            "method": "GET",
            "url": url,
            "headers": headers,
            "body": None,
            "run_id": run_id,
            "has_auth_header": "Authorization" in headers,
            "connection_timeout": connection_timeout,
            "response_timeout": response_timeout
        }
        
        extra = {
            "http_request": http_request,
            "entity_extraction_client": {
                "base_url": self.base_url,
                "run_id": run_id
            }
        }
        
        try:
            LOGGER.info(f"Fetching entity extraction status for run_id: {run_id}", extra=extra)
            
            response = await self.http_client.resolve(
                method="GET",
                url=url,
                headers=headers,
                connection_timeout=connection_timeout,
                response_timeout=response_timeout
            )
            
            status_code = response.get('status')
            response_data = response.get('data')
            response_headers = response.get('headers', {})
            
            # Add response details to extra for logging
            extra.update({
                "http_response": {
                    "status_code": status_code,
                    "headers": response_headers,
                    "data_type": type(response_data).__name__,
                    "data_length": len(str(response_data)) if response_data else 0
                }
            })
            
            if status_code == 200:
                LOGGER.debug(f"Successfully retrieved entity extraction status for run_id: {run_id}", extra=extra)
                return response_data
            else:
                error_msg = f"Entity extraction API returned status {status_code}"
                extra.update({
                    "error_details": {
                        "status_code": status_code,
                        "response_data": response_data,
                        "response_headers": response_headers
                    }
                })
                LOGGER.error(error_msg, extra=extra)
                raise Exception(f"{error_msg}: {response_data}")
                
        except Exception as e:
            # Comprehensive error logging with all context
            extra.update({
                "error": exceptionToMap(e),
                "exception_type": type(e).__name__,
                "exception_message": str(e)
            })
            
            LOGGER.error(f"Error fetching entity extraction status for run_id: {run_id}", extra=extra)
            raise
