"""
Firestore adapter for vector search.
"""
import time
import logging
from typing import List, Dict, Any, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

from models import MedispanDrug
from model_metric import Metric
import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class MedispanFirestoreVectorAdapter:
    """
    Firestore implementation of the IVectorSearchPort interface. This is the V2 implementation allowing for selectable catalogs based on app_id.
    Uses Firestore for vector similarity search.
    """
    
    def __init__(self, app_id: str, catalog: str):
        """Initialize the Firestore adapter."""
        self.app_id = app_id
        self.catalog = catalog
        self.db = firestore.Client(
            project=settings.GCP_PROJECT_ID,
            database=settings.GCP_FIRESTORE_DB
        )
    
    def _get_catalog_id(self, app_id: str) -> str:
        """
        Get the catalog ID for a given app ID.
        
        Args:
            app_id: The app ID to look up
            
        Returns:
            The catalog ID as a string
        """
        
        return self.catalog
    
    def _get_tablename(self) -> str:
        """
        Get the collection name for a given app ID.
        
        Args:
            app_id: The app ID to look up
            
        Returns:
            The collection name as a string
        """
        catalog_id = self._get_catalog_id(self.app_id)
        
        if catalog_id == "medispan":
            return settings.FIRESTOREVECTOR_COLLECTION_MEDISPAN
        elif catalog_id == "merative":
            return settings.FIRESTOREVECTOR_COLLECTION_MERATIVE        
        else:
            # Default to Medispan if catalog ID is not recognized
            return settings.FIRESTOREVECTOR_COLLECTION_MEDISPAN

    async def search_medications(self, search_term: str, dosage_form: str = None, route: str = None):
        """Search for medications using keyword or vector search."""
        from adapters.gcp_embeddings import get_embeddings
        start_time = time.time()

        extra = {
            "adapter": "alloydb",
            "search_term": search_term,
        }
        
        if settings.PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH:
            results = None
        else:
            results = await self.keyword_search(search_term, dosage_form, route)
        
        if not results:
            embeddings = await get_embeddings(search_term, settings.GCP_EMBEDDING_MODEL, settings.GCP_PROJECT_ID, settings.GCP_LOCATION_3)
            results = await self.search_by_vector(embeddings, similarity_threshold=settings.MEDDB_SIMILARIY_THRESHOLD, max_results=settings.MEDDB_MAX_RESULTS)
        
            medications = [MedispanDrug(
                id=str(medication.get('id')),
                NameDescription=medication.get('NameDescription'),
                GenericName=medication.get('GenericName'),
                Strength=medication.get('Strength'),
                StrengthUnitOfMeasure=medication.get('StrengthUnitOfMeasure'),
                Route=medication.get('Route'),
                Dosage_Form=medication.get('Dosage_Form'),
                ) for medication in results]
        
        elapsed_time = time.time() - start_time
        extra.update({            
            "elapsed_time": elapsed_time,
        })
        Metric.send("EXTRACTION::MEDDB::ELAPSEDTIME", branch="firestore", tags=extra)

        return medications
    
    async def keyword_search(self, description: str, dosage_form: str = None, route: str = None, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Search for drugs by name description using Firestore.
        
        Args:
            description: Description to search for
            dosage_form: Optional dosage form to filter by
            route: Optional route to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of matching drug records
        """
        collection_name = self._get_tablename()
        collection_ref = self.db.collection(collection_name)
        
        # Start with base query
        query = collection_ref.where(
            filter=FieldFilter("namedescription_lower", ">=", description.lower())
        ).where(
            filter=FieldFilter("namedescription_lower", "<=", description.lower() + "\uf8ff")
        )
        
        # Add optional filters
        if dosage_form:
            query = query.where(
                filter=FieldFilter("dosageform_lower", "==", dosage_form.lower())
            )
        
        if route:
            query = query.where(
                filter=FieldFilter("route_lower", "==", route.lower())
            )
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query
        try:
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"Error executing Firestore query: {str(e)}")
            raise

    async def search_by_vector(
        self, 
        embedding: List[float], 
        similarity_threshold: float = 0.7, 
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for items by vector similarity using Firestore vector search.
        
        Args:
            embedding: The embedding vector to search with
            similarity_threshold: Minimum similarity score (0-1) for results
            max_results: Maximum number of results to return
            
        Returns:
            A list of dictionaries containing the matching items with their similarity scores
        """
        self.db = firestore.Client(
            project=settings.GCP_PROJECT_ID,
            database=settings.GCP_FIRESTORE_DB
        )
        collection_name = self._get_tablename()
        collection_ref = self.db.collection(collection_name)
        
        try:
            # Create vector search query
            query = collection_ref.find_nearest(
                vector_field="med_embedding",
                query_vector=Vector(embedding),
                distance_measure=DistanceMeasure.EUCLIDEAN,
                limit=max_results
            )
            
            # Execute query
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                del data['med_embedding']
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing vector search in collection {collection_name}: {str(e)}")
            raise e
