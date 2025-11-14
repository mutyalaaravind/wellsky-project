import vertexai
from vertexai.language_models import TextGenerationModel, TextEmbeddingModel
from google.cloud import aiplatform
from typing import List, Optional

from extract_and_fill.infrastructure.ports import IPromptPort

import json, datetime


from extract_and_fill.log import getLogger

LOGGER = getLogger(__name__)

import time
from typing import List

# Vertex AI
from google.cloud import aiplatform
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient

PROMPT_COLLECTION = u"extract_prompt_templates"


class PromptAdapter(IPromptPort):
    def __init__(self, project_id, location, db_name) -> None:
        vertexai.init(project=project_id, location=location)
        aiplatform.init(project=project_id, location=location)
        if db_name != "(default)":
            self.db = AsyncFirestoreClient(project=project_id, database=db_name)
        else:
            self.db = AsyncFirestoreClient()

    async def extract(self, content, model):
        return await self.predict(content, model)

    async def predict(self, content, model):
        generation_model = TextGenerationModel.from_pretrained(model)

        response = await generation_model.predict_async(content, max_output_tokens=8000, temperature=0.2, top_p=1)
        answer = response.text

        return answer

    async def save_prompt_template(self, transcript_id: str, prompt_template: str, model: str) -> str:
        result = []
        doc_ref = self.db.collection(PROMPT_COLLECTION).document(transcript_id)
        data = {
            'transcript_id': transcript_id,
            'extract_prompt_template': prompt_template,
            'model': model,
            "updatedAt": datetime.datetime.utcnow().isoformat(),
        }
        await doc_ref.set(data)
        return True

    async def get_prompt_template(self, transcript_id: str) -> str:
        result = []
        doc_ref = self.db.collection(PROMPT_COLLECTION).document(transcript_id)
        doc = await doc_ref.get()
        if doc:
            return doc.to_dict()
