from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4


class BaseAggregate(BaseModel):
    """Base aggregate following DDD patterns"""
    id: str = Field(..., description="Unique identifier")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    events: List = Field(default_factory=list, description="Domain events")

    def mark_event(self, event):
        """Mark domain event for publishing"""
        self.events.append(event)

    def clear_events(self):
        """Clear domain events after publishing"""
        self.events.clear()


class DemoSubjectsConfigAggregate(BaseAggregate):
    """Aggregate for demo subjects configuration"""
    app_id: str = Field(..., description="Application ID this config belongs to")
    label: str = Field(default="Subject", description="Label to use for subjects (e.g., 'Patient', 'Contract')")

    @classmethod
    def create(cls, app_id: str, label: str = "Subject") -> "DemoSubjectsConfigAggregate":
        """Create a new demo subjects configuration"""
        now = datetime.utcnow()
        return cls(
            id=app_id,  # Use app_id as the aggregate ID
            app_id=app_id,
            label=label,
            created_at=now,
            updated_at=now
        )

    def update_label(self, label: str):
        """Update the subject label"""
        self.label = label
        self.updated_at = datetime.utcnow()
        # Could add domain event here if needed


class DemoSubjectAggregate(BaseAggregate):
    """Aggregate for individual demo subject"""
    app_id: str = Field(..., description="Application ID this subject belongs to")
    name: str = Field(..., description="Name of the subject")
    active: bool = Field(default=True, description="Whether the subject is active (false = soft deleted)")

    @classmethod
    def create(cls, app_id: str, name: str) -> "DemoSubjectAggregate":
        """Create a new demo subject"""
        now = datetime.utcnow()
        return cls(
            id=uuid4().hex,  # Use UUID hex format
            app_id=app_id,
            name=name,
            active=True,
            created_at=now,
            updated_at=now
        )

    def update_name(self, name: str):
        """Update the subject name"""
        if not self.active:
            raise ValueError("Cannot update inactive subject")
        self.name = name
        self.updated_at = datetime.utcnow()

    def soft_delete(self):
        """Soft delete the subject by setting active=false"""
        if not self.active:
            raise ValueError("Subject already deleted")
        self.active = False
        self.updated_at = datetime.utcnow()

    @property
    def is_deleted(self) -> bool:
        """Check if subject is deleted"""
        return not self.active