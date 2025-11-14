"""
App Configuration models for Entity Extraction API.

This module provides data models for caching app configurations locally
to eliminate cross-service HTTP dependencies during queue provisioning.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from util.date_utils import now_utc


class AppConfigCache(BaseModel):
    """
    Cached app configuration from PaperGlass API.
    
    Stored in entity_extraction_app_config Firestore collection to eliminate
    cross-service HTTP calls during queue provisioning.
    """
    
    # Core identification
    app_id: str = Field(..., description="Application identifier")
    
    # Configuration metadata
    name: Optional[str] = Field(None, description="Human-readable app name")
    description: Optional[str] = Field(None, description="App description")
    
    # Business context for queue name generation
    business_unit: Optional[str] = Field(None, description="Business unit for token replacement")
    solution_code: Optional[str] = Field(None, description="Solution code for token replacement")
    
    # Full configuration data
    config: Dict[str, Any] = Field(default_factory=dict, description="Complete app configuration")
    
    # Cache metadata
    cached_at: datetime = Field(default_factory=now_utc, description="When this config was cached")
    ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds (default 1 hour)")
    source_version: Optional[str] = Field(None, description="Version identifier from source system")
    
    # Audit fields
    created_at: datetime = Field(default_factory=now_utc, description="When record was created")
    updated_at: datetime = Field(default_factory=now_utc, description="When record was last updated")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def is_cache_expired(self) -> bool:
        """
        Check if the cached configuration has expired.
        
        Returns:
            True if cache has expired, False otherwise
        """
        if not self.cached_at:
            return True
        
        expiry_time = self.cached_at.timestamp() + self.ttl_seconds
        current_time = now_utc().timestamp()
        
        return current_time > expiry_time
    
    def get_token_replacement_values(self) -> Dict[str, str]:
        """
        Get token replacement values for queue name generation.
        
        Returns:
            Dictionary of token names to replacement values
        """
        tokens = {
            "app_id": self.app_id,
        }
        
        if self.business_unit:
            tokens["business_unit"] = self.business_unit
        
        if self.solution_code:
            tokens["solution_code"] = self.solution_code
        
        # Extract additional tokens from config if available
        if self.config:
            accounting = self.config.get("accounting", {})
            if isinstance(accounting, dict):
                if accounting.get("business_unit"):
                    tokens["business_unit"] = accounting["business_unit"]
                if accounting.get("solution_code"):
                    tokens["solution_code"] = accounting["solution_code"]
        
        return tokens
    
    def to_firestore_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary suitable for Firestore storage.
        
        Returns:
            Dictionary representation for Firestore
        """
        data = self.dict()
        
        # Convert datetime objects to ISO strings for Firestore
        for field in ["cached_at", "created_at", "updated_at"]:
            if data.get(field):
                data[field] = data[field].isoformat() if isinstance(data[field], datetime) else data[field]
        
        return data
    
    @classmethod
    def from_firestore_dict(cls, data: Dict[str, Any]) -> "AppConfigCache":
        """
        Create AppConfigCache from Firestore document data.
        
        Args:
            data: Document data from Firestore
            
        Returns:
            AppConfigCache instance
        """
        # Convert ISO string dates back to datetime objects
        for field in ["cached_at", "created_at", "updated_at"]:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # If parsing fails, use current time
                    data[field] = now_utc()
        
        return cls(**data)


class QueueProvisioningConfig(BaseModel):
    """
    Configuration for queue provisioning behavior.
    
    This can be stored as part of the app config or as separate configuration.
    """
    
    # Queue naming configuration
    queue_prefix: Optional[str] = Field(None, description="Custom prefix for queue names")
    priority_variants: List[str] = Field(
        default=["default", "high", "quarantine"], 
        description="Priority variants to create for each queue"
    )
    
    # Provisioning behavior
    auto_provision_enabled: bool = Field(True, description="Whether to auto-provision queues")
    skip_existing_queues: bool = Field(True, description="Skip queues that already exist")
    
    # Error handling
    fail_on_queue_error: bool = Field(False, description="Whether to fail pipeline creation on queue errors")
    retry_attempts: int = Field(3, description="Number of retry attempts for queue creation")
    retry_delay_seconds: int = Field(5, description="Delay between retry attempts")
    
    def get_queue_name_with_priority(self, base_name: str, priority: str = "default") -> str:
        """
        Generate queue name with priority suffix.
        
        Args:
            base_name: Base queue name
            priority: Priority variant (default, high, quarantine)
            
        Returns:
            Queue name with priority suffix
        """
        if priority == "default":
            return base_name
        else:
            return f"{base_name}-{priority}"


class QueueInfo(BaseModel):
    """
    Information about a cloud task queue.
    """
    
    name: str = Field(..., description="Queue name")
    location: str = Field(..., description="GCP location/region")
    project_id: str = Field(..., description="GCP project ID")
    created: bool = Field(False, description="Whether this queue was newly created")
    exists: bool = Field(True, description="Whether the queue exists")
    error: Optional[str] = Field(None, description="Error message if queue operation failed")
    
    @property
    def full_name(self) -> str:
        """Get the full queue resource name."""
        return f"projects/{self.project_id}/locations/{self.location}/queues/{self.name}"


class QueueProvisioningResult(BaseModel):
    """
    Result of queue provisioning operation.
    """
    
    pipeline_id: str = Field(..., description="Pipeline ID that triggered provisioning")
    app_id: str = Field(..., description="App ID associated with pipeline")
    
    # Results
    queues_created: List[QueueInfo] = Field(default_factory=list, description="Queues that were created")
    queues_existing: List[QueueInfo] = Field(default_factory=list, description="Queues that already existed")
    queues_failed: List[QueueInfo] = Field(default_factory=list, description="Queues that failed to create")
    
    # Summary metrics
    total_requested: int = Field(0, description="Total number of queues requested")
    total_created: int = Field(0, description="Total number of queues created")
    total_existing: int = Field(0, description="Total number of queues that already existed")
    total_failed: int = Field(0, description="Total number of queues that failed")
    
    # Timing
    started_at: datetime = Field(default_factory=now_utc, description="When provisioning started")
    completed_at: Optional[datetime] = Field(None, description="When provisioning completed")
    
    # Status
    success: bool = Field(True, description="Whether overall operation was successful")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")
    
    def mark_completed(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """
        Mark the provisioning operation as completed.
        
        Args:
            success: Whether the operation was successful
            error_message: Error message if operation failed
        """
        self.completed_at = now_utc()
        self.success = success
        self.error_message = error_message
        
        # Update summary metrics
        self.total_created = len(self.queues_created)
        self.total_existing = len(self.queues_existing)
        self.total_failed = len(self.queues_failed)
        self.total_requested = self.total_created + self.total_existing + self.total_failed
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get duration of provisioning operation in seconds."""
        if not self.completed_at:
            return None
        return (self.completed_at - self.started_at).total_seconds()