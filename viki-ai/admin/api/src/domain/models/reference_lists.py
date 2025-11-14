"""Domain models for reference lists (business units, solutions, etc.)."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class BusinessUnit:
    """Business unit reference data."""
    bu_code: str
    name: str

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "bu_code": self.bu_code,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BusinessUnit":
        """Create instance from dictionary."""
        return cls(
            bu_code=data.get("bu_code", ""),
            name=data.get("name", "")
        )

    def create_archive_copy(self) -> Dict[str, Any]:
        """Create a copy of the business unit for archiving."""
        archive_data = self.to_dict()
        archive_data["archived_at"] = datetime.utcnow().isoformat()
        return archive_data


@dataclass
class Solution:
    """Solution reference data."""
    solution_id: str
    code: str
    name: str
    description: Optional[str]
    bu_code: str

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "solution_id": self.solution_id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "bu_code": self.bu_code
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Solution":
        """Create instance from dictionary."""
        return cls(
            solution_id=data.get("solution_id", ""),
            code=data.get("code", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            bu_code=data.get("bu_code", "")
        )

    def create_archive_copy(self) -> Dict[str, Any]:
        """Create a copy of the solution for archiving."""
        archive_data = self.to_dict()
        archive_data["archived_at"] = datetime.utcnow().isoformat()
        return archive_data


@dataclass
class ReferenceListsData:
    """Container for all reference lists data."""
    business_units: List[BusinessUnit]
    solutions: List[Solution]

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "business_units": [bu.to_dict() for bu in self.business_units],
            "solutions": [sol.to_dict() for sol in self.solutions]
        }


@dataclass
class ReferenceListsArchive:
    """Archive record for reference lists."""
    archive_id: str
    archive_action: str  # "update", "delete", etc.
    archived_at: datetime
    archived_by: str
    business_units: Optional[List[BusinessUnit]] = None
    solutions: Optional[List[Solution]] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = {
            "archive_id": self.archive_id,
            "archive_action": self.archive_action,
            "archived_at": self.archived_at.isoformat() if isinstance(self.archived_at, datetime) else self.archived_at,
            "archived_by": self.archived_by
        }

        if self.business_units is not None:
            data["business_units"] = [bu.to_dict() for bu in self.business_units]

        if self.solutions is not None:
            data["solutions"] = [sol.to_dict() for sol in self.solutions]

        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at

        if self.updated_by:
            data["updated_by"] = self.updated_by

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferenceListsArchive":
        """Create instance from dictionary."""
        business_units = None
        if "business_units" in data:
            business_units = [BusinessUnit.from_dict(bu_data) for bu_data in data["business_units"]]

        solutions = None
        if "solutions" in data:
            solutions = [Solution.from_dict(sol_data) for sol_data in data["solutions"]]

        archived_at = data.get("archived_at")
        if isinstance(archived_at, str):
            archived_at = datetime.fromisoformat(archived_at.replace('Z', '+00:00').replace('+00:00', ''))

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00').replace('+00:00', ''))

        return cls(
            archive_id=data.get("archive_id", ""),
            archive_action=data.get("archive_action", ""),
            archived_at=archived_at or datetime.utcnow(),
            archived_by=data.get("archived_by", ""),
            business_units=business_units,
            solutions=solutions,
            updated_at=updated_at,
            updated_by=data.get("updated_by")
        )