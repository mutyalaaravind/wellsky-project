from base64 import b64encode
import json
from json.decoder import JSONDecodeError
import time
import asyncio
import datetime as datetime_base
from datetime import datetime, timedelta
from typing import List, Optional, Protocol, Tuple, Union, Dict, Any
from uuid import uuid4
from adapters.pub_sub import GooglePubSubAdapter
from pydantic import BaseModel

import settings
from settings import (
    AUDIT_LOGGER_API_URL,
    CLOUD_PROVIDER,
    AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME,
    AUDIT_LOGGER_TOPIC,
    GCP_LOCATION_2,
    GCP_PUBSUB_PROJECT_ID,
    SERVICE_ACCOUNT_EMAIL,
    STAGE,
    GCP_LOCATION_3, 
    GCP_PROJECT_ID,
    GCS_BUCKET_NAME,
    LOADTEST_LLM_EMULATOR_ENABLED,
    LLM_PROMPT_AUDIT_ENABLED,
    LLM_RESPONSE_INTERPRET_NOTJSON_ENABLED
)

from utils.json import DateTimeEncoder
from utils.exception import exceptionToMap
from utils.custom_logger import getLogger

from adapters.storage import StorageAdapter
from adapters.cloud_tasks import CloudTaskAdapter

LOGGER = getLogger(__name__)

DEFAULT_DOMAIN_ID = "extract-medication"



# import vertexai
# from vertexai.generative_models import Part
#from vertexai.preview import caching
# from vertexai.preview.generative_models import (GenerativeModel, HarmBlockThreshold, HarmCategory)
# from google.cloud import aiplatform


from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold, Part


DEFAULT_RESPONSE_MIME_TYPE = "application/json"


class PromptStats(BaseModel):
    model_name: str
    max_output_tokens: int
    temperature: float
    top_p: float
    prompt_length: int
    prompt_tokens: int
    billing_total_tokens: Optional[int] = None
    billing_total_billable_characters: Optional[int] = None
    burndown_rate: Optional[int] = None
    response_length: int
    response_tokens: int
    elapsed_time: float
    hasImage: Optional[bool] = False
    hasBinaryData: Optional[bool] = False
    input: Optional[List[Union[str, Tuple[str, str], Tuple[bytes, str]]]] = None
    output: Optional[str] = None
    error: Optional[dict] = None


class BurndownCalculator:

    MODEL_FAMILIES = {
        "gemini-1.5-flash": {
            "name": "Gemini 1.5 Flash",
            "burndown_factor": {
                "input": 1,
                "output": 4,
                "image": 1067
            }
        }
    }

    @classmethod
    def calculate_burndown(cls, model, input, output):
        input_size = 0
        image_count = 0
        for item in input:
            if isinstance(item, str):
                input_size += len(item)                
            elif isinstance(item, tuple) and len(item) == 2 and all(isinstance(element, str) for element in item):
                image_count += 1                
            else:
                image_count += 1
        
        burndown_rate = None
        if cls.is_in_model_family(model, "gemini-1.5-flash"):
            burndown_rate = cls.cypher_burndown("gemini-1.5-flash", input_size, image_count, len(output) if output else 0)

        else:
            LOGGER.warning(f"Model {model} not recognized for burndown calculation")

        return burndown_rate

    @classmethod
    def cypher_burndown(cls, family, input_size, image_count, output_size):
        if family not in cls.MODEL_FAMILIES:
            LOGGER.error(f"Family {family} not found in BurndownCalculator.MODEL_FAMILIES")
            return None
        
        burndown_factor = cls.MODEL_FAMILIES[family]["burndown_factor"]        

        burndown_rate = 0
        burndown_rate += input_size * burndown_factor["input"]
        burndown_rate += output_size * burndown_factor["output"]
        burndown_rate += image_count * burndown_factor["image"]

        return burndown_rate

    @classmethod
    def is_in_model_family(cls, model_name: str, family: str) -> bool:
        return model_name.lower().startswith(family)

