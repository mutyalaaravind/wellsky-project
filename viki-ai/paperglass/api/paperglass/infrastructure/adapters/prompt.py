from copy import deepcopy
import uuid
import vertexai
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, Part, FinishReason, HarmCategory, HarmBlockThreshold
from google.cloud import aiplatform
from typing import List, Optional, Tuple, Union


from paperglass.domain.values import (
    PromptAuditLog,
    PromptStats,
)

from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.domain.time import now_utc
from paperglass.infrastructure.ports import IPromptAdapter

import json, datetime, os

from paperglass.log import CustomLogger
LOGGER = CustomLogger(__name__)

import time
from typing import List

from ...settings import (    
    MULTIMODAL_MODEL, 
    MULTIMODAL_TEMPERATURE, 
    MULTIMODAL_TOKENS_MAX, 
    MULTIMODAL_TOP_P,
    PROMPT_AUDIT_ENABLED
)

# Vertex AI
from google.cloud import aiplatform
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient


PROMPT_AUDIT_LOG = u"paperglass_prompt_audit_log"


class PromptAdapter(IPromptAdapter):
    def __init__(self, project_id, location, db_name) -> None:
        self.project_id = project_id
        self.location = location
        vertexai.init(project=project_id, location=location)
        aiplatform.init(project=project_id, location=location)
        self.db = AsyncFirestoreClient(database=db_name) if db_name else AsyncFirestoreClient()

    async def extract(self, content, model):
        return await self.predict(content, model)

    async def predict(self, prompt_text, model):
        extra = {
            "model": {
                "name": model,
                "settings": {
                    "max_output_tokens": MULTIMODAL_TOKENS_MAX,
                    "temperature": MULTIMODAL_TEMPERATURE,
                    "top_p": MULTIMODAL_TOP_P
                }
            }            
        }
        try:
            generation_model = TextGenerationModel.from_pretrained(model)
            #generation_config = {"max_output_tokens": 8192, "temperature": 0.2, "top_p": 1, "model": model}
            response = await generation_model.predict_async(
                prompt_text,
                max_output_tokens=MULTIMODAL_TOKENS_MAX,
                temperature=MULTIMODAL_TEMPERATURE,
                top_p=MULTIMODAL_TOP_P,
            )
            LOGGER.debug("Performing predict with model %s, max_output_tokens: %s, temperature: %s, top_p: %s", model, MULTIMODAL_TOKENS_MAX, MULTIMODAL_TEMPERATURE, MULTIMODAL_TOP_P, extra=extra)
            LOGGER.debug("Prompt: %s", prompt_text, extra=extra)

            answer = response.text
            #await self.audit_prompt(prompt_text, answer, model, generation_config, {})
            return answer
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error(f"Error in predict: {e}", extra=extra)
            #await self.audit_prompt(prompt_text, "", model, generation_config, {}, str(e))
            raise e

    async def multi_modal_predict(
        self, 
        items: List[Union[str, Tuple[bytes, str]]], 
        model="gemini-1.5-pro-preview-0409",
        metadata: Optional[dict] = None,
    ):
        """
        `items` is a list of tuples, where each tuple is either a string or a tuple of bytes and a string of the mime type.

        e.g.:
        items = [
            "This is a string",
            (b"this is a byte string", "application/pdf"),
            (b"this is a byte string", "image/jpeg"),
        ]
        """
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        extra = {
            "model": {
                "name": model,
                "settings": {
                    "max_output_tokens": MULTIMODAL_TOKENS_MAX,
                    "temperature": MULTIMODAL_TEMPERATURE,
                    "top_p": MULTIMODAL_TOP_P,
                    "safety_settings": safety_settings
                },
                "metadata": metadata
            }            
        }

        try:
            start_time = now_utc()

            generation_config = {}
            contents = []
            prompt_text = None
            hasImage = False
            hasBinaryData = False
            for item in items:
                if isinstance(item, str):
                    contents.append(Part.from_text(item))
                    prompt_text = item
                else:
                    contents.append(Part.from_data(data=item[0], mime_type=item[1]))
                    hasImage = True
                    hasBinaryData = True

            generation_config = {
                "max_output_tokens": MULTIMODAL_TOKENS_MAX,
                "temperature": MULTIMODAL_TEMPERATURE,
                "top_p": MULTIMODAL_TOP_P                
            }

            model_obj = GenerativeModel(model)

            LOGGER.debug("Performing multi_modal_predict with model %s, max_output_tokens: %s, temperature: %s, top_p: %s", model, MULTIMODAL_TOKENS_MAX, MULTIMODAL_TEMPERATURE, MULTIMODAL_TOP_P, extra=extra)
            LOGGER.debug("Prompt: %s", prompt_text, extra=extra)

            billable_tokens_obj = model_obj.count_tokens(contents)
            billable_tokens = {
                "total_tokens": billable_tokens_obj.total_tokens,
                "total_billable_characters": billable_tokens_obj.total_billable_characters
            }

            result_stream = await model_obj.generate_content_async(
                contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True,
            )

            result = ""
            async for stream in result_stream:
                if stream and stream.text:
                    result = result + stream.text

            elapsed_time = now_utc() - start_time
            
            prompt_stats = PromptStats(
                model=model,
                max_output_tokens=MULTIMODAL_TOKENS_MAX,
                temperature=MULTIMODAL_TEMPERATURE,
                top_p=MULTIMODAL_TOP_P,
                prompt_length=len(prompt_text) if prompt_text else 0,
                prompt_tokens=len(prompt_text.split()) if prompt_text else 0,
                billing_total_tokens=billable_tokens["total_tokens"],
                billing_total_billable_characters=billable_tokens["total_billable_characters"],
                response_length=len(result) if result else 0,
                response_tokens=len(result.split()) if result else 0,
                elapsed_time=elapsed_time.total_seconds(),
                hasImage=hasImage,
                hasBinaryData=hasBinaryData,
            )
            extra_combined = {**prompt_stats.dict(), **metadata} if metadata else prompt_stats.dict()
            LOGGER.info("Prompt::multi_modal_predict", extra=extra_combined)            

            await self.audit_prompt(str(contents), result, model, generation_config, prompt_stats=prompt_stats, metadata=metadata)

            return result

        except Exception as e:
            #await self.audit_prompt(str(contents), "", model, generation_config, safety_settings={}, error=str(e))
            raise e

    async def multi_modal_predict_2(self, 
                                 items: List[Union[str, Tuple[str, str], Tuple[bytes, str]]], 
                                 model=MULTIMODAL_MODEL,
                                 system_prompts: Optional[List[str]] = [],
                                 response_mime_type: Optional[str] = None,
                                 metadata: Optional[dict] = None,
    ):
        """
        `items` is a list of tuples, where each tuple is either a string, tuple of string (file uri) and string (mime type), or a tuple of bytes and a string of the mime type.

        e.g.:
        items = [
            "This is a string",
            ("gs://bucket/path/to/file", "application/pdf"),
            (b"this is a byte string", "application/pdf"),
            (b"this is a byte string", "image/jpeg"),
        ]
        """
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        extra = {
            "model": {
                "name": model,
                "settings": {
                    "max_output_tokens": MULTIMODAL_TOKENS_MAX,
                    "temperature": MULTIMODAL_TEMPERATURE,
                    "top_p": MULTIMODAL_TOP_P,
                    "safety_settings": safety_settings
                },
                "metadata": metadata
            }            
        }

        try:            
            start_time = now_utc()

            generation_config = {
                "max_output_tokens": MULTIMODAL_TOKENS_MAX,
                "temperature": MULTIMODAL_TEMPERATURE,
                "top_p": MULTIMODAL_TOP_P,
            }
            
            if response_mime_type is not None:
                generation_config["response_mime_type"] = response_mime_type
            
            contents = []
            prompt_text = None
            uri = None
            hasImage = False
            hasBinaryData = False
            for item in items:
                if isinstance(item, str):
                    LOGGER.debug("Adding contents from text", extra=extra)
                    contents.append(Part.from_text(item))
                    prompt_text = item
                elif isinstance(item, tuple) and len(item) == 2 and all(isinstance(element, str) for element in item):
                    uri = item[0]
                    LOGGER.debug("Adding contents from uri: %s, mime_type: 'application/pdf'", uri, extra=extra)
                    pdf_part = Part.from_uri(uri, mime_type="application/pdf")
                    contents.append(pdf_part)
                    hasImage = True
                else:
                    LOGGER.debug("Adding contents from data", extra=extra)
                    contents.append(Part.from_data(data=item[0], mime_type=item[1]))
                    hasImage = True
                    hasBinaryData = True
            
            LOGGER.debug("Performing multi_modal_predict2 with model %s, max_output_tokens: %s, temperature: %s, top_p: %s", model, MULTIMODAL_TOKENS_MAX, MULTIMODAL_TEMPERATURE, MULTIMODAL_TOP_P, extra=extra)
            LOGGER.debug("Prompt: %s", prompt_text, extra=extra)

            model_obj = GenerativeModel(model,
                                        safety_settings=safety_settings,
                                        system_instruction=system_prompts,
                                        )
            
            billable_tokens_obj = model_obj.count_tokens(contents)    
            billable_tokens = {
                "total_tokens": billable_tokens_obj.total_tokens,
                "total_billable_characters": billable_tokens_obj.total_billable_characters
            }
            
            result_stream = await model_obj.generate_content_async(
                contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True,
            )

            result = ""
            async for stream in result_stream:
                if stream and stream.text:
                    result = result + stream.text

            LOGGER.debug("Result: %s", result, extra=extra)

            elapsed_time = now_utc() - start_time

            prompt_stats = PromptStats(
                model=model,
                max_output_tokens=MULTIMODAL_TOKENS_MAX,
                temperature=MULTIMODAL_TEMPERATURE,
                top_p=MULTIMODAL_TOP_P,
                prompt_length=len(prompt_text) if prompt_text else 0,
                prompt_tokens=len(prompt_text.split()) if prompt_text else 0,
                billing_total_tokens=billable_tokens["total_tokens"],
                billing_total_billable_characters=billable_tokens["total_billable_characters"],
                response_length=len(result) if result else 0,
                response_tokens=len(result.split()) if result else 0,
                elapsed_time=elapsed_time.total_seconds(),
                hasImage=hasImage,
                hasBinaryData=hasBinaryData,
            )
            extra = {**prompt_stats.dict(), **metadata} if metadata else prompt_stats.dict()
            LOGGER.info("Prompt::multi_modal_predict2", extra=extra)            

            await self.audit_prompt(str(contents), result, model, generation_config, prompt_stats=prompt_stats, metadata=metadata)

            return result

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error(f"Error in multi_modal_predict_2: {e}, Type: {type(e).__name__}", extra=extra)
            #await self.audit_prompt(str(contents), "", model, generation_config, safety_settings={}, error=str(e))
            raise e

    async def get_prompt_template(self, template_name: str) -> str:
        with open(f"{os.path.dirname(__file__)}/../../config/prompt_templates/{template_name}", "r") as f:
            return f.read()

    async def audit_prompt(self, prompt_text, final_result, model, generation_config, safety_settings={}, error="", prompt_stats: PromptStats = None, metadata: dict = {}):
        
        if not PROMPT_AUDIT_ENABLED:
            LOGGER.debug("Prompt audit is disabled.  skipping.")
            return       
        else:
            LOGGER.warning("Prompt audit is enabled.  Writing full prompt input and result to audit log entry")
        
        try:

            id = uuid.uuid4().hex
            prompt_audit_log = PromptAuditLog(
                id=id,
                input_prompt=str(prompt_text),
                output=str(final_result) if final_result else "",
                config=generation_config,
                model=model,
                safety_settings={},
                error=error,
                createdAt=now_utc().isoformat(),
                projectId=self.project_id,
                location=self.location,
                prompt_stats=prompt_stats,
                metadata=metadata,
            ).dict()

            await self.db.collection(PROMPT_AUDIT_LOG).document(id).set(prompt_audit_log)
        except Exception as e:
            extra = {
                "error": exceptionToMap(e),
            }
            LOGGER.error(f"prompt auditing failed: {e} for {str(prompt_text)}", extra=extra)
