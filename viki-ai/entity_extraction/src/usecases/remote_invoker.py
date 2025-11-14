from datetime import datetime
from typing import Dict, Any, Optional
import json
import aiohttp
import asyncio

from models.general import TaskParameters, TaskResults
from util.custom_logger import getLogger
from util.exception import exceptionToMap

LOGGER = getLogger(__name__)


class RemoteInvoker:
    """Invoker for remote-type tasks that call external REST endpoints."""
    
    def __init__(self):
        """Initialize the RemoteInvoker."""
        LOGGER.info("RemoteInvoker initialized")
    
    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run a remote task by calling the configured REST endpoint.
        
        :param task_params: The parameters for the remote task to run.
        :return: The task results after calling the remote endpoint.
        """
        start_time = datetime.now()
        
        try:
            remote_config = task_params.task_config.remote
            if not remote_config:
                raise ValueError("Remote configuration is required for remote task type")
            
            url = remote_config.url
            method = remote_config.method.upper()
            headers = remote_config.headers or {}
            timeout = remote_config.timeout or 30
            
            LOGGER.info(f"Running remote task: {method} {url}")
            
            # Prepare the request payload
            payload = self._prepare_payload(task_params, remote_config)
            
            # Set default content type if not specified
            if 'Content-Type' not in headers and method in ['POST', 'PUT', 'PATCH']:
                headers['Content-Type'] = 'application/json'
            
            # Make the HTTP request
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                LOGGER.debug(f"Making {method} request to {url} with timeout {timeout}s")
                
                async with session.request(
                    method=method,
                    url=url,
                    json=payload if method in ['POST', 'PUT', 'PATCH'] else None,
                    params=payload if method == 'GET' else None,
                    headers=headers
                ) as response:
                    response_text = await response.text()
                    
                    # Log response details
                    LOGGER.debug(f"Remote endpoint responded with status {response.status}")
                    
                    # Check if the response was successful
                    if response.status >= 400:
                        error_msg = f"Remote endpoint returned error status {response.status}: {response_text}"
                        LOGGER.error(error_msg)
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=response_text
                        )
                    
                    # Parse response
                    response_data = self._parse_response(response_text, response.content_type)
                    
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000  # Convert to milliseconds
                    
                    LOGGER.info(f"Remote task completed successfully in {execution_time:.2f}ms")
                    
                    return TaskResults(
                        success=True,
                        results=response_data,
                        execution_time_ms=int(execution_time),
                        metadata={
                            "invoker_type": "remote",
                            "url": url,
                            "method": method,
                            "response_status": response.status,
                            "response_content_type": response.content_type,
                            "response_length": len(response_text),
                            "timeout": timeout,
                            "headers": headers,
                            "task_params": task_params.model_dump()
                        }
                    )
                    
        except asyncio.TimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"Remote endpoint request timed out after {timeout}s"
            LOGGER.error(error_msg)
            
            return TaskResults(
                success=False,
                error_message=error_msg,
                results={},
                execution_time_ms=int(execution_time),
                metadata={
                    "invoker_type": "remote",
                    "error_type": "timeout",
                    "timeout": timeout,
                    "url": url if 'url' in locals() else None
                }
            )
            
        except aiohttp.ClientError as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"HTTP client error calling remote endpoint: {str(e)}"
            LOGGER.error(error_msg, extra={"error": exceptionToMap(e)})
            
            return TaskResults(
                success=False,
                error_message=error_msg,
                results={},
                execution_time_ms=int(execution_time),
                metadata={
                    "invoker_type": "remote",
                    "error_type": "client_error",
                    "error": exceptionToMap(e),
                    "url": url if 'url' in locals() else None
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"Error running remote task: {str(e)}"
            error_dict = exceptionToMap(e)
            LOGGER.error(error_msg, extra={"error": error_dict})
            
            return TaskResults(
                success=False,
                error_message=error_msg,
                results={},
                execution_time_ms=int(execution_time),
                metadata={
                    "invoker_type": "remote",
                    "error": error_dict,
                    "url": url if 'url' in locals() else None
                }
            )
    
    def _prepare_payload(self, task_params: TaskParameters, remote_config) -> Dict[str, Any]:
        """
        Prepare the request payload for the remote endpoint.
        
        :param task_params: The task parameters
        :param remote_config: The remote configuration
        :return: Dictionary containing the request payload
        """
        try:
            # Start with the base task parameters
            payload = {
                "task_id": task_params.task_config.id,
                "app_id": task_params.app_id,
                "tenant_id": task_params.tenant_id,
                "patient_id": task_params.patient_id,
                "document_id": task_params.document_id,
                "page_number": task_params.page_number,
                "run_id": task_params.run_id,
                "pipeline_scope": task_params.pipeline_scope,
                "pipeline_key": task_params.pipeline_key,
                "subject": task_params.subject,
                "subject_uri": task_params.subject_uri,
                "context": task_params.context,
                "entities": task_params.entities,
                "params": task_params.params
            }
            
            # Add any additional context from remote config
            if remote_config.context:
                payload.update(remote_config.context)
            
            # Remove None values to keep payload clean
            payload = {k: v for k, v in payload.items() if v is not None}
            
            LOGGER.debug(f"Prepared payload with {len(payload)} fields")
            return payload
            
        except Exception as e:
            LOGGER.error(f"Error preparing payload: {str(e)}")
            # Return minimal payload on error
            return {
                "task_id": task_params.task_config.id,
                "error": "Failed to prepare full payload"
            }
    
    def _parse_response(self, response_text: str, content_type: Optional[str]) -> Any:
        """
        Parse the response from the remote endpoint.
        
        :param response_text: Raw response text
        :param content_type: Response content type
        :return: Parsed response data
        """
        try:
            # Try to parse as JSON if content type suggests it or if it looks like JSON
            if (content_type and 'json' in content_type.lower()) or \
               (response_text.strip().startswith(('{', '['))):
                return json.loads(response_text)
            
            # For non-JSON responses, return as text
            return {"response": response_text}
            
        except json.JSONDecodeError as e:
            LOGGER.warning(f"Failed to parse response as JSON: {str(e)}, returning as text")
            return {"response": response_text}
        except Exception as e:
            LOGGER.error(f"Error parsing response: {str(e)}")
            return {"response": response_text, "parse_error": str(e)}
