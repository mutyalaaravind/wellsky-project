from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from google.cloud import logging
from google.cloud.logging_v2.types import LogEntry as GCPLogEntry
from google.cloud import firestore

from contracts.logging_contracts import ILoggingRepository, ILoggingConfigurationRepository
from models.logging_models import (
    LogEntry, 
    LogLevel, 
    LogSearchCriteria, 
    LogSearchResult, 
    LogConfiguration,
    LogAnalytics
)


class GoogleCloudLoggingAdapter(ILoggingRepository):
    """Adapter for Google Cloud Logging API"""
    
    def __init__(self, project_id: str = None):
        self.client = logging.Client(project=project_id)
        self.project_id = project_id or self.client.project
    
    def _parse_log_entry(self, entry: GCPLogEntry) -> LogEntry:
        """Convert a Google Cloud Log entry to our domain LogEntry"""
        
        # Extract timestamp
        timestamp = entry.timestamp if entry.timestamp else datetime.utcnow()
        
        # Extract log level
        severity_mapping = {
            'DEFAULT': LogLevel.INFO,
            'DEBUG': LogLevel.DEBUG,
            'INFO': LogLevel.INFO,
            'NOTICE': LogLevel.INFO,
            'WARNING': LogLevel.WARN,
            'ERROR': LogLevel.ERROR,
            'CRITICAL': LogLevel.ERROR,
            'ALERT': LogLevel.ERROR,
            'EMERGENCY': LogLevel.ERROR
        }
        level = severity_mapping.get(entry.severity, LogLevel.INFO)
        
        # Extract message and build comprehensive metadata
        metadata = {}
        app_id = None
        pipeline_id = None
        
        # First, collect all labels into metadata
        if hasattr(entry, 'labels') and entry.labels:
            metadata.update(entry.labels)
            app_id = entry.labels.get('app_id')
            pipeline_id = entry.labels.get('pipeline_id')
        
        # Handle JSON payload
        if hasattr(entry, 'json_payload') and entry.json_payload:
            payload_data = dict(entry.json_payload)
            
            # Extract message from JSON payload, with fallbacks
            if 'message' in payload_data:
                message = str(payload_data['message'])
            else:
                # If no 'message' field, look for common message fields
                message_candidates = ['msg', 'text', 'description', 'error']
                message = None
                for candidate in message_candidates:
                    if candidate in payload_data:
                        message = str(payload_data[candidate])
                        break
                
                # If still no message found, create a summary
                if not message:
                    if len(payload_data) == 1:
                        # If only one field, use its value
                        message = str(list(payload_data.values())[0])
                    else:
                        # Create a summary message
                        message = f"Log entry with {len(payload_data)} fields"
            
            # Extract known fields from payload
            app_id = app_id or payload_data.get('app_id')
            pipeline_id = pipeline_id or payload_data.get('pipeline_id')
            
            # Store the ENTIRE original JSON payload in metadata
            metadata['original_json_payload'] = payload_data
            
        # Handle text payload
        elif hasattr(entry, 'text_payload') and entry.text_payload:
            message = entry.text_payload
            metadata['original_text_payload'] = entry.text_payload
            
        # Handle other payload types
        else:
            message = str(entry.payload) if entry.payload else "Empty log entry"
            if entry.payload:
                metadata['original_payload'] = str(entry.payload)
        
        # Extract source/logger name
        source = entry.log_name.split('/')[-1] if entry.log_name else 'unknown'
        
        if hasattr(entry, 'resource') and entry.resource:
            # Add resource information to metadata
            if hasattr(entry.resource, 'labels') and entry.resource.labels:
                metadata['resource'] = dict(entry.resource.labels)
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=source,
            app_id=app_id,
            pipeline_id=pipeline_id,
            metadata=metadata
        )
    
    def _build_filter(self, criteria: LogSearchCriteria) -> str:
        """Build a filter string for Google Cloud Logging
        
        IMPORTANT: This method ALWAYS enforces app_id filtering to ensure log isolation.
        Logs are filtered by checking both labels.app_id and jsonPayload.app_id fields.
        """
        
        filter_parts = []
        
        # Filter by app_id - ALWAYS REQUIRED - look in both labels and json payload
        if not criteria.app_id:
            raise ValueError("app_id is required for log filtering")
        
        # Escape the app_id to prevent injection issues
        escaped_app_id = criteria.app_id.replace('"', '\\"')
        app_filter = f'(labels.app_id="{escaped_app_id}" OR jsonPayload.app_id="{escaped_app_id}")'
        filter_parts.append(app_filter)
        
        # Filter by time range
        if criteria.start_time:
            filter_parts.append(f'timestamp >= "{criteria.start_time.isoformat()}"')
        
        if criteria.end_time:
            filter_parts.append(f'timestamp <= "{criteria.end_time.isoformat()}"')
        
        # Filter by log level/severity
        if criteria.level:
            level_mapping = {
                LogLevel.DEBUG: 'DEBUG',
                LogLevel.INFO: ['DEFAULT', 'INFO', 'NOTICE'],
                LogLevel.WARN: 'WARNING',
                LogLevel.ERROR: ['ERROR', 'CRITICAL', 'ALERT', 'EMERGENCY']
            }
            
            severities = level_mapping.get(criteria.level)
            if isinstance(severities, list):
                severity_filter = ' OR '.join([f'severity="{s}"' for s in severities])
                filter_parts.append(f'({severity_filter})')
            elif severities:
                filter_parts.append(f'severity="{severities}"')
        
        # Filter by query text - search in both text and json message fields
        if criteria.query:
            # Escape quotes in the query
            escaped_query = criteria.query.replace('"', '\\"')
            query_filter = f'(textPayload=~"{escaped_query}" OR jsonPayload.message=~"{escaped_query}")'
            filter_parts.append(query_filter)
        
        # Default time range if none specified (last 24 hours)
        if not criteria.start_time and not criteria.end_time:
            yesterday = datetime.utcnow() - timedelta(days=1)
            filter_parts.append(f'timestamp >= "{yesterday.isoformat()}Z"')
        
        return ' AND '.join(filter_parts)
    
    async def search_logs(self, criteria: LogSearchCriteria) -> LogSearchResult:
        """Search logs using Google Cloud Logging"""
        
        try:
            # Build the filter
            filter_str = self._build_filter(criteria)
            
            # Set page size (Google Cloud Logging has a max of 1000)
            page_size = min(criteria.limit, 1000)
            
            # Execute the query
            entries_iterator = self.client.list_entries(
                filter_=filter_str,
                page_size=page_size,
                order_by=logging.DESCENDING  # Most recent first
            )
            
            # Convert entries to our domain format
            log_entries = []
            total_processed = 0
            
            for entry in entries_iterator:
                if total_processed >= page_size:
                    break
                
                try:
                    log_entry = self._parse_log_entry(entry)
                    log_entries.append(log_entry)
                    total_processed += 1
                except Exception as e:
                    # Log parsing error but continue
                    print(f"Error parsing log entry: {e}")
                    continue
            
            # Note: Google Cloud Logging doesn't provide exact total counts
            # We estimate based on whether we got a full page
            has_more = len(log_entries) == page_size
            
            return LogSearchResult(
                entries=log_entries,
                total_count=len(log_entries),  # Actual count retrieved
                has_more=has_more,
                next_page_token=None  # Could implement pagination token if needed
            )
            
        except Exception as e:
            # Return empty result with error information
            print(f"Error searching logs: {e}")
            return LogSearchResult(
                entries=[],
                total_count=0,
                has_more=False,
                next_page_token=None
            )
    
    async def get_log_analytics(self, app_id: str) -> LogAnalytics:
        """Get log analytics for an app"""
        
        try:
            # Get logs for the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            # Count total entries today
            total_criteria = LogSearchCriteria(
                app_id=app_id,
                start_time=yesterday,
                limit=1000
            )
            total_filter = self._build_filter(total_criteria)
            
            # Count errors in last 24h
            error_criteria = LogSearchCriteria(
                app_id=app_id,
                start_time=yesterday,
                level=LogLevel.ERROR,
                limit=1000
            )
            error_filter = self._build_filter(error_criteria)
            
            # Count warnings in last 24h
            warning_criteria = LogSearchCriteria(
                app_id=app_id,
                start_time=yesterday,
                level=LogLevel.WARN,
                limit=1000
            )
            warning_filter = self._build_filter(warning_criteria)
            
            # Execute queries (simplified counting - in production, might want to use aggregation)
            total_entries = sum(1 for _ in self.client.list_entries(filter_=total_filter, page_size=1000))
            error_entries = sum(1 for _ in self.client.list_entries(filter_=error_filter, page_size=1000))
            warning_entries = sum(1 for _ in self.client.list_entries(filter_=warning_filter, page_size=1000))
            
            # Calculate error rate
            error_rate = (error_entries / total_entries * 100) if total_entries > 0 else 0
            
            return LogAnalytics(
                app_id=app_id,
                total_entries_today=total_entries,
                error_count_24h=error_entries,
                warning_count_24h=warning_entries,
                error_rate_24h=round(error_rate, 2),
                storage_size_mb=0.0  # Would need separate API call to estimate storage
            )
            
        except Exception as e:
            print(f"Error getting log analytics: {e}")
            return LogAnalytics(
                app_id=app_id,
                total_entries_today=0,
                error_count_24h=0,
                warning_count_24h=0,
                error_rate_24h=0.0,
                storage_size_mb=0.0
            )


class FirestoreLoggingConfigurationAdapter(ILoggingConfigurationRepository):
    """Adapter for logging configuration stored in Firestore"""
    
    def __init__(self, project_id: str = None):
        self.db = firestore.Client(project=project_id)
        self.collection_name = "logging_configurations"
    
    async def get_configuration(self, app_id: str) -> Optional[LogConfiguration]:
        """Get logging configuration for an app"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(app_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return LogConfiguration(**data)
            else:
                # Return default configuration
                return LogConfiguration(
                    app_id=app_id,
                    log_level=LogLevel.INFO,
                    retention_days=30,
                    format="JSON",
                    storage_location="Google Cloud Logging",
                    enabled=True
                )
        except Exception as e:
            print(f"Error getting log configuration: {e}")
            return None
    
    async def update_configuration(self, config: LogConfiguration) -> LogConfiguration:
        """Update logging configuration for an app"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(config.app_id)
            doc_ref.set(config.dict())
            return config
        except Exception as e:
            print(f"Error updating log configuration: {e}")
            raise
    
    async def delete_configuration(self, app_id: str) -> bool:
        """Delete logging configuration for an app"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(app_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting log configuration: {e}")
            return False