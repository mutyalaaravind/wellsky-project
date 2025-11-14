"""
LLM execution contracts.

This module contains the request/response models for LLM execution endpoints,
including document processing and schema generation functionality.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class ModelParameters(BaseModel):
    """
    LLM model configuration parameters.
    """
    model_name: Optional[str] = Field(
        None,
        description="LLM model name to use (e.g., 'gemini-1.5-pro', 'gemini-1.5-flash-002')"
    )
    max_output_tokens: Optional[int] = Field(
        None,
        description="Maximum number of output tokens to generate"
    )
    temperature: Optional[float] = Field(
        None,
        description="Sampling temperature (0.0 to 1.0)"
    )
    top_p: Optional[float] = Field(
        None,
        description="Top-p sampling parameter (0.0 to 1.0)"
    )


class LlmExecuteRequest(BaseModel):
    """
    Request model for LLM execution endpoint.
    
    This model represents a request to execute an LLM prompt with a document
    stored in Google Cloud Storage and generate a response based on the provided
    system instructions, prompt, and optional JSON schema.
    """
    gs_uri: str = Field(
        ..., 
        description="Google Cloud Storage URI of the document to process (e.g., gs://bucket/path/to/document.pdf)"
    )
    system_instructions: Optional[str] = Field(
        None,
        description="System instructions to provide context and behavior guidelines for the LLM"
    )
    prompt: str = Field(
        ...,
        description="The main prompt describing what to extract or analyze from the document"
    )
    json_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="JSON Schema to structure the LLM response in a specific format"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata for tracking and logging purposes"
    )
    model_parameters: Optional[ModelParameters] = Field(
        None,
        description="Optional model configuration parameters (model name, tokens, temperature, etc.)"
    )
    
    @field_validator('gs_uri')
    @classmethod
    def validate_gs_uri(cls, v: str) -> str:
        """
        Validate that the URI is a valid Google Cloud Storage URI.
        
        Args:
            v: The GS URI to validate
            
        Returns:
            The validated GS URI
            
        Raises:
            ValueError: If the URI format is invalid
        """
        if not v.startswith('gs://'):
            raise ValueError('GS URI must start with "gs://"')
        
        # Basic validation - ensure there's a bucket and path
        parts = v[5:].split('/', 1)  # Remove 'gs://' and split
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError('GS URI must include both bucket and file path')
            
        return v


class LlmExecuteResponse(BaseModel):
    """
    Response model for LLM execution endpoint.
    
    This model represents the response from executing an LLM prompt,
    including the generated content and metadata about the execution.
    """
    success: bool = Field(
        ...,
        description="Whether the LLM execution was successful"
    )
    content: Optional[Dict[str, Any]] = Field(
        None,
        description="The generated content from the LLM, typically as a JSON object"
    )
    raw_response: Optional[str] = Field(
        None,
        description="The raw text response from the LLM before JSON parsing"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if the execution failed"
    )
    execution_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadata about the execution including timing, token usage, etc."
    )
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )