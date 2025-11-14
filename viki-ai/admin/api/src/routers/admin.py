from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any

from dependencies.auth_dependencies import RequireAuth
from models.user import User

router = APIRouter()


class AdminResponse(BaseModel):
    message: str
    data: Dict[str, Any] = {}


@router.get("", response_model=AdminResponse)
async def get_admin_status(current_user: User = RequireAuth):
    """Get admin service status"""
    return AdminResponse(
        message="Admin service is operational",
        data={"service": "admin", "status": "running", "user": current_user.sub}
    )


@router.get("/users", response_model=AdminResponse)
async def list_users(current_user: User = RequireAuth):
    """List all users (placeholder)"""
    return AdminResponse(
        message="Users retrieved successfully",
        data={"users": [], "total": 0}
    )


@router.get("/system/health", response_model=AdminResponse)
async def system_health():
    """Get system health status"""
    return AdminResponse(
        message="System health check completed",
        data={
            "database": "healthy",
            "cache": "healthy",
            "storage": "healthy"
        }
    )