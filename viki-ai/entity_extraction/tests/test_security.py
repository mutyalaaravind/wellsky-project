"""
Tests for security middleware and OIDC validation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from middleware.security import require_service_account_auth
from util.oidc_validator import OIDCValidationError
import settings


class TestSecurityMiddleware:
    """Test cases for security middleware."""

    @pytest.mark.asyncio
    async def test_bypass_auth_in_local_environment(self):
        """Test that authentication is bypassed when CLOUD_PROVIDER is 'local'."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://localhost/api/pipeline/test/test/start"
        mock_request.method = "POST"
        
        # Mock credentials (should be ignored in local mode)
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="fake-token"
        )
        
        # Mock settings to return 'local'
        with patch.object(settings, 'CLOUD_PROVIDER', 'local'):
            result = await require_service_account_auth(mock_request, mock_credentials)
            
            assert result["authenticated"] is False
            assert result["bypass_reason"] == "local_development"
            assert result["cloud_provider"] == "local"

    @pytest.mark.asyncio
    async def test_missing_credentials_in_cloud_environment(self):
        """Test that missing credentials raise 401 in cloud environment."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/pipeline/test/test/start"
        mock_request.method = "POST"
        
        # No credentials provided
        mock_credentials = None
        
        # Mock settings to return 'gcp'
        with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
            with pytest.raises(HTTPException) as exc_info:
                await require_service_account_auth(mock_request, mock_credentials)
            
            assert exc_info.value.status_code == 401
            assert "Authentication required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_valid_token_authentication(self):
        """Test successful token validation in cloud environment."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/pipeline/test/test/start"
        mock_request.method = "POST"
        
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-jwt-token"
        )
        
        # Mock token claims
        mock_token_claims = {
            "sub": "service-account@project.iam.gserviceaccount.com",
            "email": "service-account@project.iam.gserviceaccount.com",
            "iss": "https://accounts.google.com",
            "aud": "expected-audience",
            "iat": 1234567890,
            "exp": 1234567890 + 3600
        }
        
        # Mock the OIDC validator
        with patch('middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_token.return_value = mock_token_claims
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                result = await require_service_account_auth(mock_request, mock_credentials)
                
                assert result["authenticated"] is True
                assert result["service_account"] == "service-account@project.iam.gserviceaccount.com"
                assert result["token_subject"] == "service-account@project.iam.gserviceaccount.com"
                assert result["cloud_provider"] == "gcp"

    @pytest.mark.asyncio
    async def test_invalid_token_authentication(self):
        """Test that invalid tokens raise 401."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/pipeline/test/test/start"
        mock_request.method = "POST"
        
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-jwt-token"
        )
        
        # Mock the OIDC validator to raise validation error
        with patch('middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_token.side_effect = OIDCValidationError("Invalid token")
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                with pytest.raises(HTTPException) as exc_info:
                    await require_service_account_auth(mock_request, mock_credentials)
                
                assert exc_info.value.status_code == 401
                assert "Authentication failed" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_unexpected_error_during_authentication(self):
        """Test that unexpected errors raise 500."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/pipeline/test/test/start"
        mock_request.method = "POST"
        
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="some-token"
        )
        
        # Mock the OIDC validator to raise unexpected error
        with patch('middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_token.side_effect = Exception("Unexpected error")
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                with pytest.raises(HTTPException) as exc_info:
                    await require_service_account_auth(mock_request, mock_credentials)
                
                assert exc_info.value.status_code == 500
                assert "Internal server error" in exc_info.value.detail


class TestOIDCValidator:
    """Test cases for OIDC token validation."""

    def test_extract_token_from_header_success(self):
        """Test successful token extraction from Authorization header."""
        from util.oidc_validator import OIDCValidator
        
        validator = OIDCValidator()
        token = validator._extract_token_from_header("Bearer abc123")
        assert token == "abc123"

    def test_extract_token_from_header_missing(self):
        """Test error when Authorization header is missing."""
        from util.oidc_validator import OIDCValidator, OIDCValidationError
        
        validator = OIDCValidator()
        with pytest.raises(OIDCValidationError, match="Missing Authorization header"):
            validator._extract_token_from_header(None)

    def test_extract_token_from_header_invalid_format(self):
        """Test error when Authorization header has invalid format."""
        from util.oidc_validator import OIDCValidator, OIDCValidationError
        
        validator = OIDCValidator()
        with pytest.raises(OIDCValidationError, match="Authorization header must start with 'Bearer '"):
            validator._extract_token_from_header("Basic abc123")


class TestDJTEndpointSecurity:
    """Test cases for DJT endpoint security."""

    @pytest.mark.asyncio
    async def test_djt_status_endpoint_security_bypass_local(self):
        """Test that DJT status endpoint bypasses auth in local environment."""
        from routers.status import get_job_status
        
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://localhost/api/status/test-run-id"
        mock_request.method = "GET"
        mock_request.headers = {}
        
        # Mock credentials (should be ignored in local mode)
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="fake-token"
        )
        
        # Mock the DJT client to return test data
        mock_djt_response = {"status": "COMPLETED", "pipelines": []}
        
        with patch('routers.status.require_service_account_auth') as mock_auth:
            with patch('routers.status.get_djt_client') as mock_get_djt_client:
                # Mock auth to return local bypass
                mock_auth.return_value = {
                    "authenticated": False,
                    "bypass_reason": "local_development",
                    "cloud_provider": "local"
                }
                
                # Mock DJT client
                mock_djt_client = AsyncMock()
                mock_djt_client.get_job_pipelines.return_value = mock_djt_response
                mock_get_djt_client.return_value = mock_djt_client
                
                # Call the endpoint
                result = await get_job_status("test-run-id", mock_request, mock_auth.return_value)
                
                # Verify the result
                assert result == mock_djt_response
                mock_djt_client.get_job_pipelines.assert_called_once_with("test-run-id")

    @pytest.mark.asyncio
    async def test_djt_status_endpoint_requires_auth_cloud(self):
        """Test that DJT status endpoint requires auth in cloud environment."""
        from routers.status import get_job_status
        
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/status/test-run-id"
        mock_request.method = "GET"
        mock_request.headers = {}
        
        # Mock valid authentication
        mock_auth_info = {
            "authenticated": True,
            "service_account": "service-account@project.iam.gserviceaccount.com",
            "cloud_provider": "gcp"
        }
        
        # Mock the DJT client to return test data
        mock_djt_response = {"status": "IN_PROGRESS", "pipelines": [{"id": "test-pipeline"}]}
        
        with patch('routers.status.get_djt_client') as mock_get_djt_client:
            # Mock DJT client
            mock_djt_client = AsyncMock()
            mock_djt_client.get_job_pipelines.return_value = mock_djt_response
            mock_get_djt_client.return_value = mock_djt_client
            
            # Call the endpoint with valid auth
            result = await get_job_status("test-run-id", mock_request, mock_auth_info)
            
            # Verify the result
            assert result == mock_djt_response
            mock_djt_client.get_job_pipelines.assert_called_once_with("test-run-id")
