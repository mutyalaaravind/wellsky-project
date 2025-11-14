import base64
from functools import wraps
from functools import wraps
import asyncio
from logging import Logger
import jwt,json
import aiohttp
from typing import Dict, Optional
from kink import inject
from aiocache import cached, Cache
from paperglass.usecases.configuration import get_config
from paperglass.domain.values import Configuration
from paperglass.domain.utils.exception_utils import UnAuthorizedException, exceptionToMap
from paperglass.settings import OKTA_CLIENT_SECRET,OKTA_AUDIENCE
from paperglass.settings import OKTA_TOKEN_ISSUER_URL,OKTA_CLIENT_ID,OKTA_VERIFY, OKTA_SERVICE_ISSUER_URL, OKTA_SERVICE_AUDIENCE, CONFIG_CACHE_TTL
from okta_jwt_verifier import JWTVerifier
from okta_jwt_verifier.exceptions import JWTValidationException
from jose.exceptions import ExpiredSignatureError
from starlette.responses import JSONResponse

from paperglass.domain.context import Context
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.infrastructure.ports import IQueryPort

_logger = Logger(__name__)

@inject
def decode_token(view_func, query: IQueryPort):
    @wraps(view_func)
    async def wrapper(starlette, request, *args, **kwargs):
        from paperglass.log import getLogger

        LOGGER = getLogger(__name__)
        # Check if the JWT token exists in the request
        if 'Authorization' not in request.headers:
            raise Exception('JWT token is missing')
        #LOGGER.debug(f"Request headers: {request.headers}")
        # # Extract the JWT token from the request
        if 'Authorization2' in request.headers:
            if len(request.headers['Authorization2'].split(' '))!=2:
                raise Exception('Authorization2 header is present but JWT token is missing!')
            token = request.headers['Authorization2'].split(' ')[1]
        else:
            token = request.headers['Authorization'].split(' ')[1]
        
        try:
            # need to remove this once demo dashboard app is refactored to use signed tokens
            decoded_token = base64.b64decode(token).decode('utf-8') 
        except Exception as e:
            decoded_token = jwt.decode(token,key='', algorithms=['HS256'], options={"verify_signature": False})
        # # Perform any additional validation or processing here
        # decoded_token = token # ToDo: Decode the JWT token
        # app_id = decoded_token.get("app_id")
        # tenant_id = decoded_token.get("tenant_id")
        # untill we implement this, we will return some dummy value
        if isinstance(decoded_token, str):
            decoded_token = json.loads(decoded_token)
        app_id=decoded_token.get("appId")
        tenant_id=decoded_token.get("tenantId")
        patient_id=decoded_token.get("patientId")
        user_id = decoded_token.get("userId") or decoded_token.get("amuserkey")

        config: Configuration = await get_config(app_id, tenant_id, query)

        if config and config.token_validation and config.token_validation.enabled:
            LOGGER.debug(f"Token validation is enabled for app_id: {app_id}, tenant_id: {tenant_id}")
            is_valid = await validate_token_signature(token, config)
            if not is_valid:
                LOGGER.warning(f"Invalid token signature for app_id: {app_id}, tenant_id: {tenant_id}")
                raise UnAuthorizedException("Invalid token signature")
            else:
                LOGGER.debug(f"Token signature is valid for app_id: {app_id}, tenant_id: {tenant_id}")
        
        user = {
            "username": user_id
        }
        ctx = Context()
        await ctx.setUser(user)
        baseAggregate = {
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id            
        }
        await ctx.setBaseAggregate(baseAggregate)

        request.scope['app_id'] = str(app_id) if app_id else None
        request.scope['tenant_id'] = str(tenant_id) if tenant_id else None
        request.scope['patient_id'] = str(patient_id) if patient_id else None
        request.scope['token'] = token
        request.scope['user_id'] = str(user_id) if user_id else None
        request.scope['okta_token'] = request.headers.get('okta-token') or request.headers.get('Okta-Token')
        request.scope['ehr_token'] = request.headers.get('ehr-token') or request.headers.get('Ehr-Token')

        # Return the JWT token
        return await view_func(starlette,request,*args, **kwargs)

    return wrapper

async def verify_okta_token(okta_token,issuer_url,client_id,audience):
    if OKTA_VERIFY:
            try:
                jwt_verifier = JWTVerifier(issuer_url.replace("/v1/token",""), client_id, audience)
                result = await jwt_verifier.verify_access_token(okta_token)
                _logger.debug(f"okta token validation success: {result}")
            except JWTValidationException as e:
                    # this flag is to test okta validation in every env.
                    # if it is good, we remove this flag
                    _logger.warning(f"invalid okta token: {e}")
                    raise UnAuthorizedException(f"Invalid Okta token: {e}")
            except ExpiredSignatureError as e:
                _logger.warning(f"expired okta token: {e}")
                raise UnAuthorizedException(f"Expired Okta token: {e}")
            except Exception as e:
                _logger.warning(f"Error verifying okta token: {e}")
                raise Exception(f"Error verifying okta token: {e}")

