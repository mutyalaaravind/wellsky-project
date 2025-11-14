"""
Configuration models for Admin API.

These models define the structure for admin configuration data
stored in Firestore, including LLM model configurations for
various operations.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for an LLM model."""
    model: str = Field(..., description="Model name (e.g., 'gemini-2.5-pro')")
    max_output_tokens: Optional[int] = Field(default=8192, description="Maximum output tokens")
    temperature: Optional[float] = Field(default=0.0, description="Temperature for randomness")
    top_k: Optional[int] = Field(default=None, description="Top-k sampling parameter")
    top_p: Optional[float] = Field(default=None, description="Top-p (nucleus) sampling parameter")
    candidate_count: Optional[int] = Field(default=1, description="Number of candidates to generate")
    stop_sequences: Optional[list[str]] = Field(default=None, description="Stop sequences")


class OnboardingOperationConfig(BaseModel):
    """Configuration for a single onboarding operation."""
    llm_config: ModelConfig = Field(..., description="Model configuration for this operation")


class OnboardingConfiguration(BaseModel):
    """Configuration for onboarding operations."""
    schema_generation: OnboardingOperationConfig = Field(..., description="Schema generation configuration")
    prompt_generation: OnboardingOperationConfig = Field(..., description="Prompt generation configuration")
    test_extraction: OnboardingOperationConfig = Field(..., description="Test extraction configuration")


class Configuration(BaseModel):
    """Root configuration containing all system configurations."""
    onboarding: OnboardingConfiguration = Field(..., description="Onboarding operation configurations")