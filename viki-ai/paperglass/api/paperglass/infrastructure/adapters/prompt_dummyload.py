
import vertexai
from google.cloud import aiplatform
from typing import List, Optional, Tuple, Union
import asyncio

from paperglass.infrastructure.ports import IPromptAdapter

import json

from paperglass.log import CustomLogger
LOGGER = CustomLogger(__name__)

import time
from typing import List

from ...settings import MULTIMODAL_MODEL

JSON_FILEPATH = "./paperglass/tests/load/input/mock-prompt-data.json"

"""
NOTE:  This Dummy adapter emulates the prompt output for a very specific document as defined in the JSON file.  This will 
need to be refactored if the load test needs to support multiple documents.
"""
class DummyPromptAdapter(IPromptAdapter):
    def __init__(self, project_id, location, db_name) -> None:
        self.project_id = project_id
        self.location = location        

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

    async def extract(self, content, model):
        return await self.predict(content, model)

    async def predict(self, prompt_text, model, metadata: Optional[dict] = None,):
        try:
            LOGGER.debug("Calling mock prompt predict")
            step_id = metadata["step"]
            page_number = metadata["page_number"]
            iteration = metadata["iteration"]

            key = self.create_key(step_id, page_number, iteration)
            mock_data = self.DUMMY_DATA[key]

            elapsed_time = mock_data["elapsed_time"]
            output = mock_data["output"]

            await asyncio.sleep(elapsed_time)
            
            return output
        except Exception as e:
            LOGGER.error(f"Error in mock predict. Returning empty string: {e}")
            LOGGER.debug("Metadata: %s", json.dumps(metadata, indent=2))
            return ""

    async def multi_modal_predict(
        self, 
        items: List[Union[str, Tuple[bytes, str]]], 
        model="gemini-1.5-pro-preview-0409",
        metadata: Optional[dict] = None,
    ):
        try:
            LOGGER.debug("Calling mock prompt multi_modal_predict")
            step_id = metadata["step"]
            page_number = metadata["page_number"]
            iteration = metadata["iteration"]

            key = self.create_key(step_id, page_number, iteration)
            mock_data = self.DUMMY_DATA[key]

            elapsed_time = mock_data["elapsed_time"]
            output = mock_data["output"]

            await asyncio.sleep(elapsed_time)
            
            return output            

        except Exception as e:
            LOGGER.error(f"Error in mock multi_modal_predict.  Returning empty string: {e}")
            LOGGER.debug("Metadata: %s", json.dumps(metadata, indent=2))
            return ""

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

            key = self.create_key(step_id, page_number, iteration)
            mock_data = self.DUMMY_DATA[key]

            elapsed_time = mock_data["elapsed_time"]
            output = mock_data["output"]

            await asyncio.sleep(elapsed_time)
            
            return output

        except Exception as e:
            LOGGER.error(f"Error in mock multi_modal_predict_2.  Returning empty string: {e}, Type: {type(e).__name__}")
            LOGGER.debug("Metadata: %s", json.dumps(metadata, indent=2))
            return ""