def verify_okta(view_func):
    @wraps(view_func)
    async def wrapper(starlette, request, *args, **kwargs):
        try:
            jwt_token = request.headers.get('okta-token') or request.headers.get('Okta-Token') or request.headers.get('OktaToken')
            if jwt_token is None:
                raise UnAuthorizedException("JWT token missing")
            
            claims = extract_elements_from_token(jwt_token)
            issuer_url = claims.get("iss")

            issuer_version = issuer_url_version(issuer_url)

            if issuer_version == 2:
                client_id = claims.get("cid")
                audience = OKTA_SERVICE_AUDIENCE
            elif issuer_version == 1:
                client_id = OKTA_CLIENT_ID
                audience = OKTA_AUDIENCE            

            if not is_valid_issuer_url(issuer_url):
                raise UnAuthorizedException(f"Invalid issuer URL: {issuer_url}")
            
            await verify_okta_token(jwt_token,
                            issuer_url,
                            client_id,
                            audience
                            )
        except UnAuthorizedException as e:
            return JSONResponse(status_code=401, content={"error": str(e)})
        return await view_func(starlette,request,*args, **kwargs)

    return wrapper


def verify_service_okta(view_func):
    @wraps(view_func)
    async def wrapper(starlette, request, *args, **kwargs):
        try:
            header = request.headers.get('Authorization')
            if header is None:
                raise UnAuthorizedException("Authorization missing")
            
            jwt_token = header.split(' ')[1]
            if jwt_token is None:
                raise UnAuthorizedException("JWT token missing")
            
            claims = extract_elements_from_token(jwt_token)

            issuer_url = claims.get("iss")
            if not is_valid_issuer_url(issuer_url):
                raise UnAuthorizedException(f"Invalid issuer URL: {issuer_url}")

            await verify_okta_token(jwt_token,
                            claims.get("iss"),
                            claims.get("cid"),
                            claims.get("aud")
                            )
        except UnAuthorizedException as e:
            return JSONResponse(status_code=401, content={"error": str(e)})
        return await view_func(starlette,request,*args, **kwargs)

    return wrapper


def extract_elements_from_token(token):
    decoded_token = jwt.decode(token, key='', algorithms=['HS256'], options={"verify_signature": False})
        
    # Extract elements
    elements = {
        "cid": decoded_token.get("cid"),
        # Add other elements you want to extract here
        "sub": decoded_token.get("sub"),
        "iss": decoded_token.get("iss"),
        "aud": decoded_token.get("aud")
    }
    
    return elements

def is_valid_issuer_url(issuer_url):
    # Check if the issuer URL is valid
    if issuer_url == OKTA_SERVICE_ISSUER_URL or issuer_url == OKTA_TOKEN_ISSUER_URL.replace("/v1/token",""):
        return True
    else:
        return False
    
def issuer_url_version(issuer_url):
    # Check if the issuer URL is valid
    if issuer_url == OKTA_SERVICE_ISSUER_URL:
        return 2
    elif issuer_url == issuer_url == OKTA_TOKEN_ISSUER_URL.replace("/v1/token",""):
        return 1
    else:
        raise UnAuthorizedException(f"Invalid issuer URL: {issuer_url}")


@cached(ttl=CONFIG_CACHE_TTL, cache=Cache.MEMORY)
async def _fetch_jwks(jwks_url: str) -> Dict:
    """
    Fetch JWKS from the given URL with caching.
    
    Args:
        jwks_url: The URL to fetch JWKS from
        
    Returns:
        Dict containing the JWKS data
        
    Raises:
        Exception: If JWKS cannot be fetched or parsed
    """
    from paperglass.log import getLogger
    logger = getLogger(__name__)
    extra = {
        "jwks_url": jwks_url,
        "cache_ttl": CONFIG_CACHE_TTL
    }
    try:
        logger.debug(f"Fetching JWKS from URL: {jwks_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(jwks_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch JWKS: HTTP {response.status}")
                
                jwks_data = await response.json()
                logger.debug(f"Successfully fetched JWKS from: {jwks_url}", extra=extra)
                return jwks_data
                
    except aiohttp.ClientError as e:
        extra.update({"error": exceptionToMap(e)})
        logger.error(f"Network error fetching JWKS from {jwks_url}: {e}", extra=extra)
        raise Exception(f"Network error fetching JWKS: {e}")
    except json.JSONDecodeError as e:
        extra.update({"error": exceptionToMap(e)})
        logger.error(f"Invalid JSON in JWKS response from {jwks_url}: {e}", extra=extra)
        raise Exception(f"Invalid JSON in JWKS response: {e}")
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        logger.error(f"Unexpected error fetching JWKS from {jwks_url}: {e}", extra=extra)
        raise Exception(f"Error fetching JWKS: {e}")


