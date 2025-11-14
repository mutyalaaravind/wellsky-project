from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from usecases.logging_service import LoggingService
from models.logging_models import LogEntry, LogSearchResult, LogConfiguration, LogAnalytics
from dependencies.auth_dependencies import RequireAuth
from models.user import User


router = APIRouter()


# DTOs for the API layer
class LogEntryResponse(BaseModel):
    timestamp: str
    level: str
    message: str
    source: str
    app_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class LogSearchResponse(BaseModel):
    entries: List[LogEntryResponse]
    total_count: int
    has_more: bool
    next_page_token: Optional[str] = None


class LogConfigurationRequest(BaseModel):
    log_level: str
    retention_days: int
    enabled: bool
    format: str = "JSON"
    storage_location: str = "Google Cloud Logging"


class LogConfigurationResponse(BaseModel):
    app_id: str
    log_level: str
    retention_days: int
    format: str
    storage_location: str
    enabled: bool


class LogAnalyticsResponse(BaseModel):
    app_id: str
    total_entries_today: int
    error_count_24h: int
    warning_count_24h: int
    error_rate_24h: float
    storage_size_mb: float


# Dependency injection
def get_logging_service() -> LoggingService:
    from kink import di
    return di[LoggingService]


def _convert_log_entry_to_response(entry: LogEntry) -> LogEntryResponse:
    """Convert domain LogEntry to API response"""
    return LogEntryResponse(
        timestamp=entry.timestamp.isoformat(),
        level=entry.level.value,
        message=entry.message,
        source=entry.source,
        app_id=entry.app_id,
        pipeline_id=entry.pipeline_id,
        metadata=entry.metadata
    )


def _convert_search_result_to_response(result: LogSearchResult) -> LogSearchResponse:
    """Convert domain LogSearchResult to API response"""
    return LogSearchResponse(
        entries=[_convert_log_entry_to_response(entry) for entry in result.entries],
        total_count=result.total_count,
        has_more=result.has_more,
        next_page_token=result.next_page_token
    )


def _convert_config_to_response(config: LogConfiguration) -> LogConfigurationResponse:
    """Convert domain LogConfiguration to API response"""
    return LogConfigurationResponse(
        app_id=config.app_id,
        log_level=config.log_level.value,
        retention_days=config.retention_days,
        format=config.format,
        storage_location=config.storage_location,
        enabled=config.enabled
    )


def _convert_analytics_to_response(analytics: LogAnalytics) -> LogAnalyticsResponse:
    """Convert domain LogAnalytics to API response"""
    return LogAnalyticsResponse(
        app_id=analytics.app_id,
        total_entries_today=analytics.total_entries_today,
        error_count_24h=analytics.error_count_24h,
        warning_count_24h=analytics.warning_count_24h,
        error_rate_24h=analytics.error_rate_24h,
        storage_size_mb=analytics.storage_size_mb
    )


@router.get("/apps/{app_id}/logs", response_model=LogSearchResponse)
async def search_logs(
    app_id: str,
    start_time: Optional[str] = Query(None, description="ISO format datetime"),
    end_time: Optional[str] = Query(None, description="ISO format datetime"),
    level: Optional[str] = Query(None, description="Log level: DEBUG, INFO, WARN, ERROR"),
    limit: int = Query(100, description="Number of log entries to return"),
    query: Optional[str] = Query(None, description="Search query text"),
    logging_service: LoggingService = Depends(get_logging_service),
    current_user: User = RequireAuth
):
    """Search logs for a specific app using Google Cloud Logging"""
    
    # Validate app_id from path parameter
    if not app_id or not app_id.strip():
        raise HTTPException(status_code=400, detail="app_id is required and cannot be empty")
    
    try:
        result = await logging_service.search_logs(
            app_id=app_id,
            start_time=start_time,
            end_time=end_time,
            level=level,
            limit=limit,
            query=query
        )
        return _convert_search_result_to_response(result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/apps/{app_id}/logs/config", response_model=LogConfigurationResponse)
async def get_log_configuration(
    app_id: str,
    logging_service: LoggingService = Depends(get_logging_service),
    current_user: User = RequireAuth
):
    """Get logging configuration for an app"""
    
    try:
        config = await logging_service.get_log_configuration(app_id)
        if not config:
            raise HTTPException(status_code=404, detail="Log configuration not found")
        
        return _convert_config_to_response(config)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/apps/{app_id}/logs/config", response_model=LogConfigurationResponse)
async def update_log_configuration(
    app_id: str,
    config_request: LogConfigurationRequest,
    logging_service: LoggingService = Depends(get_logging_service),
    current_user: User = RequireAuth
):
    """Update logging configuration for an app"""
    
    try:
        config = await logging_service.update_log_configuration(
            app_id=app_id,
            log_level=config_request.log_level,
            retention_days=config_request.retention_days,
            enabled=config_request.enabled,
            format=config_request.format,
            storage_location=config_request.storage_location
        )
        
        return _convert_config_to_response(config)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/apps/{app_id}/logs/config")
async def delete_log_configuration(
    app_id: str,
    logging_service: LoggingService = Depends(get_logging_service),
    current_user: User = RequireAuth
):
    """Delete logging configuration for an app"""
    
    try:
        success = await logging_service.delete_log_configuration(app_id)
        if not success:
            raise HTTPException(status_code=404, detail="Log configuration not found")
        
        return {"message": "Log configuration deleted successfully", "app_id": app_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/apps/{app_id}/logs/analytics", response_model=LogAnalyticsResponse)
async def get_log_analytics(
    app_id: str,
    current_user: User = RequireAuth,
    logging_service: LoggingService = Depends(get_logging_service)
):
    """Get log analytics and statistics for an app"""
    
    # Validate app_id from path parameter
    if not app_id or not app_id.strip():
        raise HTTPException(status_code=400, detail="app_id is required and cannot be empty")
    
    try:
        analytics = await logging_service.get_log_analytics(app_id)
        return _convert_analytics_to_response(analytics)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/apps/{app_id}/logs/export")
async def export_logs(
    app_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    level: Optional[str] = None,
    query: Optional[str] = None,
    current_user: User = RequireAuth
):
    """Export logs for an app to a downloadable format"""
    
    # TODO: Implement actual log export functionality
    # This would involve:
    # 1. Query logs with the provided filters
    # 2. Generate a downloadable file (CSV, JSON)
    # 3. Return a download URL or stream the file
    
    return {
        "message": "Log export initiated",
        "app_id": app_id,
        "export_id": "export-123456",
        "status": "processing",
        "estimated_completion": "2024-01-25T10:35:00Z"
    }