
import vertexai
from google.cloud import aiplatform
from typing import List, Optional, Tuple, Union
import asyncio

import json

import vertexai
from vertexai.generative_models import Part
from vertexai.preview import caching
from vertexai.preview.generative_models import (GenerativeModel,
                                                HarmBlockThreshold,
                                                HarmCategory)
from google.cloud import aiplatform

from utils.custom_logger import CustomLogger
from utils.string import remove_prefix, remove_suffix
from utils.json import DateTimeEncoder

from adapters.llm import PromptStats

LOGGER = CustomLogger(__name__)

import time
from typing import List

JSON_FILEPATH = "./tests/load/input/mock-prompt-data.json"

MULTIMODAL_MODEL = "gemini-1.5-flash-002"

safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }

"""
NOTE:  This Dummy adapter emulates the prompt output for a very specific document as defined in the JSON file.  This will 
need to be refactored if the load test needs to support multiple documents.
"""
class DummyPromptAdapter:
    def __init__(self) -> None:
        # self.project_id = project_id
        # self.location = location        

        LOGGER.warning("Instantiating DummyPromptAdapter for load test.  If this is not a load test, please check the configuration!!!!!")

        try:
            with open(JSON_FILEPATH, 'r') as json_file:
                self.DUMMY_DATA = json.load(json_file)
        except Exception as e:
            LOGGER.error("Error reading mock prompt data from %s: %s", JSON_FILEPATH, e)

    def create_key(self, step_id: str, page_number:int, iteration:int):
        formatted_page_number = str(page_number).zfill(2)
        formatted_iteration = str(iteration).zfill(2)
        return f"{step_id}::{formatted_page_number}::{formatted_iteration}"
    
    def convert_to_content(self, items: List[Union[str, Tuple[str, str], Tuple[bytes, str]]], extra:dict={}):
        o = {
            "contents": [],
            "prompt_text": None,
            "uri": None,
            "hasImage": False,
            "hasBinaryData": False,
        }
        
        for item in items:
            if isinstance(item, str):
                LOGGER.debug("Adding contents from text", extra=extra)
                o["contents"].append(Part.from_text(item))
                o["prompt_text"] = item
            elif isinstance(item, tuple) and len(item) == 2 and all(isinstance(element, str) for element in item):
                o["uri"] = item[0]
                LOGGER.debug("Adding contents from uri: %s, mime_type: 'application/pdf'", uri, extra=extra)
                pdf_part = Part.from_uri(o["uri"], mime_type="application/pdf")
                o["contents"].append(pdf_part)
                o["hasImage"] = True
            else:
                LOGGER.debug("Adding contents from data", extra=extra)
                o["contents"].append(Part.from_data(data=item[0], mime_type=item[1]))
                o["hasImage"] = True
                o["hasBinaryData"] = True
        return o


    async def multi_modal_predict_2(self, 
                                 items: List[Union[str, Tuple[str, str], Tuple[bytes, str]]], 
                                 model=MULTIMODAL_MODEL,
                                 system_prompts: Optional[List[str]] = [],
                                 response_mime_type: Optional[str] = None,
                                 metadata: Optional[dict] = None,
    ):
        try:
            LOGGER.debug("Calling mock prompt multi_modal_predict_2")
            step_id = metadata["step"]
            page_number = metadata["page_number"]
            iteration = metadata["iteration"]

            # model_obj = GenerativeModel(model,
            #                             safety_settings=safety_settings,
            #                             system_instruction=system_prompts,
            #                             )
            # model_params = self.convert_to_content(items)
            # hasImage = model_params["hasImage"]
            # hasBinaryData = model_params["hasBinaryData"]
            
            # billable_tokens_obj = model_obj.count_tokens(model_params["contents"])
            # billable_tokens = {
            #     "total_tokens": billable_tokens_obj.total_tokens,
            #     "total_billable_characters": billable_tokens_obj.total_billable_characters
            # }

            key = self.create_key(step_id, page_number, iteration)
            if key not in self.DUMMY_DATA:
                LOGGER.warning("Mock multi_modal_predict_2 could not find recorded data for key: %s", key, extra=metadata)

            mock_data = self.DUMMY_DATA[key]

            elapsed_time = mock_data["elapsed_time"]
            # prompt_text = mock_data["input"]
            # prompt_text = remove_prefix(prompt_text, "[text: ")
            # prompt_text = remove_suffix(prompt_text, "]")

            output = mock_data["output"]

            await asyncio.sleep(elapsed_time)

            # prompt_stats = PromptStats(
            #     model_name=model,
            #     max_output_tokens=self.max_tokens,
            #     temperature=self.temperature,
            #     top_p=self.top_p,
            #     prompt_length=len(prompt_text) if prompt_text else 0,
            #     prompt_tokens=len(prompt_text.split()) if prompt_text else 0,
            #     billing_total_tokens=billable_tokens["total_tokens"],
            #     billing_total_billable_characters=billable_tokens["total_billable_characters"],
            #     response_length=len(output) if output else 0,
            #     response_tokens=len(output.split()) if output else 0,
            #     elapsed_time=elapsed_time.total_seconds(),
            #     hasImage=hasImage,
            #     hasBinaryData=hasBinaryData,
            # )
            # extra = {**prompt_stats.dict(), **metadata} if metadata else prompt_stats.dict()
            # extra.update({"model": {"name": model}}) # This corrects for the modelname being expected to be nested for metrics
            
            
            extra = metadata
            extra.update({
                "mock_data_key": key,
                "output": output,
            })
            LOGGER.info("Prompt::multi_modal_predict2:DUMMY %s", key, extra=extra)
            
            return output

        except KeyError as e:
            LOGGER.warning(f"Mock multi_modal_predict_2 could not find recorded data for key.  Returning empty string: {e}, Type: {type(e).__name__}", extra=metadata)            
            return ""
        except Exception as e:
            LOGGER.error(f"Error in mock multi_modal_predict_2.  Returning empty string: {e}, Type: {type(e).__name__}", extra=metadata)            
            return ""