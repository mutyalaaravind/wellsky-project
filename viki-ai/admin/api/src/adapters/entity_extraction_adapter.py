"""
Adapter for Entity Extraction Service
"""

import httpx
from typing import List, Optional, Dict, Any
from viki_shared.utils.logger import getLogger
from viki_shared.utils.gcp_auth import get_service_account_identity_token
from viki_shared.utils.exceptions import exceptionToMap

from contracts.entity_extraction_contracts import (
    EntityExtractionPort, 
    EntityExtractionPipeline,
    LlmExecuteRequest,
    LlmExecuteResponse
)
from settings import Settings

logger = getLogger(__name__)


class EntityExtractionAdapter(EntityExtractionPort):
    """Adapter for calling the entity extraction service."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.entity_extraction_url = settings.ENTITY_EXTRACTION_API_URL
        self.timeout = 30.0

    async def _get_auth_token(self) -> str:
        """Get service account identity token for authentication."""
        try:
            # In cloud environments, get the SA identity token
            token = await get_service_account_identity_token(
                target_audience=self.entity_extraction_url
            )
            logger.debug(f"Successfully obtained SA identity token for {self.entity_extraction_url}")
            return token
        except Exception as e:
            logger.warning(f"Failed to get SA identity token: {e}. Using empty token for local development.")
            return ""

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an authenticated HTTP request to the entity extraction service."""
        url = f"{self.entity_extraction_url}/api{endpoint}"
        
        # Get authentication token
        auth_token = await self._get_auth_token()
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization header if we have a token
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Prepare extra logging data
        extra = {
            "http_request": {
                "method": "GET",
                "url": url,
                "headers": {k: v for k, v in headers.items() if k != "Authorization"},  # Don't log auth token
                "params": params
            },
            "service": "entity_extraction",
            "endpoint": endpoint
        }
        
        logger.debug(f"Making request to entity extraction service: {url}", extra=extra)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                
                # Add response details to extra
                extra["http_response"] = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_length": len(response.content) if response.content else 0
                }
                
                response.raise_for_status()
                response_data = response.json()
                
                logger.debug(f"Successfully received response from entity extraction service", extra=extra)
                return response_data
                
            except httpx.HTTPStatusError as e:
                extra["http_response"] = {
                    "status_code": e.response.status_code,
                    "headers": dict(e.response.headers),
                    "text": e.response.text,
                    "content_length": len(e.response.content) if e.response.content else 0
                }
                extra["error"] = exceptionToMap(e)
                
                logger.error(f"HTTP error calling entity extraction service: {e.response.status_code} - {e.response.text}", extra=extra)
                raise Exception(f"Entity extraction service error: {e.response.status_code}")
                
            except httpx.RequestError as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Request error calling entity extraction service: {e}", extra=extra)
                raise Exception(f"Failed to connect to entity extraction service: {e}")
            
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Unexpected error calling entity extraction service: {e}", extra=extra)
                raise

    async def _get_pipeline_by_id(self, pipeline_id: str) -> Optional[EntityExtractionPipeline]:
        """Get a pipeline configuration by its unique ID."""
        extra = {
            "operation": "_get_pipeline_by_id",
            "pipeline_id": pipeline_id
        }
        
        logger.debug(f"Fetching pipeline config by ID: {pipeline_id}", extra=extra)
        
        try:
            response_data = await self._make_request(f"/config/pipelines/{pipeline_id}")
            
            # Parse response into EntityExtractionPipeline
            pipeline_config = self._parse_pipeline_config(response_data)
            
            extra["pipeline_found"] = True
            logger.debug(f"Successfully retrieved pipeline config for ID: {pipeline_id}", extra=extra)
            
            return pipeline_config
            
        except Exception as e:
            # Check if it's a 404 (not found) - return None in that case
            if "404" in str(e) or "not found" in str(e).lower():
                extra["pipeline_found"] = False
                logger.debug(f"Pipeline config not found for ID: {pipeline_id}", extra=extra)
                return None
            
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error fetching pipeline config for ID {pipeline_id}: {e}", extra=extra)
            raise

    def _parse_pipeline_config(self, config_data: Dict[str, Any]) -> EntityExtractionPipeline:
        """Parse a pipeline configuration from API response data."""
        return EntityExtractionPipeline(
            id=config_data.get("id", ""),
            key=config_data.get("key", ""),
            name=config_data.get("name", ""),
            description=config_data.get("description"),
            scope=config_data.get("scope", "default"),
            version=config_data.get("version"),
            output_entity=config_data.get("output_entity"),
            tasks=config_data.get("tasks", []),
            auto_publish_entities_enabled=config_data.get("auto_publish_entities_enabled", True),
            labels=config_data.get("labels", []),
            app_id=config_data.get("app_id"),
            created_at=config_data.get("created_at"),
            updated_at=config_data.get("modified_at"),
            created_by=config_data.get("created_by"),
            modified_by=config_data.get("modified_by"),
            active=config_data.get("active", True)
        )

    async def get_pipeline_configs(
        self,
        labels: Optional[List[str]] = None,
        app_id: Optional[str] = None
    ) -> List[EntityExtractionPipeline]:
        """Get pipeline configurations with optional filtering."""
        extra = {
            "operation": "get_pipeline_configs",
            "filters": {
                "labels": labels,
                "app_id": app_id
            }
        }
        
        logger.debug(f"Fetching pipeline configs with filters: labels={labels}, app_id={app_id}", extra=extra)
        
        params = {}
        
        if labels and len(labels) > 0:
            # Add each label as a separate query parameter
            params = {f"labels": labels}
            
        if app_id:
            params["app_id"] = app_id
        
        try:
            response_data = await self._make_request("/config/pipelines", params)
            
            configurations = response_data.get("configurations", [])
            count = response_data.get("count", len(configurations))
            
            extra.update({
                "configurations_count": count,
                "response_filters": response_data.get("filters", {})
            })
            
            logger.debug(f"Successfully parsed {count} pipeline configurations", extra=extra)
            
            return [
                self._parse_pipeline_config(config_data)
                for config_data in configurations
            ]
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error fetching pipeline configs: {e}", extra=extra)
            raise

    async def get_templates(self) -> List[EntityExtractionPipeline]:
        """Get template pipeline configurations (label=template, any scope)."""
        extra = {
            "operation": "get_templates",
            "template_filters": {
                "labels": ["template"]
            }
        }
        
        logger.debug("Fetching template pipeline configurations", extra=extra)
        
        try:
            templates = await self.get_pipeline_configs(
                labels=["template"]
            )
            
            extra["templates_count"] = len(templates)
            logger.debug(f"Successfully retrieved {len(templates)} template configurations", extra=extra)
            
            return templates
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error fetching template configurations: {e}", extra=extra)
            raise

    async def get_pipeline_by_key(self, scope: str, pipeline_key: str) -> Optional[EntityExtractionPipeline]:
        """Get a specific pipeline configuration by scope and key."""
        extra = {
            "operation": "get_pipeline_by_key",
            "scope": scope,
            "pipeline_key": pipeline_key
        }
        
        logger.debug(f"Fetching pipeline config for scope: {scope}, key: {pipeline_key}", extra=extra)
        
        try:
            response_data = await self._make_request(f"/config/pipelines/{scope}/{pipeline_key}")
            
            # Parse response into EntityExtractionPipeline
            pipeline_config = self._parse_pipeline_config(response_data)
            
            extra["pipeline_found"] = True
            logger.debug(f"Successfully retrieved pipeline config for {scope}.{pipeline_key}", extra=extra)
            
            return pipeline_config
            
        except Exception as e:
            # Check if it's a 404 (not found) - return None in that case
            if "404" in str(e) or "not found" in str(e).lower():
                extra["pipeline_found"] = False
                logger.debug(f"Pipeline config not found for {scope}.{pipeline_key}", extra=extra)
                return None
            
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error fetching pipeline config for {scope}.{pipeline_key}: {e}", extra=extra)
            raise

    async def execute_llm(self, request: LlmExecuteRequest) -> LlmExecuteResponse:
        """Execute LLM prompt with document processing."""
        extra = {
            "operation": "execute_llm",
            "request": {
                "gs_uri": request.gs_uri,
                "has_system_instructions": request.system_instructions is not None,
                "has_json_schema": request.json_schema is not None,
                "prompt_length": len(request.prompt),
                "metadata": request.metadata
            }
        }
        
        logger.debug(f"Executing LLM request for GS URI: {request.gs_uri}", extra=extra)
        
        url = f"{self.entity_extraction_url}/api/v1/llm/execute"
        
        # Get authentication token
        auth_token = await self._get_auth_token()
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization header if we have a token
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Debug: Log the request before model_dump to see if json_schema is there
        logger.debug(f"LlmExecuteRequest before model_dump: json_schema={request.json_schema}")
        
        # Prepare request payload
        payload = request.model_dump(exclude_none=True)
        
        # Debug: Log the payload after model_dump to see if json_schema is included
        has_json_schema = "json_schema" in payload
        logger.debug(f"Request payload after model_dump: json_schema in payload={has_json_schema}, payload keys={list(payload.keys())}")
        
        extra["http_request"] = {
            "method": "POST",
            "url": url,
            "headers": {k: v for k, v in headers.items() if k != "Authorization"},
            "payload_keys": list(payload.keys())
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for LLM requests
            try:
                response = await client.post(url, headers=headers, json=payload)
                
                extra["http_response"] = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_length": len(response.content) if response.content else 0
                }
                
                response.raise_for_status()
                response_data = response.json()
                
                # Parse response into LlmExecuteResponse model
                llm_response = LlmExecuteResponse(**response_data)
                
                extra.update({
                    "llm_response": {
                        "success": llm_response.success,
                        "has_content": llm_response.content is not None,
                        "has_raw_response": llm_response.raw_response is not None,
                        "has_error": llm_response.error_message is not None
                    }
                })
                
                logger.debug(f"Successfully executed LLM request", extra=extra)
                return llm_response
                
            except httpx.HTTPStatusError as e:
                extra["http_response"] = {
                    "status_code": e.response.status_code,
                    "headers": dict(e.response.headers),
                    "text": e.response.text,
                    "content_length": len(e.response.content) if e.response.content else 0
                }
                extra["error"] = exceptionToMap(e)
                
                logger.error(f"HTTP error executing LLM request: {e.response.status_code} - {e.response.text}", extra=extra)
                
                # Try to parse error response for better error handling
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error_message", f"HTTP {e.response.status_code} error")
                except:
                    error_msg = f"HTTP {e.response.status_code} error"
                
                return LlmExecuteResponse(
                    success=False,
                    error_message=error_msg,
                    execution_metadata={"http_status": e.response.status_code}
                )
                
            except httpx.RequestError as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Request error executing LLM request: {e}", extra=extra)
                
                return LlmExecuteResponse(
                    success=False,
                    error_message=f"Failed to connect to entity extraction service: {e}",
                    execution_metadata={"connection_error": str(e)}
                )
            
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Unexpected error executing LLM request: {e}", extra=extra)
                
                return LlmExecuteResponse(
                    success=False,
                    error_message=f"Unexpected error: {e}",
                    execution_metadata={"unexpected_error": str(e)}
                )

    async def create_pipeline_from_template(
        self,
        template_id: str,
        scope: str,
        pipeline_id: str,
        pipeline_config: Dict[str, Any]
    ) -> EntityExtractionPipeline:
        """Create a new pipeline by cloning from a template with customizations."""
        extra = {
            "operation": "create_pipeline_from_template",
            "template_id": template_id,
            "scope": scope,
            "pipeline_id": pipeline_id,
            "has_config": bool(pipeline_config)
        }
        
        logger.info(f"Creating pipeline {scope}.{pipeline_id} from template {template_id}", extra=extra)
        
        url = f"{self.entity_extraction_url}/api/config/pipelines/{scope}/{pipeline_id}"
        
        # Get authentication token
        auth_token = await self._get_auth_token()
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization header if we have a token
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        # Step 1: Fetch the template pipeline configuration by ID
        logger.info(f"Fetching template pipeline by ID: {template_id}")
        template_pipeline = await self._get_pipeline_by_id(template_id)
        
        if not template_pipeline:
            raise Exception(f"Template pipeline '{template_id}' not found")
        
        # Step 2: Clone the template with customizations
        pipeline_key = f"{scope}.{pipeline_id}"
        
        # Start with template data and customize
        pipeline_definition = template_pipeline.to_dict()
        
        # Update key fields for the new pipeline
        pipeline_definition["key"] = pipeline_key
        pipeline_definition["scope"] = scope
        pipeline_definition["app_id"] = pipeline_config.get("app_id")
        
        # Update metadata fields if provided
        if pipeline_config.get("entity_name"):
            pipeline_definition["name"] = pipeline_config["entity_name"]
        if pipeline_config.get("entity_description"):
            pipeline_definition["description"] = pipeline_config["entity_description"]
        
        # Add/update labels to indicate this is generated from template
        existing_labels = pipeline_definition.get("labels", [])
        new_labels = [label for label in existing_labels if label != "template"]  # Remove template label
        new_labels.extend(["generated", "from_template", template_id])
        pipeline_definition["labels"] = list(set(new_labels))  # Remove duplicates
        
        # Step 3: Update the first prompt task with the production extraction prompt
        extraction_prompt = pipeline_config.get("extraction_prompt")
        if extraction_prompt and "tasks" in pipeline_definition:
            logger.info("Updating first prompt task with production extraction prompt")
            
            # Find the first prompt task and update its prompt
            for task in pipeline_definition["tasks"]:
                if task.get("type") == "prompt" and "prompt" in task:
                    # Replace the {extraction_prompt} placeholder with the actual prompt
                    original_prompt_template = task["prompt"].get("prompt", "")
                    if "{extraction_prompt}" in original_prompt_template:
                        updated_prompt = original_prompt_template.replace("{extraction_prompt}", extraction_prompt)
                        task["prompt"]["prompt"] = updated_prompt
                        logger.info(f"Updated prompt task with production extraction prompt")
                        break

        # Step 4: Replace tokens in entity_schema_ref URIs
        entity_name = pipeline_config.get("entity_name", "entity")
        schema_id = entity_name.lower().replace(' ', '-').replace('_', '-')

        # Build token replacement dictionary
        token_replacements = {
            "{base_url}": self.settings.PAPERGLASS_API_URL,
            "{app_id}": pipeline_config.get("app_id", ""),
            "{schema_id}": schema_id
        }

        self._replace_schema_uri_tokens(pipeline_definition, token_replacements)

        # Remove fields that should not be copied from template
        fields_to_remove = ["id", "created_at", "updated_at", "active"]
        for field in fields_to_remove:
            pipeline_definition.pop(field, None)
        
        extra["http_request"] = {
            "method": "POST",
            "url": url,
            "headers": {k: v for k, v in headers.items() if k != "Authorization"},
            "payload_keys": list(pipeline_definition.keys())
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for pipeline creation
            try:
                response = await client.post(url, headers=headers, json=pipeline_definition)
                
                extra["http_response"] = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_length": len(response.content) if response.content else 0
                }
                
                response.raise_for_status()
                response_data = response.json()
                
                # Parse response into EntityExtractionPipeline
                created_pipeline = self._parse_pipeline_config(response_data)
                
                extra.update({
                    "created_pipeline": {
                        "id": created_pipeline.id,
                        "key": created_pipeline.key,
                        "name": created_pipeline.name,
                        "scope": created_pipeline.scope,
                        "active": created_pipeline.active
                    }
                })
                
                logger.info(f"Successfully created pipeline {scope}.{pipeline_id} from template {template_id}", extra=extra)
                
                # Step 4: Auto-provision cloud task queues for the pipeline
                await self._auto_provision_pipeline_queues(created_pipeline, pipeline_config)
                
                return created_pipeline
                
            except httpx.HTTPStatusError as e:
                extra["http_response"] = {
                    "status_code": e.response.status_code,
                    "headers": dict(e.response.headers),
                    "text": e.response.text,
                    "content_length": len(e.response.content) if e.response.content else 0
                }
                extra["error"] = exceptionToMap(e)
                
                logger.error(f"HTTP error creating pipeline {scope}.{pipeline_id}: {e.response.status_code} - {e.response.text}", extra=extra)
                raise Exception(f"Entity extraction service error creating pipeline: {e.response.status_code}")
                
            except httpx.RequestError as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Request error creating pipeline {scope}.{pipeline_id}: {e}", extra=extra)
                raise Exception(f"Failed to connect to entity extraction service: {e}")
            
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                logger.error(f"Unexpected error creating pipeline {scope}.{pipeline_id}: {e}", extra=extra)
                raise

    async def _auto_provision_pipeline_queues(
        self,
        pipeline: EntityExtractionPipeline,
        pipeline_config: Dict[str, Any]
    ) -> None:
        """
        Auto-provision cloud task queues for the pipeline by examining each step's queue configuration.
        
        This method:
        1. Extracts queue names from all pipeline tasks
        2. Skips pseudo queues (DEFAULT, DIRECT)
        3. Generates all permutations by replacing tokens with actual values
        4. Creates queues if they don't exist
        5. Handles priority variants (high, default, quarantine) for {priority} token
        
        Args:
            pipeline: The created pipeline configuration
            pipeline_config: Additional configuration data from the onboarding process
        """
        extra = {
            "operation": "_auto_provision_pipeline_queues",
            "pipeline_id": pipeline.id,
            "pipeline_key": pipeline.key,
            "pipeline_scope": pipeline.scope
        }
        
        logger.info(f"Starting auto-provisioning of cloud task queues for pipeline {pipeline.key}", extra=extra)
        
        try:
            # Step 1: Extract all queue names from pipeline tasks
            queue_templates = self._extract_queue_names_from_pipeline(pipeline)
            
            if not queue_templates:
                logger.info(f"No queue names found in pipeline {pipeline.key}, skipping auto-provisioning", extra=extra)
                return
            
            # Step 2: Generate queue name permutations for each template
            queue_names_to_create = self._generate_queue_name_permutations(
                queue_templates, pipeline, pipeline_config
            )
            
            if not queue_names_to_create:
                logger.info(f"No queues to create for pipeline {pipeline.key} after filtering", extra=extra)
                return
            
            extra["queues_to_check"] = len(queue_names_to_create)
            logger.info(f"Found {len(queue_names_to_create)} queue names to provision", extra=extra)
            
            # Step 3: Check and create each queue
            created_count = 0
            skipped_count = 0
            
            for queue_name in queue_names_to_create:
                try:
                    if await self._ensure_queue_exists(queue_name):
                        created_count += 1
                        logger.debug(f"Created queue: {queue_name}")
                    else:
                        skipped_count += 1
                        logger.debug(f"Queue already exists: {queue_name}")
                        
                except Exception as e:
                    logger.warning(f"Failed to create queue {queue_name}: {e}", extra={
                        **extra,
                        "queue_name": queue_name,
                        "error": exceptionToMap(e)
                    })
            
            extra.update({
                "queues_created": created_count,
                "queues_skipped": skipped_count,
                "total_queues": len(queue_names_to_create)
            })
            
            logger.info(f"Queue auto-provisioning completed for pipeline {pipeline.key}: "
                       f"created {created_count}, skipped {skipped_count}", extra=extra)
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            logger.error(f"Error during queue auto-provisioning for pipeline {pipeline.key}: {e}", extra=extra)
            # Don't re-raise - queue provisioning failure shouldn't fail pipeline creation
            
    def _extract_queue_names_from_pipeline(self, pipeline: EntityExtractionPipeline) -> List[str]:
        """
        Extract all unique queue names from pipeline tasks, excluding pseudo queues.
        
        Args:
            pipeline: The pipeline configuration
            
        Returns:
            List of unique queue name templates
        """
        queue_names = set()
        
        if not pipeline.tasks:
            return []
        
        for task in pipeline.tasks:
            # Check if task has invoke configuration with queue_name
            if (isinstance(task, dict) and 
                task.get("invoke") and 
                isinstance(task["invoke"], dict) and 
                task["invoke"].get("queue_name")):
                
                queue_name = task["invoke"]["queue_name"]
                
                # Skip pseudo queues
                if queue_name not in ["DEFAULT", "DIRECT"]:
                    queue_names.add(queue_name)
        
        return list(queue_names)
    
    def _generate_queue_name_permutations(
        self,
        queue_templates: List[str],
        pipeline: EntityExtractionPipeline,
        pipeline_config: Dict[str, Any]
    ) -> List[str]:
        """
        Generate all permutations of queue names by replacing tokens with actual values.
        
        Args:
            queue_templates: List of queue name templates with tokens
            pipeline: The pipeline configuration
            pipeline_config: Additional configuration data
            
        Returns:
            List of actual queue names
        """
        queue_names = set()
        
        # Prepare token replacement values
        token_values = {
            "app_id": pipeline_config.get("app_id", pipeline.app_id or "unknown"),
            "scope": pipeline.scope or "default",
            "pipeline_id": pipeline.key.split(".")[-1] if "." in (pipeline.key or "") else (pipeline.key or "unknown"),
            "pipeline_key": pipeline.key or "unknown",
            "business_unit": pipeline_config.get("business_unit", "unknown"),
            "solution_code": pipeline_config.get("solution_code", "unknown")
        }
        
        # Priority values for {priority} token
        priority_values = ["high", "default", "quarantine"]
        
        for template in queue_templates:
            if "{priority}" in template:
                # Generate one queue for each priority value
                for priority in priority_values:
                    current_values = {**token_values, "priority": priority}
                    queue_name = self._replace_tokens_in_queue_name(template, current_values)
                    queue_names.add(queue_name)
            else:
                # Generate single queue without priority variants
                queue_name = self._replace_tokens_in_queue_name(template, token_values)
                queue_names.add(queue_name)
        
        return list(queue_names)
    
    def _replace_tokens_in_queue_name(self, template: str, token_values: Dict[str, str]) -> str:
        """
        Replace tokens in queue name template with actual values.

        Args:
            template: Queue name template with tokens like {app_id}
            token_values: Dictionary of token->value mappings

        Returns:
            Queue name with tokens replaced
        """
        result = template
        for token, value in token_values.items():
            result = result.replace(f"{{{token}}}", str(value))
        return result

    def _replace_schema_uri_tokens(self, pipeline_definition: Dict[str, Any], token_replacements: Dict[str, str]) -> None:
        """
        Replace tokens in entity_schema_ref schema_uri fields throughout the pipeline definition.

        This method updates schema URIs in:
        - Task entity_schema_ref fields
        - Callback entity_schema_ref fields

        Args:
            pipeline_definition: The pipeline configuration dictionary to update in-place
            token_replacements: Dictionary of token->value mappings (e.g., {"{base_url}": "http://..."})
        """
        logger.info(f"Replacing schema URI tokens with: {token_replacements}")

        if "tasks" not in pipeline_definition:
            return

        for task in pipeline_definition["tasks"]:
            # Check for entity_schema_ref in the task
            if task.get("entity_schema_ref") and task["entity_schema_ref"].get("schema_uri"):
                original_uri = task["entity_schema_ref"]["schema_uri"]
                updated_uri = original_uri
                for token, value in token_replacements.items():
                    updated_uri = updated_uri.replace(token, value)

                if updated_uri != original_uri:
                    task["entity_schema_ref"]["schema_uri"] = updated_uri
                    logger.info(f"Replaced task schema URI: {original_uri} -> {updated_uri}")

            # Check for callback with entity_schema_ref
            if task.get("callback") and task["callback"].get("entity_schema_ref"):
                callback_ref = task["callback"]["entity_schema_ref"]
                if callback_ref.get("schema_uri"):
                    original_uri = callback_ref["schema_uri"]
                    updated_uri = original_uri
                    for token, value in token_replacements.items():
                        updated_uri = updated_uri.replace(token, value)

                    if updated_uri != original_uri:
                        callback_ref["schema_uri"] = updated_uri
                        logger.info(f"Replaced callback schema URI: {original_uri} -> {updated_uri}")

    async def _ensure_queue_exists(self, queue_name: str) -> bool:
        """
        Check if a queue exists and create it if it doesn't (idempotent operation).
        
        Args:
            queue_name: The name of the queue to ensure exists
            
        Returns:
            True if queue was created, False if it already existed
            
        Raises:
            Exception: If queue creation fails for reasons other than already existing
        """
        url = f"{self.entity_extraction_url}/api/admin/cloudtask/{queue_name}"
        
        # Get authentication token
        auth_token = await self._get_auth_token()
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # First, check if queue exists
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    # Queue exists
                    return False
                elif response.status_code == 404:
                    # Queue doesn't exist, create it
                    create_url = f"{self.entity_extraction_url}/api/admin/cloudtask"
                    create_payload = {
                        "queue_name": queue_name,
                        "max_concurrent_dispatches": 10,  # Default values
                        "max_dispatches_per_second": 5.0,
                        "max_attempts": 3
                    }
                    
                    create_response = await client.post(create_url, headers=headers, json=create_payload)
                    
                    if create_response.status_code in [200, 201]:
                        return True
                    elif create_response.status_code == 409:
                        # Queue was created by another process between our check and create
                        return False
                    else:
                        create_response.raise_for_status()
                else:
                    response.raise_for_status()
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409:
                    # Queue already exists (race condition)
                    return False
                else:
                    raise Exception(f"HTTP error managing queue {queue_name}: {e.response.status_code}")
            except httpx.RequestError as e:
                raise Exception(f"Request error managing queue {queue_name}: {e}")
        
        return False