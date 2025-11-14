"""
Reference lists command handlers.

This module contains commands and command handlers for reference lists operations
following the hexagonal architecture pattern.
"""

from dataclasses import dataclass
from typing import List

from domain.models.reference_lists import BusinessUnit, Solution
from domain.ports.reference_lists_ports import IReferenceListsRepository


@dataclass
class UpdateBusinessUnitsCommand:
    """Command to update business units list."""
    business_units: List[BusinessUnit]
    updated_by: str


@dataclass
class UpdateSolutionsCommand:
    """Command to update solutions list."""
    solutions: List[Solution]
    updated_by: str


class ReferenceListsCommandHandler:
    """Handler for reference lists related commands."""

    def __init__(self, reference_lists_repository: IReferenceListsRepository):
        """
        Initialize command handler.

        Args:
            reference_lists_repository: Reference lists repository for data operations
        """
        self.reference_lists_repository = reference_lists_repository

    async def handle_update_business_units(self, command: UpdateBusinessUnitsCommand) -> bool:
        """
        Handle business units update command.

        Args:
            command: Update business units command

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
            Exception: If update operation fails
        """
        # Validate business units
        self._validate_business_units(command.business_units)

        # Update business units through repository
        success = await self.reference_lists_repository.update_business_units(command.business_units)

        if not success:
            raise Exception("Failed to update business units in repository")

        return success

    async def handle_update_solutions(self, command: UpdateSolutionsCommand) -> bool:
        """
        Handle solutions update command.

        Args:
            command: Update solutions command

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
            Exception: If update operation fails
        """
        # Validate solutions
        await self._validate_solutions(command.solutions)

        # Update solutions through repository
        success = await self.reference_lists_repository.update_solutions(command.solutions)

        if not success:
            raise Exception("Failed to update solutions in repository")

        return success

    def _validate_business_units(self, business_units: List[BusinessUnit]) -> None:
        """
        Validate business units data.

        Args:
            business_units: List of business units to validate

        Raises:
            ValueError: If validation fails
        """
        if not business_units:
            raise ValueError("Business units list cannot be empty")

        seen_codes = set()
        for bu in business_units:
            # Check required fields
            if not bu.bu_code or not bu.bu_code.strip():
                raise ValueError("Business unit code is required and cannot be empty")

            if not bu.name or not bu.name.strip():
                raise ValueError("Business unit name is required and cannot be empty")

            # Check for duplicates
            if bu.bu_code in seen_codes:
                raise ValueError(f"Duplicate business unit code found: {bu.bu_code}")
            seen_codes.add(bu.bu_code)

            # Validate code format (alphanumeric and underscores only)
            if not bu.bu_code.replace('_', '').isalnum():
                raise ValueError(f"Business unit code must be alphanumeric (underscores allowed): {bu.bu_code}")

    async def _validate_solutions(self, solutions: List[Solution]) -> None:
        """
        Validate solutions data.

        Args:
            solutions: List of solutions to validate

        Raises:
            ValueError: If validation fails
        """
        if not solutions:
            raise ValueError("Solutions list cannot be empty")

        # Get current business units to validate bu_code references
        business_units = await self.reference_lists_repository.get_business_units()
        valid_bu_codes = {bu.bu_code for bu in business_units}

        seen_solution_ids = set()
        seen_codes = set()

        for solution in solutions:
            # Check required fields
            if not solution.solution_id or not solution.solution_id.strip():
                raise ValueError("Solution ID is required and cannot be empty")

            if not solution.code or not solution.code.strip():
                raise ValueError("Solution code is required and cannot be empty")

            if not solution.name or not solution.name.strip():
                raise ValueError("Solution name is required and cannot be empty")

            if not solution.bu_code or not solution.bu_code.strip():
                raise ValueError("Business unit code is required and cannot be empty")

            # Check for duplicate solution IDs
            if solution.solution_id in seen_solution_ids:
                raise ValueError(f"Duplicate solution ID found: {solution.solution_id}")
            seen_solution_ids.add(solution.solution_id)

            # Check for duplicate solution codes
            if solution.code in seen_codes:
                raise ValueError(f"Duplicate solution code found: {solution.code}")
            seen_codes.add(solution.code)

            # Validate business unit code exists
            if solution.bu_code not in valid_bu_codes:
                raise ValueError(f"Invalid business unit code: {solution.bu_code}")

            # Validate code format (alphanumeric and underscores only)
            if not solution.code.replace('_', '').isalnum():
                raise ValueError(f"Solution code must be alphanumeric (underscores allowed): {solution.code}")