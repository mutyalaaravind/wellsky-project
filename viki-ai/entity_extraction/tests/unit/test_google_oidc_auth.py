"""
Unit tests for src.util.google_oidc_auth module.
"""

import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
import httpx
from google.oauth2 import service_account
import google.auth

# Import test environment setup
from tests.test_env import setup_test_env
setup_test_env()

# Import the module under test
from src.util.google_oidc_auth import (
    get_oidc_token,
    get_oidc_headers,
    _get_oidc_token_from_service_account,
    _get_oidc_token_from_metadata_server
)


class TestGetOIDCToken:
    """Test the get_oidc_token function."""

    @pytest.mark.asyncio
    async def test_get_oidc_token_local_environment(self):
        """Test OIDC token generation in local environment."""
        with patch('src.util.google_oidc_auth.settings.CLOUD_PROVIDER', 'local'):
            with patch('src.util.google_oidc_auth.settings.DJT_API_URL', 'http://localhost:8080'):
                result = await get_oidc_token()
                
                assert result == "mock-oidc-token-for-local-development"

    # Note: Skipping tests that involve the cached get_oidc_token function
    # due to cache decorator complications. The individual helper functions
    # are tested separately below.


class TestGetOIDCTokenFromServiceAccount:
    """Test the _get_oidc_token_from_service_account function."""

    @pytest.mark.asyncio
    async def test_get_oidc_token_from_service_account_success(self):
        """Test successful OIDC token creation from service account."""
        # Mock service account credentials
        mock_signer = Mock()
        mock_signer.key_id = "test-key-id"
        
        mock_credentials = Mock(spec=service_account.Credentials)
        mock_credentials.service_account_email = "test@project.iam.gserviceaccount.com"
        mock_credentials.signer = mock_signer
        mock_credentials.with_claims.return_value = mock_credentials
        
        audience = "https://target-service.example.com"
        expected_token = "mocked-jwt-token"
        
        # Mock JWT encoding (jwt is imported inside the function)
        with patch('jwt.encode', return_value=expected_token) as mock_jwt_encode:
            result = await _get_oidc_token_from_service_account(mock_credentials, audience)
            
            assert result == expected_token
            
            # Verify JWT was encoded with correct parameters
            mock_jwt_encode.assert_called_once()
            args, kwargs = mock_jwt_encode.call_args
            
            # Check payload structure
            payload = args[0]
            assert payload["iss"] == "test@project.iam.gserviceaccount.com"
            assert payload["sub"] == "test@project.iam.gserviceaccount.com"
            assert payload["aud"] == audience
            assert "iat" in payload
            assert "exp" in payload
            assert payload["exp"] == payload["iat"] + 3600  # 1 hour expiration
            
            # Check other parameters
            assert args[1] == "test-key-id"  # key
            assert kwargs["algorithm"] == "RS256"
            assert kwargs["headers"]["kid"] == "test-key-id"

    @pytest.mark.asyncio
    async def test_get_oidc_token_from_service_account_failure(self):
        """Test OIDC token creation failure from service account."""
        mock_credentials = Mock(spec=service_account.Credentials)
        mock_credentials.service_account_email = "test@project.iam.gserviceaccount.com"
        mock_credentials.with_claims.side_effect = Exception("Credentials error")
        
        audience = "https://target-service.example.com"
        
        with pytest.raises(Exception) as exc_info:
            await _get_oidc_token_from_service_account(mock_credentials, audience)
        
        assert "Credentials error" in str(exc_info.value)


