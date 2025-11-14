import asyncio
import json
from typing import Dict, Any, List, Union, Optional
import aiohttp
from datetime import datetime
from pydantic import BaseModel

from models.general import TaskParameters, TaskResults, EntityWrapper
from models.pipeline_config import PublishCallbackConfig
from util.custom_logger import getLogger
from util.exception import exceptionToMap


class EntityRequest(BaseModel):
    """Request model for entity endpoint."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    entity_schema_id: str
    run_id: Optional[str] = None
    data: List[Dict[str, Any]] = []

LOGGER = getLogger(__name__)


class PublishCallbackInvoker:
    """
    Invoker for publishing entities to callback endpoints based on PublishCallbackConfig.
    """
    
    def __init__(self):
        """Initialize the PublishCallbackInvoker."""
        LOGGER.info("PublishCallbackInvoker initialized")
    
    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run the publish callback task with the given parameters.
        
        :param task_params: The parameters for the publish callback task to run.
        :return: The task results after running the publish callback.
        """
        start_time = datetime.now()
        
        try:
            if not task_params.task_config.callback:
                return TaskResults(
                    success=False,
                    error_message="No callback configuration found in task config",
                    results={},
                    metadata={"invoker_type": "publish_callback"}
                )
            
            callback_config = task_params.task_config.callback
            
            if not callback_config.enabled:
                LOGGER.debug("Callback is disabled, skipping invocation")
                elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
                return TaskResults(
                    success=True,
                    results={"callback_invoked": False, "callback_disabled": True},
                    execution_time_ms=int(elapsed_time),
                    metadata={"invoker_type": "publish_callback", "callback_enabled": False}
                )
            
            extra = {
                "callback_url": callback_config.endpoint.url,
                "callback_method": callback_config.endpoint.method,
                "pipeline_scope": task_params.pipeline_scope,
                "pipeline_key": task_params.pipeline_key,
                "task_id": task_params.task_config.id,
                "run_id": task_params.run_id
            }
            
            LOGGER.info("Running publish callback task", extra=extra)
            
            # Find entities for the current pipeline scope and key
            entities = self._extract_entities(task_params)
            
            if not entities:
                LOGGER.info("No entities found to publish", extra=extra)
                elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
                return TaskResults(
                    success=True,
                    results={"callback_invoked": False, "no_entities": True},
                    execution_time_ms=int(elapsed_time),
                    metadata={
                        "invoker_type": "publish_callback",
                        "callback_url": callback_config.endpoint.url,
                        "callback_method": callback_config.endpoint.method,
                        "callback_enabled": callback_config.enabled
                    }
                )
            
            # Publish entities based on configuration
            success = await self._publish_entities(callback_config, entities, task_params, extra)
            
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if success:
                LOGGER.info("Successfully published entities to callback endpoint", extra={
                    **extra,
                    "entities_count": len(entities) if isinstance(entities, list) else 1
                })
                return TaskResults(
                    success=True,
                    results={"callback_invoked": True, "callback_success": True},
                    execution_time_ms=int(elapsed_time),
                    metadata={
                        "invoker_type": "publish_callback",
                        "callback_url": callback_config.endpoint.url,
                        "callback_method": callback_config.endpoint.method,
                        "callback_enabled": callback_config.enabled,
                        "entities_count": len(entities) if isinstance(entities, list) else 1
                    }
                )
            else:
                LOGGER.error("Failed to publish entities to callback endpoint", extra=extra)
                return TaskResults(
                    success=False,
                    error_message="Failed to publish entities to callback endpoint",
                    results={"callback_invoked": True, "callback_success": False},
                    execution_time_ms=int(elapsed_time),
                    metadata={
                        "invoker_type": "publish_callback",
                        "callback_url": callback_config.endpoint.url,
                        "callback_method": callback_config.endpoint.method,
                        "callback_enabled": callback_config.enabled,

                    }
                )
            
        except Exception as e:
            elapsed_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"Error running publish callback task: {str(e)}"
            error_dict = exceptionToMap(e)
            LOGGER.error(error_msg, extra={"error": error_dict})
            
            return TaskResults(
                success=False,
                error_message=error_msg,
                results={},
                execution_time_ms=int(elapsed_time),
                metadata={
                    "invoker_type": "publish_callback",
                    "error": error_dict
                }
            )
    
    def _extract_entities(self, task_params: TaskParameters) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Extract entities from task parameters by filtering through the scope and pipeline_id
        until an entry is found that has a schema_ref matching the callback config entity_schema_ref.
        
        :param task_params: Task parameters containing entities
        :return: Entities data or None if not found
        """
        if not task_params.entities:
            return None
        
        callback_config = task_params.task_config.callback
        if not callback_config or not callback_config.entity_schema_ref:
            return None
        
        target_schema_uri = callback_config.entity_schema_ref.schema_uri
        scope = callback_config.scope or task_params.pipeline_scope
        pipeline_id = callback_config.pipeline_id or task_params.pipeline_key
        
        # Navigate the hierarchical structure: [scope][pipeline_id]
        scope_entities = task_params.entities.get(scope)
        if not scope_entities:
            return None
        
        pipeline_entities = scope_entities.get(pipeline_id)
        if not pipeline_entities:
            return None
        
        # Iterate through all task entries in the pipeline to find matching schema_ref
        for task_id, task_entities in pipeline_entities.items():
            # Handle EntityWrapper objects
            if isinstance(task_entities, EntityWrapper):
                if hasattr(task_entities, 'schema_ref') and task_entities.schema_ref == target_schema_uri:
                    return task_entities.entities
            elif isinstance(task_entities, dict):
                # Handle serialized EntityWrapper or dict with schema_ref
                if task_entities.get('schema_ref') == target_schema_uri:
                    return task_entities.get('entities', task_entities)
                # Also check if it's a nested structure with entities
                elif 'entities' in task_entities and task_entities.get('schema_ref') == target_schema_uri:
                    return task_entities['entities']
        
        return None
    
    async def _publish_entities(
        self, 
        callback_config: PublishCallbackConfig, 
        entities: Union[Dict[str, Any], List[Dict[str, Any]]], 
        task_params: TaskParameters,
        extra: Dict[str, Any]
    ) -> bool:
        """
        Publish entities to the callback endpoint using EntityRequest format.
        
        :param callback_config: Callback configuration
        :param entities: Entities to publish
        :param task_params: Task parameters containing context information
        :param extra: Extra logging context
        :return: True if request succeeded, False otherwise
        """
        # Extract entity_schema_id from callback config or task config
        entity_schema_id = "unknown"
        if callback_config.entity_schema_ref:
            entity_schema_id = callback_config.entity_schema_ref.schema_uri
        elif task_params.task_config.entity_schema_ref:
            entity_schema_id = task_params.task_config.entity_schema_ref.schema_uri
        
        entity_request = EntityRequest(
            app_id=task_params.app_id,
            tenant_id=task_params.tenant_id,
            patient_id=task_params.patient_id,
            document_id=task_params.document_id,
            entity_schema_id=entity_schema_id,
            run_id=task_params.run_id,
            data=entities if isinstance(entities, list) else [entities]
        )
        
        return await self._make_request(callback_config.endpoint, entity_request.model_dump(), extra)
    
    async def _make_request(
        self, 
        endpoint, 
        payload: Union[Dict[str, Any], List[Dict[str, Any]]], 
        extra: Dict[str, Any]
    ) -> bool:
        """
        Make HTTP request to the callback endpoint.
        
        :param endpoint: PublishCallbackEndpoint configuration
        :param payload: Data to send in request body
        :param extra: Extra logging context
        :return: True if request succeeded, False otherwise
        """
        request_extra = {
            **extra,
            "payload_type": "list" if isinstance(payload, list) else "dict",
            "payload_size": len(payload) if isinstance(payload, (list, dict)) else 0
        }
        
        try:
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "EntityExtraction-CallbackInvoker/1.0"
            }
            if endpoint.headers:
                headers.update(endpoint.headers)
            
            # Prepare request data
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            
            LOGGER.debug(f"Making {endpoint.method} request to {endpoint.url}", extra=request_extra)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=endpoint.method,
                    url=endpoint.url,
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
