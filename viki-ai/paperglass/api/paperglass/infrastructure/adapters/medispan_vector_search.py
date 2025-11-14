from typing import Dict, List, Optional
import json
import uuid
import traceback

from kink import inject

from ...domain.values import VectorSearchResponseItem
from ...domain.models import MedispanDrug

from ..ports import IMedispanPort

from ...settings import (
    MEDISPAN_VECTOR_SEARCH_PROJECT_ID,
    MEDISPAN_VECTOR_SEARCH_REGION,    
    MEDISPAN_VECTOR_SEARCH_DEPLOYMENT_ID,        
    MEDISPAN_VECTOR_SEARCH_MODEL_NAME,
    MEDISPAN_VECTOR_SEARCH_ENDPOINT_ID,
    MEDISPAN_VECTOR_SEARCH_TASK,
    MEDISPAN_VECTOR_SEARCH_DIMENSIONALITY
)

from ..ports import IQueryPort

from google.cloud import aiplatform    
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from ...log import getLogger
LOGGER = getLogger(__name__)

class MedispanVectorSearchAdapter(IMedispanPort):

    @inject
    def __init__(self, client_id: str, client_secret: str, query: IQueryPort):
        self.client_id = client_id
        self.client_secret = client_secret
        self.query = query
        self.endpoint_name = f"projects/{MEDISPAN_VECTOR_SEARCH_PROJECT_ID}/locations/{MEDISPAN_VECTOR_SEARCH_REGION}/indexEndpoints/{MEDISPAN_VECTOR_SEARCH_ENDPOINT_ID}"
        
        aiplatform.init(project=MEDISPAN_VECTOR_SEARCH_PROJECT_ID, location=MEDISPAN_VECTOR_SEARCH_REGION)

    def embed_text(self,
                    texts: List[str],
                    task: str = MEDISPAN_VECTOR_SEARCH_TASK,
                    model_name: str = MEDISPAN_VECTOR_SEARCH_MODEL_NAME,
                    dimensionality: Optional[int] = MEDISPAN_VECTOR_SEARCH_DIMENSIONALITY,
                ) -> List[List[float]]:
        
        # Embeds texts with a pre-trained, foundational model
        model = TextEmbeddingModel.from_pretrained(model_name)
        inputs = [TextEmbeddingInput(text, task) for text in texts]
        kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
        embeddings = model.get_embeddings(inputs, **kwargs)
        return [embedding.values for embedding in embeddings]

    async def search_medications(self, search_term: str) -> List[MedispanDrug]:

        LOGGER.debug("Performing medispan vector search for medications with search term: %s", search_term)        
        LOGGER.debug("Medispan vector search endpoint name: %s", self.endpoint_name)
        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=self.endpoint_name               
        )

        LOGGER.debug("Performing vector search for Medispan medications with search term: %s", search_term)

        query_emb = self.embed_text(texts=[search_term])[0]
        #LOGGER.debug(str(query_emb))

        # run query
        response = my_index_endpoint.find_neighbors(
            deployed_index_id = MEDISPAN_VECTOR_SEARCH_DEPLOYMENT_ID,
            queries = [query_emb],
            num_neighbors = 10
        )

        response_data = []
        for idx, neighbor in enumerate(response[0]):
            item: VectorSearchResponseItem = VectorSearchResponseItem(
                id=neighbor.id,
                distance=neighbor.distance,
                data=None
            )

            LOGGER.debug("VectorSearchResponseItem: %s:", json.dumps(item.dict(), indent=2))

            try:
                LOGGER.debug("Getting Medispan data for medispanId: %s", neighbor.id)
                drug = await self.query.get_medispan_by_id(neighbor.id)
                if drug:
                    if "med_embedding"  in drug:
                        del drug["med_embedding"]
                    normalized_drug = MedispanDrug(
                                medication_id=neighbor.id,
                                id=drug.get("ExternalDrugId"),
                                NameDescription=drug.get("NameDescription"),
                                GenericName=drug.get("GenericName"),
                                Route=drug.get("Route"),
                                Strength=drug.get("Strength"),
                                StrengthUnitOfMeasure=drug.get("StrengthUnitOfMeasure"),
                                Dosage_Form=drug.get("Dosage_Form"))

                    response_data.append(normalized_drug)
                else:
                    LOGGER.warn("No drug returned from the query for medispanId: %s", neighbor.id)

            except Exception as e:
                LOGGER.error("Error retrieving Medispan data for medispanId: %s: %s", neighbor.id, str(e))
                LOGGER.error(traceback.format_exc())
                continue

        return response_data   
        
        