from datetime import datetime
from typing import List, Union, Tuple, Optional, Dict, Any
import json

from models.general import TaskParameters, TaskResults
from models.metric import Metric
from adapters.llm import StandardPromptAdapter, LLMResponse, UsageMetadata
from util.custom_logger import getLogger
from util.exception import exceptionToMap

LOGGER = getLogger(__name__)


class PromptInvoker:
    """Invoker for prompt-type tasks using Google AI."""
    
    def __init__(self):
        """Initialize the PromptInvoker."""
        LOGGER.info("PromptInvoker initialized")

    def _validate_llm_response_format(self, response_object: Any) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Validate LLM response format - must be either Dict[str, Any] or List[Dict[str, Any]].
        No fallbacks - strict validation with clear error messages.

        Args:
            response_object: Raw parsed JSON response from LLM

        Returns:
            Validated dict or list of dicts

        Raises:
            ValueError: If response format is invalid with specific error details
        """
        if isinstance(response_object, dict):
            # Single dictionary - this is valid
            return response_object

        elif isinstance(response_object, list):
            if not response_object:
                # Empty list is valid
                return response_object

            # Validate that ALL items in the list are dictionaries
            for i, item in enumerate(response_object):
                if not isinstance(item, dict):
                    raise ValueError(
                        f"List item at index {i} must be a dictionary. "
                        f"Got {type(item).__name__}: {repr(item)[:100]}{'...' if len(repr(item)) > 100 else ''}"
                    )

            # All items are dictionaries - this is valid
            return response_object

        else:
            # Anything else is invalid - no fallbacks
            raise ValueError(
                f"LLM response must be either a dictionary or a list of dictionaries. "
                f"Got {type(response_object).__name__}: {repr(response_object)[:100]}{'...' if len(repr(response_object)) > 100 else ''}"
            )
    
    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run a prompt task with the given parameters.
        
        :param task_params: The parameters for the prompt task to run.
        :return: The task results after running the prompt.
        """
        start_time = datetime.now()
        
        try:
            prompt_config = task_params.task_config.prompt
            model_name = prompt_config.model
            
            LOGGER.info(f"Running prompt task with model: {model_name}")
            
            # Prepare metadata for tracking and auditing
            metadata = task_params.model_dump()
            
            # Add subject_uri to extra logging for debugging
            extra = {
                "subject_uri": task_params.subject_uri,
                "is_add_document_uri_to_context": getattr(prompt_config, 'is_add_document_uri_to_context', False),
                "task_id": task_params.task_config.id,
                "pipeline_scope": task_params.pipeline_scope,
                "pipeline_key": task_params.pipeline_key,
                "document_id": task_params.document_id
            }
            
            LOGGER.debug(f"Running prompt task with subject_uri: {task_params.subject_uri}", extra=extra)
                        
            # Prepare the prompt content
            prompt_items = []
            
            # Add the main prompt text with template formatting
            if hasattr(prompt_config, 'prompt') and prompt_config.prompt:
                formatted_prompt = self._format_prompt_template(prompt_config.prompt, metadata)
                prompt_items.append(formatted_prompt)
            else:
                # Fallback to a basic prompt
                prompt_items.append("Please analyze the provided content and extract relevant entities.")
            
            # Add any file references or binary data from context
            if task_params.context:
                file_items = self._extract_file_items_from_context(task_params)
                prompt_items.extend(file_items)
                LOGGER.info(f"Added {len(file_items)} file items to prompt", extra={**extra, "file_items_count": len(file_items)})
            
            # Prepare system prompts
            system_prompts = []
            if hasattr(prompt_config, 'system_instructions') and prompt_config.system_instructions:
                # Format system instructions with context as well
                formatted_instructions = [
                    self._format_prompt_template(instruction, metadata) 
                    for instruction in prompt_config.system_instructions
                ]
                system_prompts.extend(formatted_instructions)
            
            # Set response format if specified
            # response_mime_type = None
            # if hasattr(prompt_config, 'response_format'):
            #     if prompt_config.response_format == 'json':
            #         response_mime_type = "application/json"
            #     elif hasattr(prompt_config, 'response_mime_type'):
            #         response_mime_type = prompt_config.response_mime_type

            # Hard setting this to application/json for now            
            response_mime_type = "application/json"
            
            # Create adapter instance with model-specific settings from prompt config
            adapter = StandardPromptAdapter(
                model_name=model_name,
                max_tokens=getattr(prompt_config, 'max_output_tokens', 8192),
                temperature=getattr(prompt_config, 'temperature', 0.0),
                top_p=getattr(prompt_config, 'top_p', 0.95),
                response_mime_type=response_mime_type
            )
            
            # Get schema from entity_schema_ref if provided
            schema = None
            if task_params.task_config.entity_schema_ref:
                from adapters.schema_client import SchemaClient
                schema_client = SchemaClient()
                schema = await schema_client.get_entity_schema(task_params.task_config.entity_schema_ref.schema_uri)
                if schema:
                    LOGGER.info(f"Retrieved entity schema from {task_params.task_config.entity_schema_ref.schema_uri}")
                else:
                    LOGGER.warning(f"Failed to retrieve entity schema from {task_params.task_config.entity_schema_ref.schema_uri}")
            
            # Send LLM request start metric
            llm_start_metadata = {
                "model": model_name,
                "task_id": task_params.task_config.id,
                "pipeline_scope": task_params.pipeline_scope,
                "pipeline_key": task_params.pipeline_key,
                "run_id": task_params.run_id,
                "app_id": task_params.app_id,
                "tenant_id": task_params.tenant_id,
                "patient_id": task_params.patient_id,
                "document_id": task_params.document_id,
                "page_number": task_params.page_number,
                "prompt_items_count": len(prompt_items),
                "system_prompts_count": len(system_prompts),
                "response_mime_type": response_mime_type,
                "max_tokens": getattr(prompt_config, 'max_output_tokens', 8192),
                "temperature": getattr(prompt_config, 'temperature', 0.0),
                "event": "llm_request_start"
            }
            
            Metric.send(Metric.MetricType.LLM_REQUEST_START, llm_start_metadata)
            
            # Execute the prompt
            LOGGER.debug(f"Executing prompt with {len(prompt_items)} items")
            llm_response = await adapter.generate_content_async(
                items=prompt_items,
                system_prompts=system_prompts if system_prompts else None,
                response_mime_type=response_mime_type,
                schema=schema,
                metadata=metadata,
                stream=True,
                app_id=task_params.app_id
            )
            
            # Process the response text
            processed_response = self._process_response(llm_response.text, prompt_config)

            response_object = json.loads(processed_response)

            # Validate response format - strict validation with no fallbacks
            validated_results = self._validate_llm_response_format(response_object)

            elapsed_time = (datetime.now() - start_time).total_seconds()
            execution_time = elapsed_time * 1000  # Convert to milliseconds
            
            LOGGER.info(f"Prompt task with model {model_name} completed in {execution_time:.2f}ms")
            
            # Send LLM request complete metric with token usage
            llm_complete_metadata = {
                "model": model_name,
                "task_id": task_params.task_config.id,
                "pipeline_scope": task_params.pipeline_scope,
                "pipeline_key": task_params.pipeline_key,
                "run_id": task_params.run_id,
                "app_id": task_params.app_id,
                "tenant_id": task_params.tenant_id,
                "patient_id": task_params.patient_id,
                "document_id": task_params.document_id,
                "page_number": task_params.page_number,
                "elapsed_time": elapsed_time,
                "response_length": len(llm_response.text) if llm_response.text else 0,
                "event": "llm_request_complete"
            }
            
            # Add token usage metadata if available
            if llm_response.usage_metadata:
                llm_complete_metadata["token_usage"] = llm_response.usage_metadata.model_dump()
            
            Metric.send(Metric.MetricType.LLM_REQUEST_COMPLETE, llm_complete_metadata)
            
            # Add response format analysis with structured logging
            response_format_info = {
                "response_format": "dict" if isinstance(validated_results, dict) else "list_of_dicts",
                "entity_count": 1 if isinstance(validated_results, dict) else len(validated_results)
            }

            if isinstance(validated_results, list) and validated_results:
                first_entity = validated_results[0]
                response_format_info["first_entity_keys"] = list(first_entity.keys())
                response_format_info["first_entity_key_count"] = len(first_entity.keys())
            elif isinstance(validated_results, dict):
                response_format_info["entity_keys"] = list(validated_results.keys())
                response_format_info["entity_key_count"] = len(validated_results.keys())

            # Structured metadata for comprehensive logging
            llm_response_data = {
                "response_length": len(llm_response.text) if llm_response.text else 0,
                "processed_response_length": len(processed_response),
                "raw_response": llm_response.text,
                "processed_response": processed_response
            }

            validation_data = {
                "validation_successful": True,
                "original_type": type(response_object).__name__,
                "validated_type": "dict" if isinstance(validated_results, dict) else "list",
                "validation_errors": None
            }

            result_metadata = {
                "invoker_type": "prompt",
                "model": model_name,
                "prompt_config": {
                    "prompt_items_count": len(prompt_items),
                    "system_prompts_count": len(system_prompts),
                    "response_mime_type": response_mime_type,
                    "max_tokens": getattr(prompt_config, 'max_output_tokens', 8192),
                    "temperature": getattr(prompt_config, 'temperature', 0.0)
                },
                "llm_response": llm_response_data,
                "validation": validation_data,
                "response_format": response_format_info,
                "task_params": task_params.model_dump(),
                "elapsed_time": elapsed_time
            }
            
            # Add usage metadata if available
            if llm_response.usage_metadata:
                result_metadata["usage"] = llm_response.usage_metadata.model_dump()

            if schema:
                result_metadata["entity_schema"] = schema

            LOGGER.info(f"LLM response validated successfully: {response_format_info['response_format']} with {response_format_info['entity_count']} entities")

            return TaskResults(
                success=True,
                results=validated_results,
                execution_time_ms=int(execution_time),
                metadata=result_metadata
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            elapsed_time = execution_time / 1000  # Convert back to seconds for consistency
            error_msg = f"Error running prompt task: {str(e)}"
            error_dict = exceptionToMap(e)
            # Structured error logging
            error_context = {
                "error": error_dict,
                "task_context": {
                    "task_id": task_params.task_config.id,
                    "subject_uri": task_params.subject_uri,
                    "pipeline_scope": task_params.pipeline_scope,
                    "pipeline_key": task_params.pipeline_key,
                    "document_id": task_params.document_id
                },
                "execution_context": {
                    "elapsed_time": elapsed_time,
                    "model": getattr(task_params.task_config.prompt, 'model', 'unknown')
                }
            }

            # Add validation context if we got that far
            if 'response_object' in locals():
                error_context["validation_context"] = {
                    "response_object_type": type(response_object).__name__,
                    "response_object_preview": str(response_object)[:200] + "..." if len(str(response_object)) > 200 else str(response_object)
                }

            LOGGER.error(error_msg, extra=error_context)
            
            # Send LLM request error metric with token usage if available
            model_name = getattr(task_params.task_config.prompt, 'model', 'unknown')
            llm_error_metadata = {
                "model": model_name,
                "task_id": task_params.task_config.id,
                "pipeline_scope": task_params.pipeline_scope,
                "pipeline_key": task_params.pipeline_key,
                "run_id": task_params.run_id,
                "app_id": task_params.app_id,
                "tenant_id": task_params.tenant_id,
                "patient_id": task_params.patient_id,
                "document_id": task_params.document_id,
                "page_number": task_params.page_number,
                "elapsed_time": elapsed_time,
                "error_message": error_msg,
                "error": error_dict,
                "event": "llm_request_error"
            }
            
            # Try to include token usage if the error occurred after LLM response
            if 'llm_response' in locals() and hasattr(llm_response, 'usage_metadata') and llm_response.usage_metadata:
                llm_error_metadata["token_usage"] = llm_response.usage_metadata.model_dump()
            
            Metric.send(Metric.MetricType.LLM_REQUEST_ERROR, llm_error_metadata)
            
            return TaskResults(
                success=False,
                error_message=error_msg,
                results={},
                execution_time_ms=int(execution_time),
                metadata={
                    "invoker_type": "prompt",
                    "error": exceptionToMap(e),
                    "model": model_name
                }
            )
    
    def _format_prompt_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Format a prompt template with context variables.
        
        :param template: The prompt template string
        :param context: Context variables for template formatting
        :return: Formatted prompt string
        """
        try:
            # Simple string formatting - can be enhanced with more sophisticated templating
            return template.format(**context)
        except KeyError as e:
            LOGGER.warning(f"Missing context variable for template: {e}")
            return template
        except Exception as e:
            LOGGER.error(f"Error formatting prompt template: {e}")
            return template
    
    def _extract_file_items_from_context(self, task_params: TaskParameters) -> List[Union[Tuple[str, str], Tuple[bytes, str]]]:
        """
        Extract file items (URIs or binary data) from the task context.
        
        :param task_params: The task parameters containing context and configuration
        :return: List of file items for the prompt
        """
        file_items = []
        
        extra = {
            "subject_uri": task_params.subject_uri,
            "is_add_document_uri_to_context": task_params.task_config.prompt.is_add_document_uri_to_context,
            "task_id": task_params.task_config.id,
            "document_id": task_params.document_id
        }
        
        LOGGER.info(f"Extracting file items from context", extra=extra)

        if task_params.task_config.prompt.is_add_document_uri_to_context:
            file_uri = task_params.subject_uri
            if file_uri:
                file_items.append((file_uri, 'application/pdf'))
                LOGGER.info(f"Added document URI to prompt: {file_uri}", extra={**extra, "file_uri": file_uri, "mime_type": "application/pdf"})
            else:
                LOGGER.warning("is_add_document_uri_to_context is True but subject_uri is None/empty", extra=extra)
        else:
            LOGGER.debug("is_add_document_uri_to_context is False, not adding document URI", extra=extra)
        
        LOGGER.info(f"Extracted {len(file_items)} file items from context", extra={**extra, "file_items_count": len(file_items)})
        return file_items
    
    def _process_response(self, response: str, prompt_config) -> Any:
        """
        Process the raw response based on the prompt configuration.
        
        :param response: Raw response from the model
        :param prompt_config: Prompt configuration
        :return: Processed response
        """
        try:
            # If expecting JSON response, try to parse it
            if hasattr(prompt_config, 'response_format') and prompt_config.response_format == 'json':
                return StandardPromptAdapter.extract_json_from_response(response)
            
            # Otherwise return the raw response
            return response
            
        except Exception as e:
            LOGGER.warning(f"Error processing response: {e}, returning raw response")
            return response
