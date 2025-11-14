"""
OAuth Client Credentials Utility

Provides reusable OAuth 2.0 client credentials flow implementation
with token caching for service-to-service authentication.
"""

import aiohttp
import aiocache
from typing import Optional
from datetime import datetime
import json
from paperglass.log import getLogger
from paperglass.domain.utils.exception_utils import exceptionToMap

LOGGER = getLogger(__name__)


@aiocache.cached(ttl=3300, key_builder=lambda func, auth_server_url, client_id, client_secret, scope=None: f"oauth_token:{hash(auth_server_url)}:{hash(client_id)}:{hash(scope) if scope else 'no_scope'}")
async def get_oauth_token(
    auth_server_url: str,
    client_id: str,
    client_secret: str,
    scope: Optional[str] = None
) -> str:
    """
    Get an OAuth access token using client credentials flow.

    Tokens are cached for 55 minutes (3300 seconds) to avoid unnecessary
    OAuth requests. Most OAuth tokens are valid for 3600 seconds (1 hour),
    so we expire the cache 5 minutes early to prevent using expired tokens.

    Args:
        auth_server_url: The OAuth token endpoint URL
        client_id: OAuth client ID
        client_secret: OAuth client secret
        scope: Optional scope for the token request

    Returns:
        str: Access token for use in Authorization headers

    Raises:
        Exception: If token acquisition fails
    """
    start_time = datetime.utcnow()

    # Build the payload for client credentials grant
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    if scope:
        payload["scope"] = scope

    # Logging context (without sensitive data)
    extra = {
        "oauth_request": {
            "url": auth_server_url,
            "client_id": client_id,
            "has_scope": bool(scope),
            "payload": "**SENSITIVE**"
        }
    }

    LOGGER.debug("Requesting OAuth access token via client credentials", extra=extra)

    try:
        # Use a reasonable timeout for OAuth requests
        timeout = aiohttp.ClientTimeout(total=10.0)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(auth_server_url, data=payload) as response:
                end_time = datetime.utcnow()
                elapsed_time = (end_time - start_time).total_seconds()

                response_text = await response.text()

                extra["oauth_response"] = {
                    "status_code": response.status,
                    "elapsed_time": elapsed_time,
                    "body": "**SENSITIVE**"
                }

                if response.status == 200:
                    
                    response_data = json.loads(response_text)
                    access_token = response_data.get("access_token")

                    if not access_token:
                        raise Exception("OAuth response missing access_token field")

                    token_type = response_data.get("token_type", "Bearer")
                    expires_in = response_data.get("expires_in", 3600)

                    extra["oauth_response"].update({
                        "token_type": token_type,
                        "expires_in": expires_in,
                        "token_length": len(access_token)
                    })

                    LOGGER.info(
                        f"Successfully obtained OAuth access token (expires in {expires_in}s)",
                        extra=extra
                    )

                    return access_token
                else:
                    error_detail = response_text[:500]  # Limit error message length
                    extra["oauth_response"]["error_detail"] = error_detail

                    LOGGER.error(
                        f"OAuth token request failed with status {response.status}",
                        extra=extra
                    )

                    raise Exception(
                        f"OAuth token request failed: {response.status} - {error_detail}"
                    )

    except aiohttp.ClientError as e:
        end_time = datetime.utcnow()
        elapsed_time = (end_time - start_time).total_seconds()

        extra["error"] = exceptionToMap(e)
        extra["elapsed_time"] = elapsed_time

        LOGGER.error(
            f"OAuth token request failed with client error: {str(e)}",
            extra=extra
        )

        raise Exception(f"Failed to connect to OAuth server: {str(e)}")

    except Exception as e:
        end_time = datetime.utcnow()
        elapsed_time = (end_time - start_time).total_seconds()

        extra["error"] = exceptionToMap(e)
        extra["elapsed_time"] = elapsed_time

        LOGGER.error(
            f"Unexpected error getting OAuth token: {str(e)}",
            extra=extra
        )

        raise Exception(f"Failed to obtain OAuth access token: {str(e)}")
