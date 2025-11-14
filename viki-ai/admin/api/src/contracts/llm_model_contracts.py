from typing import List, Optional
from pydantic import BaseModel, Field

from models.llm_model import LLMModel, SupportProfile, BurndownRateFactors, Lifecycle, ProvisionedThroughput


class LLMModelCreateRequest(BaseModel):
    family: str = Field(..., description="Model family name")
    name: str = Field(..., description="Model display name")
    model_id: str = Field(..., description="Model API identifier (e.g., 'gemini-2.5-flash-lite')")
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


class LLMModelUpdateRequest(BaseModel):
    family: Optional[str] = Field(None, description="Model family name")
    name: Optional[str] = Field(None, description="Model display name")
    model_id: Optional[str] = Field(None, description="Model API identifier (e.g., 'gemini-2.5-flash-lite')")
    version: Optional[str] = Field(None, description="Model version identifier")
    description: Optional[str] = Field(None, description="Detailed description of the model")
    support_profile: Optional[SupportProfile] = Field(None, description="Supported input/output types")
    per_second_throughput_per_gsu: Optional[int] = Field(None, description="Throughput per GSU per second")
    units: Optional[str] = Field(None, description="Units for throughput measurement")
    minimum_gsu_purchase_increment: Optional[int] = Field(None, description="Minimum GSU purchase increment")
    burndown_rate_factors: Optional[BurndownRateFactors] = Field(None, description="Token burndown rate factors")
    knowledge_cutoff_date: Optional[str] = Field(None, description="Knowledge cutoff date")
    lifecycle: Optional[Lifecycle] = Field(None, description="Model lifecycle information")
    provisioned_throughput: Optional[List[ProvisionedThroughput]] = Field(None, description="Provisioned throughput by region")
    priority: Optional[float] = Field(None, description="Model priority")
    active: Optional[bool] = Field(None, description="Whether the model is active")


class LLMModelResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[LLMModel] = Field(None, description="LLM model data")


class LLMModelListResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: List[LLMModel] = Field(..., description="List of LLM models")
    total: int = Field(..., description="Total number of models")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=10, description="Number of models per page")


class LLMModelSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    family: Optional[str] = Field(None, description="Filter by model family")
    active: Optional[bool] = Field(None, description="Filter by active status")
    page: int = Field(default=1, description="Page number")
    page_size: int = Field(default=10, description="Number of results per page")


class LLMModelDeleteResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    deleted_id: str = Field(..., description="ID of the deleted model")