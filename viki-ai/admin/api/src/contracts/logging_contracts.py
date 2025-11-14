from abc import ABC, abstractmethod
from typing import Optional
from models.logging_models import (
    LogSearchCriteria, 
    LogSearchResult, 
    LogConfiguration,
    LogAnalytics
)


class ILoggingRepository(ABC):
    """Port for logging repository operations"""
    
    @abstractmethod
    async def search_logs(self, criteria: LogSearchCriteria) -> LogSearchResult:
        """Search logs based on criteria"""
        pass
    
    @abstractmethod
    async def get_log_analytics(self, app_id: str) -> LogAnalytics:
        """Get log analytics for an app"""
        pass


class ILoggingConfigurationRepository(ABC):
    """Port for logging configuration operations"""
    
    @abstractmethod
    async def get_configuration(self, app_id: str) -> Optional[LogConfiguration]:
        """Get logging configuration for an app"""
        pass
    
    @abstractmethod
    async def update_configuration(self, config: LogConfiguration) -> LogConfiguration:
        """Update logging configuration for an app"""
        pass
    
    @abstractmethod
    async def delete_configuration(self, app_id: str) -> bool:
        """Delete logging configuration for an app"""
        pass