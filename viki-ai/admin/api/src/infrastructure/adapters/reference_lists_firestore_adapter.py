"""
Firestore adapter for Reference Lists operations
"""

from typing import List, Optional, Dict, Any
from google.cloud.firestore import AsyncClient, Query
from datetime import datetime
import os

from viki_shared.utils.logger import getLogger
from domain.models.reference_lists import BusinessUnit, Solution, ReferenceListsData, ReferenceListsArchive
from domain.ports.reference_lists_ports import IReferenceListsRepository
from domain.models.user_context import get_current_user_sync, get_audit_context

logger = getLogger(__name__)


class ReferenceListsFirestoreAdapter(IReferenceListsRepository):
    """Firestore implementation for reference lists repository."""

    def __init__(self, firestore_client: AsyncClient):
        self.client = firestore_client
        self.collection_name = "admin_ref_lists"

    def _get_collection_ref(self):
        """Get reference to the reference lists collection."""
        return self.client.collection(self.collection_name)

    def _get_archive_collection_ref(self, document_id: str):
        """Get reference to the archive subcollection for a reference list document."""
        return (
            self.client
            .collection(self.collection_name)
            .document(document_id)
            .collection("archive")
        )

    async def get_business_units(self) -> List[BusinessUnit]:
        """Fetch all business units from Firestore."""
        try:
            doc_ref = self._get_collection_ref().document("bus")
            doc_snapshot = await doc_ref.get()

            if not doc_snapshot.exists:
                logger.warning("Business units document 'bus' not found in admin_ref_lists collection")
                return []

            data = doc_snapshot.to_dict()
            business_units_data = data.get("business_units", [])

            business_units = []
            for bu_data in business_units_data:
                business_units.append(BusinessUnit.from_dict(bu_data))

            logger.info(f"Retrieved {len(business_units)} business units")
            return business_units

        except Exception as e:
            logger.error(f"Error fetching business units: {str(e)}")
            raise

    async def get_solutions(self, bu_code: Optional[str] = None) -> List[Solution]:
        """Fetch solutions from Firestore, optionally filtered by business unit."""
        try:
            doc_ref = self._get_collection_ref().document("solutions")
            doc_snapshot = await doc_ref.get()

            if not doc_snapshot.exists:
                logger.warning("Solutions document 'solutions' not found in admin_ref_lists collection")
                return []

            data = doc_snapshot.to_dict()
            solutions_data = data.get("solutions", [])

            solutions = []
            for sol_data in solutions_data:
                solution = Solution.from_dict(sol_data)
                # Filter by business unit if specified
                if bu_code is None or solution.bu_code == bu_code:
                    solutions.append(solution)

            logger.info(f"Retrieved {len(solutions)} solutions" + (f" for bu_code '{bu_code}'" if bu_code else ""))
            return solutions

        except Exception as e:
            logger.error(f"Error fetching solutions: {str(e)}")
            raise

    async def get_all_reference_data(self) -> ReferenceListsData:
        """Fetch all reference lists data."""
        try:
            business_units = await self.get_business_units()
            solutions = await self.get_solutions()

            return ReferenceListsData(
                business_units=business_units,
                solutions=solutions
            )

        except Exception as e:
            logger.error(f"Error fetching all reference data: {str(e)}")
            raise

    async def update_business_units(self, business_units: List[BusinessUnit]) -> bool:
        """Update business units in Firestore and archive the previous version."""
        # Get current user from context for audit purposes
        current_user = get_current_user_sync()
        current_user_email = current_user.email if current_user else "system"

        # Get audit context from user context
        audit_context = get_audit_context()

        extra = {
            "operation": "update_business_units",
            "count": len(business_units),
            "collection": self.collection_name,
            "acting_user": current_user_email,
            **audit_context
        }

        logger.info("Updating business units in Firestore", extra=extra)

        try:
            # Get the current business units for archiving
            current_business_units = await self.get_business_units()
            if current_business_units:
                # Archive the current version before updating
                await self.archive_business_units(current_business_units, "update", current_user_email)

            # Update with new data
            doc_ref = self._get_collection_ref().document("bus")
            business_units_data = [bu.to_dict() for bu in business_units]

            await doc_ref.set({
                "business_units": business_units_data,
                "updated_at": datetime.utcnow(),
                "updated_by": current_user_email
            })

            logger.debug(f"Successfully updated {len(business_units)} business units by {current_user_email}", extra=extra)
            return True

        except Exception as e:
            logger.error(f"Error updating business units: {str(e)}")
            return False

    async def update_solutions(self, solutions: List[Solution]) -> bool:
        """Update solutions in Firestore and archive the previous version."""
        # Get current user from context for audit purposes
        current_user = get_current_user_sync()
        current_user_email = current_user.email if current_user else "system"

        # Get audit context from user context
        audit_context = get_audit_context()

        extra = {
            "operation": "update_solutions",
            "count": len(solutions),
            "collection": self.collection_name,
            "acting_user": current_user_email,
            **audit_context
        }

        logger.info("Updating solutions in Firestore", extra=extra)

        try:
            # Get the current solutions for archiving
            current_solutions = await self.get_solutions()
            if current_solutions:
                # Archive the current version before updating
                await self.archive_solutions(current_solutions, "update", current_user_email)

            # Update with new data
            doc_ref = self._get_collection_ref().document("solutions")
            solutions_data = [sol.to_dict() for sol in solutions]

            await doc_ref.set({
                "solutions": solutions_data,
                "updated_at": datetime.utcnow(),
                "updated_by": current_user_email
            })

            logger.debug(f"Successfully updated {len(solutions)} solutions by {current_user_email}", extra=extra)
            return True

        except Exception as e:
            logger.error(f"Error updating solutions: {str(e)}")
            return False

    async def archive_business_units(self, business_units: List[BusinessUnit], action: str, archived_by: str) -> None:
        """Archive business units to the archive subcollection."""
        # Get current user from context for audit purposes
        current_user = get_current_user_sync()
        current_user_email = current_user.email if current_user else archived_by

        # Get audit context from user context
        audit_context = get_audit_context()

        extra = {
            "operation": "archive_business_units",
            "action": action,
            "count": len(business_units),
            "collection": self.collection_name,
            "acting_user": current_user_email,
            **audit_context
        }

        logger.info("Archiving business units", extra=extra)

        # Create archive data
        archive_data = {
            "business_units": [bu.to_dict() for bu in business_units],
            "archive_action": action,
            "archived_at": datetime.utcnow(),
            "archived_by": current_user_email,
            "updated_at": datetime.utcnow(),
            "updated_by": current_user_email
        }

        # Generate unique archive document ID with timestamp
        archive_id = f"{action}_{datetime.utcnow().isoformat()}"

        # Save to archive subcollection
        archive_ref = self._get_archive_collection_ref("bus").document(archive_id)
        await archive_ref.set(archive_data)

        logger.debug(f"Successfully archived {len(business_units)} business units: bus/{archive_id}", extra=extra)

    async def archive_solutions(self, solutions: List[Solution], action: str, archived_by: str) -> None:
        """Archive solutions to the archive subcollection."""
        # Get current user from context for audit purposes
        current_user = get_current_user_sync()
        current_user_email = current_user.email if current_user else archived_by

        # Get audit context from user context
        audit_context = get_audit_context()

        extra = {
            "operation": "archive_solutions",
            "action": action,
            "count": len(solutions),
            "collection": self.collection_name,
            "acting_user": current_user_email,
            **audit_context
        }

        logger.info("Archiving solutions", extra=extra)

        # Create archive data
        archive_data = {
            "solutions": [sol.to_dict() for sol in solutions],
            "archive_action": action,
            "archived_at": datetime.utcnow(),
            "archived_by": current_user_email,
            "updated_at": datetime.utcnow(),
            "updated_by": current_user_email
        }

        # Generate unique archive document ID with timestamp
        archive_id = f"{action}_{datetime.utcnow().isoformat()}"

        # Save to archive subcollection
        archive_ref = self._get_archive_collection_ref("solutions").document(archive_id)
        await archive_ref.set(archive_data)

        logger.debug(f"Successfully archived {len(solutions)} solutions: solutions/{archive_id}", extra=extra)

    async def get_business_units_history(self) -> List[ReferenceListsArchive]:
        """Get the historical versions of business units from the archive."""
        extra = {
            "operation": "get_business_units_history",
            "collection": self.collection_name
        }

        logger.debug("Getting business units history from Firestore", extra=extra)

        # Query the archive subcollection
        archive_query = (
            self._get_archive_collection_ref("bus")
            .order_by("archived_at", direction=Query.DESCENDING)
        )

        docs = await archive_query.get()
        history = []

        for doc in docs:
            history_data = doc.to_dict()
            history_data["archive_id"] = doc.id

            # Convert business units data
            if "business_units" in history_data:
                business_units = [BusinessUnit.from_dict(bu_data) for bu_data in history_data["business_units"]]
                archive_record = ReferenceListsArchive(
                    archive_id=history_data["archive_id"],
                    archive_action=history_data.get("archive_action", ""),
                    archived_at=history_data.get("archived_at", datetime.utcnow()),
                    archived_by=history_data.get("archived_by", ""),
                    business_units=business_units,
                    updated_at=history_data.get("updated_at"),
                    updated_by=history_data.get("updated_by")
                )
                history.append(archive_record)

        logger.debug(f"Successfully retrieved {len(history)} business units historical versions",
                    extra={**extra, "count": len(history)})
        return history

    async def get_solutions_history(self) -> List[ReferenceListsArchive]:
        """Get the historical versions of solutions from the archive."""
        extra = {
            "operation": "get_solutions_history",
            "collection": self.collection_name
        }

        logger.debug("Getting solutions history from Firestore", extra=extra)

        # Query the archive subcollection
        archive_query = (
            self._get_archive_collection_ref("solutions")
            .order_by("archived_at", direction=Query.DESCENDING)
        )

        docs = await archive_query.get()
        history = []

        for doc in docs:
            history_data = doc.to_dict()
            history_data["archive_id"] = doc.id

            # Convert solutions data
            if "solutions" in history_data:
                solutions = [Solution.from_dict(sol_data) for sol_data in history_data["solutions"]]
                archive_record = ReferenceListsArchive(
                    archive_id=history_data["archive_id"],
                    archive_action=history_data.get("archive_action", ""),
                    archived_at=history_data.get("archived_at", datetime.utcnow()),
                    archived_by=history_data.get("archived_by", ""),
                    solutions=solutions,
                    updated_at=history_data.get("updated_at"),
                    updated_by=history_data.get("updated_by")
                )
                history.append(archive_record)

        logger.debug(f"Successfully retrieved {len(history)} solutions historical versions",
                    extra={**extra, "count": len(history)})
        return history