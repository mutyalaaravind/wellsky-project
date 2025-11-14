import aiohttp
import json
from typing import Optional, Dict, Any
from aiocache import cached, Cache
from util.custom_logger import getLogger

LOGGER = getLogger(__name__)


class SchemaClient:
    """Client for making HTTP requests to retrieve entity schemas from any network location."""
    
    def __init__(self):
        """
        Initialize the Schema client.
        """
        
    @cached(ttl=300, cache=Cache.MEMORY)  # Cache for 5 minutes
    async def get_entity_schema(self, schema_url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an entity schema from the given URL with usecase=extract parameter.
        Results are cached for 5 minutes to improve performance.
        
        :param schema_url: The URL to retrieve the schema from
        :return: The schema dictionary or None if failed
        """
        try:
            # Ensure the URL has the usecase=extract parameter
            if "?" in schema_url:
                full_url = f"{schema_url}&usecase=extract"
            else:
                full_url = f"{schema_url}?usecase=extract"
            
            LOGGER.debug(f"Fetching entity schema from: {full_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url) as response:
                    if response.status == 200:
                        schema_data = await response.json()
                        LOGGER.info(f"Successfully retrieved entity schema from {full_url}")
                        return schema_data
                    else:
                        LOGGER.error(f"Failed to retrieve entity schema from {full_url}. Status: {response.status}")
                        error_text = await response.text()
                        LOGGER.error(f"Error response: {error_text}")
                        return None
                        
        except Exception as e:
            LOGGER.error(f"Exception while fetching entity schema from {schema_url}: {str(e)}")
            return None
