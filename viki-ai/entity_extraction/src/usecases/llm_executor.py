"""
LLM execution usecase.

This module contains the business logic for executing LLM prompts with documents
stored in Google Cloud Storage, handling document processing and response generation.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Tuple
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from adapters.llm import StandardPromptAdapter
from contracts.llm import LlmExecuteRequest, LlmExecuteResponse
import settings

LOGGER = getLogger(__name__)


def _uppercase_types_for_vertex_ai(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert JSON Schema types to uppercase format required by Vertex AI.
    Also removes JSON Schema meta-schema fields and custom extension fields
    that Vertex AI doesn't accept.

    Args:
        schema_dict: The JSON schema dictionary to transform

    Returns:
        Dict containing the transformed JSON schema with uppercased types
    """
    # Create a copy to avoid modifying the original
    result = schema_dict.copy()

    LOGGER.debug("Converting schema types to Vertex AI format", extra={"schema": result})

    # Remove JSON Schema meta-schema fields that Vertex AI doesn't accept
    meta_schema_fields = ["$schema", "$id", "$ref", "$defs", "$vocabulary"]
    for field in meta_schema_fields:
        if field in result:
            del result[field]

    # Remove custom extension fields (x-*) to avoid Pydantic validation errors
    # Google GenAI SDK uses Pydantic with extra='forbid' which rejects these fields
    result = _remove_extension_fields(result)

    # Uppercase the main schema type
    if "type" in result and isinstance(result["type"], str):
        result["type"] = result["type"].upper()

    # Uppercase types in properties
    if "properties" in result and isinstance(result["properties"], dict):
        result["properties"] = _uppercase_property_types(result["properties"])

    return result


