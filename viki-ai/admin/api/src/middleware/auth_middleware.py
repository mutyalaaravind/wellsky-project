"""
Authentication middleware for FastAPI application.
Validates JWT tokens from Okta and extracts user context.
"""

import jwt
import logging
from typing import Optional
import json
import aiohttp
import requests

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from settings import Settings
from models.user import User
from domain.models.user_context import set_current_user_sync

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle JWT authentication for all requests.
    Validates tokens against Okta JWKS and sets user context.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self._jwks_cache = None
        self._jwks_cache_ttl = 3600  # Cache JWKS for 1 hour

    async def dispatch(self, request: Request, call_next):
        """
        Process incoming requests and validate authentication.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain
            
        Returns:
            Response object
        """
        # Skip authentication for health checks, docs, and CORS preflight requests
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Skip authentication for CORS preflight OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            settings = Settings()
            
            # Skip authentication in development mode FIRST - before any token processing
            if settings.OKTA_DISABLE:
                logger.info("Authentication disabled in development mode")
                # Set a mock user for development
                mock_user_email = settings.OKTA_DISABLE_MOCK_USER or "dev@example.com"
                mock_user_name = mock_user_email.split('@')[0].split('.')
                mock_user_name = ' '.join([token.capitalize() for token in mock_user_name]) + " (MOCK)"

                mock_claims = {
                    "sub": mock_user_email,
                    "email": mock_user_email,
                    "name": mock_user_name,
                    "group-roles": "superuser",
                    "aud": "viki.prod.wellsky.io",
                    "iss": "https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7",
                    "exp": 9999999999,  # Far future expiration
                    "iat": 1234567890,  # Issued at timestamp
                }

                mock_user = User(
                    sub=mock_user_email,
                    email=mock_user_email,
                    name=mock_user_name,
                    claims=mock_claims
                )
                request.state.user = mock_user
                # Set user in context for cross-cutting access
                set_current_user_sync(mock_user)
                return await call_next(request)
            
            # Only process JWT tokens if Okta is enabled
            # Extract Bearer token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing or invalid authorization header"}
                )
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Validate JWT token
            user = await self._validate_jwt_token(token, settings)
            if not user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"}
                )
            
            # Set user context for downstream handlers
            request.state.user = user
            # Set user in context for cross-cutting access
            set_current_user_sync(user)
            logger.info(f"Authenticated user: {user.sub}")

            return await call_next(request)
            
        except Exception as e:
            logger.warning(f"Authentication failed: {str(e)}")
            # If Okta is disabled, don't fail on authentication errors
            settings = Settings()
            if settings.OKTA_DISABLE:
                logger.info("Okta disabled - using development user despite error")
                mock_user_email = settings.OKTA_DISABLE_MOCK_USER or "dev@example.com"
                mock_user_name = mock_user_email.split('@')[0].split('.')
                mock_user_name = ' '.join([token.capitalize() for token in mock_user_name]) + " (MOCK)"

                mock_claims = {
                    "sub": mock_user_email,
                    "email": mock_user_email,
                    "name": mock_user_name,
                    "group-roles": "superuser",
                    "aud": "viki.prod.wellsky.io",
                    "iss": "https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7",
                    "exp": 9999999999,  # Far future expiration
                    "iat": 1234567890,  # Issued at timestamp
                }

                fallback_user = User(
                    sub=mock_user_email,
                    email=mock_user_email,
                    name=mock_user_name,
                    claims=mock_claims
                )
                request.state.user = fallback_user
                # Set user in context for cross-cutting access
                set_current_user_sync(fallback_user)
                return await call_next(request)
            
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication credentials"}
            )

    async def _validate_jwt_token(self, token: str, settings) -> Optional[User]:
        """
        Validate JWT token against Okta JWKS.
        
        Args:
            token: JWT token string
            settings: Application settings
            
        Returns:
            Optional[User]: User object if token is valid, None otherwise
        """
        try:
            # Verify required Okta settings
            if not all([settings.OKTA_ISSUER, settings.OKTA_AUDIENCE]):
                logger.error("Missing required Okta configuration")
                return None
            
            # Construct JWKS URI from issuer (standard Okta pattern)
            jwks_uri = f"{settings.OKTA_ISSUER}/v1/keys"
            logger.debug(f"Using JWKS URI: {jwks_uri}")
            
            # Get JWKS for token validation
            jwks = await self._get_jwks(jwks_uri)
            if not jwks:
                logger.error("Failed to retrieve JWKS")
                return None
            
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                logger.error("Token missing key ID")
                return None
            
            # Find matching key in JWKS
            signing_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    signing_key = key
                    break
            
            if not signing_key:
                logger.error(f"No matching key found for kid: {kid}")
                return None
            
            # Convert JWK to RSA public key for proper validation
            public_key = self._jwk_to_rsa_key(signing_key)
            if not public_key:
                logger.error("Failed to convert JWK to RSA public key")
                return None
            
            # Debug: Log the token payload to see actual audience
            try:
                # First decode without audience verification to see what's in the token
                unverified_payload = jwt.decode(
                    token,
                    options={"verify_signature": False, "verify_aud": False}
                )
                logger.info(f"Token audience: {unverified_payload.get('aud')}")
                logger.info(f"Expected audience: {settings.OKTA_AUDIENCE}")
                logger.info(f"Token scopes: {unverified_payload.get('scp', [])}")
            except Exception as debug_e:
                logger.warning(f"Debug decode failed: {str(debug_e)}")
            
            # Properly validate JWT token with correct audience
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.OKTA_AUDIENCE,
                issuer=settings.OKTA_ISSUER,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,  # Re-enabled with correct audience
                    "verify_iss": True
                }
            )
            
            # Create user object from token claims
            # Extract user information from JWT payload
            sub = payload.get("sub", "")
            email = payload.get("email") or sub
            name = payload.get("name") or payload.get("preferred_username") or email or "Unknown User"

            user = User(
                sub=sub,  # Keep original JWT sub claim
                email=email,  # Use email from JWT or fallback to sub
                name=name,  # Use name from JWT or fallback to email
                claims=payload  # Store all JWT claims for downstream use
            )

            return user
            
        except Exception as e:
            logger.warning(f"JWT validation error: {str(e)}")
            return None

    async def _get_jwks(self, jwks_uri: str) -> Optional[dict]:
        """
        Retrieve JWKS from Okta with caching.
        
        Args:
            jwks_uri: JWKS endpoint URL
            
        Returns:
            Optional[dict]: JWKS data or None if failed
        """
        try:
            # Return cached JWKS if available
            if self._jwks_cache:
                return self._jwks_cache
            
            # Fetch JWKS from Okta
            async with aiohttp.ClientSession() as session:
                async with session.get(jwks_uri) as response:
                    if response.status == 200:
                        jwks_data = await response.json()
                        self._jwks_cache = jwks_data
                        return jwks_data
                    else:
                        logger.error(f"Failed to fetch JWKS: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching JWKS: {str(e)}")
            return None

    def _jwk_to_rsa_key(self, jwk_key: dict):
        """
        Convert JWK to RSA public key for JWT validation.
        
        Args:
            jwk_key: JWK key data from JWKS
            
        Returns:
            RSA public key object or None if conversion fails
        """
        try:
            import base64
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            
            # Extract modulus (n) and exponent (e) from JWK
            n_bytes = base64.urlsafe_b64decode(jwk_key['n'] + '==')
            e_bytes = base64.urlsafe_b64decode(jwk_key['e'] + '==')
            
            # Convert to integers
            n_int = int.from_bytes(n_bytes, 'big')
            e_int = int.from_bytes(e_bytes, 'big')
            
            # Create RSA public key
            public_numbers = rsa.RSAPublicNumbers(e_int, n_int)
            public_key = public_numbers.public_key()
            
            # Return the key object directly for PyJWT
            return public_key
            
        except Exception as e:
            logger.error(f"Error converting JWK to RSA key: {str(e)}")
            return None

