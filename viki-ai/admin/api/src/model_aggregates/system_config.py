"""
System Configuration aggregate for Admin API.

This aggregate represents the system configuration envelope with audit fields
and business logic for retrieving model configurations.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from models.config import Configuration, ModelConfig


class SystemConfig(BaseModel):
    """System configuration aggregate with audit fields."""
    id: str = Field(default="admin_config", description="Configuration document ID")
    config: Configuration = Field(..., description="The actual configuration data")
    active: bool = Field(default=True, description="Whether this configuration is active")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    def get_model_config(self, operation: str) -> ModelConfig:
        """
        Get model configuration for a specific onboarding operation.
        
        Args:
            operation: Operation name (e.g., 'schema_generation', 'prompt_generation', 'test_extraction')
            
        Returns:
            ModelConfig: Configuration for the specified operation
            
        Raises:
            ValueError: If operation is not supported
        """
        if operation == "schema_generation":
            return self.config.onboarding.schema_generation.llm_config
        elif operation == "prompt_generation":
            return self.config.onboarding.prompt_generation.llm_config
        elif operation == "test_extraction":
            return self.config.onboarding.test_extraction.llm_config
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    def get_model_parameters(self, operation: str) -> Dict[str, Any]:
        """
        Get model parameters as a dictionary for LLM requests.
        
        Args:
            operation: Operation name
            
        Returns:
            Dict[str, Any]: Model parameters ready for LLM requests
        """
        model_config = self.get_model_config(operation)
        params = {
            "model_name": model_config.model,
            "max_output_tokens": model_config.max_output_tokens,
            "temperature": model_config.temperature
        }
        
        # Add optional parameters if set
        if model_config.top_k is not None:
            params["top_k"] = model_config.top_k
        if model_config.top_p is not None:
            params["top_p"] = model_config.top_p
        if model_config.candidate_count is not None:
            params["candidate_count"] = model_config.candidate_count
        if model_config.stop_sequences is not None:
            params["stop_sequences"] = model_config.stop_sequences
            
        return params