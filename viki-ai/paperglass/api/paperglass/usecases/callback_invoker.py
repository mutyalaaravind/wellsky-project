import asyncio
import json
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime
from pydantic import BaseModel

from paperglass.domain.models import Document
from paperglass.domain.values import Configuration
from paperglass.usecases.configuration import get_config
from paperglass.infrastructure.ports import IQueryPort
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.infrastructure.adapters.oauth_client import get_oauth_token
from kink import inject

import settings

from paperglass.log import getLogger
LOGGER = getLogger(__name__)


class DocumentProcessingCompleteRequest(BaseModel):
    """Request model for document processing complete callback."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    source_id: Optional[str] = None
    status: str = "completed"
    timestamp: str
    run_id: str
    metadata: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None


class CallbackInvoker:
    """
    Invoker for publishing document processing completion callbacks based on integration configuration.
    """
    
    def __init__(self):
        """Initialize the CallbackInvoker."""
        LOGGER.info("CallbackInvoker initialized")
    
    async def _get_oauth_token_with_logging(self, extra: Dict[str, Any]) -> Optional[str]:
        """
        Get OAuth token for callback authentication with error handling and logging.
        
        :param extra: Extra logging context
        :return: OAuth token if successful, None otherwise
        """
        try:
            oauth_token = await get_oauth_token(
                auth_server_url=settings.OKTA_TOKEN_ISSUER_URL,
                client_id=settings.OKTA_CLIENT_ID,
                client_secret=settings.OKTA_CLIENT_SECRET,
                scope=settings.OKTA_SCOPE
            )
            extra["oauth_token_acquired"] = True
            LOGGER.debug("Successfully obtained OAuth token for callback authentication", extra=extra)
            return oauth_token
        except Exception as token_error:
            extra["oauth_token_error"] = str(token_error)

            # In non-local environments, OAuth authentication is mandatory
            if settings.CLOUD_PROVIDER != "local":
                LOGGER.error(
                    f"Failed to obtain OAuth token in {settings.CLOUD_PROVIDER} environment: {str(token_error)}. "
                    "Authentication is required for callbacks in non-local environments.",
                    extra=extra
                )
                raise  # Re-raise the exception - OAuth is mandatory in production

            # In local environment, OAuth failure is acceptable
            LOGGER.warning(
                f"Failed to obtain OAuth token for callback: {str(token_error)}. "
                "Callback may fail if target requires authentication.",
                extra=extra
            )
            return None
    
    @inject
    async def invoke_document_processing_complete(
        self, 
        document: Document, 
        query: IQueryPort
    ) -> bool:
        """
        Invoke callback for document processing completion.
        
        :param document: The document that completed processing
        :param query: Query port for database operations
        :return: True if callback was invoked successfully, False otherwise
        """
        start_time = datetime.now()
        
        extra = {
            "app_id": document.app_id,
            "tenant_id": document.tenant_id,
            "patient_id": document.patient_id,
            "document_id": document.id
        }
        
        try:
            # Pull the app config
            config: Configuration = await get_config(document.app_id, document.tenant_id, query)
            
            # Check for integration override in document metadata
            integration_config = config.integration
            if document.metadata and "integration" in document.metadata:
                extra["integration_override_found"] = True
                LOGGER.info("Found integration override in document metadata", extra=extra)
                integration_config = self._apply_integration_override(config.integration, document.metadata["integration"])
            else:
                extra["integration_override_found"] = False
            
            # Check that integration exists, callback is configured and enabled
            if not (integration_config and 
                    integration_config.callback and
                    integration_config.callback.enabled and 
                    integration_config.callback.endpoint):
                
                LOGGER.debug("Document processing complete - integration callback not configured", extra={
                    **extra,
                    "integration_exists": integration_config is not None,
                    "callback_exists": integration_config.callback is not None if integration_config else None,
                    "callback_enabled": integration_config.callback.enabled if integration_config and integration_config.callback else None,
                    "callback_endpoint": integration_config.callback.endpoint if integration_config and integration_config.callback else None
                })
                return True  # Not an error, just not configured
            
            # Handle URL templating - replace {base_url} with integration.base_url
            base_url = integration_config.base_url or ""
            raw_endpoint_template = integration_config.callback.endpoint
            callback_url = raw_endpoint_template.format(base_url=base_url)

            # Validate URL resolution
            if "{base_url}" in callback_url:
                LOGGER.warning("URL template did not resolve properly - base_url placeholder still present", extra={
                    **extra,
                    "raw_endpoint_template": raw_endpoint_template,
                    "base_url": base_url,
                    "callback_url": callback_url
                })

            # Test URL format validity
            import urllib.parse
            try:
                parsed_url = urllib.parse.urlparse(callback_url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    LOGGER.error("Invalid callback URL format detected", extra={
                        **extra,
                        "callback_url": callback_url,
                        "parsed_scheme": parsed_url.scheme,
                        "parsed_netloc": parsed_url.netloc,
                        "raw_endpoint_template": raw_endpoint_template,
                        "base_url": base_url
                    })
                    return False
            except Exception as url_parse_error:
                LOGGER.error("Failed to parse callback URL", extra={
                    **extra,
                    "callback_url": callback_url,
                    "url_parse_error": str(url_parse_error)
                })
                return False
            
            extra.update({
                "callback_url": callback_url,
                "callback_endpoint_template": integration_config.callback.endpoint,
                "base_url": base_url,
                "callback_enabled": integration_config.callback.enabled,
                "callback_embed_entities_enabled": integration_config.callback.embed_entities_enabled,
                "callback_cloudtask_enabled": integration_config.callback.cloudtask_enabled,
                "callback_headers_count": len(integration_config.callback.headers) if integration_config.callback.headers else 0,
                "url_template_resolved_successfully": "{base_url}" not in callback_url
            })
            
            LOGGER.info("Invoking document processing complete callback", extra=extra)

            # Pre-callback validation logging
            LOGGER.info("Callback pre-validation details", extra={
                **extra,
                "callback_method": "cloudtask" if integration_config.callback.cloudtask_enabled else "direct_http",
                "callback_url_length": len(callback_url),
                "callback_url_domain": urllib.parse.urlparse(callback_url).netloc if callback_url else "unknown",
                "has_custom_headers": bool(integration_config.callback.headers),
                "entity_embedding_requested": integration_config.callback.embed_entities_enabled
            })
            
            # Fetch entities if embed_entities_enabled is True
            entities = None
            if integration_config.callback.embed_entities_enabled:
                LOGGER.info("Embed entities is enabled, fetching entities for document", extra=extra)
                try:
                    # Import locally to avoid circular dependencies
                    from paperglass.usecases.entities import search_entities
                    
                    # Fetch entities for the document
                    search_result = await search_entities(
                        app_id=document.app_id,
                        tenant_id=document.tenant_id,
                        patient_id=document.patient_id,
                        document_id=document.id,
                        query=query
                    )
                    entities = search_result.get("entities", [])
                    extra.update({"entities_count": len(entities) if entities else 0})
                    LOGGER.info("Fetched entities for document", extra={
                        **extra,
                        "search_result_keys": list(search_result.keys()) if search_result else None,
                        "entities_type": type(entities).__name__,
                        "entities_sample": entities[0] if entities and len(entities) > 0 else None
                    })
                except Exception as e:
                    LOGGER.warning("Failed to fetch entities for document", extra={
                        **extra,
                        "error": exceptionToMap(e)
                    })
                    entities = []  # Continue with empty entities list on error
            else:
                LOGGER.info("Embed entities is disabled, no entities will be included in callback", extra=extra)
            
            # Extract run_id and status from document operation status
            run_id = None
            document_status = "completed"  # Default status
            
            if document.operation_status:
                # Try to get run_id and status from entity extraction first, then medication extraction
                from paperglass.domain.values import DocumentOperationType
                for op_type in [DocumentOperationType.ENTITY_EXTRACTION, DocumentOperationType.MEDICATION_EXTRACTION]:
                    if op_type in document.operation_status:
                        operation_snapshot = document.operation_status[op_type]
                        run_id = operation_snapshot.operation_instance_id
                        # Convert DocumentOperationStatus enum to string
                        document_status = operation_snapshot.status.value if operation_snapshot.status else "completed"
                        break
            
            if not run_id:
                run_id = "unknown"  # Fallback if no operation instance ID found
                LOGGER.warning("No run_id found in document operation status", extra=extra)
            
            extra.update({
                "run_id": run_id,
                "document_status": document_status
            })
            
            # Create the callback request payload
            callback_request = DocumentProcessingCompleteRequest(
                app_id=document.app_id,
                tenant_id=document.tenant_id,
                patient_id=document.patient_id,
                document_id=document.id,
                source_id=document.source_id,
                status=document_status,
                timestamp=datetime.now().isoformat(),
                run_id=run_id,
                metadata=document.metadata if hasattr(document, 'metadata') else None,
                data=entities
            )
            
            # Log the payload being sent
            payload_dict = callback_request.dict()
            LOGGER.info("Sending callback payload", extra={
                **extra,
                "payload_data_type": type(payload_dict.get('data')).__name__,
                "payload_data_length": len(payload_dict.get('data')) if payload_dict.get('data') else 0,
                "payload_data_is_none": payload_dict.get('data') is None,
                "payload_sample": payload_dict.get('data')[0] if payload_dict.get('data') and len(payload_dict.get('data')) > 0 else None
            })
            
            # Route the callback request based on cloudtask_enabled setting
            if integration_config.callback.cloudtask_enabled:
                success = await self._send_via_cloudtask(callback_url, callback_request.dict(), integration_config.callback, extra)
            else:
                success = await self._send_direct_request(callback_url, callback_request.dict(), integration_config.callback, extra)
            
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if success:
                LOGGER.info("Successfully invoked document processing complete callback", extra={
                    **extra,
                    "elapsed_time_ms": int(elapsed_time)
                })
                return True
            else:
                LOGGER.error("Failed to invoke document processing complete callback", extra={
                    **extra,
                    "elapsed_time_ms": int(elapsed_time)
                })
                return False
                
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"Error invoking document processing complete callback: {str(e)}"
            error_dict = exceptionToMap(e)
            
            LOGGER.error(error_msg, extra={
                **extra,
                "error": error_dict,
                "elapsed_time_ms": int(elapsed_time)
            })
            return False
    
    async def _send_direct_request(
        self,
        callback_url: str,
        payload: Dict[str, Any],
        callback_config,
        extra: Dict[str, Any]
    ) -> bool:
        """
        Send callback request directly to the host API.

        :param callback_url: URL to send the callback to
        :param payload: Data to send in request body
        :param callback_config: Callback configuration with headers
        :param extra: Extra logging context
        :return: True if request succeeded, False otherwise
        """
        request_extra = {
            **extra,
            "delivery_method": "direct",
            "payload_size": len(json.dumps(payload)) if payload else 0
        }

        try:
            # Get OAuth access token for Admin API authentication
            oauth_token = await self._get_oauth_token_with_logging(request_extra)

            # Prepare headers - merge default headers with configured headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Paperglass-CallbackInvoker/1.0"
            }

            # Add OAuth Authorization header if token was obtained
            if oauth_token:
                headers["Authorization"] = f"Bearer {oauth_token}"

            # Add configured headers (may override the above)
            if callback_config.headers:
                headers.update(callback_config.headers)

            # Prepare request data
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout

            # Enhanced pre-request logging with structured data
            LOGGER.info(f"Making direct POST request to {callback_url}", extra={
                **request_extra,
                "http_request": {
                    "method": "POST",
                    "url": callback_url,
                    "headers": {k: v for k, v in headers.items() if k.lower() not in ['authorization', 'api-key']},  # Hide sensitive headers
                    "timeout_seconds": 30,
                    "payload": {
                        "keys": list(payload.keys()) if payload else [],
                        "has_data": bool(payload.get('data')),
                        "data_count": len(payload.get('data', [])) if payload.get('data') else 0,
                        "size_bytes": len(json.dumps(payload)) if payload else 0
                    }
                }
            })
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url=callback_url,
                    json=payload,
                    headers=headers
                ) as response:

                    response_text = await response.text()

                    # Enhanced response logging with structured data
                    request_extra.update({
                        "http_response": {
                            "status_code": response.status,
                            "headers": {k: v for k, v in response.headers.items() if k.lower() not in ['set-cookie', 'authorization']},
                            "content_type": response.headers.get('Content-Type', 'unknown'),
                            "body": {
                                "length": len(response_text),
                                "preview": response_text[:500] if response_text else None
                            }
                        }
                    })

                    if response.status >= 200 and response.status < 300:
                        # Add success indicators to response data
                        request_extra["http_response"]["success_indicators"] = {
                            "status_success": True,
                            "body_contains_success": "success" in response_text.lower() if response_text else False
                        }
                        LOGGER.info(f"Direct callback request succeeded with status {response.status}", extra=request_extra)
                        return True
                    else:
                        # Enhanced failure logging with structured error analysis
                        error_analysis = {
                            "json_parseable": False,
                            "error_message": None,
                            "full_body": response_text[:2000] if response_text else None
                        }

                        # Try to parse JSON error response for additional context
                        if response_text:
                            try:
                                response_json = json.loads(response_text)
                                error_analysis["json_parseable"] = True
                                error_analysis["error_message"] = response_json.get('detail', response_json.get('message', str(response_json)))
                                error_analysis["parsed_json"] = response_json
                            except json.JSONDecodeError:
                                error_analysis["json_parse_error"] = True

                        request_extra["http_response"]["error_analysis"] = error_analysis
                        LOGGER.error(f"Direct callback request failed with status {response.status}", extra=request_extra)
                        return False
                        
        except asyncio.TimeoutError:
            LOGGER.error("Direct callback request timed out", extra=request_extra)
            return False
        except aiohttp.ClientError as e:
            request_extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"HTTP client error during direct callback request: {str(e)}", extra=request_extra)
            return False
        except Exception as e:
            request_extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Unexpected error during direct callback request: {str(e)}", extra=request_extra)
            return False
    
    async def _send_via_cloudtask(
        self,
        callback_url: str,
        payload: Dict[str, Any],
        callback_config,
        extra: Dict[str, Any]
    ) -> bool:
        """
        Send callback request via Google Cloud Task.
        
        :param callback_url: URL to send the callback to
        :param payload: Data to send in request body
        :param callback_config: Callback configuration with headers
        :param extra: Extra logging context
        :return: True if task was created successfully, False otherwise
        """
        request_extra = {
            **extra,
            "delivery_method": "cloudtask",
            "payload_size": len(json.dumps(payload)) if payload else 0
        }

        try:
            # Import locally to avoid circular dependencies
            from paperglass.infrastructure.adapters.google import GoogleCloudTaskClient

            # Get OAuth access token for Admin API authentication
            oauth_token = await self._get_oauth_token_with_logging(request_extra)

            # Prepare headers for the cloud task
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Paperglass-CallbackInvoker/1.0"
            }

            # Add OAuth Authorization header if token was obtained
            if oauth_token:
                headers["Authorization"] = f"Bearer {oauth_token}"

            # Add configured headers (may override the above)
            if callback_config.headers:
                headers.update(callback_config.headers)
            
            LOGGER.debug(f"Creating cloud task for callback to {callback_url}", extra=request_extra)
            
            # Create cloud task client and submit task
            cloud_task_client = GoogleCloudTaskClient()
            task_name = await cloud_task_client.create_http_task(
                url=callback_url,
                payload=payload,
                headers=headers,
                schedule_time=None  # Send immediately
            )
            
            request_extra.update({
                "task_name": task_name
            })
            
            LOGGER.info(f"Successfully created cloud task for callback", extra=request_extra)
            return True
            
        except Exception as e:
            request_extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error creating cloud task for callback: {str(e)}", extra=request_extra)
            return False
    
    async def _make_request(
        self, 
        callback_url: str, 
        payload: Dict[str, Any], 
        extra: Dict[str, Any]
    ) -> bool:
        """
        Make HTTP POST request to the callback endpoint.
        
        :param callback_url: URL to send the callback to
        :param payload: Data to send in request body
        :param extra: Extra logging context
        :return: True if request succeeded, False otherwise
        """
        request_extra = {
            **extra,
            "payload_size": len(json.dumps(payload)) if payload else 0
        }
        
        try:
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Paperglass-CallbackInvoker/1.0"
            }
            
            # Prepare request data
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            
            LOGGER.debug(f"Making POST request to {callback_url}", extra=request_extra)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url=callback_url,
                    json=payload,
                    headers=headers
                ) as response:
                    
                    response_text = await response.text()
                    
                    request_extra.update({
                        "response_status": response.status,
                        "response_headers": dict(response.headers),
                        "response_length": len(response_text)
                    })
                    
                    if response.status >= 200 and response.status < 300:
                        LOGGER.debug(f"Callback request succeeded with status {response.status}", extra=request_extra)
                        return True
                    else:
                        request_extra.update({
                            "response_text": response_text[:1000]  # Limit response text in logs
                        })
                        LOGGER.error(f"Callback request failed with status {response.status}", extra=request_extra)
                        return False
                        
        except asyncio.TimeoutError:
            LOGGER.error("Callback request timed out", extra=request_extra)
            return False
        except aiohttp.ClientError as e:
            request_extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"HTTP client error during callback request: {str(e)}", extra=request_extra)
            return False
        except Exception as e:
            request_extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Unexpected error during callback request: {str(e)}", extra=request_extra)
            return False
    
    def _apply_integration_override(self, base_integration, override_data):
        """
        Apply integration override from document metadata to base integration config.
        
        :param base_integration: Base IntegrationConfiguration from app config
        :param override_data: Override data from document metadata
        :return: Merged IntegrationConfiguration
        """
        from paperglass.domain.values import IntegrationConfiguration, IntegrationCallbackConfiguration
        
        # Start with base integration or create empty one
        if base_integration:
            # Convert to dict for easier manipulation
            merged_config = base_integration.dict()
        else:
            merged_config = {
                "base_url": "",
                "endpoints": {},
                "callback": None
            }
        
        # Apply overrides
        if "base_url" in override_data:
            merged_config["base_url"] = override_data["base_url"]
        
        if "endpoints" in override_data:
            if merged_config["endpoints"] is None:
                merged_config["endpoints"] = {}
            merged_config["endpoints"].update(override_data["endpoints"])
        
        if "callback" in override_data:
            callback_override = override_data["callback"]
            
            # Start with base callback or create empty one
            if merged_config.get("callback"):
                merged_callback = merged_config["callback"].copy()
            else:
                merged_callback = {
                    "enabled": False,
                    "endpoint": None,
                    "embed_entities_enabled": False,
                    "cloudtask_enabled": True,
                    "headers": {}
                }
            
            # Apply callback overrides
            for key, value in callback_override.items():
                merged_callback[key] = value
            
            merged_config["callback"] = merged_callback
        
        # Convert back to IntegrationConfiguration object
        try:
            if merged_config.get("callback"):
                merged_config["callback"] = IntegrationCallbackConfiguration(**merged_config["callback"])
            return IntegrationConfiguration(**merged_config)
        except Exception as e:
            LOGGER.warning(f"Failed to apply integration override, using base config: {str(e)}")
            return base_integration