class StandardPromptAdapter:
    
    def __init__(
        self,
        project_id=GCP_PROJECT_ID,
        location=GCP_LOCATION_3,
        max_tokens: int=8192,
        temperature: float=0.0,
        top_p: float=0.95,
        safety_settings: dict = None,
        response_mime_type: str = DEFAULT_RESPONSE_MIME_TYPE,
        default_labels: dict = None
    ):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.project_id = project_id
        self.location = location
        self.storage = StorageAdapter()
        self.cta = CloudTaskAdapter(project_id=project_id)
        self.pubsub_client = GooglePubSubAdapter(project_id=GCP_PUBSUB_PROJECT_ID)
        http_options = types.HttpOptions(
            api_version="v1",
        )
        self.genai_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            http_options=http_options
        )
        self.safety_settings_dict = safety_settings or {}
        self.response_mime_type = response_mime_type or DEFAULT_RESPONSE_MIME_TYPE
        self.default_labels = default_labels or {
            "owner": "balki",
            "environment": getattr(settings, 'STAGE', 'dev'),
            "application": "medication-extraction",
            "service": getattr(settings, 'SERVICE', 'medication-extraction')
        }
        
    @staticmethod
    def extract_json_from_response(response_text):
        """Extract JSON from response that might be wrapped in markdown code block"""
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
            if LLM_RESPONSE_INTERPRET_NOTJSON_ENABLED and isinstance(e, JSONDecodeError):
                extra = {
                    "error": str(e),
                    "response_text": response_text,
                    "json_str": json_str
                }
                LOGGER.warning(f"Failed to parse JSON: {str(e)}\n Response: {response_text}", extra=extra)
                # Return an empty list if JSON parsing fails
                return []
            else:
                extra = {
                    "error": exceptionToMap(e),
                    "response_text": response_text,
                    "json_str": json_str
                }
                LOGGER.error(f"Failed to parse JSON: {str(e)}\n Response: {response_text}", extra=extra)
                raise ValueError(f"Failed to parse JSON: {str(e)}\nResponse: {response_text}")

    
    async def multi_modal_predict_2(self,
                                 items: List[Union[str, Tuple[str, str], Tuple[bytes, str]]],
                                 model=None,
                                 system_prompts: Optional[List[str]] = [],
                                 response_mime_type: Optional[str] = None,
                                 schema: Optional[Dict[str, Any]] = None,
                                 metadata: Optional[dict] = None,
                                 thinking_budget: Optional[int] = 0,
    ):
        LOGGER.debug("LLM Metadata: %s", json.dumps(metadata, indent=2, cls=DateTimeEncoder))
        
        """
        `items` is a list of tuples, where each tuple is either a string, tuple of string (file uri) and string (mime type), or a tuple of bytes and a string of the mime type.

        e.g.:
        items = [
            "This is a string",
            ("gs://bucket/path/to/file", "application/pdf"),
            (b"this is a byte string", "application/pdf"),
            (b"this is a byte string", "image/jpeg"),
        ]
        
        `schema` is an optional JSON schema dictionary that constrains the LLM response structure.
        When provided, the schema should already be in Vertex AI format (UPPERCASE types).
        """

        safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
            )
        ]
        
        effective_response_mime_type = response_mime_type if response_mime_type is not None else self.response_mime_type
        business_unit = metadata.get("business_unit", "unknown") if metadata else "unknown"
        solution_id = metadata.get("solution_id", "unknown") if metadata else "unknown"
        domain_id = metadata.get("domain_id", DEFAULT_DOMAIN_ID) if metadata else DEFAULT_DOMAIN_ID
        tenant_id = metadata.get("tenant_id", "none") if metadata else "none"
        app_id = metadata.get("app_id", "none") if metadata else "none"

        # Merge billing labels (custom labels override defaults)
        final_labels = self.default_labels.copy()
        final_labels.update({
            "business-unit": business_unit,
            "solution-id": solution_id,
            "domain-id": domain_id,
            "app-id": app_id,
            "tenant-id": tenant_id
        })

        extra = {
            "model": {
                "name": model,
                "settings": {
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "safety_settings": [{"category": s.category, "threshold": s.threshold} for s in safety_settings],
                    "thinking_budget": thinking_budget
                },
                "metadata": metadata
            },
            "schema": schema,
            "has_schema": schema is not None
        }

        # Add system prompts if provided
        system_instruction = None
        if system_prompts:
            system_instruction = "\n".join(system_prompts)
            extra.get("model", {}).get("settings", {}).update({
                "system_instruction": system_instruction
            })
            LOGGER.debug(f"Using system instruction: {system_instruction[:100]}...", extra=extra)

        # Log billing labels for transparency
        LOGGER.debug(f"Using billing labels: {final_labels}", extra=extra)

        generate_content_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self.temperature,
            top_p=self.top_p,
            max_output_tokens=self.max_tokens,
            safety_settings=safety_settings,
            thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget),
            response_mime_type=effective_response_mime_type,
            labels=final_labels
        )
        
        # Add schema if provided
        if schema:
            LOGGER.debug(f"Using schema: {json.dumps(schema, indent=2, cls=DateTimeEncoder)}", extra=extra)
            generate_content_config.response_schema = schema

        try:
            start_time = datetime.now(datetime_base.timezone.utc)
            prompt_stats = None
            burndown_rate = None
            elapsed_time = None
            generation_config = {
                "max_output_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
            
            if response_mime_type is not None:
                generation_config["response_mime_type"] = response_mime_type
            
            parts = []
            prompt_text = None
            uri = None
            hasImage = False
            hasBinaryData = False
            for item in items:
                if isinstance(item, str):
                    LOGGER.debug("Adding contents from text", extra=extra)
                    parts.append(Part.from_text(text=item))
                    prompt_text = item
                elif isinstance(item, tuple) and len(item) == 2 and all(isinstance(element, str) for element in item):
                    uri = item[0]
                    LOGGER.debug("Adding contents from uri: %s, mime_type: 'application/pdf'", uri, extra=extra)
                    pdf_part = Part.from_uri(file_uri=uri, mime_type="application/pdf")
                    parts.append(pdf_part)
                    hasImage = True
                else:
                    LOGGER.debug("Adding contents from data", extra=extra)
                    parts.append(Part.from_data(data=item[0], mime_type=item[1]))
                    hasImage = True
                    hasBinaryData = True
            
            LOGGER.debug("Performing multi_modal_predict2 with model %s, max_output_tokens: %s, temperature: %s, top_p: %s", model, self.max_tokens, self.temperature, self.top_p, extra=extra)
            LOGGER.debug("Prompt: %s", prompt_text, extra=extra)
            
            billable_tokens_obj = await self.genai_client.aio.models.count_tokens(
                model=model,
                contents=parts
            )
            billable_tokens = {
                "total_tokens": billable_tokens_obj.total_tokens,
                "total_billable_characters": None
            }

            if STAGE == "prod" or not LOADTEST_LLM_EMULATOR_ENABLED:
                result = await self.genai_client.aio.models.generate_content(
                    model = model,
                    contents = [types.Content(role="user", parts=parts)],
                    config = generate_content_config
                )
            else:
                from adapters.llm_dummyload import DummyPromptAdapter
                LOGGER.warning("Using DummyPromptAdapter for load testing")
                dummy = DummyPromptAdapter()
                result = await dummy.multi_modal_predict_2(items, model, system_prompts, response_mime_type, metadata)

            LOGGER.debug("Result: %s", result.text, extra=extra)

            elapsed_time = datetime.now(datetime_base.timezone.utc) - start_time

            
            try:
                burndown_rate = BurndownCalculator.calculate_burndown(model, items, result.text)
            except Exception as e:
                extra2 = {**extra, "error": exceptionToMap(e)}
                LOGGER.warning("(Ignorning) Error calculating burndown rate: %s", str(e), extra=extra2)

            prompt_stats = PromptStats(
                model_name=model,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                prompt_length=len(prompt_text) if prompt_text else 0,
                prompt_tokens=len(prompt_text.split()) if prompt_text else 0,
                billing_total_tokens=billable_tokens["total_tokens"],
                billing_total_billable_characters=billable_tokens["total_billable_characters"],
                burndown_rate=burndown_rate,
                response_length=len(result.text) if result.text else 0,
                response_tokens=len(result.text.split()) if result.text else 0,
                elapsed_time=elapsed_time.total_seconds(),
                hasImage=hasImage,
                hasBinaryData=hasBinaryData,
            )
            extra = {**prompt_stats.dict(), **metadata} if metadata else prompt_stats.dict()
            extra.update({"model": {"name": model}}) # This corrects for the modelname being expected to be nested for metrics
            LOGGER.info("Prompt::multi_modal_predict2", extra=extra)            

            if LLM_PROMPT_AUDIT_ENABLED:
                await self.audit_prompt(items, result.text, prompt_stats=prompt_stats, metadata=metadata)

            return result.text

        except Exception as e:
            err = exceptionToMap(e)
            extra["error"] = err
            LOGGER.error(f"Error in multi_modal_predict_2: {e}, Type: {type(e).__name__}", extra=extra) 
            
            if not prompt_stats:
                prompt_stats = PromptStats(
                    model_name=model,
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    prompt_length=len(prompt_text) if prompt_text else 0,
                    prompt_tokens=len(prompt_text.split()) if prompt_text else 0,
                    billing_total_tokens=billable_tokens["total_tokens"],
                    billing_total_billable_characters=billable_tokens["total_billable_characters"],
                    burndown_rate=burndown_rate,
                    response_length=len(result) if result else 0,
                    response_tokens=len(result.split()) if result else 0,
                    elapsed_time=elapsed_time.total_seconds() if elapsed_time else 0,
                    hasImage=hasImage,
                    hasBinaryData=hasBinaryData,
                )  
            await self.audit_prompt(items, result, prompt_stats=prompt_stats, metadata=metadata, error=err)
            raise e
    
    def create_key(self, step_id: str, page_number:int, iteration:int):
        formatted_page_number = str(page_number).zfill(2)
        formatted_iteration = str(iteration).zfill(2)
        return f"{step_id}::{formatted_page_number}::{formatted_iteration}"


    async def _mktoken2(self, app_id, tenant_id, patient_id):
        return b64encode(json.dumps({'appId': app_id, 'tenantId': tenant_id, 'patientId': patient_id}).encode()).decode()
    
    async def audit_prompt(self, input, output, prompt_stats:PromptStats, metadata:dict={}, error:dict=None):
        """
        Non-blocking function that creates a background task for audit logging
        """
        try:
            step_id = metadata.get("step", "unknown")
            page_number = metadata.get("page_number", "unknown")
            iteration = metadata.get("iteration", "unknown")
            run_id = metadata.get("run_id", "unknown")

            app_id = metadata.get("app_id", "unknown")
            tenant_id = metadata.get("tenant_id", "unknown")
            patient_id = metadata.get("patient_id", "unknown")
            document_id = metadata.get("document_id", "unknown")
            base_path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}"

            prompt_stats.input = input
            prompt_stats.output = output
            if error:
                prompt_stats.error = error

            log_key = self.create_key(step_id, page_number, iteration)

            LOGGER.debug("Persisting audit_prompt: %s: %s", log_key, str(prompt_stats.dict().update(metadata)))
            # Below stattement is used in audit log reporting. so dont change anything in this statement
            LOGGER.info(f"PROMPT_AUDIT_LOG|PROMPT:{log_key}|PROMPT_STATS:{prompt_stats.dict()}|METADATA:{json.dumps(metadata, indent=2, cls=DateTimeEncoder)}")
            contents = json.dumps(prompt_stats.dict(), indent=2, cls=DateTimeEncoder)

            # try:
            #     # Use async with to properly handle the storage operation
            #     await self.storage.write_text(
            #         GCS_BUCKET_NAME,
            #         f"{base_path}/logs/{run_id}/prompt/{log_key}.json",
            #         contents,
            #         content_type="application/json"
            #     )

            #     # Prepare payload for cloud task, need to make metadata values dynamic
            #     task_payload = {
            #         "gcs_uri": f"gs://{GCS_BUCKET_NAME}/{base_path}/logs/{run_id}/prompt/{log_key}.json",
            #         "app_id": app_id,
            #         "tenant_id": tenant_id,
            #         "patient_id": patient_id,
            #         "document_id": document_id,
            #         "run_id": run_id,
            #         "step_id": step_id,
            #         "page_number": int(page_number),
            #         "iteration": int(iteration)
            #     }
                
            #     if CLOUD_PROVIDER == "local":
            #         await self.pubsub_client.publish(AUDIT_LOGGER_TOPIC, task_payload)
            #         LOGGER.debug("Created pubsub message for audit_prompt: %s", log_key)
            #     else:
            #         # Create cloud task
            #         await self.cta.create_task(
            #             token=await self._mktoken2(app_id, tenant_id, patient_id),
            #             location=GCP_LOCATION_2,
            #             service_account_email=SERVICE_ACCOUNT_EMAIL,
            #             queue=AUDIT_LOGGER_CLOUD_TASK_QUEUE_NAME,
            #             url=f"{AUDIT_LOGGER_API_URL}/process-task",
            #             payload=task_payload
            #         )
                    
            #         LOGGER.debug("Created cloud task for audit_prompt: %s", log_key)
            # except Exception as err:
            #     extra = {"error": exceptionToMap(err)}
            #     LOGGER.error("Error writing to storage in audit_prompt background task", extra=extra)
        except Exception as e:
            extra = {**metadata, "error": exceptionToMap(e)}
            LOGGER.error("Error in audit_prompt background task", extra=extra)
