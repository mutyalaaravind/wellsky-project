"""
Domain ports for reference lists operations.

This module defines the interfaces for reference lists repositories,
following the hexagonal architecture pattern.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from domain.models.reference_lists import BusinessUnit, Solution, ReferenceListsData, ReferenceListsArchive


class IReferenceListsRepository(ABC):
    """Interface for reference lists repository operations."""

    @abstractmethod
    async def get_business_units(self) -> List[BusinessUnit]:
        """
        Fetch all business units.

        Returns:
            List of business units

        Raises:
            Exception: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_solutions(self, bu_code: Optional[str] = None) -> List[Solution]:
        """
        Fetch solutions, optionally filtered by business unit.

        Args:
            bu_code: Optional business unit code to filter by

        Returns:
            List of solutions

        Raises:
            Exception: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_all_reference_data(self) -> ReferenceListsData:
        """
        Fetch all reference lists data.

        Returns:
            All reference lists data

        Raises:
            Exception: If retrieval fails
        """
        pass

    @abstractmethod
    async def update_business_units(self, business_units: List[BusinessUnit]) -> bool:
        """
        Update business units list.

        Args:
            business_units: List of business units to update

        Returns:
            True if successful, False otherwise

        Raises:
            Exception: If update fails
        """
        pass

    @abstractmethod
    async def update_solutions(self, solutions: List[Solution]) -> bool:
        """
        Update solutions list.

        Args:
            solutions: List of solutions to update

        Returns:
            True if successful, False otherwise

        Raises:
            Exception: If update fails
        """
        pass

    @abstractmethod
    async def archive_business_units(self, business_units: List[BusinessUnit], action: str, archived_by: str) -> None:
        """
        Archive business units to the archive subcollection.

        Args:
            business_units: List of business units to archive
            action: Action type (e.g., "update", "delete")
            archived_by: User who performed the action

        Raises:
            Exception: If archiving fails
        """
        pass

    @abstractmethod
    async def archive_solutions(self, solutions: List[Solution], action: str, archived_by: str) -> None:
        """
        Archive solutions to the archive subcollection.

        Args:
            solutions: List of solutions to archive
            action: Action type (e.g., "update", "delete")
            archived_by: User who performed the action

        Raises:
            Exception: If archiving fails
        """
        pass

    @abstractmethod
    async def get_business_units_history(self) -> List[ReferenceListsArchive]:
        """
        Get the historical versions of business units from the archive.

        Returns:
            List of archived business unit versions

        Raises:
            Exception: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_solutions_history(self) -> List[ReferenceListsArchive]:
        """
        Get the historical versions of solutions from the archive.

        Returns:
            List of archived solution versions

        Raises:
            Exception: If retrieval fails
        """
        pass