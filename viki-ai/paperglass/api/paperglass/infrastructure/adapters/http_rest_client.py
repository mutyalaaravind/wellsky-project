from aiohttp import ClientSession, ClientResponse, ClientError, ClientTimeout
from typing import Optional, Dict, Any, Union
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.log import getLogger

LOGGER = getLogger(__name__)

class HttpRestClient:
    """
    An asynchronous HTTP REST client adapter.
    """

    async def resolve(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]] = None,
        connection_timeout: Optional[float] = 5.0,
        response_timeout: Optional[float] = 5.0
    ) -> Dict[str, Union[Dict[str, Any], bytes]]:
        """
        Resolves an HTTP request asynchronously.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: The endpoint URL.
            headers: Map of header values.
            body: Optional payload for PUT/POST requests.
            connection_timeout: Optional connection timeout in seconds (default: 5.0).
            response_timeout: Optional response timeout in seconds (default: 5.0).

        Returns:
            A dictionary containing the response status, data (JSON or bytes), and headers.

        Raises:
            ClientError: If the request fails due to client-side issues.
            Exception: For other unexpected errors during the request.
        """
        extra = {
            "request": {
                "method": method,
                "url": url,
                "headers": headers,
                "body": body
            }
        }

        try:
            async with ClientSession() as session:
                timeout = ClientTimeout(connect=connection_timeout, total=response_timeout)
                async with session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=body if body else None,
                    timeout=timeout
                ) as response:
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type.lower():
                        response_data = await response.json()
                    else:
                        response_data = await response.read()
                    return {
                        'status': response.status,
                        'data': response_data,
                        'headers': dict(response.headers)
                    }
        except ClientError as e:
            extra.update({
                "error": exceptionToMap(e)
            })
            LOGGER.error("ClientError during request", extra=extra)
            raise
        except Exception as e:
            extra.update({
                "error": exceptionToMap(e)
            })
            LOGGER.error("Unexpected error during request", extra=extra)
            raise
