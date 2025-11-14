"""
PGVector adapter for vector search.
"""
import logging
import time
from typing import List, Dict, Any, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

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


class MedispanPgVectorAdapter:
    """
    PGVector implementation of the IVectorSearchPort interface.
    Uses PostgreSQL with pgvector extension for vector similarity search.
    """
    
    def __init__(self, app_id: str, catalog: str):
        """Initialize the PGVector adapter with connection parameters from settings."""
        self.app_id = app_id
        self.catalog = catalog
        self.connection_params = {
            "host": settings.PGVECTOR_HOST,
            "port": settings.PGVECTOR_PORT,
            "user": settings.PGVECTOR_USER,
            "password": settings.PGVECTOR_PASSWORD,
            "database": settings.PGVECTOR_DATABASE,
            "sslmode": settings.PGVECTOR_SSL_MODE,
            "connect_timeout": settings.PGVECTOR_CONNECTION_TIMEOUT
        }        
    
    def _get_connection(self) -> Tuple[Any, Any]:
        """
        Get a connection to the PostgreSQL database.
        
        Returns:
            A tuple containing (connection, cursor)
        """
        try:
            connection = psycopg2.connect(**self.connection_params)
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            return connection, cursor
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {str(e)}")
            raise

    def _get_catalog_id(self, app_id:str) -> str:
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
        Get the table name for a given app ID.
        
        Args:
            app_id: The app ID to look up
            
        Returns:
            The table name as a string
        """
        
        catalog_id = self._get_catalog_id(self.app_id)
        
        if catalog_id == "medispan":
            return settings.PGVECTOR_TABLE_MEDISPAN
        elif catalog_id == "merative":
            return settings.PGVECTOR_TABLE_MERATIVE        
        else:
            # Default to Medispan if catalog ID is not recognized
            return settings.PGVECTOR_TABLE_MEDISPAN


    def _get_functionname(self) -> str:
        """
        Get the function name for a given app ID.
        
        Args:
            app_id: The app ID to look up
            
        Returns:
            The function name as a string
        """
        
        catalog_id = self._get_catalog_id(self.app_id)
        
        if catalog_id == "medispan":
            return settings.PGVECTOR_SEARCH_FUNCTION_MEDISPAN
        elif catalog_id == "merative":
            return settings.PGVECTOR_SEARCH_FUNCTION_MERATIVE        
        else:
            # Default to Medispan if catalog ID is not recognized
            logger.warning(f"Unknown catalog ID {catalog_id}. Defaulting to Medispan.")
            return settings.PGVECTOR_SEARCH_FUNCTION_MEDISPAN
        
        
    async def search_medications(self, search_term:str, dosage_form:str=None, route:str=None):
        start_time = time.time()
        from adapters.gcp_embeddings import get_embeddings

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
            results = await self.search_by_vector(embeddings, similarity_threshold=settings.MEDDB_SIMILARIY_THRESHOLD, max_results=settings.MEDDB_TOP_K)
        
        medications = [MedispanDrug(
                id=str(medication.get('id')),
                NameDescription=medication.get('namedescription'),
                GenericName=medication.get('genericname'),
                Route=medication.get('route'),
                Strength=medication.get('strength'),
                StrengthUnitOfMeasure=medication.get('strengthunit'),
                Dosage_Form=medication.get('dosageform'),
                ) for medication in results]
        
        elapsed_time = time.time() - start_time
        extra.update({          
            "elapsed_time": elapsed_time,
        })
        Metric.send("EXTRACTION::MEDDB::ELAPSEDTIME", branch="alloydb", tags=extra)
        return medications
    
    async def keyword_search(self, description: str, dosage_form:str=None,route:str=None, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Search for drugs by name description.
        
        Args:
            description: Description to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching drug records
        """
        table_name = self._get_tablename()

        query = f"""
        SELECT *
        FROM {table_name}
        WHERE LOWER(namedescription) LIKE LOWER('%{description}%')
        """
        
        query = query + f" AND LOWER(dosageform) LIKE LOWER('%{dosage_form}%')" if dosage_form else query
        query = query + f" AND LOWER(route) LIKE LOWER('%{route}%')" if route else query
        query = query + f" LIMIT {limit}" if limit else query    

        logger.debug(f"keyword_search query: {query} description: {description} dosageform: {dosage_form} route: {route} limit: {limit}")
        
        return await self.execute_query(query)
    
    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Optional tuple of parameters for the query
            
        Returns:
            List of dictionaries containing the query results
        """
        try:
            connection, cursor = self._get_connection()
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            result_list = [dict(row) for row in results]
            
            cursor.close()
            connection.close()
            
            return result_list
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    async def search_by_vector(
        self, 
        embedding: List[float], 
        similarity_threshold: float = 0.7, 
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for items by vector similarity using the vector_search function.
        
        Args:
            embedding: The embedding vector to search with
            similarity_threshold: Minimum similarity score (0-1) for results
            max_results: Maximum number of results to return
            
        Returns:
            A list of dictionaries containing the matching items with their similarity scores
        """
        
        function_name = self._get_functionname()

        try:
            # Get database connection and cursor
            connection, cursor = self._get_connection()
            
            # Convert embedding list to PostgreSQL array format
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            
            # Call the vector_search function
            # query = f"""
            # SELECT * FROM {self.table_name}
            # ORDER BY embedding <=> '{embedding_str}'::vector
            # LIMIT {max_results};
            # """
            
            # Execute the query
            #cursor.execute(query)

            logger.debug(f"search_by_vector: function_name: {function_name} similarity_threshold: {similarity_threshold} max_results: {max_results}")
            
            cursor.callproc(function_name, (embedding_str, similarity_threshold, max_results))
                        
            # Fetch all results
            results = cursor.fetchall()
            
            #results = sorted(results, key=lambda x: int(x['id']), reverse=False)
            
            # Convert results to list of dictionaries
            result_list = [dict(row) for row in results]
            
            # if not result_list:
            #     cursor.callproc("vector_search_gcp_768_2_euclidean", (embedding_str, similarity_threshold, max_results))
            #     results = cursor.fetchall()
            #     result_list = [dict(row) for row in results]
            
            # Close cursor and connection
            cursor.close()
            connection.close()
            
            return result_list
            
        except Exception as e:
            logger.error(f"Error performing vector search using function {function_name}: {str(e)}")
            # Return empty list on error
            raise e