def _uppercase_property_types(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively uppercase type values in properties.

    Args:
        properties: Dictionary of property definitions

    Returns:
        Dict with uppercased type values
    """
    result = {}

    for prop_name, prop_def in properties.items():
        if isinstance(prop_def, dict):
            prop_copy = prop_def.copy()

            # Uppercase the type if it exists and is a string
            if "type" in prop_copy and isinstance(prop_copy["type"], str):
                prop_copy["type"] = prop_copy["type"].upper()

            # Recursively handle nested properties (for object types)
            if "properties" in prop_copy and isinstance(prop_copy["properties"], dict):
                prop_copy["properties"] = _uppercase_property_types(prop_copy["properties"])

            # Handle array items (for array types)
            if "items" in prop_copy and isinstance(prop_copy["items"], dict):
                items_copy = prop_copy["items"].copy()
                if "type" in items_copy and isinstance(items_copy["type"], str):
                    items_copy["type"] = items_copy["type"].upper()

                # Recursively handle nested properties in array items
                if "properties" in items_copy and isinstance(items_copy["properties"], dict):
                    items_copy["properties"] = _uppercase_property_types(items_copy["properties"])

                prop_copy["items"] = items_copy

            result[prop_name] = prop_copy
        else:
            result[prop_name] = prop_def

    return result


def _remove_extension_fields(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively remove all JSON Schema extension fields (keys starting with 'x-').

    These custom extension fields (like x-schema-id, x-app-id, x-label) are used
    internally but cause validation errors when passed to external APIs like
    Google's GenAI SDK which uses Pydantic with extra='forbid'.

    Args:
        schema_dict: The JSON schema dictionary to clean

    Returns:
        Dict with all x-* extension fields removed
    """
    if not isinstance(schema_dict, dict):
        return schema_dict

    result = {}

    for key, value in schema_dict.items():
        # Skip any keys starting with 'x-'
        if key.startswith('x-'):
            LOGGER.debug(f"Removing extension field: {key}", extra={"field": key})
            continue

        # Recursively process nested dictionaries
        if isinstance(value, dict):
            result[key] = _remove_extension_fields(value)
        # Recursively process lists that might contain dictionaries
        elif isinstance(value, list):
            result[key] = [
                _remove_extension_fields(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result


class LlmExecutionService:
    """
    Service for executing LLM prompts with documents from Google Cloud Storage.
    
    This service handles the complete workflow of:
    1. Processing the GS URI and document
    2. Constructing the appropriate prompt with system instructions
    3. Executing the LLM with the document and prompt
    4. Parsing and structuring the response
    """
    
    def __init__(self):
        """Initialize the LLM execution service."""
        # We'll create the adapter dynamically based on request parameters
        LOGGER.info("LLM Execution Service initialized")
    
    async def execute_llm_request(self, request: LlmExecuteRequest) -> LlmExecuteResponse:
        """
        Execute an LLM request with a document from Google Cloud Storage.
        
        Args:
            request: The LLM execution request containing GS URI, prompt, and schema
            
        Returns:
            LlmExecuteResponse: The response containing generated content and metadata
            
        Raises:
            Exception: If LLM execution fails
        """
        start_time = datetime.utcnow()
        
        # Create LLM adapter with custom parameters if provided
        llm_adapter_kwargs = {}
        if request.model_parameters:
            if request.model_parameters.model_name:
                llm_adapter_kwargs["model_name"] = request.model_parameters.model_name
            if request.model_parameters.max_output_tokens:
                llm_adapter_kwargs["max_tokens"] = request.model_parameters.max_output_tokens
            if request.model_parameters.temperature:
                llm_adapter_kwargs["temperature"] = request.model_parameters.temperature
            if request.model_parameters.top_p:
                llm_adapter_kwargs["top_p"] = request.model_parameters.top_p
        
        llm_adapter = StandardPromptAdapter(**llm_adapter_kwargs)
        
        execution_metadata = {
            "start_time": start_time.isoformat(),
            "gs_uri": request.gs_uri,
            "has_system_instructions": request.system_instructions is not None,
            "has_json_schema": request.json_schema is not None,
            "prompt_length": len(request.prompt),
            "request_metadata": request.metadata,
            "model_parameters": request.model_parameters.model_dump() if request.model_parameters else None
        }
        
        LOGGER.info(f"Starting LLM execution for GS URI: {request.gs_uri}", extra=execution_metadata)
        
        try:
            # Prepare the content items for the LLM
            content_items = []
            
            # Add the document from GS URI
            # Determine MIME type based on file extension
            mime_type = self._determine_mime_type(request.gs_uri)
            content_items.append((request.gs_uri, mime_type))
            
            # Add the prompt text
            content_items.append(request.prompt)
            
            # Prepare system instructions
            system_prompts = []
            if request.system_instructions:
                system_prompts.append(request.system_instructions)
            
            # Prepare response configuration and convert schema for Vertex AI if provided
            response_mime_type = "application/json" if request.json_schema else None
            vertex_ai_schema = None
            if request.json_schema:
                vertex_ai_schema = _uppercase_types_for_vertex_ai(request.json_schema)
                LOGGER.debug("Converted schema for Vertex AI", extra={
                    **execution_metadata,
                    "original_schema": request.json_schema,
                    "vertex_ai_schema": vertex_ai_schema
                })
            
            # Execute the LLM
            LOGGER.debug(f"Executing LLM with {len(content_items)} content items", extra=execution_metadata)
            
            llm_response = await llm_adapter.generate_content_async(
                items=content_items,
                system_prompts=system_prompts,
                response_mime_type=response_mime_type,
                schema=vertex_ai_schema,
                metadata={
                    **request.metadata,
                    **execution_metadata
                }
            )
            
            # Process the response
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            execution_metadata.update({
                "end_time": end_time.isoformat(),
                "execution_time_ms": execution_time_ms,
                "response_length": len(llm_response.text) if llm_response.text else 0,
                "usage_metadata": llm_response.usage_metadata.model_dump() if llm_response.usage_metadata else None
            })
            
            # Parse JSON response if it appears to be JSON
            parsed_content = None
            if llm_response.text:
                try:
                    # Always attempt JSON parsing since we expect structured responses
                    parsed_content = llm_adapter.extract_json_from_response(llm_response.text)
                    execution_metadata["json_parsing_success"] = True
                    LOGGER.debug("Successfully parsed JSON response", extra=execution_metadata)
                except Exception as e:
                    LOGGER.warning(f"Failed to parse JSON response: {str(e)}", extra=execution_metadata)
                    execution_metadata["json_parsing_success"] = False
                    execution_metadata["json_parsing_error"] = str(e)
                    # If JSON parsing fails, leave parsed_content as None
            
            LOGGER.info(f"LLM execution completed successfully", extra=execution_metadata)
            
            return LlmExecuteResponse(
                success=True,
                content=parsed_content,
                raw_response=llm_response.text,
                execution_metadata=execution_metadata
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            error_info = exceptionToMap(e)
            execution_metadata.update({
                "end_time": end_time.isoformat(),
                "execution_time_ms": execution_time_ms,
                "error": error_info
            })
            
            LOGGER.error(f"LLM execution failed: {str(e)}", extra=execution_metadata)
            
            return LlmExecuteResponse(
                success=False,
                error_message=str(e),
                execution_metadata=execution_metadata
            )
    
    def _determine_mime_type(self, gs_uri: str) -> str:
        """
        Determine the MIME type based on the file extension in the GS URI.
        
        Args:
            gs_uri: The Google Cloud Storage URI
            
        Returns:
            str: The MIME type for the file
        """
        # Extract file extension
        file_path = gs_uri.lower()
        
        if file_path.endswith('.pdf'):
            return 'application/pdf'
        elif file_path.endswith(('.png', '.jpg', '.jpeg')):
            return 'image/jpeg' if file_path.endswith(('.jpg', '.jpeg')) else 'image/png'
        elif file_path.endswith('.txt'):
            return 'text/plain'
        elif file_path.endswith('.doc'):
            return 'application/msword'
        elif file_path.endswith('.docx'):
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            # Default to PDF if unknown
            LOGGER.warning(f"Unknown file extension for {gs_uri}, defaulting to application/pdf")
            return 'application/pdf'


async def execute_llm_request(request: LlmExecuteRequest) -> LlmExecuteResponse:
    """
    Execute an LLM request - convenience function for the service.
    
    Args:
        request: The LLM execution request
        
    Returns:
        LlmExecuteResponse: The response from the LLM execution
    """
    service = LlmExecutionService()
    return await service.execute_llm_request(request)