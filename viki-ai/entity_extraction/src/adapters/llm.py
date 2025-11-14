import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union, Tuple
from base64 import b64encode
from pydantic import BaseModel

import google.genai as genai
import google.genai.types as types
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold, Part

import settings

from util.custom_logger import getLogger
from util.exception import exceptionToMap
from util.json_utils import DateTimeEncoder
from util.tracing import trace_function, add_span_attributes, add_span_event

LOGGER = getLogger(__name__)

DEFAULT_SAFETY_SETTINGS = {
    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE"    
}
DEFAULT_RESPONSE_MIME_TYPE = "application/json"

class UsageMetadata(BaseModel):
    """Usage metadata from Vertex AI response."""
    prompt_token_count: Optional[int] = None
    candidates_token_count: Optional[int] = None
    total_token_count: Optional[int] = None
    cached_content_token_count: Optional[int] = None


class LLMResponse(BaseModel):
    """Response object containing both text and usage metadata from LLM."""
    text: str
    usage_metadata: Optional[UsageMetadata] = None


class PromptStats(BaseModel):
    """Statistics and metadata for prompt execution."""
    model_name: str
    max_output_tokens: int
    temperature: float
    top_p: float
    prompt_length: int
    prompt_tokens: int
    response_length: int
    response_tokens: int
    total_tokens: Optional[int] = None
    elapsed_time: float
    has_image: Optional[bool] = False
    has_binary_data: Optional[bool] = False
    input: Optional[List[Union[str, Tuple[str, str], Tuple[bytes, str]]]] = None
    output: Optional[str] = None
    error: Optional[dict] = None


