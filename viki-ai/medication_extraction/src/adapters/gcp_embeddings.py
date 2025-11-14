# Configure logging
import logging
from typing import List

from google import genai
from google.genai import types

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class GcpEmbeddingsAdapter:
    """
    Google Cloud Platform implementation of the IEmbeddingsPort interface.
    Uses Vertex AI for generating text embeddings.
    """
    
    async def get_embeddings(self, text: str, model_name: str, project_id: str, location: str) -> List[float]:
        """
        Generate embeddings for the given text using GCP Vertex AI.
        
        Args:
            text: The text to generate embeddings for
            model_name: The name of the embedding model to use
            project_id: The GCP project ID
            location: The GCP location
            
        Returns:
            A list of float values representing the embedding vector
        """

        http_options = types.HttpOptions(
            api_version="v1",
        )

        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            http_options=http_options
        )

        result = client.models.embed_content(
            model=model_name,
            contents=text
        )

        # Return the first embedding (since we only sent one text)
        if result.embeddings and len(result.embeddings[0].values) > 0:
            return list(result.embeddings[0].values)
        
        # Return empty list if no embeddings were generated
        return []


# Legacy function for backward compatibility
async def get_embeddings(text: str, model_name: str, project_id: str, location: str) -> List[float]:
    """
    Legacy function for backward compatibility.
    Use GcpEmbeddingsAdapter instead for new code.
    """
    adapter = GcpEmbeddingsAdapter()
    return await adapter.get_embeddings(text, model_name, project_id, location)