class TestGetOIDCTokenFromMetadataServer:
    """Test the _get_oidc_token_from_metadata_server function."""

    @pytest.mark.asyncio
    async def test_get_oidc_token_from_metadata_server_success(self):
        """Test successful OIDC token retrieval from metadata server."""
        audience = "https://target-service.example.com"
        expected_token = "metadata-server-token"
        
        # Mock httpx response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = f"  {expected_token}  "  # With whitespace to test stripping
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('src.util.google_oidc_auth.httpx.AsyncClient', return_value=mock_client):
            result = await _get_oidc_token_from_metadata_server(audience)
            
            assert result == expected_token
            
            # Verify the request was made correctly
            mock_client.get.assert_called_once_with(
                "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity",
                headers={"Metadata-Flavor": "Google"},
                params={
                    "audience": audience,
                    "format": "full",
                    "include_email": "true"
                },
                timeout=10.0
            )

    @pytest.mark.asyncio
    async def test_get_oidc_token_from_metadata_server_failure(self):
        """Test OIDC token retrieval failure from metadata server."""
        audience = "https://target-service.example.com"
        
        # Mock httpx response with error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('src.util.google_oidc_auth.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await _get_oidc_token_from_metadata_server(audience)
            
            assert "Metadata server returned status 404" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_oidc_token_from_metadata_server_network_error(self):
        """Test OIDC token retrieval with network error."""
        audience = "https://target-service.example.com"
        
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.RequestError("Network timeout")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('src.util.google_oidc_auth.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await _get_oidc_token_from_metadata_server(audience)
            
            assert "Network timeout" in str(exc_info.value)


class TestGetOIDCHeaders:
    """Test the get_oidc_headers function."""

    @pytest.mark.asyncio
    async def test_get_oidc_headers_local_environment(self):
        """Test OIDC headers generation in local environment."""
        with patch('src.util.google_oidc_auth.settings.CLOUD_PROVIDER', 'local'):
            result = await get_oidc_headers()
            
            expected = {
                "Content-Type": "application/json"
            }
            assert result == expected

    @pytest.mark.asyncio
    async def test_get_oidc_headers_with_token(self):
        """Test OIDC headers generation with valid token."""
        mock_token = "valid-oidc-token"
        
        with patch('src.util.google_oidc_auth.settings.CLOUD_PROVIDER', 'gcp'):
            with patch('src.util.google_oidc_auth.get_oidc_token', return_value=mock_token):
                result = await get_oidc_headers()
                
                expected = {
                    "Authorization": f"Bearer {mock_token}",
                    "Content-Type": "application/json"
                }
                assert result == expected

    @pytest.mark.asyncio
    async def test_get_oidc_headers_with_custom_audience(self):
        """Test OIDC headers generation with custom audience."""
        mock_token = "custom-audience-token"
        custom_audience = "https://custom-service.example.com"
        
        with patch('src.util.google_oidc_auth.settings.CLOUD_PROVIDER', 'gcp'):
            with patch('src.util.google_oidc_auth.get_oidc_token', return_value=mock_token) as mock_get_token:
                result = await get_oidc_headers(custom_audience)
                
                expected = {
                    "Authorization": f"Bearer {mock_token}",
                    "Content-Type": "application/json"
                }
                assert result == expected
                
                # Verify get_oidc_token was called with custom audience
                mock_get_token.assert_called_once_with(custom_audience)

    @pytest.mark.asyncio
    async def test_get_oidc_headers_token_failure(self):
        """Test OIDC headers generation when token acquisition fails."""
        with patch('src.util.google_oidc_auth.settings.CLOUD_PROVIDER', 'gcp'):
            with patch('src.util.google_oidc_auth.get_oidc_token', side_effect=Exception("Token acquisition failed")):
                with pytest.raises(Exception) as exc_info:
                    await get_oidc_headers()
                
                assert "Failed to create authenticated headers for service-to-service communication" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_oidc_headers_local_environment_custom_audience(self):
        """Test OIDC headers generation in local environment with custom audience."""
        custom_audience = "https://local-service.example.com"
        
        with patch('src.util.google_oidc_auth.settings.CLOUD_PROVIDER', 'local'):
            result = await get_oidc_headers(custom_audience)
            
            expected = {
                "Content-Type": "application/json"
            }
            assert result == expected


class TestLoggingAndErrorHandling:
    """Test logging and error handling behaviors."""

    # Note: Skipping cache-related logging tests due to cache decorator complications

    @pytest.mark.asyncio
    async def test_service_account_success_logging(self):
        """Test that successful service account token creation is logged."""
        mock_signer = Mock()
        mock_signer.key_id = "test-key"
        
        mock_credentials = Mock(spec=service_account.Credentials)
        mock_credentials.service_account_email = "test@project.iam.gserviceaccount.com"
        mock_credentials.signer = mock_signer
        mock_credentials.with_claims.return_value = mock_credentials
        
        with patch('jwt.encode', return_value="token"):
            with patch('src.util.google_oidc_auth.LOGGER') as mock_logger:
                await _get_oidc_token_from_service_account(mock_credentials, "audience")
                
                # Verify success logging
                mock_logger.debug.assert_called()
                debug_calls = mock_logger.debug.call_args_list
                assert any("Successfully created OIDC token using service account" in str(call) for call in debug_calls)

    @pytest.mark.asyncio
    async def test_metadata_server_success_logging(self):
        """Test that successful metadata server token retrieval is logged."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "token"
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('src.util.google_oidc_auth.httpx.AsyncClient', return_value=mock_client):
            with patch('src.util.google_oidc_auth.LOGGER') as mock_logger:
                await _get_oidc_token_from_metadata_server("audience")
                
                # Verify success logging
                mock_logger.debug.assert_called()
                debug_calls = mock_logger.debug.call_args_list
                assert any("Successfully obtained OIDC token from metadata server" in str(call) for call in debug_calls)


if __name__ == '__main__':
    pytest.main([__file__])