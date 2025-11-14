"""
Unit tests for Okta Integration Adapter
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import aiohttp
import json

from infrastructure.adapters.okta_integration_adapter import OktaIntegrationAdapter, OktaAPIException
from domain.ports.okta_integration_port import OktaUser, AppAssignment, OktaAppAssignmentResult
from settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.OKTA_DOMAIN = "test-domain.okta.com"
    settings.OKTA_API_TOKEN = "test-api-token"
    settings.OKTA_APP_ID = "test-app-id"
    settings.OKTA_AUTO_ASSIGN_ENABLED = True
    return settings


@pytest.fixture
def okta_adapter(mock_settings):
    """Create OktaIntegrationAdapter instance for testing."""
    return OktaIntegrationAdapter(mock_settings)


@pytest.fixture
def mock_user_response():
    """Mock Okta user API response."""
    return [{
        "id": "user123",
        "profile": {
            "email": "test@example.com",
            "login": "test@example.com",
            "firstName": "Test",
            "lastName": "User"
        },
        "status": "ACTIVE",
        "created": "2023-01-01T12:00:00.000Z",
        "activated": "2023-01-01T12:00:00.000Z"
    }]


@pytest.fixture
def mock_assignment_response():
    """Mock Okta app assignment API response."""
    return {
        "id": "assignment123",
        "appName": "Test App",
        "status": "ACTIVE",
        "created": "2023-01-01T12:00:00.000Z",
        "credentials": {
            "userName": "test@example.com"
        },
        "profile": {}
    }


class TestOktaIntegrationAdapter:
    """Test cases for OktaIntegrationAdapter."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, okta_adapter, mock_user_response):
        """Test successful user retrieval by email."""
        with patch.object(okta_adapter, '_make_request', return_value=mock_user_response) as mock_request:
            result = await okta_adapter.get_user_by_email("test@example.com")

            assert result is not None
            assert isinstance(result, OktaUser)
            assert result.email == "test@example.com"
            assert result.id == "user123"
            assert result.first_name == "Test"
            assert result.last_name == "User"
            assert result.status == "ACTIVE"

            mock_request.assert_called_once_with(
                method="GET",
                endpoint="/users",
                params={"q": "test@example.com", "limit": 1}
            )

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, okta_adapter):
        """Test user not found scenario."""
        with patch.object(okta_adapter, '_make_request', return_value=[]) as mock_request:
            result = await okta_adapter.get_user_by_email("notfound@example.com")

            assert result is None
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_api_error(self, okta_adapter):
        """Test API error handling."""
        with patch.object(okta_adapter, '_make_request', side_effect=OktaAPIException("API Error")):
            result = await okta_adapter.get_user_by_email("test@example.com")

            assert result is None

    @pytest.mark.asyncio
    async def test_check_user_app_assignment_has_access(self, okta_adapter, mock_user_response):
        """Test checking user app assignment when user has access."""
        mock_assignment = {"id": "assignment123"}

        with patch.object(okta_adapter, 'get_user_by_email') as mock_get_user:
            mock_get_user.return_value = OktaUser(
                id="user123",
                email="test@example.com",
                login="test@example.com"
            )

            with patch.object(okta_adapter, '_make_request', return_value=mock_assignment):
                result = await okta_adapter.check_user_app_assignment("test@example.com", "test-app-id")

                assert result is True

    @pytest.mark.asyncio
    async def test_check_user_app_assignment_no_access(self, okta_adapter, mock_user_response):
        """Test checking user app assignment when user has no access."""
        with patch.object(okta_adapter, 'get_user_by_email') as mock_get_user:
            mock_get_user.return_value = OktaUser(
                id="user123",
                email="test@example.com",
                login="test@example.com"
            )

            with patch.object(okta_adapter, '_make_request', return_value=None):
                result = await okta_adapter.check_user_app_assignment("test@example.com", "test-app-id")

                assert result is False

    @pytest.mark.asyncio
    async def test_check_user_app_assignment_user_not_found(self, okta_adapter):
        """Test checking user app assignment when user doesn't exist."""
        with patch.object(okta_adapter, 'get_user_by_email', return_value=None):
            result = await okta_adapter.check_user_app_assignment("notfound@example.com", "test-app-id")

            assert result is False

    @pytest.mark.asyncio
    async def test_assign_app_to_user_success(self, okta_adapter, mock_assignment_response):
        """Test successful app assignment to user."""
        mock_user = OktaUser(
            id="user123",
            email="test@example.com",
            login="test@example.com"
        )

        with patch.object(okta_adapter, 'get_user_by_email', return_value=mock_user):
            with patch.object(okta_adapter, '_make_request', return_value=mock_assignment_response):
                result = await okta_adapter.assign_app_to_user("test@example.com", "test-app-id")

                assert result.success is True
                assert result.user_id == "user123"
                assert result.app_id == "test-app-id"
                assert result.assignment is not None
                assert result.assignment.id == "assignment123"

    @pytest.mark.asyncio
    async def test_assign_app_to_user_user_not_found(self, okta_adapter):
        """Test app assignment when user doesn't exist."""
        with patch.object(okta_adapter, 'get_user_by_email', return_value=None):
            result = await okta_adapter.assign_app_to_user("notfound@example.com", "test-app-id")

            assert result.success is False
            assert "not found in Okta" in result.error_message

    @pytest.mark.asyncio
    async def test_assign_app_to_user_api_error(self, okta_adapter):
        """Test app assignment with API error."""
        mock_user = OktaUser(
            id="user123",
            email="test@example.com",
            login="test@example.com"
        )

        with patch.object(okta_adapter, 'get_user_by_email', return_value=mock_user):
            with patch.object(okta_adapter, '_make_request', side_effect=OktaAPIException("Assignment failed")):
                result = await okta_adapter.assign_app_to_user("test@example.com", "test-app-id")

                assert result.success is False
                assert result.error_message == "Assignment failed"

    @pytest.mark.asyncio
    async def test_verify_and_grant_access_auto_assign_disabled(self, okta_adapter):
        """Test verify_and_grant_access when auto-assign is disabled."""
        okta_adapter.auto_assign_enabled = False

        result = await okta_adapter.verify_and_grant_access("test@example.com", "test-app-id")

        assert result.success is True
        assert "Auto-assign disabled" in result.error_message

    @pytest.mark.asyncio
    async def test_verify_and_grant_access_user_not_found(self, okta_adapter):
        """Test verify_and_grant_access when user doesn't exist."""
        with patch.object(okta_adapter, 'get_user_by_email', return_value=None):
            result = await okta_adapter.verify_and_grant_access("notfound@example.com", "test-app-id")

            assert result.success is False
            assert "not found in Okta" in result.error_message

    @pytest.mark.asyncio
    async def test_verify_and_grant_access_already_has_access(self, okta_adapter):
        """Test verify_and_grant_access when user already has access."""
        mock_user = OktaUser(
            id="user123",
            email="test@example.com",
            login="test@example.com"
        )

        with patch.object(okta_adapter, 'get_user_by_email', return_value=mock_user):
            with patch.object(okta_adapter, 'check_user_app_assignment', return_value=True):
                result = await okta_adapter.verify_and_grant_access("test@example.com", "test-app-id")

                assert result.success is True
                assert result.user_id == "user123"
                assert "already has access" in result.error_message

    @pytest.mark.asyncio
    async def test_verify_and_grant_access_grants_access(self, okta_adapter, mock_assignment_response):
        """Test verify_and_grant_access grants access when needed."""
        mock_user = OktaUser(
            id="user123",
            email="test@example.com",
            login="test@example.com"
        )

        expected_result = OktaAppAssignmentResult(
            success=True,
            user_id="user123",
            app_id="test-app-id",
            assignment=AppAssignment(
                id="assignment123",
                user_id="user123",
                app_id="test-app-id",
                app_name="Test App",
                status="ACTIVE",
                created=datetime.utcnow()
            )
        )

        with patch.object(okta_adapter, 'get_user_by_email', return_value=mock_user):
            with patch.object(okta_adapter, 'check_user_app_assignment', return_value=False):
                with patch.object(okta_adapter, 'assign_app_to_user', return_value=expected_result):
                    result = await okta_adapter.verify_and_grant_access("test@example.com", "test-app-id")

                    assert result.success is True
                    assert result.user_id == "user123"
                    assert result.app_id == "test-app-id"

    @pytest.mark.asyncio
    async def test_list_user_apps_success(self, okta_adapter):
        """Test successful listing of user apps."""
        mock_user = OktaUser(
            id="user123",
            email="test@example.com",
            login="test@example.com"
        )

        mock_app_links = [
            {
                "id": "link1",
                "appInstanceId": "app1",
                "label": "App 1"
            },
            {
                "id": "link2",
                "appInstanceId": "app2",
                "label": "App 2"
            }
        ]

        with patch.object(okta_adapter, 'get_user_by_email', return_value=mock_user):
            with patch.object(okta_adapter, '_make_request', return_value=mock_app_links):
                result = await okta_adapter.list_user_apps("test@example.com")

                assert len(result) == 2
                assert all(isinstance(assignment, AppAssignment) for assignment in result)
                assert result[0].app_id == "app1"
                assert result[1].app_id == "app2"

    @pytest.mark.asyncio
    async def test_list_user_apps_user_not_found(self, okta_adapter):
        """Test listing apps when user doesn't exist."""
        with patch.object(okta_adapter, 'get_user_by_email', return_value=None):
            result = await okta_adapter.list_user_apps("notfound@example.com")

            assert result == []

    @pytest.mark.asyncio
    async def test_make_request_success(self, okta_adapter):
        """Test successful HTTP request."""
        mock_response_data = {"test": "data"}

        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = json.dumps(mock_response_data)

            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.request.return_value.__aenter__.return_value = mock_response

            result = await okta_adapter._make_request("GET", "/test")

            assert result == mock_response_data

    @pytest.mark.asyncio
    async def test_make_request_404_not_found(self, okta_adapter):
        """Test HTTP request returning 404."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404

            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.request.return_value.__aenter__.return_value = mock_response

            result = await okta_adapter._make_request("GET", "/test")

            assert result is None

    @pytest.mark.asyncio
    async def test_make_request_api_error(self, okta_adapter):
        """Test HTTP request returning API error."""
        error_response = {
            "errorSummary": "API Error",
            "errorCode": "E0000001"
        }

        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.text.return_value = json.dumps(error_response)

            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.request.return_value.__aenter__.return_value = mock_response

            with pytest.raises(OktaAPIException) as exc_info:
                await okta_adapter._make_request("GET", "/test")

            assert exc_info.value.message == "API Error"
            assert exc_info.value.status_code == 400
            assert exc_info.value.error_code == "E0000001"

    def test_parse_datetime_success(self, okta_adapter):
        """Test successful datetime parsing."""
        date_str = "2023-01-01T12:00:00.000Z"
        result = okta_adapter._parse_datetime(date_str)

        assert result is not None
        assert isinstance(result, datetime)

    def test_parse_datetime_none(self, okta_adapter):
        """Test datetime parsing with None input."""
        result = okta_adapter._parse_datetime(None)
        assert result is None

    def test_parse_datetime_invalid(self, okta_adapter):
        """Test datetime parsing with invalid input."""
        result = okta_adapter._parse_datetime("invalid-date")
        assert result is None