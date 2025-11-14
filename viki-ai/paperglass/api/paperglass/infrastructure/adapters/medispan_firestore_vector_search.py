from typing import Dict, List, Optional
import json
import uuid
import traceback

from kink import inject

from ...domain.values import VectorSearchResponseItem
from ...domain.models import MedispanDrug
from paperglass.domain.utils.exception_utils import exceptionToMap

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

from google.cloud import aiplatform,firestore   
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

from ...log import getLogger
LOGGER = getLogger(__name__)
COLLECTION = "medispan_meds"

class MedispanFireStoreVectorSearchAdapter(IMedispanPort):

    @inject
    def __init__(self, project_id:str,db_name: str, query: IQueryPort):
        self.query = query
        self.firestore_client = firestore.Client(project=project_id,database=db_name)
        self.medispan_ref = self.firestore_client.collection(COLLECTION)

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

    async def search_medications(self, search_term: str,) -> List[dict]:
        extra = {
            "search_term": search_term,
        }
        LOGGER.debug("Performing vector search for Medispan medications with search term from firestore: %s", search_term, extra=extra)

        query_emb = self.embed_text(texts=[search_term])[0]
        #LOGGER.debug(str(query_emb))

        # run query

        query = self.medispan_ref.find_nearest(
            vector_field="med_embedding",
            query_vector=Vector(query_emb),
            distance_measure=DistanceMeasure.EUCLIDEAN,
            limit=10)
        docs = query.get()

        results = []

        idx = 0
        for doc in docs:
            extra2 = {
                "index": idx,
            }
            drug_name = None
            try:                
                drug = doc.to_dict()
                drug_name = drug.get("NameDescription")
                del drug["med_embedding"]

                extra2.update({
                    "medispan_record": drug,
                })
                extra2.update(extra)
                #LOGGER.debug("firestore data", extra=extra2)

                results.append(MedispanDrug(
                                medication_id=doc.id,
                                id=drug.get("ExternalDrugId"),
                                NameDescription=drug.get("NameDescription"),
                                GenericName=drug.get("GenericName"),
                                Route=drug.get("Route"),
                                Strength=drug.get("Strength"),
                                StrengthUnitOfMeasure=drug.get("StrengthUnitOfMeasure"),
                                Dosage_Form=drug.get("Dosage_Form"))
                            )

            except Exception as e:
                extra2["error"] = exceptionToMap(e)
                LOGGER.error("Exception creating MedispanDrug from Firestore data: %s", drug_name, extra=extra2)
                continue
            finally:
                idx += 1
        return results
        
        