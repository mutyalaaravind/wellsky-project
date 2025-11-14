from typing import Dict, List, Optional
import json
import uuid
import traceback
import time

from settings import GCP_FIRESTORE_DB, GCP_PROJECT_ID
from models import MedispanDrug
from model_metric import Metric
from utils.exception import exceptionToMap



from google.cloud import aiplatform,firestore   
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

from utils.custom_logger import getLogger
LOGGER = getLogger(__name__)
COLLECTION = "medispan_meds"

class MedispanFireStoreVectorSearchAdapter:

    def __init__(self, project_id:str=GCP_PROJECT_ID,db_name: str= GCP_FIRESTORE_DB):
        self.firestore_client = firestore.Client(project=project_id,database=db_name)
        self.medispan_ref = self.firestore_client.collection(COLLECTION)

    def embed_text(self,
                    texts: List[str],
                    task: str = "RETRIEVAL_DOCUMENT",
                    model_name: str = "text-embedding-004",
                    dimensionality: Optional[int] = 768,
                ) -> List[List[float]]:
        
        # Embeds texts with a pre-trained, foundational model
        model = TextEmbeddingModel.from_pretrained(model_name)
        inputs = [TextEmbeddingInput(text, task) for text in texts]
        kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
        embeddings = model.get_embeddings(inputs, **kwargs)
        return [embedding.values for embedding in embeddings]

    async def search_medications(self, search_term: str,) -> List[dict]:
        start_time = time.time()
        extra = {
            "adapter": "firestore-orig",
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

        elapsed_time = time.time() - start_time
        extra.update({            
            "elapsed_time": elapsed_time,
        })
        Metric.send("EXTRACTION::MEDDB::ELAPSEDTIME", branch="firestore-orig", tags=extra)
        return results
        
        