async def get_current_user_from_request(token: str) -> Optional[User]:
    """
    Helper function to extract user from JWT token.
    Used by authentication dependencies.
    
    Args:
        token: JWT token string
        
    Returns:
        Optional[User]: User object if token is valid, None otherwise
    """
    try:
        settings = Settings()
        
        # Skip validation in development mode
        if settings.OKTA_DISABLE:
            mock_user_email = settings.OKTA_DISABLE_MOCK_USER or "dev@example.com"
            mock_user_name = mock_user_email.split('@')[0].split('.')
            mock_user_name = ' '.join([token.capitalize() for token in mock_user_name]) + " (MOCK)"

            mock_claims = {
                "sub": mock_user_email,
                "email": mock_user_email,
                "name": mock_user_name,
                "group-roles": "superuser",
                "aud": "viki.prod.wellsky.io",
                "iss": "https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7",
                "exp": 9999999999,  # Far future expiration
                "iat": 1234567890,  # Issued at timestamp
            }

            return User(
                sub=mock_user_email,
                email=mock_user_email,
                name=mock_user_name,
                claims=mock_claims
            )
        
        # Create middleware instance to reuse validation logic
        middleware = AuthMiddleware(None)
        return await middleware._validate_jwt_token(token, settings)
        
    except Exception as e:
        logger.warning(f"Token validation failed: {str(e)}")
        return None