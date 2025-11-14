from typing import Optional
from datetime import datetime

from contracts.logging_contracts import ILoggingRepository, ILoggingConfigurationRepository
from models.logging_models import (
    LogSearchCriteria, 
    LogSearchResult, 
    LogConfiguration, 
    LogAnalytics,
    LogLevel
)


class LoggingService:
    """Application service for logging operations"""
    
    def __init__(
        self, 
        logging_repository: ILoggingRepository,
        config_repository: ILoggingConfigurationRepository
    ):
        self._logging_repository = logging_repository
        self._config_repository = config_repository
    
    async def search_logs(
        self,
        app_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100,
        query: Optional[str] = None
    ) -> LogSearchResult:
        """Search logs for an application"""
        
        # Validate app_id is required and not empty
        if not app_id or not app_id.strip():
            raise ValueError("app_id is required and cannot be empty")
        
        # Parse datetime strings
        parsed_start_time = None
        parsed_end_time = None
        
        if start_time:
            try:
                parsed_start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(f"Invalid start_time format: {start_time}")
        
        if end_time:
            try:
                parsed_end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(f"Invalid end_time format: {end_time}")
        
        # Parse log level
        parsed_level = None
        if level:
            try:
                parsed_level = LogLevel(level.upper())
            except ValueError:
                raise ValueError(f"Invalid log level: {level}")
        
        # Validate limit
        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        
        # Create search criteria
        criteria = LogSearchCriteria(
            app_id=app_id,
            start_time=parsed_start_time,
            end_time=parsed_end_time,
            level=parsed_level,
            limit=limit,
            query=query
        )
        
        # Execute search
        return await self._logging_repository.search_logs(criteria)
    
    async def get_log_analytics(self, app_id: str) -> LogAnalytics:
        """Get log analytics for an application"""
        
        # Validate app_id is required and not empty
        if not app_id or not app_id.strip():
            raise ValueError("app_id is required and cannot be empty")
        
        return await self._logging_repository.get_log_analytics(app_id)
    
    async def get_log_configuration(self, app_id: str) -> Optional[LogConfiguration]:
        """Get logging configuration for an application"""
        return await self._config_repository.get_configuration(app_id)
    
    async def update_log_configuration(
        self,
        app_id: str,
        log_level: str,
        retention_days: int,
        enabled: bool,
        format: str = "JSON",
        storage_location: str = "Google Cloud Logging"
    ) -> LogConfiguration:
        """Update logging configuration for an application"""
        
        # Validate log level
        try:
            parsed_level = LogLevel(log_level.upper())
        except ValueError:
            raise ValueError(f"Invalid log level: {log_level}")
        
        # Validate retention days
        if retention_days < 1 or retention_days > 365:
            raise ValueError("Retention days must be between 1 and 365")
        
        # Create configuration
        config = LogConfiguration(
            app_id=app_id,
            log_level=parsed_level,
            retention_days=retention_days,
            format=format,
            storage_location=storage_location,
            enabled=enabled
        )
        
        # Update configuration
        return await self._config_repository.update_configuration(config)
    
    async def delete_log_configuration(self, app_id: str) -> bool:
        """Delete logging configuration for an application"""
        return await self._config_repository.delete_configuration(app_id)