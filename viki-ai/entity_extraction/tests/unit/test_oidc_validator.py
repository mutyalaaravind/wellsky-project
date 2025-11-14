"""
Unit tests for src.util.oidc_validator module.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from urllib.error import URLError
import jwt

# Import test environment setup
from tests.test_env import setup_test_env
setup_test_env()

# Import the module under test
from src.util.oidc_validator import (
    OIDCValidator,
    OIDCValidationError,
    get_oidc_validator,
    GOOGLE_DISCOVERY_URL,
    GOOGLE_CERTS_URL
)


class TestOIDCValidationError:
    """Test the OIDCValidationError exception class."""
    
    def test_oidc_validation_error_creation(self):
        """Test creating OIDCValidationError."""
        error = OIDCValidationError("Token expired")
        assert str(error) == "Token expired"
        assert isinstance(error, Exception)


class TestOIDCValidator:
    """Test the OIDCValidator class."""
    
    def test_init(self):
        """Test OIDCValidator initialization."""
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_jwks_client.return_value = mock_client
            
            validator = OIDCValidator()
            
            # Verify PyJWKClient was initialized correctly
            mock_jwks_client.assert_called_once_with(
                GOOGLE_CERTS_URL, 
                cache_jwk_set=True, 
                lifespan=3600
            )
            assert validator.jwks_client == mock_client

    @pytest.mark.asyncio
    async def test_get_google_discovery_doc_success(self):
        """Test successful retrieval of Google discovery document."""
        # Mock discovery document
        mock_discovery_doc = {
            "issuer": "https://accounts.google.com",
            "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_endpoint": "https://oauth2.googleapis.com/token"
        }
        
        # Mock urlopen
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(mock_discovery_doc).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        
        with patch('src.util.oidc_validator.PyJWKClient'):
            with patch('src.util.oidc_validator.urlopen', return_value=mock_response):
                validator = OIDCValidator()
                result = await validator._get_google_discovery_doc()
                
                assert result == mock_discovery_doc

    @pytest.mark.asyncio
    async def test_get_google_discovery_doc_failure(self):
        """Test failure to retrieve Google discovery document."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            with patch('src.util.oidc_validator.urlopen', side_effect=URLError("Network error")):
                validator = OIDCValidator()
                
                with pytest.raises(OIDCValidationError) as exc_info:
                    await validator._get_google_discovery_doc()
                
                assert "Failed to fetch OIDC discovery document" in str(exc_info.value)

    def test_extract_token_from_header_success(self):
        """Test successful token extraction from Authorization header."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            validator = OIDCValidator()
            
            token = validator._extract_token_from_header("Bearer abc123token")
            assert token == "abc123token"

    def test_extract_token_from_header_missing(self):
        """Test token extraction with missing Authorization header."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            validator = OIDCValidator()
            
            with pytest.raises(OIDCValidationError) as exc_info:
                validator._extract_token_from_header(None)
            
            assert "Missing Authorization header" in str(exc_info.value)

    def test_extract_token_from_header_wrong_format(self):
        """Test token extraction with wrong header format."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            validator = OIDCValidator()
            
            with pytest.raises(OIDCValidationError) as exc_info:
                validator._extract_token_from_header("Basic abc123")
            
            assert "Authorization header must start with 'Bearer '" in str(exc_info.value)

    def test_decode_token_header_success(self):
        """Test successful token header decoding."""
        # Valid JWT header
        mock_header = {"alg": "RS256", "typ": "JWT", "kid": "key123"}
        
        with patch('src.util.oidc_validator.PyJWKClient'):
            with patch('src.util.oidc_validator.jwt.get_unverified_header', return_value=mock_header):
                validator = OIDCValidator()
                
                result = validator._decode_token_header("fake.jwt.token")
                assert result == mock_header

    def test_decode_token_header_invalid(self):
        """Test token header decoding with invalid token."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            with patch('src.util.oidc_validator.jwt.get_unverified_header', side_effect=jwt.InvalidTokenError("Invalid token")):
                validator = OIDCValidator()
                
                with pytest.raises(OIDCValidationError) as exc_info:
                    validator._decode_token_header("invalid.token")
                
                assert "Invalid token format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_success(self):
        """Test successful token validation."""
        # Mock components
        mock_discovery_doc = {
            "issuer": "https://accounts.google.com"
        }
        
        mock_decoded_token = {
            "sub": "service-account@project.iam.gserviceaccount.com",
            "email": "service-account@project.iam.gserviceaccount.com",
            "iss": "https://accounts.google.com",
            "aud": "expected-audience",
            "iat": int(time.time()) - 100,  # 100 seconds ago
            "exp": int(time.time()) + 3500   # Valid for another 3500 seconds
        }
        
        mock_signing_key = Mock()
        mock_signing_key.key = "mock-key"
        
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_jwks_client.return_value = mock_client
            
            with patch('src.util.oidc_validator.jwt.decode', return_value=mock_decoded_token):
                with patch.object(OIDCValidator, '_get_google_discovery_doc', return_value=mock_discovery_doc):
                    with patch('src.util.oidc_validator.settings.SERVICE_ACCOUNT_EMAIL', 'expected-audience'):
                        validator = OIDCValidator()
                        
                        result = await validator.validate_token("Bearer fake.jwt.token")
                        
                        assert result == mock_decoded_token

    @pytest.mark.asyncio
    async def test_validate_token_expired(self):
        """Test token validation with expired token."""
        mock_discovery_doc = {"issuer": "https://accounts.google.com"}
        
        # Token that's expired
        mock_decoded_token = {
            "sub": "service-account@project.iam.gserviceaccount.com",
            "iat": int(time.time()) - 3700,  # Issued 3700 seconds ago
            "exp": int(time.time()) - 100    # Expired 100 seconds ago
        }
        
        mock_signing_key = Mock()
        mock_signing_key.key = "mock-key"
        
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_jwks_client.return_value = mock_client
            
            with patch('src.util.oidc_validator.jwt.decode', return_value=mock_decoded_token):
                with patch.object(OIDCValidator, '_get_google_discovery_doc', return_value=mock_discovery_doc):
                    validator = OIDCValidator()
                    
                    with pytest.raises(OIDCValidationError) as exc_info:
                        await validator.validate_token("Bearer fake.jwt.token")
                    
                    assert "Token has expired" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_future_iat(self):
        """Test token validation with future issued-at time."""
        mock_discovery_doc = {"issuer": "https://accounts.google.com"}
        
        # Token with future iat (beyond clock skew tolerance)
        mock_decoded_token = {
            "sub": "service-account@project.iam.gserviceaccount.com",
            "iat": int(time.time()) + 120,  # Issued 120 seconds in the future
            "exp": int(time.time()) + 3600
        }
        
        mock_signing_key = Mock()
        mock_signing_key.key = "mock-key"
        
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_jwks_client.return_value = mock_client
            
            with patch('src.util.oidc_validator.jwt.decode', return_value=mock_decoded_token):
                with patch.object(OIDCValidator, '_get_google_discovery_doc', return_value=mock_discovery_doc):
                    validator = OIDCValidator()
                    
                    with pytest.raises(OIDCValidationError) as exc_info:
                        await validator.validate_token("Bearer fake.jwt.token")
                    
                    assert "Token used before valid time" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_jwt_expired_signature_error(self):
        """Test token validation with JWT ExpiredSignatureError."""
        mock_signing_key = Mock()
        mock_signing_key.key = "mock-key"
        
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_jwks_client.return_value = mock_client
            
            with patch('src.util.oidc_validator.jwt.decode', side_effect=jwt.ExpiredSignatureError("Token expired")):
                with patch.object(OIDCValidator, '_get_google_discovery_doc', return_value={}):
                    validator = OIDCValidator()
                    
                    with pytest.raises(OIDCValidationError) as exc_info:
                        await validator.validate_token("Bearer fake.jwt.token")
                    
                    assert "Token has expired" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_invalid_audience_error(self):
        """Test token validation with JWT InvalidAudienceError."""
        mock_signing_key = Mock()
        mock_signing_key.key = "mock-key"
        
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_jwks_client.return_value = mock_client
            
            with patch('src.util.oidc_validator.jwt.decode', side_effect=jwt.InvalidAudienceError("Invalid audience")):
                with patch.object(OIDCValidator, '_get_google_discovery_doc', return_value={}):
                    validator = OIDCValidator()
                    
                    with pytest.raises(OIDCValidationError) as exc_info:
                        await validator.validate_token("Bearer fake.jwt.token")
                    
                    assert "Token has invalid audience" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_invalid_issuer_error(self):
        """Test token validation with JWT InvalidIssuerError."""
        mock_signing_key = Mock()
        mock_signing_key.key = "mock-key"
        
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_jwks_client.return_value = mock_client
            
            with patch('src.util.oidc_validator.jwt.decode', side_effect=jwt.InvalidIssuerError("Invalid issuer")):
                with patch.object(OIDCValidator, '_get_google_discovery_doc', return_value={}):
                    validator = OIDCValidator()
                    
                    with pytest.raises(OIDCValidationError) as exc_info:
                        await validator.validate_token("Bearer fake.jwt.token")
                    
                    assert "Token has invalid issuer" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_invalid_token_error(self):
        """Test token validation with JWT InvalidTokenError."""
        mock_signing_key = Mock()
        mock_signing_key.key = "mock-key"
        
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_jwks_client.return_value = mock_client
            
            with patch('src.util.oidc_validator.jwt.decode', side_effect=jwt.InvalidTokenError("Malformed token")):
                with patch.object(OIDCValidator, '_get_google_discovery_doc', return_value={}):
                    validator = OIDCValidator()
                    
                    with pytest.raises(OIDCValidationError) as exc_info:
                        await validator.validate_token("Bearer fake.jwt.token")
                    
                    assert "Invalid token: Malformed token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_unexpected_error(self):
        """Test token validation with unexpected error."""
        with patch('src.util.oidc_validator.PyJWKClient') as mock_jwks_client:
            mock_client = Mock()
            mock_client.get_signing_key_from_jwt.side_effect = ConnectionError("Network error")
            mock_jwks_client.return_value = mock_client
            
            validator = OIDCValidator()
            
            with pytest.raises(OIDCValidationError) as exc_info:
                await validator.validate_token("Bearer fake.jwt.token")
            
            assert "Token validation error: Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_token_oidc_validation_error_passthrough(self):
        """Test that OIDCValidationError is passed through without wrapping."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            validator = OIDCValidator()
            
            # Mock _extract_token_from_header to raise OIDCValidationError
            with patch.object(validator, '_extract_token_from_header', side_effect=OIDCValidationError("Missing header")):
                with pytest.raises(OIDCValidationError) as exc_info:
                    await validator.validate_token(None)
                
                assert str(exc_info.value) == "Missing header"


class TestGetOIDCValidator:
    """Test the get_oidc_validator function."""
    
    def test_get_oidc_validator_singleton(self):
        """Test that get_oidc_validator returns a singleton instance."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            # Clear any existing global validator
            import src.util.oidc_validator
            src.util.oidc_validator._validator = None
            
            # First call should create the validator
            validator1 = get_oidc_validator()
            assert validator1 is not None
            assert isinstance(validator1, OIDCValidator)
            
            # Second call should return the same instance
            validator2 = get_oidc_validator()
            assert validator2 is validator1

    def test_get_oidc_validator_reuse_existing(self):
        """Test that get_oidc_validator reuses an existing instance."""
        with patch('src.util.oidc_validator.PyJWKClient'):
            # Create a validator instance manually
            import src.util.oidc_validator
            existing_validator = OIDCValidator()
            src.util.oidc_validator._validator = existing_validator
            
            # get_oidc_validator should return the existing instance
            result = get_oidc_validator()
            assert result is existing_validator


class TestConstants:
    """Test module constants."""
    
    def test_google_discovery_url(self):
        """Test Google discovery URL constant."""
        assert GOOGLE_DISCOVERY_URL == "https://accounts.google.com/.well-known/openid_configuration"
    
    def test_google_certs_url(self):
        """Test Google certificates URL constant."""
        assert GOOGLE_CERTS_URL == "https://www.googleapis.com/oauth2/v3/certs"


if __name__ == '__main__':
    pytest.main([__file__])