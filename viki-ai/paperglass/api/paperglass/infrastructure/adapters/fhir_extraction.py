from google.cloud import aiplatform
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient

class FhirExtractAdapter:
    def __init__(self, project_id, location, db_name) -> None:
        vertexai.init(project=project_id, location=location)
        aiplatform.init(project=project_id, location=location)
    
    def extract_patient(self, raw_text:str):
        pass
    
    def _prompt_for_patient(self, raw_text:str):
        pass
    
    def _run_prompt(self, prompt, model):
        pass
    
    async def predict(self, content, model):
        generation_model = TextGenerationModel.from_pretrained(model)

        response = await generation_model.predict_async(content, max_output_tokens=1024, temperature=0.2, top_p=1)
        answer = response.text
