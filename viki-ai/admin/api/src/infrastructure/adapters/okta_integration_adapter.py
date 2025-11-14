"""
Okta Integration Adapter - Infrastructure implementation of Okta operations
"""

import aiohttp
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from domain.ports.okta_integration_port import (
    IOktaIntegrationPort,
    OktaUser,
    AppAssignment,
    OktaAppAssignmentResult,
    OktaUserValidationResult,
    OktaAppRemovalResult,
    OktaGroupAssignmentResult
)
from settings import Settings

logger = logging.getLogger(__name__)


class OktaAPIException(Exception):
    """Custom exception for Okta API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class OktaIntegrationAdapter(IOktaIntegrationPort):
    """
    Adapter implementation for Okta integration.
    Handles all communication with Okta API.
    """

    def __init__(self, settings: Settings):
        """
        Initialize Okta integration adapter.

        Args:
            settings: Application settings containing Okta configuration
        """
        self.settings = settings
        self.base_url = f"https://{settings.OKTA_DOMAIN}"
        self.api_token = settings.OKTA_API_TOKEN
        self.app_id = settings.OKTA_APP_ID
        self.auto_assign_enabled = settings.OKTA_AUTO_ASSIGN_ENABLED

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"SSWS {self.api_token}"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(aiohttp.ClientError)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make an HTTP request to Okta API with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            json_data: JSON body for POST/PUT requests
            params: Query parameters

        Returns:
            Response data as dictionary or None

        Raises:
            OktaAPIException: On API errors
        """
        url = f"{self.base_url}/api/v1{endpoint}"

        logger.debug(f"Making {method} request to {url}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json_data,
                    params=params
                ) as response:
                    response_text = await response.text()

                    if response.status == 404:
                        return None

                    if response.status >= 400:
                        error_data = None
                        try:
                            import json
                            error_data = json.loads(response_text)
                            error_message = error_data.get("errorSummary", response_text)
                            error_code = error_data.get("errorCode")
                        except:
                            error_message = response_text
                            error_code = None

                        raise OktaAPIException(
                            message=error_message,
                            status_code=response.status,
                            error_code=error_code
                        )

                    if response_text and response.status != 204:
                        import json
                        return json.loads(response_text)

                    return {}

            except aiohttp.ClientError as e:
                logger.error(f"HTTP client error: {str(e)}")
                raise
            except OktaAPIException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Okta API request: {str(e)}")
                raise OktaAPIException(f"Unexpected error: {str(e)}")

    async def get_user_by_email(self, email: str) -> Optional[OktaUser]:
        """
        Get Okta user by email address.

        Args:
            email: User's email address

        Returns:
            OktaUser if found, None otherwise
        """
        try:
            # Search for user by email
            response = await self._make_request(
                method="GET",
                endpoint="/users",
                params={"q": email, "limit": 1}
            )

            if not response or len(response) == 0:
                logger.info(f"No Okta user found for email: {email}")
                return None

            user_data = response[0]

            return OktaUser(
                id=user_data["id"],
                email=user_data["profile"].get("email", email),
                login=user_data["profile"].get("login", email),
                first_name=user_data["profile"].get("firstName"),
                last_name=user_data["profile"].get("lastName"),
                status=user_data.get("status", "ACTIVE"),
                created=self._parse_datetime(user_data.get("created")),
                activated=self._parse_datetime(user_data.get("activated")),
                status_changed=self._parse_datetime(user_data.get("statusChanged")),
                last_login=self._parse_datetime(user_data.get("lastLogin"))
            )

        except OktaAPIException as e:
            logger.error(f"Okta API error getting user {email}: {e.message}")
            return None
        except Exception as e:
            logger.error(f"Error getting Okta user {email}: {str(e)}")
            return None

    async def check_user_app_assignment(self, email: str, app_id: str) -> bool:
        """
        Check if a user has access to a specific application.

        Args:
            email: User's email address
            app_id: Okta application ID

        Returns:
            True if user has access, False otherwise
        """
        try:
            # First get the user
            user = await self.get_user_by_email(email)
            if not user:
                logger.info(f"User {email} not found in Okta")
                return False

            # Check specific app assignment
            response = await self._make_request(
                method="GET",
                endpoint=f"/apps/{app_id}/users/{user.id}"
            )

            return response is not None

        except OktaAPIException as e:
            if e.status_code == 404:
                return False
            logger.error(f"Error checking app assignment for {email}: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Error checking app assignment for {email}: {str(e)}")
            return False

    async def assign_app_to_user(self, email: str, app_id: str) -> OktaAppAssignmentResult:
        """
        Assign an application to a user.

        Args:
            email: User's email address
            app_id: Okta application ID to assign

        Returns:
            OktaAppAssignmentResult with assignment details or error
        """
        try:
            # Get user first
            user = await self.get_user_by_email(email)
            if not user:
                return OktaAppAssignmentResult(
                    success=False,
                    error_message=f"User {email} not found in Okta"
                )

            # Assignment payload
            assignment_data = {
                "id": user.id,
                "scope": "USER",
                "credentials": {
                    "userName": email
                }
            }

            # Assign app to user
            response = await self._make_request(
                method="POST",
                endpoint=f"/apps/{app_id}/users",
                json_data=assignment_data
            )

            if response:
                assignment = AppAssignment(
                    id=response.get("id"),
                    user_id=user.id,
                    app_id=app_id,
                    app_name=response.get("appName", ""),
                    status=response.get("status", "ACTIVE"),
                    created=self._parse_datetime(response.get("created")),
                    credentials=response.get("credentials"),
                    profile=response.get("profile")
                )

                logger.info(f"Successfully assigned app {app_id} to user {email}")
                return OktaAppAssignmentResult(
                    success=True,
                    user_id=user.id,
                    app_id=app_id,
                    assignment=assignment
                )

            return OktaAppAssignmentResult(
                success=False,
                user_id=user.id,
                app_id=app_id,
                error_message="Assignment created but no response received"
            )

        except OktaAPIException as e:
            logger.error(f"Okta API error assigning app to {email}: {e.message}")
            return OktaAppAssignmentResult(
                success=False,
                error_message=e.message,
                error_code=e.error_code
            )
        except Exception as e:
            logger.error(f"Error assigning app to {email}: {str(e)}")
            return OktaAppAssignmentResult(
                success=False,
                error_message=str(e)
            )

    async def list_user_apps(self, email: str) -> List[AppAssignment]:
        """
        List all applications assigned to a user.

        Args:
            email: User's email address

        Returns:
            List of AppAssignment objects
        """
        try:
            # Get user first
            user = await self.get_user_by_email(email)
            if not user:
                logger.info(f"User {email} not found in Okta")
                return []

            # Get user's app links
            response = await self._make_request(
                method="GET",
                endpoint=f"/users/{user.id}/appLinks"
            )

            if not response:
                return []

            assignments = []
            for app_link in response:
                # For each app link, we might need to get more details
                assignment = AppAssignment(
                    id=app_link.get("id"),
                    user_id=user.id,
                    app_id=app_link.get("appInstanceId"),
                    app_name=app_link.get("label", ""),
                    status="ACTIVE",
                    created=datetime.utcnow()  # App links don't have created date
                )
                assignments.append(assignment)

            return assignments

        except OktaAPIException as e:
            logger.error(f"Error listing apps for {email}: {e.message}")
            return []
        except Exception as e:
            logger.error(f"Error listing apps for {email}: {str(e)}")
            return []

    async def verify_and_grant_access(self, email: str, app_id: str) -> OktaAppAssignmentResult:
        """
        Verify if user has app access and grant it if not.
        This is a convenience method that combines check and assign operations.

        Args:
            email: User's email address
            app_id: Okta application ID

        Returns:
            OktaAppAssignmentResult with operation outcome
        """
        try:
            # Check if auto-assign is enabled
            if not self.auto_assign_enabled:
                logger.info("Okta auto-assign is disabled, skipping assignment check")
                return OktaAppAssignmentResult(
                    success=True,
                    error_message="Auto-assign disabled"
                )

            # First check if user exists
            user = await self.get_user_by_email(email)
            if not user:
                return OktaAppAssignmentResult(
                    success=False,
                    error_message=f"User {email} not found in Okta"
                )

            # Check if already assigned
            has_access = await self.check_user_app_assignment(email, app_id)

            if has_access:
                logger.info(f"User {email} already has access to app {app_id}")
                return OktaAppAssignmentResult(
                    success=True,
                    user_id=user.id,
                    app_id=app_id,
                    error_message="User already has access"
                )

            # Grant access
            logger.info(f"Granting app {app_id} access to user {email}")
            return await self.assign_app_to_user(email, app_id)

        except Exception as e:
            logger.error(f"Error in verify_and_grant_access for {email}: {str(e)}")
            return OktaAppAssignmentResult(
                success=False,
                error_message=str(e)
            )

    async def validate_user_exists(self, email: str) -> OktaUserValidationResult:
        """
        Validate that a user exists in Okta before attempting operations.

        Args:
            email: User's email address

        Returns:
            OktaUserValidationResult with validation outcome
        """
        try:
            user = await self.get_user_by_email(email)

            if user:
                return OktaUserValidationResult(
                    user_exists=True,
                    user_id=user.id
                )
            else:
                return OktaUserValidationResult(
                    user_exists=False,
                    error_message=f"User {email} not found in Okta"
                )

        except Exception as e:
            logger.error(f"Error validating user existence for {email}: {str(e)}")
            return OktaUserValidationResult(
                user_exists=False,
                error_message=str(e)
            )

    async def remove_app_assignment(self, email: str, app_id: str) -> OktaAppRemovalResult:
        """
        Remove an application assignment from a user.

        Args:
            email: User's email address
            app_id: Okta application ID to remove

        Returns:
            OktaAppRemovalResult with removal details or error
        """
        try:
            # Get user first
            user = await self.get_user_by_email(email)
            if not user:
                return OktaAppRemovalResult(
                    success=False,
                    error_message=f"User {email} not found in Okta"
                )

            # Remove app assignment
            response = await self._make_request(
                method="DELETE",
                endpoint=f"/apps/{app_id}/users/{user.id}"
            )

            logger.info(f"Successfully removed app {app_id} assignment from user {email}")
            return OktaAppRemovalResult(
                success=True,
                user_id=user.id,
                app_id=app_id
            )

        except OktaAPIException as e:
            if e.status_code == 404:
                # User was not assigned to the app, consider this a success
                logger.info(f"User {email} was not assigned to app {app_id}, no removal needed")
                return OktaAppRemovalResult(
                    success=True,
                    app_id=app_id,
                    error_message="User was not assigned to app"
                )
            else:
                logger.error(f"Okta API error removing app assignment for {email}: {e.message}")
                return OktaAppRemovalResult(
                    success=False,
                    error_message=e.message,
                    error_code=e.error_code
                )
        except Exception as e:
            logger.error(f"Error removing app assignment for {email}: {str(e)}")
            return OktaAppRemovalResult(
                success=False,
                error_message=str(e)
            )

    async def assign_user_to_group(self, email: str, group_id: str) -> OktaGroupAssignmentResult:
        """
        Assign a user to an Okta group.

        Args:
            email: User's email address
            group_id: Okta group ID

        Returns:
            OktaGroupAssignmentResult with assignment details or error
        """
        try:
            # Get user first
            user = await self.get_user_by_email(email)
            if not user:
                return OktaGroupAssignmentResult(
                    success=False,
                    operation="assigned",
                    error_message=f"User {email} not found in Okta"
                )

            # Add user to group
            response = await self._make_request(
                method="PUT",
                endpoint=f"/groups/{group_id}/users/{user.id}"
            )

            logger.info(f"Successfully assigned user {email} to group {group_id}")
            return OktaGroupAssignmentResult(
                success=True,
                user_id=user.id,
                group_id=group_id,
                operation="assigned"
            )

        except OktaAPIException as e:
            if e.status_code == 409:
                # User is already in the group, consider this a success
                logger.info(f"User {email} is already in group {group_id}")
                return OktaGroupAssignmentResult(
                    success=True,
                    group_id=group_id,
                    operation="assigned",
                    error_message="User already in group"
                )
            else:
                logger.error(f"Okta API error assigning user to group for {email}: {e.message}")
                return OktaGroupAssignmentResult(
                    success=False,
                    operation="assigned",
                    error_message=e.message,
                    error_code=e.error_code
                )
        except Exception as e:
            logger.error(f"Error assigning user to group for {email}: {str(e)}")
            return OktaGroupAssignmentResult(
                success=False,
                operation="assigned",
                error_message=str(e)
            )

    async def remove_user_from_group(self, email: str, group_id: str) -> OktaGroupAssignmentResult:
        """
        Remove a user from an Okta group.

        Args:
            email: User's email address
            group_id: Okta group ID

        Returns:
            OktaGroupAssignmentResult with removal details or error
        """
        try:
            # Get user first
            user = await self.get_user_by_email(email)
            if not user:
                return OktaGroupAssignmentResult(
                    success=False,
                    operation="removed",
                    error_message=f"User {email} not found in Okta"
                )

            # Remove user from group
            response = await self._make_request(
                method="DELETE",
                endpoint=f"/groups/{group_id}/users/{user.id}"
            )

            logger.info(f"Successfully removed user {email} from group {group_id}")
            return OktaGroupAssignmentResult(
                success=True,
                user_id=user.id,
                group_id=group_id,
                operation="removed"
            )

        except OktaAPIException as e:
            if e.status_code == 404:
                # User was not in the group, consider this a success
                logger.info(f"User {email} was not in group {group_id}, no removal needed")
                return OktaGroupAssignmentResult(
                    success=True,
                    group_id=group_id,
                    operation="removed",
                    error_message="User was not in group"
                )
            else:
                logger.error(f"Okta API error removing user from group for {email}: {e.message}")
                return OktaGroupAssignmentResult(
                    success=False,
                    operation="removed",
                    error_message=e.message,
                    error_code=e.error_code
                )
        except Exception as e:
            logger.error(f"Error removing user from group for {email}: {str(e)}")
            return OktaGroupAssignmentResult(
                success=False,
                operation="removed",
                error_message=str(e)
            )

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse ISO format datetime string to datetime object.

        Args:
            date_str: ISO format datetime string

        Returns:
            datetime object or None
        """
        if not date_str:
            return None

        try:
            # Remove timezone info for simplicity
            if 'T' in date_str:
                date_str = date_str.split('Z')[0].split('+')[0]
                return datetime.fromisoformat(date_str)
            return None
        except Exception as e:
            logger.debug(f"Error parsing datetime {date_str}: {str(e)}")
            return None