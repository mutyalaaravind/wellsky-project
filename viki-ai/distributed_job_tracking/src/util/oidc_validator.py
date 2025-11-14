"""
OIDC Token Validation Utilities

This module provides utilities for validating Google OIDC tokens from Cloud Tasks
and other Google Cloud services.
"""

import json
import time
from typing import Dict, Optional, Any
from urllib.request import urlopen
from urllib.error import URLError
import jwt
from jwt import PyJWKClient
import aiocache
from util.custom_logger import getLogger
from util.exception import exceptionToMap
import settings

LOGGER = getLogger(__name__)

# Google's OIDC discovery endpoint
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid_configuration"
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"

class OIDCValidationError(Exception):
    """Exception raised when OIDC token validation fails."""
    pass

class OIDCValidator:
    """Validates Google OIDC tokens from Cloud Tasks and other Google services."""
    
    def __init__(self):
        # Cache for 1 hour (3600 seconds) - same as the old cache_ttl=3600 behavior
        self.jwks_client = PyJWKClient(GOOGLE_CERTS_URL, cache_jwk_set=True, lifespan=3600)
    
    @aiocache.cached(ttl=3600)  # Cache for 1 hour
    async def _get_google_discovery_doc(self) -> Dict[str, Any]:
        """Get Google's OIDC discovery document."""
        extra = {"function": "_get_google_discovery_doc"}
        try:
            with urlopen(GOOGLE_DISCOVERY_URL) as response:
                return json.loads(response.read().decode())
        except URLError as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Failed to fetch Google OIDC discovery document: {e}", extra=extra)
            raise OIDCValidationError(f"Failed to fetch OIDC discovery document: {e}")
    
    def _extract_token_from_header(self, authorization_header: Optional[str]) -> str:
        """Extract the token from the Authorization header."""
        if not authorization_header:
            raise OIDCValidationError("Missing Authorization header")
        
        if not authorization_header.startswith("Bearer "):
            raise OIDCValidationError("Authorization header must start with 'Bearer '")
        
        return authorization_header[7:]  # Remove "Bearer " prefix
    
    def _decode_token_header(self, token: str) -> Dict[str, Any]:
        """Decode the token header without verification to get key ID."""
        extra = {"function": "_decode_token_header"}
        try:
            return jwt.get_unverified_header(token)
        except jwt.InvalidTokenError as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Invalid token format: {e}", extra=extra)
            raise OIDCValidationError(f"Invalid token format: {e}")
    
    async def validate_token(self, authorization_header: Optional[str]) -> Dict[str, Any]:
        """
        Validate a Google OIDC token from the Authorization header.
        
        Args:
            authorization_header: The Authorization header value (e.g., "Bearer <token>")
            
        Returns:
            Dict containing the validated token claims
            
        Raises:
            OIDCValidationError: If token validation fails
        """
        extra = {
            "function": "validate_token",
            "cloud_provider": settings.CLOUD_PROVIDER
        }
        
        try:
            # Extract token from header
            token = self._extract_token_from_header(authorization_header)
            
            # Get the signing key
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Get discovery document for validation parameters
            discovery_doc = await self._get_google_discovery_doc()
            
            # Validate and decode the token
            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.SERVICE_ACCOUNT_EMAIL,  # Expected audience
                issuer=discovery_doc.get("issuer", "https://accounts.google.com"),
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                }
            )
            
            # Additional validation
            current_time = int(time.time())
            
            # Check if token is not expired (additional check)
            if decoded_token.get("exp", 0) < current_time:
                raise OIDCValidationError("Token has expired")
            
            # Check if token is not used before its time
            if decoded_token.get("iat", 0) > current_time + 60:  # Allow 60 seconds clock skew
                raise OIDCValidationError("Token used before valid time")
            
            # Log successful validation
            extra.update({
                "token_subject": decoded_token.get("sub"),
                "token_email": decoded_token.get("email"),
                "token_issuer": decoded_token.get("iss"),
                "token_audience": decoded_token.get("aud"),
                "validation_status": "success"
            })
            LOGGER.info("Successfully validated OIDC token", extra=extra)
            
            return decoded_token
            
        except jwt.ExpiredSignatureError as e:
            extra.update({
                "validation_status": "expired",
                "error": exceptionToMap(e)
            })
            LOGGER.warning("OIDC token has expired", extra=extra)
            raise OIDCValidationError("Token has expired")
        except jwt.InvalidAudienceError as e:
            extra.update({
                "validation_status": "invalid_audience",
                "error": exceptionToMap(e)
            })
            LOGGER.warning("OIDC token has invalid audience", extra=extra)
            raise OIDCValidationError("Token has invalid audience")
        except jwt.InvalidIssuerError as e:
            extra.update({
                "validation_status": "invalid_issuer",
                "error": exceptionToMap(e)
            })
            LOGGER.warning("OIDC token has invalid issuer", extra=extra)
            raise OIDCValidationError("Token has invalid issuer")
        except jwt.InvalidTokenError as e:
            extra.update({
                "validation_status": "invalid_token",
                "error": exceptionToMap(e)
            })
            LOGGER.warning("OIDC token validation failed", extra=extra)
            raise OIDCValidationError(f"Invalid token: {e}")
        except OIDCValidationError as e:
            # Re-raise our custom exceptions without logging again
            raise e
        except Exception as e:
            extra.update({
                "validation_status": "error",
                "error": exceptionToMap(e)
            })
            LOGGER.error("Unexpected error during OIDC token validation", extra=extra)
            raise OIDCValidationError(f"Token validation error: {e}")

# Global validator instance
_validator = None

def get_oidc_validator() -> OIDCValidator:
    """Get a singleton OIDC validator instance."""
    global _validator
    if _validator is None:
        _validator = OIDCValidator()
    return _validator
