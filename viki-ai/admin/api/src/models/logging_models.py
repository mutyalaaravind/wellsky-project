from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class LogEntry(BaseModel):
    """Domain model for a log entry"""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    app_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LogSearchCriteria(BaseModel):
    """Domain model for log search criteria"""
    app_id: str = Field(min_length=1, description="Application ID - required for filtering logs")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    level: Optional[LogLevel] = None
    limit: int = Field(default=100, ge=1, le=1000)
    query: Optional[str] = None
    

class LogSearchResult(BaseModel):
    """Domain model for log search results"""
    entries: List[LogEntry]
    total_count: int
    has_more: bool
    next_page_token: Optional[str] = None


class LogConfiguration(BaseModel):
    """Domain model for logging configuration"""
    app_id: str
    log_level: LogLevel
    retention_days: int = Field(ge=1, le=365)
    format: str = "JSON"
    storage_location: str = "Google Cloud Logging"
    enabled: bool = True


class LogAnalytics(BaseModel):
    """Domain model for log analytics"""
    app_id: str
    total_entries_today: int
    error_count_24h: int
    warning_count_24h: int
    error_rate_24h: float
    storage_size_mb: float
