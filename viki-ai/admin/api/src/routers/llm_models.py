from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import uuid
from datetime import datetime

from dependencies.auth_dependencies import RequireAuth
from models.user import User

from contracts.llm_model_contracts import (
    LLMModelCreateRequest,
    LLMModelUpdateRequest,
    LLMModelResponse,
    LLMModelListResponse,
    LLMModelSearchRequest,
    LLMModelDeleteResponse
)
from models.llm_model import LLMModel
from adapters.llm_model_firestore_adapter import LLMModelFirestoreAdapter
from settings import get_settings, Settings

router = APIRouter()


async def get_firestore_adapter() -> LLMModelFirestoreAdapter:
    """Dependency to get Firestore adapter instance."""
    settings = await get_settings()
    return LLMModelFirestoreAdapter(settings)


@router.get("", response_model=LLMModelListResponse)
async def list_llm_models(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of models per page"),
    adapter: LLMModelFirestoreAdapter = Depends(get_firestore_adapter),
    current_user: User = RequireAuth
):
    """List all LLM models with pagination"""
    models, total = await adapter.list_models(page=page, page_size=page_size)
    
    return LLMModelListResponse(
        success=True,
        message="LLM models retrieved successfully",
        data=models,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{model_id}", response_model=LLMModelResponse)
async def get_llm_model(
    model_id: str,
    adapter: LLMModelFirestoreAdapter = Depends(get_firestore_adapter),
    current_user: User = RequireAuth
):
    """Get a specific LLM model by ID"""
    model = await adapter.get_model(model_id)
    
    if not model or model.deleted_at is not None:
        raise HTTPException(status_code=404, detail="LLM model not found")
    
    return LLMModelResponse(
        success=True,
        message="LLM model retrieved successfully",
        data=model
    )


@router.post("", response_model=LLMModelResponse)
async def create_llm_model(
    model_data: LLMModelCreateRequest,
    adapter: LLMModelFirestoreAdapter = Depends(get_firestore_adapter),
    current_user: User = RequireAuth
):
    """Create a new LLM model"""
    model_id = str(uuid.uuid4())
    
    new_model = LLMModel(
        id=model_id,
        model_id=model_data.model_id,
        family=model_data.family,
        name=model_data.name,
        version=model_data.version,
        description=model_data.description,
        support_profile=model_data.support_profile,
        per_second_throughput_per_gsu=model_data.per_second_throughput_per_gsu,
        units=model_data.units or "tokens",
        minimum_gsu_purchase_increment=model_data.minimum_gsu_purchase_increment or 1,
        burndown_rate_factors=model_data.burndown_rate_factors,
        knowledge_cutoff_date=model_data.knowledge_cutoff_date,
        lifecycle=model_data.lifecycle,
        provisioned_throughput=model_data.provisioned_throughput or [],
        priority=model_data.priority,
        active=model_data.active if model_data.active is not None else True
    )
    
    created_model = await adapter.create_model(new_model)
    
    return LLMModelResponse(
        success=True,
        message="LLM model created successfully",
        data=created_model
    )


@router.put("/{model_id}", response_model=LLMModelResponse)
async def update_llm_model(
    model_id: str,
    model_data: LLMModelUpdateRequest,
    adapter: LLMModelFirestoreAdapter = Depends(get_firestore_adapter),
    current_user: User = RequireAuth
):
    """Update an existing LLM model"""
    existing_model = await adapter.get_model(model_id)
    
    if not existing_model or existing_model.deleted_at is not None:
        raise HTTPException(status_code=404, detail="LLM model not found")
    
    # Update only provided fields
    update_data = model_data.model_dump(exclude_unset=True)
    
    updated_model = await adapter.update_model_fields(model_id, update_data)
    
    return LLMModelResponse(
        success=True,
        message="LLM model updated successfully",
        data=updated_model
    )


@router.delete("/{model_id}", response_model=LLMModelDeleteResponse)
async def delete_llm_model(
    model_id: str,
    adapter: LLMModelFirestoreAdapter = Depends(get_firestore_adapter),
    current_user: User = RequireAuth
):
    """Soft delete an LLM model"""
    existing_model = await adapter.get_model(model_id)
    
    if not existing_model or existing_model.deleted_at is not None:
        raise HTTPException(status_code=404, detail="LLM model not found")
    
    await adapter.soft_delete_model(model_id)
    
    return LLMModelDeleteResponse(
        success=True,
        message="LLM model deleted successfully",
        deleted_id=model_id
    )


@router.post("/search", response_model=LLMModelListResponse)
async def search_llm_models(
    search_request: LLMModelSearchRequest,
    adapter: LLMModelFirestoreAdapter = Depends(get_firestore_adapter),
    current_user: User = RequireAuth
):
    """Search LLM models with filters"""
    models, total = await adapter.search_models(
        query=search_request.query,
        family=search_request.family,
        active=search_request.active,
        page=search_request.page,
        page_size=search_request.page_size
    )
    
    return LLMModelListResponse(
        success=True,
        message="LLM models search completed successfully",
        data=models,
        total=total,
        page=search_request.page,
        page_size=search_request.page_size
    )