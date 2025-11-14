"""
Unit tests for User Profile Commands with Okta integration
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from application.commands.user_profile_commands import (
    UserProfileCommandHandler,
    CreateUserProfileCommand
)
from domain.ports.user_profile_ports import IUserProfileRepositoryPort
from domain.ports.okta_integration_port import IOktaIntegrationPort, OktaAppAssignmentResult
from domain.models.user_profile import UserProfile


@pytest.fixture
def mock_profile_repository():
    """Create mock user profile repository."""
    repository = Mock(spec=IUserProfileRepositoryPort)
    repository.create_profile = AsyncMock(return_value="test@example.com")
    return repository


@pytest.fixture
def mock_okta_integration():
    """Create mock Okta integration."""
    integration = Mock(spec=IOktaIntegrationPort)
    integration.verify_and_grant_access = AsyncMock()
    return integration


@pytest.fixture
def command_handler(mock_profile_repository, mock_okta_integration):
    """Create UserProfileCommandHandler with mocked dependencies."""
    return UserProfileCommandHandler(
        profile_repository=mock_profile_repository,
        okta_integration=mock_okta_integration
    )


@pytest.fixture
def create_command():
    """Create a sample CreateUserProfileCommand."""
    return CreateUserProfileCommand(
        name="Test User",
        email="test@example.com",
        organizations=[{
            "business_unit": "Engineering",
            "solution_code": "ENG"
        }],
        roles=["user", "admin"],
        settings={"extract": {"enabled": True}},
        created_by="admin@example.com"
    )


class TestUserProfileCommandsOkta:
    """Test cases for UserProfileCommandHandler with Okta integration."""

    @pytest.mark.asyncio
    async def test_create_profile_success_with_okta_assignment(
        self,
        command_handler,
        create_command,
        mock_profile_repository,
        mock_okta_integration
    ):
        """Test successful profile creation with successful Okta assignment."""
        # Mock successful Okta assignment
        mock_okta_integration.verify_and_grant_access.return_value = OktaAppAssignmentResult(
            success=True,
            user_id="user123",
            app_id="test-app-id"
        )

        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            mock_settings.OKTA_AUTO_ASSIGN_ENABLED = True
            mock_settings.OKTA_APP_ID = "test-app-id"
            mock_settings_class.return_value = mock_settings

            result = await command_handler.handle_create_profile(create_command)

            # Verify profile was created
            assert result == "test@example.com"
            mock_profile_repository.create_profile.assert_called_once()

            # Verify Okta assignment was attempted
            mock_okta_integration.verify_and_grant_access.assert_called_once_with(
                "test@example.com",
                "test-app-id"
            )

    @pytest.mark.asyncio
    async def test_create_profile_success_okta_disabled(
        self,
        command_handler,
        create_command,
        mock_profile_repository,
        mock_okta_integration
    ):
        """Test successful profile creation with Okta auto-assign disabled."""
        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            mock_settings.OKTA_AUTO_ASSIGN_ENABLED = False
            mock_settings_class.return_value = mock_settings

            result = await command_handler.handle_create_profile(create_command)

            # Verify profile was created
            assert result == "test@example.com"
            mock_profile_repository.create_profile.assert_called_once()

            # Verify Okta assignment was not attempted
            mock_okta_integration.verify_and_grant_access.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_profile_okta_assignment_failure_does_not_fail_creation(
        self,
        command_handler,
        create_command,
        mock_profile_repository,
        mock_okta_integration
    ):
        """Test that Okta assignment failure doesn't fail profile creation."""
        # Mock failed Okta assignment
        mock_okta_integration.verify_and_grant_access.return_value = OktaAppAssignmentResult(
            success=False,
            error_message="User not found in Okta"
        )

        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            mock_settings.OKTA_AUTO_ASSIGN_ENABLED = True
            mock_settings.OKTA_APP_ID = "test-app-id"
            mock_settings_class.return_value = mock_settings

            result = await command_handler.handle_create_profile(create_command)

            # Verify profile creation still succeeded
            assert result == "test@example.com"
            mock_profile_repository.create_profile.assert_called_once()

            # Verify Okta assignment was attempted
            mock_okta_integration.verify_and_grant_access.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_profile_okta_exception_does_not_fail_creation(
        self,
        command_handler,
        create_command,
        mock_profile_repository,
        mock_okta_integration
    ):
        """Test that Okta integration exception doesn't fail profile creation."""
        # Mock Okta integration raising an exception
        mock_okta_integration.verify_and_grant_access.side_effect = Exception("Network error")

        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            mock_settings.OKTA_AUTO_ASSIGN_ENABLED = True
            mock_settings.OKTA_APP_ID = "test-app-id"
            mock_settings_class.return_value = mock_settings

            result = await command_handler.handle_create_profile(create_command)

            # Verify profile creation still succeeded
            assert result == "test@example.com"
            mock_profile_repository.create_profile.assert_called_once()

            # Verify Okta assignment was attempted
            mock_okta_integration.verify_and_grant_access.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_okta_app_assignment_success(self, command_handler):
        """Test successful Okta app assignment handling."""
        mock_result = OktaAppAssignmentResult(
            success=True,
            user_id="user123",
            app_id="test-app-id",
            assignment=Mock()
        )
        mock_result.assignment.id = "assignment123"

        command_handler.okta_integration.verify_and_grant_access = AsyncMock(return_value=mock_result)

        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            mock_settings.OKTA_AUTO_ASSIGN_ENABLED = True
            mock_settings.OKTA_APP_ID = "test-app-id"
            mock_settings_class.return_value = mock_settings

            # Should not raise any exception
            await command_handler._handle_okta_app_assignment("test@example.com", "profile123")

            command_handler.okta_integration.verify_and_grant_access.assert_called_once_with(
                "test@example.com",
                "test-app-id"
            )

    @pytest.mark.asyncio
    async def test_handle_okta_app_assignment_user_already_has_access(self, command_handler):
        """Test Okta app assignment when user already has access."""
        mock_result = OktaAppAssignmentResult(
            success=True,
            user_id="user123",
            app_id="test-app-id",
            assignment=None,  # No assignment means user already had access
            error_message="User already has access"
        )

        command_handler.okta_integration.verify_and_grant_access = AsyncMock(return_value=mock_result)

        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            mock_settings.OKTA_AUTO_ASSIGN_ENABLED = True
            mock_settings.OKTA_APP_ID = "test-app-id"
            mock_settings_class.return_value = mock_settings

            # Should not raise any exception
            await command_handler._handle_okta_app_assignment("test@example.com", "profile123")

            command_handler.okta_integration.verify_and_grant_access.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_okta_app_assignment_failure(self, command_handler):
        """Test Okta app assignment failure handling."""
        mock_result = OktaAppAssignmentResult(
            success=False,
            error_message="User not found in Okta",
            error_code="E0000007"
        )

        command_handler.okta_integration.verify_and_grant_access = AsyncMock(return_value=mock_result)

        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            mock_settings.OKTA_AUTO_ASSIGN_ENABLED = True
            mock_settings.OKTA_APP_ID = "test-app-id"
            mock_settings_class.return_value = mock_settings

            # Should not raise any exception
            await command_handler._handle_okta_app_assignment("test@example.com", "profile123")

            command_handler.okta_integration.verify_and_grant_access.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_okta_app_assignment_missing_settings_attribute(self, command_handler):
        """Test Okta app assignment when settings attribute is missing."""
        with patch('application.commands.user_profile_commands.Settings') as mock_settings_class:
            mock_settings = Mock()
            # Simulate missing OKTA_AUTO_ASSIGN_ENABLED attribute
            del mock_settings.OKTA_AUTO_ASSIGN_ENABLED
            mock_settings_class.return_value = mock_settings

            # Should not raise any exception
            await command_handler._handle_okta_app_assignment("test@example.com", "profile123")

            # Okta integration should not be called
            command_handler.okta_integration.verify_and_grant_access.assert_not_called()