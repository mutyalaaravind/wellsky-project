"""
App Access Control Service

This service handles filtering of app configurations based on user profile
organizations, implementing additive access control where multiple organizations
grant cumulative access rights.
"""

import logging
from typing import List, Optional
from viki_shared.utils.logger import getLogger

from contracts.paperglass import AppConfigResponse
from domain.models.user_profile import UserProfile, Organization

logger = getLogger(__name__)


class AppAccessService:
    """
    Service for filtering app configurations based on user access rights.

    Implements additive organization-based access control where:
    - Each organization in user profile grants independent access
    - Wildcard (*) values grant access to all items in that dimension
    - Final access is the union of all organization-based access grants
    """

    def filter_apps_by_user_access(
        self,
        apps: List[AppConfigResponse],
        user_profile: Optional[UserProfile]
    ) -> List[AppConfigResponse]:
        """
        Filter app configurations based on user profile organizations.

        Args:
            apps: List of app configurations from PaperGlass API
            user_profile: User profile containing organizations

        Returns:
            List[AppConfigResponse]: Filtered list of apps user has access to
        """
        extra = {
            "operation": "filter_apps_by_user_access",
            "total_apps": len(apps),
            "user_profile_id": user_profile.id if user_profile else None
        }

        # If no user profile, no access
        if not user_profile:
            logger.warning("No user profile provided, denying access to all apps", extra=extra)
            return []

        # If no organizations, no access
        if not user_profile.organizations:
            logger.warning(
                f"User {user_profile.id} has no organizations, denying access to all apps",
                extra={**extra, "user_organizations_count": 0}
            )
            return []

        extra["user_organizations_count"] = len(user_profile.organizations)
        logger.debug(
            f"Filtering {len(apps)} apps for user {user_profile.id} with {len(user_profile.organizations)} organizations",
            extra=extra
        )

        # Filter apps based on user's organizational access
        filtered_apps = []

        for app in apps:
            if self._user_has_access_to_app(app, user_profile.organizations):
                filtered_apps.append(app)

        extra.update({
            "filtered_apps_count": len(filtered_apps),
            "apps_filtered_out": len(apps) - len(filtered_apps)
        })

        logger.debug(
            f"User {user_profile.id} has access to {len(filtered_apps)}/{len(apps)} apps",
            extra=extra
        )

        return filtered_apps

    def _user_has_access_to_app(
        self,
        app: AppConfigResponse,
        user_orgs: List[Organization]
    ) -> bool:
        """
        Check if user has access to a specific app based on their organizations.

        Args:
            app: App configuration to check access for
            user_orgs: User's organizations

        Returns:
            bool: True if user has access, False otherwise
        """
        # Extract app's business unit and solution code from accounting config
        # Handle case where accounting key exists but is None
        accounting_config = app.config.get("accounting") or {}
        app_business_unit = accounting_config.get("business_unit")
        app_solution_code = accounting_config.get("solution_code")

        # Log app details for debugging
        app_extra = {
            "app_id": app.app_id,
            "app_business_unit": app_business_unit,
            "app_solution_code": app_solution_code
        }

        # If app has no accounting info (None or empty string), deny access by default
        if not app_business_unit or not app_solution_code:
            logger.debug(
                f"App {app.app_id} missing accounting info, denying access",
                extra=app_extra
            )
            return False

        # Check if ANY user organization grants access to this app
        for org in user_orgs:
            if self._organization_grants_access_to_app(
                org, app_business_unit, app_solution_code, app_extra
            ):
                logger.debug(
                    f"Organization {org.business_unit}/{org.solution_code} grants access to app {app.app_id}",
                    extra={**app_extra, "granting_org_bu": org.business_unit, "granting_org_sc": org.solution_code}
                )
                return True

        logger.debug(
            f"No organization grants access to app {app.app_id}",
            extra=app_extra
        )
        return False

    def _organization_grants_access_to_app(
        self,
        org: Organization,
        app_business_unit: str,
        app_solution_code: str,
        app_extra: dict
    ) -> bool:
        """
        Check if a single organization grants access to an app.

        Args:
            org: User organization
            app_business_unit: App's business unit
            app_solution_code: App's solution code
            app_extra: Extra logging context

        Returns:
            bool: True if this organization grants access
        """
        # Business unit check: match or user has wildcard
        business_unit_match = (
            org.business_unit == "*" or
            org.business_unit == app_business_unit
        )

        # Solution code check: match or user has wildcard
        solution_code_match = (
            org.solution_code == "*" or
            org.solution_code == app_solution_code
        )

        # Both must match for this organization to grant access
        grants_access = business_unit_match and solution_code_match

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Organization access check: {org.business_unit}/{org.solution_code} -> "
                f"BU match: {business_unit_match}, SC match: {solution_code_match}, "
                f"Grants access: {grants_access}",
                extra={
                    **app_extra,
                    "org_business_unit": org.business_unit,
                    "org_solution_code": org.solution_code,
                    "business_unit_match": business_unit_match,
                    "solution_code_match": solution_code_match,
                    "grants_access": grants_access
                }
            )

        return grants_access

    def get_user_access_summary(self, user_profile: Optional[UserProfile]) -> dict:
        """
        Get a summary of user's access rights for debugging/logging.

        Args:
            user_profile: User profile to analyze

        Returns:
            dict: Summary of access rights
        """
        if not user_profile or not user_profile.organizations:
            return {"access_type": "none", "organizations": []}

        # Check for super admin access
        has_super_admin = any(
            org.business_unit == "*" and org.solution_code == "*"
            for org in user_profile.organizations
        )

        if has_super_admin:
            return {
                "access_type": "super_admin",
                "organizations": len(user_profile.organizations),
                "description": "Full access to all apps"
            }

        # Analyze specific access patterns
        business_units = set()
        solution_codes = set()
        wildcard_patterns = []

        for org in user_profile.organizations:
            business_units.add(org.business_unit)
            solution_codes.add(org.solution_code)

            if org.business_unit == "*" or org.solution_code == "*":
                wildcard_patterns.append(f"{org.business_unit}/{org.solution_code}")

        return {
            "access_type": "restricted",
            "organizations": len(user_profile.organizations),
            "unique_business_units": len(business_units),
            "unique_solution_codes": len(solution_codes),
            "wildcard_patterns": wildcard_patterns,
            "description": f"Access to {len(user_profile.organizations)} organization combinations"
        }


# Global service instance
_app_access_service = AppAccessService()

def get_app_access_service() -> AppAccessService:
    """
    Get the global app access service instance.

    Returns:
        AppAccessService: The service instance
    """
    return _app_access_service