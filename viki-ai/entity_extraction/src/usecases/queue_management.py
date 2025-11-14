"""
Queue Management Service for Entity Extraction API.

This service handles the auto-provisioning of cloud task queues for pipelines,
eliminating the need for manual queue creation and cross-service dependencies.
"""

import asyncio
import re
from typing import Dict, List, Optional, Set, Any
from models.pipeline_config import PipelineConfig
from models.app_config import AppConfigCache, QueueInfo, QueueProvisioningResult, QueueProvisioningConfig
from adapters.firestore import FirestoreAdapter
from adapters.cloud_tasks import CloudTaskAdapter
from util.custom_logger import getLogger
from util.exception import exceptionToMap

LOGGER = getLogger(__name__)


class QueueManagementService:
    """
    Service for managing cloud task queue provisioning for pipelines.
    
    This service handles:
    - Extracting queue names from pipeline configurations
    - Generating queue name permutations with token replacement
    - Auto-provisioning cloud task queues
    - Caching app configurations locally to eliminate cross-service calls
    """
    
    def __init__(
        self, 
        firestore_adapter: FirestoreAdapter,
        cloud_tasks_adapter: CloudTaskAdapter,
        paperglass_api_url: Optional[str] = None
    ):
        """
        Initialize the queue management service.
        
        Args:
            firestore_adapter: Adapter for Firestore operations
            cloud_tasks_adapter: Adapter for Cloud Tasks operations
            paperglass_api_url: Optional URL for PaperGlass API (for config fetching)
        """
        self.firestore_adapter = firestore_adapter
        self.cloud_tasks_adapter = cloud_tasks_adapter
        self.paperglass_api_url = paperglass_api_url
        
        # Default provisioning configuration
        self.default_config = QueueProvisioningConfig()
    
    async def provision_queues_for_pipeline(
        self, 
        pipeline: PipelineConfig,
        app_id: Optional[str] = None
    ) -> QueueProvisioningResult:
        """
        Auto-provision cloud task queues for a specific pipeline.
        
        Args:
            pipeline: The pipeline configuration
            app_id: Optional app_id override (uses pipeline.app_id if not provided)
            
        Returns:
            QueueProvisioningResult with provisioning details and results
        """
        # Use app_id from parameter or extract from pipeline
        effective_app_id = app_id or getattr(pipeline, 'app_id', None) or pipeline.scope
        
        result = QueueProvisioningResult(
            pipeline_id=pipeline.id or pipeline.key,
            app_id=effective_app_id
        )
        
        extra = {
            "operation": "provision_queues_for_pipeline",
            "pipeline_id": result.pipeline_id,
            "pipeline_key": pipeline.key,
            "pipeline_scope": pipeline.scope,
            "app_id": effective_app_id
        }
        
        LOGGER.info(f"Starting queue provisioning for pipeline {pipeline.key}", extra=extra)
        
        try:
            # Step 1: Extract queue names from pipeline tasks
            queue_templates = self._extract_queue_names_from_pipeline(pipeline)
            
            if not queue_templates:
                LOGGER.info(f"No queue names found in pipeline {pipeline.key}, skipping provisioning", extra=extra)
                result.mark_completed(success=True)
                return result
            
            extra["queue_templates"] = queue_templates
            LOGGER.debug(f"Extracted {len(queue_templates)} queue templates from pipeline", extra=extra)
            
            # Step 2: Get app configuration for token replacement
            app_config = await self._get_app_config_with_caching(effective_app_id)
            
            # Step 3: Generate queue name permutations
            queue_names_to_create = self._generate_queue_name_permutations(
                queue_templates, app_config, pipeline
            )
            
            if not queue_names_to_create:
                LOGGER.info(f"No queues to create for pipeline {pipeline.key} after filtering", extra=extra)
                result.mark_completed(success=True)
                return result
            
            extra["queues_to_create"] = len(queue_names_to_create)
            LOGGER.info(f"Will provision {len(queue_names_to_create)} queues", extra=extra)
            
            # Step 4: Provision each queue
            await self._provision_queues(queue_names_to_create, result)
            
            # Step 5: Mark operation as completed
            success = result.total_failed == 0
            error_message = f"Failed to create {result.total_failed} queues" if not success else None
            result.mark_completed(success=success, error_message=error_message)
            
            extra.update({
                "total_created": result.total_created,
                "total_existing": result.total_existing,
                "total_failed": result.total_failed,
                "success": success
            })
            
            LOGGER.info(f"Queue provisioning completed for pipeline {pipeline.key}", extra=extra)
            return result
            
        except Exception as e:
            error_msg = f"Error during queue provisioning for pipeline {pipeline.key}: {str(e)}"
            extra["error"] = exceptionToMap(e)
            LOGGER.error(error_msg, extra=extra)
            
            result.mark_completed(success=False, error_message=str(e))
            return result
    
    async def _get_app_config_with_caching(self, app_id: str) -> Optional[AppConfigCache]:
        """
        Get app configuration with local caching to eliminate cross-service calls.
        
        Args:
            app_id: Application identifier
            
        Returns:
            AppConfigCache if found, None otherwise
        """
        extra = {
            "operation": "_get_app_config_with_caching",
            "app_id": app_id
        }
        
        try:
            # Try to get from cache first
            cached_config = await self.firestore_adapter.get_app_config_cache(app_id)
            
            if cached_config:
                LOGGER.debug(f"Using cached app config for app_id: {app_id}", extra=extra)
                return cached_config
            
            # Cache miss or expired - fetch from PaperGlass API
            LOGGER.info(f"Cache miss for app_id {app_id}, fetching from PaperGlass API", extra=extra)
            
            if not self.paperglass_api_url:
                LOGGER.warning(f"No PaperGlass API URL configured, cannot fetch config for app_id: {app_id}", extra=extra)
                return None
            
            # Fetch from PaperGlass API and cache it
            fresh_config = await self._fetch_app_config_from_paperglass(app_id)
            
            if fresh_config:
                # Cache the fresh configuration
                await self.firestore_adapter.save_app_config_cache(fresh_config)
                LOGGER.info(f"Cached fresh app config for app_id: {app_id}", extra=extra)
                return fresh_config
            
            return None
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error(f"Error getting app config for app_id {app_id}: {str(e)}", extra=extra)
            # Return None rather than raise - queue provisioning should continue without config
            return None
    
    async def _fetch_app_config_from_paperglass(self, app_id: str) -> Optional[AppConfigCache]:
        """
        Fetch app configuration from PaperGlass API.
        
        Args:
            app_id: Application identifier
            
        Returns:
            AppConfigCache if successful, None otherwise
        """
        if not self.paperglass_api_url:
            LOGGER.warning(f"No PaperGlass API URL configured, cannot fetch config for app_id: {app_id}")
            return None
            
        extra = {
            "operation": "_fetch_app_config_from_paperglass",
            "app_id": app_id,
            "paperglass_api_url": self.paperglass_api_url
        }
        
        try:
            import httpx
            from util.date_utils import now_utc
            
            # Construct the API endpoint
            url = f"{self.paperglass_api_url}/api/v1/configs/{app_id}"
            
            # Set up headers (similar to existing adapters)
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "EntityExtraction-QueueManager/1.0"
            }
            
            # Make the HTTP request
            async with httpx.AsyncClient(timeout=30.0) as client:
                LOGGER.debug(f"Fetching app config from PaperGlass API: {url}", extra=extra)
                
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                config_data = response.json()
                
                if not config_data:
                    LOGGER.warning(f"Empty response from PaperGlass API for app_id: {app_id}", extra=extra)
                    return None
                
                # Extract relevant fields for caching
                app_config_cache = AppConfigCache(
                    app_id=app_id,
                    name=config_data.get("name"),
                    description=config_data.get("description"),
                    config=config_data.get("config", {}),
                    cached_at=now_utc(),
                    ttl_seconds=3600  # 1 hour cache TTL
                )
                
                # Extract business context from config if available
                if app_config_cache.config:
                    accounting = app_config_cache.config.get("accounting", {})
                    if isinstance(accounting, dict):
                        app_config_cache.business_unit = accounting.get("business_unit")
                        app_config_cache.solution_code = accounting.get("solution_code")
                
                extra.update({
                    "has_business_unit": bool(app_config_cache.business_unit),
                    "has_solution_code": bool(app_config_cache.solution_code),
                    "config_size": len(str(app_config_cache.config))
                })
                
                LOGGER.info(f"Successfully fetched app config from PaperGlass API for app_id: {app_id}", extra=extra)
                return app_config_cache
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                LOGGER.info(f"App config not found in PaperGlass API for app_id: {app_id}", extra=extra)
                return None
            else:
                extra["error"] = {
                    "status_code": e.response.status_code,
                    "response_text": e.response.text
                }
                LOGGER.error(f"HTTP error fetching app config from PaperGlass API: {e.response.status_code}", extra=extra)
                return None
                
        except httpx.ConnectError as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error(f"Connection error to PaperGlass API: {str(e)}", extra=extra)
            return None
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error(f"Error fetching app config from PaperGlass API for app_id {app_id}: {str(e)}", extra=extra)
            return None
    
    def _extract_queue_names_from_pipeline(self, pipeline: PipelineConfig) -> List[str]:
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
            # Handle different task formats
            if isinstance(task, dict):
                # Check for invoke configuration with queue_name
                invoke_config = task.get("invoke")
                if isinstance(invoke_config, dict) and invoke_config.get("queue_name"):
                    queue_name = invoke_config["queue_name"]
                    
                    # Skip pseudo queues
                    if queue_name not in ["DEFAULT", "DIRECT"]:
                        queue_names.add(queue_name)
                
                # Check for direct queue_name field
                elif task.get("queue_name"):
                    queue_name = task["queue_name"]
                    
                    # Skip pseudo queues
                    if queue_name not in ["DEFAULT", "DIRECT"]:
                        queue_names.add(queue_name)
        
        return list(queue_names)
    
    def _generate_queue_name_permutations(
        self,
        queue_templates: List[str],
        app_config: Optional[AppConfigCache],
        pipeline: PipelineConfig
    ) -> List[str]:
        """
        Generate all permutations of queue names by replacing tokens with actual values.
        
        Args:
            queue_templates: List of queue name templates with tokens
            app_config: App configuration for token replacement (may be None)
            pipeline: Pipeline configuration for additional context
            
        Returns:
            List of resolved queue names with priority variants
        """
        if not queue_templates:
            return []
        
        # Get token replacement values
        tokens = self._get_token_replacement_values(app_config, pipeline)
        
        resolved_queues = set()
        
        for template in queue_templates:
            # Replace tokens in template
            resolved_name = self._replace_tokens_in_string(template, tokens)
            
            # Generate priority variants for this queue
            priority_variants = self._generate_priority_variants(resolved_name)
            resolved_queues.update(priority_variants)
        
        return list(resolved_queues)
    
    def _get_token_replacement_values(
        self, 
        app_config: Optional[AppConfigCache], 
        pipeline: PipelineConfig
    ) -> Dict[str, str]:
        """
        Get token replacement values from app config and pipeline.
        
        Args:
            app_config: App configuration (may be None)
            pipeline: Pipeline configuration
            
        Returns:
            Dictionary of token names to replacement values
        """
        tokens = {}
        
        # Extract from app config if available
        if app_config:
            tokens.update(app_config.get_token_replacement_values())
        
        # Extract from pipeline
        if hasattr(pipeline, 'app_id') and pipeline.app_id:
            tokens["app_id"] = pipeline.app_id
        elif pipeline.scope:
            tokens["app_id"] = pipeline.scope
        
        # Provide fallback values
        if "app_id" not in tokens:
            tokens["app_id"] = "unknown"
        
        if "business_unit" not in tokens:
            tokens["business_unit"] = "default"
        
        if "solution_code" not in tokens:
            tokens["solution_code"] = "generic"
        
        return tokens
    
    def _replace_tokens_in_string(self, template: str, tokens: Dict[str, str]) -> str:
        """
        Replace tokens in a string template.
        
        Args:
            template: String template with tokens like {app_id}, {business_unit}
            tokens: Dictionary of token names to replacement values
            
        Returns:
            String with tokens replaced
        """
        result = template
        
        for token_name, token_value in tokens.items():
            # Replace both {token} and ${token} formats
            result = result.replace(f"{{{token_name}}}", str(token_value))
            result = result.replace(f"${{{token_name}}}", str(token_value))
        
        return result
    
    def _generate_priority_variants(self, base_queue_name: str) -> List[str]:
        """
        Generate priority variants for a base queue name.
        
        Args:
            base_queue_name: Base queue name
            
        Returns:
            List of queue names with priority variants
        """
        variants = [base_queue_name]  # Default priority
        
        # Add high and quarantine variants
        for priority in ["high", "quarantine"]:
            variant = self.default_config.get_queue_name_with_priority(base_queue_name, priority)
            if variant != base_queue_name:  # Only add if different
                variants.append(variant)
        
        return variants
    
    async def _provision_queues(
        self, 
        queue_names: List[str], 
        result: QueueProvisioningResult
    ) -> None:
        """
        Provision the specified queues and update the result.
        
        Args:
            queue_names: List of queue names to provision
            result: Result object to update with provisioning outcomes
        """
        extra = {
            "operation": "_provision_queues",
            "total_queues": len(queue_names)
        }
        
        LOGGER.info(f"Provisioning {len(queue_names)} queues", extra=extra)
        
        # Provision queues concurrently (but with some limit to avoid overwhelming the API)
        semaphore = asyncio.Semaphore(5)  # Limit concurrent operations
        
        tasks = [
            self._provision_single_queue(queue_name, result, semaphore)
            for queue_name in queue_names
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        extra.update({
            "created": len(result.queues_created),
            "existing": len(result.queues_existing),
            "failed": len(result.queues_failed)
        })
        
        LOGGER.info(f"Queue provisioning completed", extra=extra)
    
    async def _provision_single_queue(
        self, 
        queue_name: str, 
        result: QueueProvisioningResult,
        semaphore: asyncio.Semaphore
    ) -> None:
        """
        Provision a single queue and update the result.
        
        Args:
            queue_name: Name of the queue to provision
            result: Result object to update
            semaphore: Semaphore to limit concurrent operations
        """
        async with semaphore:
            extra = {
                "operation": "_provision_single_queue",
                "queue_name": queue_name
            }
            
            try:
                LOGGER.debug(f"Provisioning queue: {queue_name}", extra=extra)
                
                # Check if queue already exists
                exists = await self.cloud_tasks_adapter.queue_exists(queue_name)
                
                if exists:
                    LOGGER.debug(f"Queue already exists: {queue_name}", extra=extra)
                    queue_info = QueueInfo(
                        name=queue_name,
                        location=self.cloud_tasks_adapter.location,
                        project_id=self.cloud_tasks_adapter.project_id,
                        created=False,
                        exists=True
                    )
                    result.queues_existing.append(queue_info)
                else:
                    # Create the queue
                    LOGGER.debug(f"Creating queue: {queue_name}", extra=extra)
                    success = await self.cloud_tasks_adapter.create_queue(queue_name)
                    
                    if success:
                        LOGGER.info(f"Successfully created queue: {queue_name}", extra=extra)
                        queue_info = QueueInfo(
                            name=queue_name,
                            location=self.cloud_tasks_adapter.location,
                            project_id=self.cloud_tasks_adapter.project_id,
                            created=True,
                            exists=True
                        )
                        result.queues_created.append(queue_info)
                    else:
                        LOGGER.error(f"Failed to create queue: {queue_name}", extra=extra)
                        queue_info = QueueInfo(
                            name=queue_name,
                            location=self.cloud_tasks_adapter.location,
                            project_id=self.cloud_tasks_adapter.project_id,
                            created=False,
                            exists=False,
                            error="Queue creation failed"
                        )
                        result.queues_failed.append(queue_info)
                
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error(f"Error provisioning queue {queue_name}: {str(e)}", extra=extra)
                
                queue_info = QueueInfo(
                    name=queue_name,
                    location=getattr(self.cloud_tasks_adapter, 'location', 'unknown'),
                    project_id=getattr(self.cloud_tasks_adapter, 'project_id', 'unknown'),
                    created=False,
                    exists=False,
                    error=str(e)
                )
                result.queues_failed.append(queue_info)