def _get_public_key_from_jwks(jwks: Dict, kid: str) -> Optional[str]:
    """
    Extract the public key from JWKS for the given key ID.
    
    Args:
        jwks: The JWKS data
        kid: The key ID to look for
        
    Returns:
        The public key in PEM format, or None if not found
    """
    from paperglass.log import getLogger
    logger = getLogger(__name__)
    
    try:
        keys = jwks.get('keys', [])
        for key in keys:
            if key.get('kid') == kid:
                # Convert JWK to PEM format using PyJWT
                from jwt.algorithms import RSAAlgorithm
                public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                logger.debug(f"Found matching public key for kid: {kid}")
                return public_key
        
        logger.warning(f"No matching key found for kid: {kid}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting public key from JWKS for kid {kid}: {e}")
        return None


def verify_gcp_service_account(view_func):
    """
    Decorator to verify GCP service account identity tokens.
    Validates that the Authorization header contains a valid GCP service account identity token.
    """
    @wraps(view_func)
    async def wrapper(starlette, request, *args, **kwargs):
        from paperglass.log import getLogger
        logger = getLogger(__name__)
        
        try:
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                logger.warning("GCP service account validation failed: Authorization header missing")
                return JSONResponse(status_code=401, content={"error": "Authorization header required"})
            
            # Extract Bearer token
            if not auth_header.startswith('Bearer '):
                logger.warning("GCP service account validation failed: Invalid Authorization header format")
                return JSONResponse(status_code=401, content={"error": "Invalid Authorization header format"})
            
            token = auth_header.split(' ')[1]
            if not token:
                logger.warning("GCP service account validation failed: Empty token")
                return JSONResponse(status_code=401, content={"error": "Empty token"})
            
            # Validate GCP service account identity token
            is_valid = await _validate_gcp_identity_token(token)
            if not is_valid:
                logger.warning("GCP service account validation failed: Invalid token")
                return JSONResponse(status_code=401, content={"error": "Invalid GCP service account token"})
            
            logger.debug("GCP service account token validation successful")
            return await view_func(starlette, request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error during GCP service account validation: {e}")
            return JSONResponse(status_code=401, content={"error": "Token validation failed"})
    
    return wrapper


def verify_gcp_service_account(view_func, query: IQueryPort = None):
    """
    Decorator to validate Google Cloud service account identity tokens.
    Specifically designed for M2M communication from Admin API.
    """
    @wraps(view_func)
    async def wrapper(starlette, request, *args, **kwargs):
        from paperglass.log import getLogger

        LOGGER = getLogger(__name__)

        # Check if the Authorization header exists
        if 'Authorization' not in request.headers:
            LOGGER.warning("Missing Authorization header for GCP service account endpoint")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing Authorization header"}
            )

        # Extract the token
        auth_header = request.headers['Authorization']
        if not auth_header.startswith('Bearer '):
            LOGGER.warning("Invalid Authorization header format")
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid Authorization header format"}
            )

        token = auth_header.split(' ')[1]

        try:
            # Validate the GCP identity token
            is_valid = await _validate_gcp_identity_token(token)
            if not is_valid:
                LOGGER.warning("Invalid GCP service account identity token")
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid GCP service account token"}
                )

            LOGGER.debug("GCP service account token validation successful")
            return await view_func(starlette, request, *args, **kwargs)

        except Exception as e:
            LOGGER.error(f"Error during GCP service account validation: {e}")
            return JSONResponse(
                status_code=401,
                content={"error": "Token validation failed"}
            )

    return wrapper


