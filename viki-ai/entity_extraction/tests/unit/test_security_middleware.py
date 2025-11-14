"""
Additional unit tests for middleware.security module to improve coverage.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.middleware.security import optional_service_account_auth, security, require_service_account_auth
from util.oidc_validator import OIDCValidationError
import settings


class TestOptionalServiceAccountAuth:
    """Test cases for optional_service_account_auth function."""

    def test_bypass_auth_in_local_environment(self):
        """Test that optional authentication is bypassed when CLOUD_PROVIDER is 'local'."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://localhost/api/test"
        mock_request.method = "GET"
        
        # Mock credentials (should be ignored in local mode)
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="fake-token"
        )
        
        # Mock settings to return 'local'
        with patch.object(settings, 'CLOUD_PROVIDER', 'local'):
            result = optional_service_account_auth(mock_request, mock_credentials)
            
            assert result["authenticated"] is False
            assert result["bypass_reason"] == "local_development"
            assert result["cloud_provider"] == "local"

    def test_no_credentials_provided(self):
        """Test that no credentials returns unauthenticated."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "GET"
        
        # No credentials provided
        mock_credentials = None
        
        # Mock settings to return 'gcp'
        with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
            result = optional_service_account_auth(mock_request, mock_credentials)
            
            assert result["authenticated"] is False
            assert result["reason"] == "no_credentials_provided"

    def test_optional_auth_not_implemented(self):
        """Test that optional auth with credentials returns not implemented."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "GET"
        
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="some-token"
        )
        
        # Mock the OIDC validator
        with patch('middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = Mock()
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                result = optional_service_account_auth(mock_request, mock_credentials)
                
                assert result["authenticated"] is False
                assert result["reason"] == "optional_auth_not_implemented"

    def test_validation_error_handling(self):
        """Test that validation errors are handled gracefully."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "GET"
        
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        
        # Mock the OIDC validator to raise an exception
        with patch('middleware.security.get_oidc_validator') as mock_get_validator:
            mock_get_validator.side_effect = Exception("Validation service down")
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                result = optional_service_account_auth(mock_request, mock_credentials)
                
                assert result["authenticated"] is False
                assert result["reason"] == "optional_auth_not_implemented"

    def test_general_exception_handling(self):
        """Test that general exceptions are handled gracefully."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "GET"
        
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="some-token"
        )
        
        # Mock settings to return 'gcp'
        with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
            # Mock get_oidc_validator to raise an exception
            with patch('middleware.security.get_oidc_validator', side_effect=RuntimeError("Service error")):
                result = optional_service_account_auth(mock_request, mock_credentials)
                
                assert result["authenticated"] is False
                assert result["reason"] == "optional_auth_not_implemented"


class TestSecurityScheme:
    """Test cases for the security scheme configuration."""

    def test_security_scheme_exists(self):
        """Test that the HTTPBearer security scheme is properly configured."""
        assert security is not None
        assert hasattr(security, 'auto_error')
        assert security.auto_error is False


class TestRequireServiceAccountAuthAdditional:
    """Additional test cases for require_service_account_auth to improve coverage."""

    @pytest.mark.asyncio
    async def test_token_claims_extraction(self):
        """Test that all token claims are properly extracted and returned."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "POST"
        
        # Mock credentials with properly formatted JWT token
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        
        # Mock comprehensive token claims
        mock_token_claims = {
            "sub": "service-account@project.iam.gserviceaccount.com",
            "email": "service-account@project.iam.gserviceaccount.com",
            "iss": "https://accounts.google.com",
            "aud": "expected-audience",
            "iat": 1234567890,
            "exp": 1234567890 + 3600,
            "extra_claim": "extra_value"
        }
        
        # Mock the OIDC validator
        with patch('src.middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_token.return_value = mock_token_claims
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                result = await require_service_account_auth(mock_request, mock_credentials)
                
                # Verify all expected fields are present
                assert result["authenticated"] is True
                assert result["token_subject"] == "service-account@project.iam.gserviceaccount.com"
                assert result["token_email"] == "service-account@project.iam.gserviceaccount.com"
                assert result["token_issuer"] == "https://accounts.google.com"
                assert result["token_audience"] == "expected-audience"
                assert result["service_account"] == "service-account@project.iam.gserviceaccount.com"
                assert result["cloud_provider"] == "gcp"
                assert result["validation_time"] == 1234567890
                assert result["expiration_time"] == 1234567890 + 3600
                
                # Verify the validator was called with correct header
                mock_validator.validate_token.assert_called_once_with("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")

    @pytest.mark.asyncio
    async def test_missing_token_claims(self):
        """Test handling when token claims are missing some fields."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "POST"
        
        # Mock credentials with properly formatted JWT token
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        
        # Mock minimal token claims (missing some fields)
        mock_token_claims = {
            "sub": "service-account@project.iam.gserviceaccount.com",
        }
        
        # Mock the OIDC validator
        with patch('src.middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_token.return_value = mock_token_claims
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                result = await require_service_account_auth(mock_request, mock_credentials)
                
                # Verify handling of missing claims
                assert result["authenticated"] is True
                assert result["token_subject"] == "service-account@project.iam.gserviceaccount.com"
                assert result["token_email"] is None
                assert result["token_issuer"] is None
                assert result["token_audience"] is None
                assert result["service_account"] is None
                assert result["validation_time"] is None
                assert result["expiration_time"] is None

    @pytest.mark.asyncio
    async def test_oidc_validation_error_details(self):
        """Test that OIDC validation error details are properly handled."""
        # Mock the request
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "POST"
        
        # Mock credentials with properly formatted JWT token
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        
        # Mock the OIDC validator to raise validation error with specific message
        validation_error = OIDCValidationError("Token expired at 2023-01-01T00:00:00Z")
        
        with patch('src.middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_token.side_effect = validation_error
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                with pytest.raises(HTTPException) as exc_info:
                    await require_service_account_auth(mock_request, mock_credentials)
                
                assert exc_info.value.status_code == 401
                assert "Authentication failed: Token expired at 2023-01-01T00:00:00Z" in exc_info.value.detail
                assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_request_headers_logging(self):
        """Test that request headers are properly included in logging context."""
        # Mock the request with specific headers
        mock_request = Mock()
        mock_request.url = "http://example.com/api/test"
        mock_request.method = "POST"
        mock_request.headers = {"User-Agent": "TestClient/1.0", "X-Request-ID": "test-123"}
        
        # Mock credentials
        mock_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        
        # Mock token claims
        mock_token_claims = {"sub": "test@example.com", "email": "test@example.com"}
        
        # Mock the OIDC validator
        with patch('src.middleware.security.get_oidc_validator') as mock_get_validator:
            mock_validator = AsyncMock()
            mock_validator.validate_token.return_value = mock_token_claims
            mock_get_validator.return_value = mock_validator
            
            with patch.object(settings, 'CLOUD_PROVIDER', 'gcp'):
                with patch('src.middleware.security.LOGGER') as mock_logger:
                    result = await require_service_account_auth(mock_request, mock_credentials)
                    
                    # Verify that logger was called with proper context
                    assert mock_logger.debug.called or mock_logger.info.called
                    # The function should have logged successfully
                    assert result["authenticated"] is True