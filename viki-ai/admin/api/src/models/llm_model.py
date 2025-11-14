from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SupportProfile(BaseModel):
    input: List[str] = Field(..., description="List of supported input types")
    output: List[str] = Field(..., description="List of supported output types")


class BurndownRateFactors(BaseModel):
    input_text_token: float = Field(default=1.0, description="Burndown rate for input text tokens")
    input_image_token: float = Field(default=1.0, description="Burndown rate for input image tokens")
    input_video_token: float = Field(default=1.0, description="Burndown rate for input video tokens")
    input_audio_token: float = Field(default=3.0, description="Burndown rate for input audio tokens")
    output_response_text_token: float = Field(default=4.0, description="Burndown rate for output response text tokens")
    output_reasoning_text_token: float = Field(default=4.0, description="Burndown rate for output reasoning text tokens")


class LifecycleProvider(BaseModel):
    available_date: str = Field(..., description="Date when the model becomes available")
    sunset_date: str = Field(..., description="Date when the model will be sunset")


class Lifecycle(BaseModel):
    google: Optional[LifecycleProvider] = None
    wsky: Optional[LifecycleProvider] = None


class ProvisionedThroughput(BaseModel):
    region: str = Field(..., description="Region where throughput is provisioned")
    gsus: int = Field(..., description="Number of GSUs provisioned")
    term: str = Field(default="1 mo", description="Provisioned throughput term (1 wk, 1 mo, 3 mo, 12 mo)")


class LLMModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the LLM model")
    model_id: str = Field(..., description="Model API identifier (e.g., 'gemini-2.5-flash-lite')")
    family: str = Field(..., description="Model family name")
    name: str = Field(..., description="Model display name")
    version: str = Field(..., description="Model version identifier")
    description: str = Field(..., description="Detailed description of the model")
    support_profile: SupportProfile = Field(..., description="Supported input/output types")
    per_second_throughput_per_gsu: int = Field(..., description="Throughput per GSU per second")
    units: str = Field(default="tokens", description="Units for throughput measurement")
    minimum_gsu_purchase_increment: int = Field(default=1, description="Minimum GSU purchase increment")
    burndown_rate_factors: BurndownRateFactors = Field(..., description="Token burndown rate factors")
    knowledge_cutoff_date: str = Field(..., description="Knowledge cutoff date")
    lifecycle: Lifecycle = Field(..., description="Model lifecycle information")
    provisioned_throughput: List[ProvisionedThroughput] = Field(default_factory=list, description="Provisioned throughput by region")
    priority: float = Field(..., description="Model priority")
    active: bool = Field(default=True, description="Whether the model is active")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(default=None, description="Soft deletion timestamp")