async def _validate_gcp_identity_token(token: str) -> bool:
    """
    Validate GCP identity token with enhanced development mode support.

    Args:
        token: The GCP identity token to validate

    Returns:
        bool: True if the token is valid, False otherwise
    """
    from paperglass.log import getLogger
    from paperglass.settings import CLOUD_PROVIDER, SERVICE_ACCOUNT_EMAIL
    logger = getLogger(__name__)

    # Check for local development environment
    if CLOUD_PROVIDER == "local":
        try:
            # Decode without verification for development
            import jwt
            decoded = jwt.decode(token, options={"verify_signature": False})

            # Check if it's a valid Google-issued token structure
            if (decoded.get("iss") == "https://accounts.google.com" and
                SERVICE_ACCOUNT_EMAIL in str(decoded.get("sub", ""))):
                logger.debug(f"Accepting GCP identity token in local development mode for {SERVICE_ACCOUNT_EMAIL}")
                return True
        except Exception as e:
            logger.debug(f"Local development token validation failed: {e}")

    # Production GCP token validation
    try:
        # Import Google auth libraries
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        # Create a request object for token verification
        request = google_requests.Request()
        
        # Verify the token
        # This will validate the signature, expiration, and issuer
        id_info = id_token.verify_oauth2_token(token, request)
        
        # Additional validation: check if it's from Google's service account
        if id_info.get('iss') not in ['https://accounts.google.com', 'accounts.google.com']:
            logger.warning(f"Invalid issuer in GCP identity token: {id_info.get('iss')}")
            return False
        
        # Check if token has email claim for service account validation
        email = id_info.get('email')
        if email:
            # If email is present, validate it's a service account
            if not email.endswith('.gserviceaccount.com'):
                logger.warning(f"Token email does not appear to be a service account: {email}")
                return False
            logger.debug(f"GCP identity token validation successful for service account: {email}")
        else:
            # If no email claim, check if it has 'sub' claim which indicates a service account
            sub = id_info.get('sub')
            if not sub:
                logger.warning("GCP identity token missing both email and sub claims")
                return False
            logger.debug(f"GCP identity token validation successful for service account with sub: {sub}")
        
        logger.debug(f"GCP identity token validation successful for service account: {email}")
        return True
        
    except ValueError as e:
        # Token is invalid
        logger.warning(f"GCP identity token validation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during GCP identity token validation: {e}")
        return False


async def validate_token_signature(token: str, config: Configuration) -> bool:
    """
    Validate the signature of a JWT token against JWKS retrieved from the configuration.
    
    Args:
        token: The JWT token to validate
        config: Configuration object containing token validation settings
        
    Returns:
        bool: True if the token signature is valid, False otherwise
        
    Raises:
        Exception: For configuration errors or critical validation failures
    """
    from paperglass.log import getLogger
    logger = getLogger(__name__)

    extra = {
        "token": token,
    }

    logger.debug("Starting token signature validation", extra=extra)
    
    # Validate inputs
    if not token:
        logger.warning("Token validation failed: empty token provided", extra=extra)
        raise UnAuthorizedException("Invalid token signature: Empty token provided")
    
    if not config or not config.token_validation:
        logger.warning("Token validation failed: no token validation configuration", extra=extra)
        raise UnAuthorizedException("Invalid token signature: No token validation configuration found")
    
    if not config.token_validation.enabled:
        logger.debug("Token validation is disabled in configuration", extra=extra)
        return True  # If validation is disabled, consider token valid
    
    try:
        # Decode token header to get the key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        if not kid:
            logger.warning("Token validation failed: no 'kid' in token header", extra=extra)
            raise UnAuthorizedException("Invalid token signature: No 'kid' in token header")
        
        logger.debug(f"Validating token with kid: {kid}")
        
        # Determine JWKS URL
        jwks_url = config.token_validation.jwks_url
        if not jwks_url:
            # Fallback: use issuer claim from token + "/v1/keys"
            try:
                unverified_payload = jwt.decode(token, options={"verify_signature": False})
                issuer = unverified_payload.get('iss')
                if not issuer:
                    logger.error("Token validation failed: no JWKS URL configured and no 'iss' claim in token", extra=extra)
                    raise Exception("No JWKS URL configured and no 'iss' claim in token")
                
                # Strip trailing slash from issuer and append "/v1/keys"
                issuer = issuer.rstrip('/')
                jwks_url = f"{issuer}/v1/keys"
                logger.debug(f"Using fallback JWKS URL from token issuer: {jwks_url}")
                
            except Exception as e:
                extra.update({
                    "error": exceptionToMap(e)
                })
                logger.error(f"Failed to extract issuer from token for JWKS URL fallback: {e}", extra=extra)
                raise Exception("Token validation enabled but no JWKS URL configured and cannot extract issuer from token")
        
        # Fetch JWKS
        jwks = await _fetch_jwks(jwks_url)
        
        # Get the public key for this kid
        public_key = _get_public_key_from_jwks(jwks, kid)
        if not public_key:
            logger.warning(f"Token validation failed: no public key found for kid: {kid}", extra=extra)
            return False
        
        # Verify the token signature
        try:
            # Decode and verify the token
            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=['RS256', 'RS384', 'RS512'],  # Common RSA algorithms
                options={"verify_signature": True, "verify_exp": True}
            )
            logger.debug("Token signature validation successful", extra=extra)
            return True
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: token has expired", extra=extra)
            return False
        except jwt.InvalidSignatureError:
            logger.warning("Token validation failed: invalid signature", extra=extra)
            return False
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: invalid token - {e}", extra=extra)
            return False
            
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e)
        })
        logger.error(f"Unexpected error during token signature validation: {e}")
        # For unexpected errors, we should fail securely
        return False
