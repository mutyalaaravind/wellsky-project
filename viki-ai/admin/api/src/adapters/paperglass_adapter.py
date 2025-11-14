"""
Adapter for Paperglass API
"""

import httpx
from typing import Optional, Dict, Any, List
from viki_shared.utils.logger import getLogger
from viki_shared.utils.gcp_auth import get_service_account_identity_token
from viki_shared.utils.exceptions import exceptionToMap

from contracts.paperglass import PaperglassPort, AppConfigResponse, AppConfigUpdateRequest, EntitySchemaCreateRequest, EntitySchemaCreateResponse
from settings import Settings

logger = getLogger(__name__)


class PaperglassAdapter(PaperglassPort):
    """Adapter for calling the Paperglass API."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.paperglass_url = settings.PAPERGLASS_API_URL
        self.timeout = 30.0

    async def _get_auth_token(self) -> str:
        """Get service account identity token for authentication."""
        try:
            # This should work in both cloud and local environments with ADC
            token = await get_service_account_identity_token(
                target_audience=self.paperglass_url
            )
            logger.debug(f"Successfully obtained SA identity token for {self.paperglass_url}")
            return token
        except Exception as e:
            # More specific error handling to understand why token acquisition fails
            logger.error(f"Failed to get SA identity token: {e}. Check ADC setup and service account permissions.")
            # Instead of returning empty string, we should fail fast with helpful guidance
            raise Exception(
                f"Authentication failed: Unable to obtain identity token for {self.paperglass_url}. "
                f"For local development, ensure 'gcloud auth application-default login --impersonate-service-account=admin-api@viki-dev-app-wsky.iam.gserviceaccount.com' is configured. "
                f"Original error: {e}"
            )

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET", json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an authenticated HTTP request to the Paperglass API."""
        url = f"{self.paperglass_url}{endpoint}"

        # Get authentication token - this should always succeed with proper ADC setup
        try:
            auth_token = await self._get_auth_token()
        except Exception as e:
            logger.error(f"Authentication failed for {url}: {e}")
            # Provide helpful guidance for local development
            logger.error("For local development, ensure you're logged in with: gcloud auth application-default login --impersonate-service-account=admin-api@viki-dev-app-wsky.iam.gserviceaccount.com")
            raise

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"  # Always include Authorization header
        }
        
        # Prepare extra logging data
        extra = {
            "http_request": {
                "method": method,
                "url": url,
                "headers": {k: v for k, v in headers.items() if k != "Authorization"},  # Don't log auth token
                "params": params,
                "has_json_data": json_data is not None
            },
            "service": "paperglass",
            "endpoint": endpoint
        }
        
        logger.debug(f"Making request to Paperglass API: {url}", extra=extra)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, params=params, json=json_data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, params=params, json=json_data)
                else:
                    raise Exception(f"Unsupported HTTP method: {method}")
                
                # Add response details to extra
                extra["http_response"] = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_length": len(response.content) if response.content else 0
                }
                
                response.raise_for_status()
                response_data = response.json()
                
                logger.debug(f"Successfully received response from Paperglass API", extra=extra)
                return response_data
                
            except httpx.HTTPStatusError as e:
                extra["http_response"] = {
                    "status_code": e.response.status_code,
                    "headers": dict(e.response.headers),
                    "text": e.response.text,
                    "content_length": len(e.response.content) if e.response.content else 0
                }
                extra["error"] = exceptionToMap(e)

                # Handle 404 as None (not found) - this is expected behavior during onboarding
                if e.response.status_code == 404:
                    logger.debug(f"Resource not found (404) from Paperglass API: {e.response.text}", extra=extra)
                    return None

                # Log other HTTP errors as actual errors
                logger.error(f"HTTP error calling Paperglass API: {e.response.status_code} - {e.response.text}", extra=extra)

                raise Exception(f"Paperglass API error: {e.response.status_code}")
                
            except httpx.RequestError as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Request error calling Paperglass API: {e}", extra=extra)
                raise Exception(f"Failed to connect to Paperglass API: {e}")
            
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Unexpected error calling Paperglass API: {e}", extra=extra)
                raise

    async def get_app_config(self, app_id: str, generate_if_missing: bool = False) -> Optional[AppConfigResponse]:
        """
        Get app configuration for the given app_id.
        
        Args:
            app_id: The application identifier
            
        Returns:
            AppConfigResponse if found, None if not found
            
        Raises:
            Exception: If there's an error calling the API
        """
        extra = {
            "operation": "get_app_config",
            "app_id": app_id
        }
        
        logger.debug(f"Fetching app config for app_id: {app_id}", extra=extra)
        
        try:
            # Call the /api/v1/configs/{app_id} endpoint 
            params = {"generate_if_missing": str(generate_if_missing).lower()}
            response_data = await self._make_request(f"/api/v1/configs/{app_id}", params)
            
            # Handle case where app config is not found
            if response_data is None:
                logger.debug(f"App config not found for app_id: {app_id}", extra=extra)
                return None
            
            # Parse the response into AppConfigResponse
            # Note: The Paperglass API returns the Configuration object directly
            # We need to construct an AppConfigResponse with the config data
            app_config = AppConfigResponse(
                id=response_data.get("id", app_id),  # Use actual ID if available
                app_id=app_id,
                name=response_data.get("name"),
                description=response_data.get("description"),
                config=response_data.get("config", response_data),  # Config might be nested or the whole response
                active=response_data.get("active", True),
                created_at=response_data.get("created_at", "1970-01-01T00:00:00Z"),
                modified_at=response_data.get("modified_at", "1970-01-01T00:00:00Z"),
                created_by=response_data.get("created_by"),
                modified_by=response_data.get("modified_by")
            )
            
            extra["config_found"] = True
            logger.debug(f"Successfully retrieved app config for app_id: {app_id}", extra=extra)
            
            return app_config
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error fetching app config for app_id {app_id}: {e}", extra=extra)
            raise

    async def list_app_configs(self, limit: int = 50, offset: int = 0) -> List[AppConfigResponse]:
        """
        List all app configurations with pagination.
        
        Args:
            limit: Maximum number of configs to return (default: 50)
            offset: Number of configs to skip (default: 0)
            
        Returns:
            List of AppConfigResponse objects
            
        Raises:
            Exception: If there's an error calling the API
        """
        extra = {
            "operation": "list_app_configs",
            "limit": limit,
            "offset": offset
        }
        
        logger.debug(f"Listing app configs with limit: {limit}, offset: {offset}", extra=extra)
        
        try:
            # Call the /api/v1/configs endpoint with pagination parameters
            params = {
                "limit": str(limit),
                "offset": str(offset)
            }
            response_data = await self._make_request("/api/v1/configs", params)
            
            # Handle case where no configs are found
            if response_data is None or not response_data:
                logger.debug("No app configs found", extra=extra)
                return []
            
            # Parse the response into list of AppConfigResponse objects
            app_configs = []
            configs_list = response_data if isinstance(response_data, list) else response_data.get("configs", [])
            
            for config_data in configs_list:
                app_config = AppConfigResponse(
                    id=config_data.get("id", config_data.get("app_id", "")),
                    app_id=config_data.get("app_id", ""),
                    name=config_data.get("name"),
                    description=config_data.get("description"),
                    config=config_data.get("config", config_data),  # Config might be nested or the whole response
                    active=config_data.get("active", True),
                    created_at=config_data.get("created_at", "1970-01-01T00:00:00Z"),
                    modified_at=config_data.get("modified_at", "1970-01-01T00:00:00Z"),
                    created_by=config_data.get("created_by"),
                    modified_by=config_data.get("modified_by")
                )
                app_configs.append(app_config)
            
            extra.update({
                "configs_found": len(app_configs),
                "total_returned": len(app_configs)
            })
            
            logger.debug(f"Successfully retrieved {len(app_configs)} app configs", extra=extra)
            
            return app_configs
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error listing app configs: {e}", extra=extra)
            raise

    async def update_app_config(self, app_id: str, config_update: AppConfigUpdateRequest) -> AppConfigResponse:
        """
        Update app configuration for the given app_id.
        
        Args:
            app_id: The application identifier
            config_update: The configuration update request
            
        Returns:
            Updated AppConfigResponse
            
        Raises:
            Exception: If there's an error calling the API
        """
        extra = {
            "operation": "update_app_config",
            "app_id": app_id,
            "archive_current": config_update.archive_current
        }
        
        logger.debug(f"Updating app config for app_id: {app_id}", extra=extra)
        
        try:
            # Prepare the update payload
            update_payload = {
                "app_id": app_id,  # Always include app_id
                "config": config_update.config,
                "archive_current": config_update.archive_current
            }
            
            # Add root-level name and description if provided
            if config_update.name:
                update_payload["name"] = config_update.name
            if config_update.description:
                update_payload["description"] = config_update.description
            
            if config_update.version_comment:
                update_payload["version_comment"] = config_update.version_comment
            
            # Add active field to the update payload
            update_payload["active"] = True
            
            # Call the POST /api/admin/config endpoint with proper archiving support
            response_data = await self._make_request(
                "/api/admin/config", 
                method="POST",
                json_data=update_payload
            )
            
            # Handle case where update failed
            if response_data is None:
                logger.error(f"Failed to update app config for app_id: {app_id}", extra=extra)
                raise Exception(f"Failed to update app config for app_id: {app_id}")
            
            # Parse the response into AppConfigResponse
            # The Paperglass admin API returns a nested response structure
            if "data" in response_data and isinstance(response_data["data"], dict):
                config_data = response_data["data"]
                app_config = AppConfigResponse(
                    id=config_data.get("id", app_id),
                    app_id=config_data.get("app_id", app_id),
                    name=config_data.get("name"),
                    description=config_data.get("description"),
                    config=config_data.get("config", {}),
                    active=config_data.get("active", True),
                    created_at=config_data.get("created_at", "1970-01-01T00:00:00Z"),
                    modified_at=config_data.get("modified_at", "1970-01-01T00:00:00Z"),
                    created_by=config_data.get("created_by"),
                    modified_by=config_data.get("modified_by")
                )
            else:
                # Fallback to original parsing if structure is different
                app_config = AppConfigResponse(
                    id=app_id,
                    app_id=app_id,
                    config=response_data,
                    active=True,
                    created_at=response_data.get("created_at", "1970-01-01T00:00:00Z"),
                    modified_at=response_data.get("modified_at", "1970-01-01T00:00:00Z"),
                    created_by=response_data.get("created_by"),
                    modified_by=response_data.get("modified_by")
                )
            
            extra.update({
                "config_updated": True,
                "updated_at": app_config.modified_at
            })
            
            logger.debug(f"Successfully updated app config for app_id: {app_id}", extra=extra)
            
            return app_config
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error updating app config for app_id {app_id}: {e}", extra=extra)
            raise

    async def create_entity_schema(self, schema_request: EntitySchemaCreateRequest) -> EntitySchemaCreateResponse:
        """
        Create a new entity schema via PaperGlass API.
        
        Args:
            schema_request: The entity schema creation request
            
        Returns:
            EntitySchemaCreateResponse with creation details
            
        Raises:
            Exception: If there's an error calling the API
        """
        extra = {
            "operation": "create_entity_schema",
            "app_id": schema_request.app_id,
            "schema_name": schema_request.name
        }
        
        logger.debug(f"Creating entity schema: {schema_request.name} for app_id: {schema_request.app_id}", extra=extra)
        
        try:
            # Prepare the request payload matching PaperGlass API format
            payload = {
                "name": schema_request.name,
                "description": schema_request.description,
                "app_id": schema_request.app_id,
                "label": schema_request.label,
                "required_scopes": schema_request.required_scopes,
                "schema": schema_request.schema
            }
            
            # Remove None values to avoid sending them
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # DEBUG: Log the exact payload being sent to PaperGlass
            logger.info(f"Entity schema payload being sent to PaperGlass: app_id={payload.get('app_id')}, name={payload.get('name')}")
            
            # Call the POST /api/admin/entity_schema endpoint
            response_data = await self._make_request(
                "/api/admin/entity_schema", 
                method="POST",
                json_data=payload
            )
            
            # Handle case where creation failed
            if response_data is None or not response_data.get("success", False):
                error_msg = response_data.get("error", "Unknown error") if response_data else "No response from API"
                logger.error(f"Failed to create entity schema: {error_msg}", extra=extra)
                raise Exception(f"Failed to create entity schema: {error_msg}")
            
            # Parse the response into EntitySchemaCreateResponse
            entity_schema_response = EntitySchemaCreateResponse(
                success=response_data.get("success", False),
                schema_id=response_data.get("schema_id", ""),
                message=response_data.get("message", ""),
                id=response_data.get("id"),
                title=response_data.get("title"),
                app_id=response_data.get("app_id")
            )
            
            extra.update({
                "schema_created": True,
                "schema_id": entity_schema_response.schema_id,
                "entity_id": entity_schema_response.id
            })
            
            logger.debug(f"Successfully created entity schema: {entity_schema_response.schema_id}", extra=extra)
            
            return entity_schema_response
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error creating entity schema: {e}", extra=extra)
            raise

    async def submit_external_document(
        self, 
        gs_uri: str, 
        app_id: str, 
        tenant_id: str, 
        patient_id: str, 
        host_file_id: str,
        file_name: str,
        file_type: str = "application/pdf",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit an external document to PaperGlass for processing.
        
        Args:
            gs_uri: Google Cloud Storage URI of the document
            app_id: Application identifier
            tenant_id: Tenant identifier
            patient_id: Patient identifier (subject_id in admin demo context)
            host_file_id: Document identifier from the host system
            file_name: Name of the file
            file_type: MIME type of the file (default: application/pdf)
            metadata: Optional metadata including integration overrides
            
        Returns:
            Dict with response from PaperGlass API
            
        Raises:
            Exception: If there's an error calling the API
        """
        extra = {
            "operation": "submit_external_document",
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id,
            "host_file_id": host_file_id,
            "gs_uri": gs_uri,
            "has_integration_override": metadata and "integration" in metadata if metadata else False
        }
        
        logger.info(f"Submitting external document to PaperGlass: {file_name}", extra=extra)
        
        try:
            from datetime import datetime
            
            # Prepare the external document creation payload
            payload = {
                "appId": app_id,
                "tenantId": tenant_id,
                "patientId": patient_id,
                "hostFileId": host_file_id,
                "fileName": file_name,
                "fileType": file_type,
                "createdOn": datetime.now().isoformat(),
                "repositoryType": "URI",
                "uri": {
                    "uri": gs_uri
                },
                "metadata": metadata or {}
            }
            
            # Call the POST internal document create endpoint
            response_data = await self._make_request(
                self.settings.PAPERGLASS_INTERNAL_DOCUMENT_CREATE_ENDPOINT, 
                method="POST",
                json_data=payload
            )
            
            # Handle case where submission failed
            if response_data is None:
                logger.error(f"Failed to submit external document: {file_name}", extra=extra)
                raise Exception(f"Failed to submit external document: {file_name}")
            
            extra.update({
                "document_submitted": True,
                "response_status": response_data.get("status", "unknown")
            })
            
            logger.info(f"Successfully submitted external document to PaperGlass: {file_name}", extra=extra)
            
            return response_data
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error submitting external document {file_name}: {e}", extra=extra)
            raise

    async def get_document_status(
        self,
        document_id: str,
        app_id: str,
        tenant_id: str,
        patient_id: str
    ) -> Dict[str, Any]:
        """
        Get document processing status from PaperGlass.

        Args:
            document_id: The document identifier (same as host_file_id used in submission)
            app_id: Application identifier
            tenant_id: Tenant identifier
            patient_id: Patient identifier (subject_id in admin demo context)

        Returns:
            Dict with response from PaperGlass status API including progress data from DJT

        Raises:
            Exception: If there's an error calling the API
        """
        extra = {
            "operation": "get_document_status",
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id,
            "document_id": document_id
        }

        logger.info(f"Getting document status from PaperGlass: {document_id}", extra=extra)

        try:
            # Call the PaperGlass V1 API status endpoint with proper authentication
            params = {
                "host_attachment_id": document_id,  # Admin UI passes host_attachment_id as document_id
                "app_id": app_id,
                "tenant_id": tenant_id,
                "patient_id": patient_id
            }

            response_data = await self._make_request(
                "/api/v1/documents/status",
                params=params
            )

            # Handle case where document status is not found
            if response_data is None:
                logger.warning(f"Document status not found for document_id: {document_id}", extra=extra)
                return {
                    "pipelineStatuses": [],
                    "status": "NOT_STARTED",
                    "failed": 0
                }

            extra.update({
                "status_retrieved": True,
                "pipeline_count": len(response_data.get("pipelineStatuses", []))
            })

            logger.info(f"Successfully retrieved document status from PaperGlass: {document_id}", extra=extra)

            return response_data

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error getting document status for document_id {document_id}: {e}", extra=extra)
            raise