class StandardPromptAdapter:
    """
    Adapter for Google AI using the google-genai library.
    Provides a standardized interface for prompt execution with Gemini models.
    """
    
    def __init__(
        self,        
        model_name: str = settings.LLM_MODEL_DEFAULT,
        max_tokens: int = settings.LLM_MAX_OUTPUT_TOKENS_DEFAULT,
        temperature: float = settings.LLM_TEMPERATURE_DEFAULT,
        top_p: float = settings.LLM_TOP_P_DEFAULT,
        safety_settings: dict = None,
        response_mime_type: str = DEFAULT_RESPONSE_MIME_TYPE,
        default_labels: dict = None
    ):
        """
        Initialize the StandardPromptAdapter.
        
        :param api_key: Google AI API key
        :param model_name: Name of the model to use (e.g., 'gemini-1.5-flash')
        :param max_tokens: Maximum number of output tokens
        :param temperature: Sampling temperature (0.0 to 1.0)
        :param top_p: Top-p sampling parameter (0.0 to 1.0)
        """
        
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.safety_settings_dict = safety_settings or {}
        self.response_mime_type = response_mime_type or DEFAULT_RESPONSE_MIME_TYPE
        self.default_labels = default_labels or {
            "owner": "balki",
            "business-unit": "viki",
            "environment": getattr(settings, 'STAGE', 'dev'),
            "application": "entity-extraction",
            "service": getattr(settings, 'SERVICE', 'entity-extraction')
        }
        
        # Configure the Google AI client
        http_options = types.HttpOptions(
            api_version=settings.LLM_API_VERSION,
            #async_client_args={'cookies': ..., 'ssl': ...},
        )

        self.client = genai.Client(
            vertexai=True,
            project=settings.GCP_PROJECT_ID,
            location=settings.GCP_LOCATION_3,
            http_options=http_options,
        )
        
        self.safety_settings_dict = DEFAULT_SAFETY_SETTINGS.copy()
        if safety_settings:            
            self.safety_settings_dict.update(safety_settings)
        else:
            safety_settings = DEFAULT_SAFETY_SETTINGS

        self.safety_settings = self._dict_to_safety_settings(self.safety_settings_dict)            

        
        LOGGER.info(f"Initialized StandardPromptAdapter with model: {model_name}")

    def _dict_to_safety_settings(self, safety_settings: dict) -> List[SafetySetting]:
        """
        Convert a dictionary of safety settings to a list of SafetySetting objects.
        
        :param safety_settings: Dictionary with safety settings
        :return: List of SafetySetting objects
        """
        settings_list = []
        for category, threshold in safety_settings.items():
            settings_list.append(
                SafetySetting(
                    category=category,
                    threshold=threshold
                )
            )
        return settings_list

    @staticmethod
    def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from response that might be wrapped in markdown code block.
        
        :param response_text: The response text from the model
        :return: Parsed JSON object or None if empty
        :raises ValueError: If JSON parsing fails
        """
        try:
            # If the response is wrapped in ```json ... ```
            if response_text.startswith('```'):
                # Remove ```json and ``` markers
                json_str = response_text.split('```')[1]
                if json_str.startswith('json'):
                    json_str = json_str[4:]
            else:
                json_str = response_text

            stripped_json_str = json_str.strip()

            if stripped_json_str == "":
                return None
            else:
                return json.loads(stripped_json_str)
                
        except Exception as e:
            extra = {
                "error": exceptionToMap(e),
                "response_text": response_text,
                "json_str": json_str if 'json_str' in locals() else None
            }
            LOGGER.error(f"Failed to parse JSON: {str(e)}\nResponse: {response_text}", extra=extra)
            raise ValueError(f"Failed to parse JSON: {str(e)}\nResponse: {response_text}")

    @trace_function(
        name="llm.generate_content",
        attributes={
            "operation.type": "llm_generation",
            "service.component": "entity_extraction"
        }
    )
    async def generate_content_async(
        self,
        items: List[Union[str, Tuple[str, str], Tuple[bytes, str]]],
        system_prompts: Optional[List[str]] = None,
        response_mime_type: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,        
        stream: bool = True,
        app_id: Optional[str] = "viki"
    ) -> LLMResponse:
        """
        Generate content using the Google AI model with async support.
        
        :param items: List of content items (text, file URIs, or binary data)
        :param system_prompts: Optional system instructions
        :param response_mime_type: Optional MIME type for structured responses
        :param metadata: Optional metadata for logging and tracking
        :param stream: Whether to use streaming response
        :return: LLMResponse object containing text and usage metadata
        """
        LOGGER.debug("LLM Metadata: %s", json.dumps(metadata or {}, indent=2, cls=DateTimeEncoder))

        business_unit = metadata.get("business_unit", "unknown") if metadata else "unknown"
        solution_id = metadata.get("solution_id", "unknown") if metadata else "unknown"
        domain_id = metadata.get("domain_id", "extract") if metadata else "extract"
        tenant_id = metadata.get("tenant_id", "none") if metadata else "none"
        
        # Add span attributes for tracing
        add_span_attributes({
            "llm.model_name": self.model_name,
            "llm.max_tokens": self.max_tokens,
            "llm.temperature": self.temperature,
            "llm.top_p": self.top_p,
            "llm.business_unit": business_unit,
            "llm.solution_id": solution_id,
            "llm.app_id": app_id,
            "llm.tenant_id": tenant_id,
            "llm.has_schema": schema is not None,
            "llm.response_mime_type": response_mime_type or self.response_mime_type
        })
                
        extra = {
            "business_unit": business_unit,
            "solution_id": solution_id,            
            "app_id": app_id,
            "tenant_id": tenant_id,
            "model": {
                "name": self.model_name,
                "settings": {
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "safety_settings": self.safety_settings_dict
                },
                "metadata": metadata
            },
            "schema": schema,
        }

        try:
            start_time = datetime.now()
            prompt_stats = None
            elapsed_time = None
            
            # Process input items
            contents = []
            prompt_text = None
            has_image = False
            has_binary_data = False
            
            for item in items:
                if isinstance(item, str):
                    LOGGER.debug("Adding text content", extra=extra)
                    contents.append(item)
                    prompt_text = item
                elif isinstance(item, tuple) and len(item) == 2:
                    if isinstance(item[0], str) and isinstance(item[1], str):
                        # File URI with MIME type
                        uri, mime_type = item
                        LOGGER.debug(f"Adding content from URI: {uri}, MIME type: {mime_type}", extra=extra)                        
                        contents.append(types.Part.from_uri(
                            file_uri=uri,
                            mime_type=mime_type
                        ))
                        has_image = True
                    elif isinstance(item[0], bytes) and isinstance(item[1], str):
                        # Binary data with MIME type
                        data, mime_type = item
                        LOGGER.debug(f"Adding binary content, MIME type: {mime_type}", extra=extra)
                        # Use the correct from_bytes method
                        contents.append(Part.from_bytes(
                            data=data,
                            mime_type=mime_type
                        ))
                        has_image = True
                        has_binary_data = True
                else:
                    LOGGER.warning(f"Unsupported item type: {type(item)}", extra=extra)
            
            # Add system prompts if provided
            system_instruction = None
            if system_prompts:
                system_instruction = "\n".join(system_prompts)

                extra.get("model", {}).get("settings", {}).update({
                    "system_instruction": system_instruction
                })

                LOGGER.debug(f"Using system instruction: {system_instruction[:100]}...", extra=extra)
                        
            LOGGER.debug(
                f"Generating content with model {self.model_name}, "
                f"max_tokens: {self.max_tokens}, temperature: {self.temperature}, top_p: {self.top_p}",
                extra=extra
            )
            LOGGER.debug(f"Prompt: {prompt_text[:500] if prompt_text else 'N/A'}...", extra=extra)

            # Construct configuration
            # Use the passed response_mime_type parameter if provided, otherwise use instance default
            effective_response_mime_type = response_mime_type if response_mime_type is not None else self.response_mime_type
            
            # Merge billing labels (custom labels override defaults)
            final_labels = self.default_labels.copy()            
            final_labels.update({
                "business-unit": business_unit,
                "solution-id": solution_id,
                "domain-id": domain_id,
                "app-id": app_id,
                "tenant-id": tenant_id
            })            
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                safety_settings=self.safety_settings,
                response_mime_type=effective_response_mime_type,
                labels=final_labels
            )

            if response_mime_type or schema:
                config.response_mime_type = response_mime_type

            if schema:
                LOGGER.debug(f"Using schema: {json.dumps(schema, indent=2, cls=DateTimeEncoder)}", extra=extra)
                config.response_schema = schema
            
            # Log billing labels for transparency
            LOGGER.debug(f"Using billing labels: {final_labels}", extra=extra)

            # Use non-streaming approach to avoid JSON parsing issues with chunks
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            result = response.text if hasattr(response, 'text') else str(response)
            
            # Extract usage metadata from the response
            usage_metadata = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage_metadata = UsageMetadata(
                    prompt_token_count=getattr(response.usage_metadata, 'prompt_token_count', None),
                    candidates_token_count=getattr(response.usage_metadata, 'candidates_token_count', None),
                    total_token_count=getattr(response.usage_metadata, 'total_token_count', None),
                    cached_content_token_count=getattr(response.usage_metadata, 'cached_content_token_count', None)
                )
                
                # Log the usage metadata for transparency
                LOGGER.info(f"Vertex AI usage metadata: {usage_metadata.model_dump()}", extra={
                    **extra,
                    "usage_metadata": usage_metadata.model_dump()
                })
            else:
                LOGGER.warning("No usage metadata available in Vertex AI response", extra=extra)
            
            LOGGER.debug(f"Generated content: {result[:500]}...", extra=extra)

            elapsed_time = datetime.now() - start_time

            # Create prompt statistics with actual token counts if available
            actual_prompt_tokens = usage_metadata.prompt_token_count if usage_metadata else len(prompt_text.split()) if prompt_text else 0
            actual_response_tokens = usage_metadata.candidates_token_count if usage_metadata else len(result.split()) if result else 0
            
            prompt_stats = PromptStats(
                model_name=self.model_name,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                prompt_length=len(prompt_text) if prompt_text else 0,
                prompt_tokens=actual_prompt_tokens,
                response_length=len(result) if result else 0,
                response_tokens=actual_response_tokens,
                total_tokens=usage_metadata.total_token_count if usage_metadata else None,
                elapsed_time=elapsed_time.total_seconds(),
                has_image=has_image,
                has_binary_data=has_binary_data,
            )
            
            extra_stats = {**prompt_stats.model_dump(), **(metadata or {})}
            extra_stats.update({"model": {"name": self.model_name}})
            if usage_metadata:
                extra_stats.update({"usage_metadata": usage_metadata.model_dump()})
            LOGGER.info("Prompt::generate_content_async", extra=extra_stats)

            if settings.LLM_PROMPT_AUDIT_ENABLED:
                await self._audit_prompt(items, result, prompt_stats=prompt_stats, metadata=metadata)

            # Return LLMResponse object with text and usage metadata
            return LLMResponse(
                text=result,
                usage_metadata=usage_metadata
            )

        except Exception as e:
            err = exceptionToMap(e)
            extra["error"] = err
            LOGGER.error(f"Error in generate_content_async: {e}, Type: {type(e).__name__}", extra=extra)
            
            if not prompt_stats:
                prompt_stats = PromptStats(
                    model_name=self.model_name,
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    prompt_length=len(prompt_text) if prompt_text else 0,
                    prompt_tokens=len(prompt_text.split()) if prompt_text else 0,
                    response_length=0,
                    response_tokens=0,
                    elapsed_time=elapsed_time.total_seconds() if elapsed_time else 0,
                    has_image=has_image,
                    has_binary_data=has_binary_data,
                )
            
            if settings.LLM_PROMPT_AUDIT_ENABLED:
                await self._audit_prompt(items, "", prompt_stats=prompt_stats, metadata=metadata, error=err)
            
            raise e

    async def _audit_prompt(
        self,
        input_items: List[Union[str, Tuple[str, str], Tuple[bytes, str]]],
        output: str,
        prompt_stats: PromptStats,
        metadata: Dict[str, Any] = None,
        error: Dict[str, Any] = None
    ):
        """
        Audit prompt execution for logging and tracking purposes.
        
        :param input_items: The input items sent to the model
        :param output: The output received from the model
        :param prompt_stats: Statistics about the prompt execution
        :param metadata: Additional metadata
        :param error: Error information if execution failed
        """
        try:
            metadata = metadata or {}
            
            step_id = metadata.get("step", "unknown")
            page_number = metadata.get("page_number", "unknown")
            iteration = metadata.get("iteration", "unknown")
            run_id = metadata.get("run_id", "unknown")

            prompt_stats.input = input_items
            prompt_stats.output = output
            if error:
                prompt_stats.error = error

            log_key = f"{step_id}::{str(page_number).zfill(2)}::{str(iteration).zfill(2)}"

            LOGGER.debug(f"Auditing prompt: {log_key}")
            LOGGER.info(
                f"PROMPT_AUDIT_LOG|PROMPT:{log_key}|"
                f"PROMPT_STATS:{prompt_stats.model_dump()}|"
                f"METADATA:{json.dumps(metadata, indent=2, cls=DateTimeEncoder)}"
            )

        except Exception as e:
            extra = {**(metadata or {}), "error": exceptionToMap(e)}
            LOGGER.error("Error in audit_prompt", extra=extra)

    def count_tokens(self, content: str) -> int:
        """
        Estimate token count for the given content.
        Note: This is a simple estimation. For accurate counts, use the model's token counting API.
        
        :param content: The content to count tokens for
        :return: Estimated token count
        """
        # Simple word-based estimation (actual implementation may vary)
        return len(content.split())
