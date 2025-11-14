"""
Domain model for UserProfile aggregate
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import Field, validator
from viki_shared.models.common import AggBase


class UserInfo(AggBase):
    """Value object for user information."""
    name: str
    email: str

    class Config:
        use_enum_values = True


class Organization(AggBase):
    """Value object for organization information."""
    business_unit: str
    solution_code: str

    class Config:
        use_enum_values = True


class Authorization(AggBase):
    """Value object for user authorization."""
    roles: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class Settings(AggBase):
    """Value object for user settings."""
    extract: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class Audit(AggBase):
    """Value object for audit information."""
    created_by: str
    created_on: datetime
    modified_by: str
    modified_on: datetime

    class Config:
        use_enum_values = True


class UserProfile(AggBase):
    """UserProfile aggregate root."""

    # Override id to use email as the primary identifier
    id: str
    user: UserInfo
    organizations: List[Organization] = Field(default_factory=list)
    authorization: Authorization
    settings: Settings = Field(default_factory=Settings)
    active: bool = True
    audit: Optional[Audit] = None

    @validator('id', pre=True, always=True)
    def set_id_from_email(cls, v, values):
        """Use email as the ID if not provided."""
        if v is None and 'user' in values and hasattr(values['user'], 'email'):
            return values['user'].email
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert UserProfile to dictionary for storage."""
        data = {
            "id": self.id,
            "user": {
                "name": self.user.name,
                "email": self.user.email
            },
            "organizations": [
                {
                    "business_unit": org.business_unit,
                    "solution_code": org.solution_code
                }
                for org in self.organizations
            ],
            "authorization": {
                "roles": self.authorization.roles
            },
            "settings": {
                "extract": self.settings.extract
            },
            "active": self.active,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "created_by": self.created_by,
            "modified_by": self.modified_by
        }

        # Add audit if present
        if self.audit:
            data["audit"] = {
                "created_by": self.audit.created_by,
                "created_on": self.audit.created_on.isoformat() if isinstance(self.audit.created_on, datetime) else self.audit.created_on,
                "modified_by": self.audit.modified_by,
                "modified_on": self.audit.modified_on.isoformat() if isinstance(self.audit.modified_on, datetime) else self.audit.modified_on
            }

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Create UserProfile from dictionary."""
        # Extract user info
        user_data = data.get("user", {})
        user = UserInfo(
            name=user_data.get("name", ""),
            email=user_data.get("email", data.get("id", ""))
        )

        # Extract organizations
        organizations = [
            Organization(
                business_unit=org.get("business_unit", ""),
                solution_code=org.get("solution_code", "")
            )
            for org in data.get("organizations", [])
        ]

        # Extract authorization
        auth_data = data.get("authorization", {})
        authorization = Authorization(
            roles=auth_data.get("roles", [])
        )

        # Extract settings
        settings_data = data.get("settings", {})
        settings = Settings(
            extract=settings_data.get("extract", {})
        )

        # Extract audit if present
        audit = None
        if "audit" in data:
            audit_data = data["audit"]
            audit = Audit(
                created_by=audit_data.get("created_by", ""),
                created_on=audit_data.get("created_on", datetime.utcnow()),
                modified_by=audit_data.get("modified_by", ""),
                modified_on=audit_data.get("modified_on", datetime.utcnow())
            )

        return cls(
            id=data.get("id", user.email),
            user=user,
            organizations=organizations,
            authorization=authorization,
            settings=settings,
            active=data.get("active", True),
            audit=audit,
            created_at=data.get("created_at", datetime.utcnow()),
            modified_at=data.get("modified_at", datetime.utcnow()),
            created_by=data.get("created_by"),
            modified_by=data.get("modified_by")
        )

    def create_archive_copy(self) -> Dict[str, Any]:
        """Create a copy of the profile for archiving."""
        archive_data = self.to_dict()
        archive_data["archived_at"] = datetime.utcnow().isoformat()
        return archive_data