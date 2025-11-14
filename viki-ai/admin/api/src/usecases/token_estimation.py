import time
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from typing import Optional


class TokenEstimator:
    """
    A class for estimating token counts for various inputs including text prompts
    and Google Cloud Storage documents using Google's GenAI API.
    """
    
    def __init__(self):
        self.client = genai.Client(http_options=HttpOptions(api_version="v1"))
    
    def compute_tokens(self, model_id: str, text_prompt: str, document_uri: Optional[str] = None) -> dict:
        """
        Compute token count for a given model, text prompt, and optional document URI.
        
        Args:
            model_id (str): The model ID (e.g., "gemini-2.5-flash-lite")
            text_prompt (str): The text prompt to analyze
            document_uri (Optional[str]): URI to a Google Cloud Storage object 
                                        (e.g., "gs://bucket/path/to/document.pdf")
        
        Returns:
            dict: Response from the GenAI API containing token count information
        """

        start_time = time.time()

        print(f"Text_prompt: {text_prompt}")

        contents = []
        contents.append(types.Part(text=text_prompt))
        
        if document_uri:
            # Add the document URI as additional content
            mime_type = self._infer_mime_type(document_uri)
            contents.append(types.Part(file_data=types.FileData(file_uri=document_uri, mime_type=mime_type)))
        
        response = self.client.models.generate_content(
            model=model_id,
            contents=contents,
        )
        
        # Extract token usage information from the response
        usage_metadata = response.usage_metadata

        elapsed_time = time.time() - start_time
        
        #print(usage_metadata)
        return {
            "elapsed_time": elapsed_time,
            'prompt_token_count': usage_metadata.prompt_token_count,
            'candidates_token_count': usage_metadata.candidates_token_count,
            'total_token_count': usage_metadata.total_token_count,
            'cached_content_token_count': getattr(usage_metadata, 'cached_content_token_count', 0)
        }
    
    def _infer_mime_type(self, uri: str) -> str:
        """
        Infer MIME type from file extension in the URI.
        
        Args:
            uri (str): The file URI
            
        Returns:
            str: The inferred MIME type
        """
        # Extract file extension from URI
        if uri.lower().endswith('.pdf'):
            return 'application/pdf'
        elif uri.lower().endswith('.txt'):
            return 'text/plain'
        elif uri.lower().endswith('.doc'):
            return 'application/msword'
        elif uri.lower().endswith('.docx'):
            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif uri.lower().endswith('.jpg') or uri.lower().endswith('.jpeg'):
            return 'image/jpeg'
        elif uri.lower().endswith('.png'):
            return 'image/png'
        else:
            # Default to PDF for unknown extensions
            return 'application/pdf'