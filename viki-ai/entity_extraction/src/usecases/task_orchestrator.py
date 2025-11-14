from typing import List, Dict, Any
from datetime import datetime, timedelta
from models.general import TaskParameters, TaskResults, PipelineParameters, EntityWrapper
from models.pipeline_config import TaskType, TaskConfig
from models.metric import Metric
from usecases.module_invoker import ModuleInvoker
from usecases.prompt_invoker import PromptInvoker
from usecases.pipelines_invoker import PipelinesInvoker
from usecases.remote_invoker import RemoteInvoker
from usecases.publish_callback_invoker import PublishCallbackInvoker
from adapters.storage import StorageAdapter
from adapters.firestore import search_pipeline_config
from adapters.cloud_tasks import CloudTaskAdapter
from adapters.djt_client import get_djt_client
from models.djt_models import PipelineStatusUpdate, PipelineStatus
from util.custom_logger import getLogger, set_pipeline_context
from util.exception import exceptionToMap
from util.json_utils import JsonUtil
from util.tracing import trace_function, trace_pipeline_step, add_span_attributes, add_span_event, traced_operation
from decorators.task_metric import task_metric
import settings

LOGGER = getLogger(__name__)

QUEUE_DIRECT = "DIRECT"  # Pseudo queue for direct invocation
QUEUE_DEFAULT = "DEFAULT"  # Default queue for task invocations

class TaskOrchestrator:
    """
    A class to orchestrate tasks based on the provided task parameters and type.
    """

    def __init__(self, task_name: str):
        self.task_name = task_name
    
    def _build_gcs_path(self, task_params: TaskParameters, filename: str) -> str:
        """
        Build the GCS path for storing task data.
        
        Path format: {app_id}/{tenant_id}/{patient_id}/{document_id}/{page_number}/{run_id}/{task_config.id}/{filename}
        """
        page_number = task_params.page_number or "document"
        return f"{task_params.app_id}/{task_params.tenant_id}/{task_params.patient_id}/{task_params.document_id}/{task_params.run_id}/{page_number}/{task_params.pipeline_scope}/{task_params.pipeline_key}/{task_params.task_config.id}/{filename}"
    
    async def _persist_task_params_to_gcs(self, task_params: TaskParameters) -> None:
        """
        Persist TaskParameters to Google Cloud Storage.
        
        :param task_params: The task parameters to persist
        """
        try:
            # Create storage adapter with custom bucket name
            bucket_name = f"entityextraction-context-{settings.STAGE}"
            storage_adapter = StorageAdapter(bucket_name=bucket_name)
            
            # Build path for input file
            input_path = self._build_gcs_path(task_params, "input.json")
            
            extra = {
                "bucket_name": bucket_name,
                "input_path": input_path,
                "task_name": self.task_name
            }
            
            LOGGER.debug(f"Persisting task parameters to GCS for task {self.task_name}", extra=extra)
            
            # Convert to JSON string
            input_json = JsonUtil.dumps(task_params.model_dump())
            
            # Save to GCS
            await storage_adapter.save_document(
                document_path=input_path,
                content=input_json,
                content_type="application/json",
                metadata={
                    "task_name": self.task_name,
                    "task_type": str(task_params.task_config.type),
                    "run_id": task_params.run_id,
                    "app_id": task_params.app_id,
                    "tenant_id": task_params.tenant_id
                }
            )
            
            LOGGER.info(f"Successfully persisted task parameters to GCS for task {self.task_name}", extra=extra)
            
        except Exception as e:
            extra = {
                "task_name": self.task_name,
                "error": exceptionToMap(e)
            }
            LOGGER.error(f"Failed to persist task parameters to GCS for task {self.task_name}: {str(e)}", extra=extra)
            # Don't re-raise the exception as persistence failure shouldn't fail the task
    
    async def _persist_task_results_to_gcs(self, task_params: TaskParameters, results: TaskResults) -> None:
        """
        Persist TaskResults to Google Cloud Storage.
        
        :param task_params: The task parameters (needed for path building)
        :param results: The task results to persist
        """
        extra = {}

        try:
            # Create storage adapter with custom bucket name
            bucket_name = f"entityextraction-context-{settings.STAGE}"
            storage_adapter = StorageAdapter(bucket_name=bucket_name)
            
            # Build path for output file
            results_path = self._build_gcs_path(task_params, "results.json")
            output_path = self._build_gcs_path(task_params, "output.json")
            
            extra = {
                "bucket_name": bucket_name,
                "results_path": results_path,
                "task_name": self.task_name
            }

            LOGGER.debug(f"Persisting task results to GCS for task {self.task_name} with output_path {output_path} results_path {results_path}", extra=extra)
            
            # Convert to JSON string
            results_json = JsonUtil.dumps(results.model_dump())
            output_json = JsonUtil.dumps(task_params.model_dump())
            
            # Save to GCS
            await storage_adapter.save_document(
                document_path=output_path,
                content=output_json,
                content_type="application/json",
                metadata={
                    "task_name": self.task_name,
                    "task_type": str(task_params.task_config.type),
                    "run_id": task_params.run_id,
                    "app_id": task_params.app_id,
                    "tenant_id": task_params.tenant_id,
                    "success": str(results.success)
                }
            )

            await storage_adapter.save_document(
                document_path=results_path,
                content=results_json,
                content_type="application/json",
                metadata={
                    "task_name": self.task_name,
                    "task_type": str(task_params.task_config.type),
                    "run_id": task_params.run_id,
                    "app_id": task_params.app_id,
                    "tenant_id": task_params.tenant_id,
                    "success": str(results.success)
                }
            )
            
            LOGGER.info(f"Successfully persisted task output and results to GCS for task {self.task_name}", extra=extra)
            
        except Exception as e:
            extra.update({
                "task_name": self.task_name,
                "error": exceptionToMap(e)
            })
            LOGGER.error(f"Failed to persist task results to GCS for task {self.task_name}: {str(e)}", extra=extra)
            # Don't re-raise the exception as persistence failure shouldn't fail the task

    def _add_task_results_to_context(self, task_params: TaskParameters, results: TaskResults) -> None:
        """
        Add task results to the task parameters context for use by subsequent tasks.
        
        Uses hierarchical structure [scope][pipeline][task_id] for both context and entities storage.
        If the task has an entity_schema_ref, the results will be wrapped in EntityWrapper.
        
        Args:
            task_params: The task parameters to update with results
            results: The task results to add to context
        """
        try:
            # Initialize context and entities if they don't exist
            if not task_params.context:
                task_params.context = {}
            if not task_params.entities:
                task_params.entities = {}
            
            # Set up hierarchical structure for context: [scope][pipeline][task_id]
            scope_context = task_params.context.setdefault(task_params.pipeline_scope, {})
            pipeline_context = scope_context.setdefault(task_params.pipeline_key, {})
            
            # Set up hierarchical structure for entities: [scope][pipeline][task_id]
            scope_entities = task_params.entities.setdefault(task_params.pipeline_scope, {})
            pipeline_entities = scope_entities.setdefault(task_params.pipeline_key, {})
            
            # Update subject with the results of the just executed task
            task_params.subject = results.results

            # Check if task has entity_schema_ref
            if task_params.task_config.entity_schema_ref:
                # If there's an entity schema defined, wrap the results in EntityWrapper
                # Handle both Dict and List[Dict] formats from validated results
                validated_results = results.results or {}

                # Ensure we have proper entity data for EntityWrapper initialization
                if isinstance(validated_results, list):
                    # List of entities - pass as is
                    initial_entities = validated_results
                elif isinstance(validated_results, dict):
                    # Single entity dict - pass as is
                    initial_entities = validated_results
                else:
                    # Fallback to empty dict if something unexpected (shouldn't happen with validation)
                    LOGGER.warning(f"Unexpected entity data type: {type(validated_results)}, using empty dict", extra={
                        "task_id": task_params.task_config.id,
                        "entity_data_type": type(validated_results).__name__
                    })
                    initial_entities = {}

                entity_wrapper = EntityWrapper(
                    schema_ref=task_params.task_config.entity_schema_ref.schema_uri,
                    app_id=task_params.app_id,
                    tenant_id=task_params.tenant_id,
                    patient_id=task_params.patient_id,
                    document_id=task_params.document_id,
                    page_number=task_params.page_number,
                    run_id=task_params.run_id,
                    entities=initial_entities  # Use validated entity data
                )

                # Use add_entities method to set the entity data and is_entity_list flag
                entity_wrapper.add_entities(validated_results)

                # Add EntityWrapper to context (serialized)
                pipeline_context[task_params.task_config.id] = entity_wrapper.model_dump()

                # Add EntityWrapper to entities (object)
                pipeline_entities[task_params.task_config.id] = entity_wrapper

                # Enhanced logging with entity format details
                entity_logging_data = {
                    "task_id": task_params.task_config.id,
                    "schema_ref": task_params.task_config.entity_schema_ref.schema_uri,
                    "is_entity_list": entity_wrapper.is_entity_list,
                    "entity_count": len(entity_wrapper.entities) if isinstance(entity_wrapper.entities, list) else 1,
                    "entity_data_type": "list_of_dicts" if isinstance(validated_results, list) else "dict",
                    "context_path": f"{task_params.pipeline_scope}.{task_params.pipeline_key}.{task_params.task_config.id}",
                    "entities_path": f"{task_params.pipeline_scope}.{task_params.pipeline_key}.{task_params.task_config.id}",
                    "saved_to_context": True,
                    "saved_to_entities": True
                }

                # Add first entity keys for debugging
                if isinstance(validated_results, list) and validated_results:
                    entity_logging_data["first_entity_keys"] = list(validated_results[0].keys()) if validated_results[0] else []
                elif isinstance(validated_results, dict):
                    entity_logging_data["entity_keys"] = list(validated_results.keys())

                LOGGER.debug(f"Added task results to context and entities as EntityWrapper using hierarchical structure", extra=entity_logging_data)
            else:
                # No entity schema, store raw results using hierarchical structure
                pipeline_context[task_params.task_config.id] = results.model_dump()
                
                LOGGER.debug("Added task results to context using hierarchical structure (no entity schema)", extra={
                    "task_id": task_params.task_config.id,
                    "pipeline_scope": task_params.pipeline_scope,
                    "pipeline_key": task_params.pipeline_key,
                    "context_path": f"{task_params.pipeline_scope}.{task_params.pipeline_key}.{task_params.task_config.id}",
                    "saved_to_context": True,
                    "saved_to_entities": False
                })

            return task_params
        
        except Exception as e:
            LOGGER.error(f"Failed to add task results to context for task {task_params.task_config.id}: {str(e)}", extra={
                "task_id": task_params.task_config.id,
                "error": exceptionToMap(e)
            })
            # Don't re-raise as this shouldn't fail the task

    async def invoke(self, task_params: TaskParameters) -> TaskParameters:
        """
        Invokes the task based on the task name.
        """

        LOGGER.info(f"Invoking task {self.task_name} with parameters: {task_params.model_dump()}")
        
        extra = {
            "task_params": task_params.model_dump()
        }

        if (settings.CLOUD_PROVIDER == "local" and not settings.CLOUDTASK_EMULATOR_ENABLED) or (task_params.task_config.invoke and task_params.task_config.invoke.queue_name==QUEUE_DIRECT) :
            # For local development, we can directly call the run method
            LOGGER.info(f"Invoking task {self.task_name} directly", extra={"task_params": task_params.model_dump()})
            return await self.run(task_params)
        else:
            # For cloud environments, invoke the task using Cloud Task queue (or the emulator if enabled in local environment)
            LOGGER.info(f"Invoking cloud task {self.task_name} via Cloud Tasks", extra=extra)
            
            try:
                cloud_task_adapter = CloudTaskAdapter()
                queue = task_params.task_config.invoke.queue_name or settings.INTRA_TASK_INVOCATION_DEFAULT_QUEUE
                
                # Accept the pseudo queue name "DEFAULT" to mean the default intra-task invocation queue
                if queue == QUEUE_DEFAULT:
                    queue = settings.INTRA_TASK_INVOCATION_DEFAULT_QUEUE
                
                # Create a task that will call the pipeline task endpoint
                response = await cloud_task_adapter.create_task_for_next_step(
                    task_id=self.task_name,
                    task_parameters=task_params,
                    queue=queue
                )
                
                LOGGER.info(f"Successfully created cloud task for {self.task_name}", extra={
                    "task_params": task_params.model_dump(),
                    "cloud_task_response": response
                })
                
                # Return the task parameters as they were submitted to the queue
                # The actual execution will happen asynchronously via the cloud task
                return task_params
                
            except Exception as e:
                extra.update({"error": exceptionToMap(e)})
                LOGGER.error(f"Failed to create cloud task for {self.task_name}: {str(e)}", extra=extra)
                raise
            finally:
                if 'cloud_task_adapter' in locals():
                    await cloud_task_adapter.close()
        
    
    @task_metric
    @trace_pipeline_step(
        step_name="task_execution",
        attributes={
            "task.type": "orchestrator_run",
            "service.component": "entity_extraction"
        }
    )
    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run the task with the given parameters using the discriminator pattern.
        
        :param task_params: The parameters for the task to run.
        :return: The processed task parameters after running the task.
        """
        task_type = task_params.task_config.type

        # Add span attributes for detailed tracing
        add_span_attributes({
            "task.id": task_params.task_config.id,
            "task.name": self.task_name,
            "task.type": str(task_type),
            "task.iteration": task_params.task_iteration,
            "task.retry_count": task_params.task_retry_count,
            "pipeline.scope": task_params.pipeline_scope,
            "pipeline.key": task_params.pipeline_key,
            "pipeline.run_id": task_params.run_id,
            "document.id": task_params.document_id,
            "document.page_number": task_params.page_number,
            "app.id": task_params.app_id,
            "tenant.id": task_params.tenant_id
        })

        extra = {
            "task_params": task_params.model_dump()
        }
        
        add_span_event("task_execution_started", {
            "task_id": task_params.task_config.id,
            "task_type": str(task_type)
        })
        
        LOGGER.debug(f"Running task {self.task_name} of type {task_type}", extra=extra)
        
        # Set task context for logging
        set_pipeline_context(
            app_id=task_params.app_id,
            tenant_id=task_params.tenant_id,
            patient_id=task_params.patient_id,
            document_id=task_params.document_id,
            page_number=task_params.page_number,
            run_id=task_params.run_id,
            pipeline_scope=task_params.pipeline_scope,
            pipeline_key=task_params.pipeline_key,
            task_id=task_params.task_config.id
        )
        
        # Persist task parameters to GCS at the beginning
        if settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED:
            LOGGER.debug(f"Persisting task parameters to GCS for task {self.task_name}", extra=extra)
            await self._persist_task_params_to_gcs(task_params)
        
        try:
            # Execute the main task logic
            results = await self._execute_task(task_params, task_type, extra)

            # Add results to task parameters context for the next task
            self._add_task_results_to_context(task_params, results)
            
            # Persist the results to GCS
            if settings.ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED:                
                await self._persist_task_results_to_gcs(task_params, results)

            # Determine next tasks to execute (this will now include the updated entities)
            next_tasks = await self._determine_next_tasks(task_params, results)
            
            # Handle next tasks or pipeline completion
            if next_tasks:
                # Add next tasks information to results metadata
                if not results.metadata:
                    results.metadata = {}
                results.metadata["next_tasks"] = [
                    {
                        "task_id": next_task.task_config.id,
                        "task_type": next_task.task_config.type,
                        "page_number": next_task.page_number
                    } for next_task in next_tasks
                ]
                LOGGER.info(f"Determined {len(next_tasks)} next task(s) for execution", extra=extra)

                # Submit next tasks via Cloud Tasks (emulator or real)
                cloud_task_adapter = CloudTaskAdapter()
                try:
                    for next_task in next_tasks:                        
                        LOGGER.info(f"Submitting next task: {next_task.task_config.id} (Type: {next_task.task_config.type}, Page: {next_task.page_number})", extra=extra)
                        
                        await cloud_task_adapter.create_task_for_next_step(
                            task_id=next_task.task_config.id,
                            task_parameters=next_task
                        )
                        
                        LOGGER.debug(f"Successfully submitted task {next_task.task_config.id} to Cloud Tasks", extra=extra)
                        
                finally:
                    await cloud_task_adapter.close()
            else:
                LOGGER.info("No next tasks determined - pipeline may be complete", extra=extra)
                
                # Handle pipeline completion
                await self._on_pipeline_complete(task_params, results, extra)

                # Update pipeline status to COMPLETED in DJT service
                await self._update_status(task_params, results, extra)

            return results

        except Exception as e:
            # Handle task failure with retry logic
            return await self._handle_task_failure(task_params, e, extra)

    async def _determine_next_tasks(self, task_params: TaskParameters, task_results: TaskResults) -> List[TaskParameters]:
        """
        Determine the next task(s) to execute in the pipeline.

        Args:
            task_params: Parameters of the current task
            task_results: Results from the current task

        Returns:
            List of TaskParameters for the next task(s) to execute.
            Empty list if pipeline is complete.
        """
        extra = {
            "current_task_id": task_params.task_config.id,
            "pipeline_scope": task_params.pipeline_scope,
            "pipeline_key": task_params.pipeline_key,
            "run_id": task_params.run_id,
            "operation": "determine_next_tasks"
        }

        try:
            LOGGER.debug("Determining next task(s) in pipeline", extra=extra)

            # Retrieve pipeline configuration
            pipeline_config = await search_pipeline_config(
                task_params.pipeline_scope, 
                task_params.pipeline_key
            )

            if pipeline_config is None:
                LOGGER.warning(f"Pipeline configuration not found for scope '{task_params.pipeline_scope}' and key '{task_params.pipeline_key}'", extra=extra)
                return []

            # Find current task index
            current_task_index = self._find_task_index(pipeline_config.tasks, task_params.task_config.id)
            if current_task_index == -1:
                LOGGER.warning(f"Task '{task_params.task_config.id}' not found in pipeline", extra=extra)
                return []

            current_task = pipeline_config.tasks[current_task_index]

            # Check if there's a next task
            next_task_index = current_task_index + 1
            if next_task_index >= len(pipeline_config.tasks):
                LOGGER.debug("Pipeline execution complete - no more tasks", extra=extra)
                return []

            next_task = pipeline_config.tasks[next_task_index]

            context = task_params.context.copy() if task_params.context else {}
            
            last_task_context_insertion_data = task_results.model_dump()
            last_task_context_task = {}
            last_task_context_task[task_params.task_config.id] = last_task_context_insertion_data
            last_task_context_pipeline = {}
            last_task_context_pipeline[task_params.pipeline_key] = last_task_context_task
            last_task_context_scope = {}
            last_task_context_scope[task_params.pipeline_scope] = last_task_context_pipeline

            context.update(last_task_context_scope)

            # Copy entities to ensure they're passed to next tasks
            entities = task_params.entities.copy() if task_params.entities else {}
            
            LOGGER.debug(f"Entities being passed to next task: {entities}", extra={
                **extra,
                "entities_count": len(entities) if entities else 0,
                "entity_keys": list(entities.keys()) if entities else []
            })

            # Create PipelineParameters for next task creation
            pipeline_params = PipelineParameters(
                app_id=task_params.app_id,
                tenant_id=task_params.tenant_id,
                patient_id=task_params.patient_id,
                document_id=task_params.document_id,
                page_number=task_params.page_number,
                pipeline_scope=task_params.pipeline_scope,
                pipeline_key=task_params.pipeline_key,
                pipeline_start_date=task_params.pipeline_start_date,
                run_id=task_params.run_id,
                subject=last_task_context_insertion_data,
                context=context,
                entities=entities
            )

            # Check for post-processing on the current (completed) task
            if (current_task.post_processing and 
                current_task.post_processing.for_each == "page" and 
                task_results):

                LOGGER.debug("Processing post-processing logic for pages", extra=extra)
                
                # Extract pages from task results
                pages = self._extract_pages_from_results(task_results)
                if not pages:
                    LOGGER.warning("No pages found in task results for post-processing", extra=extra)
                    # Fall back to single task if no pages found
                    task_params_next = TaskParameters.from_pipeline_parameters(pipeline_params, next_task)
                    return [task_params_next]

                extra.update({"page_count": len(pages)})
                LOGGER.debug(f"Creating {len(pages)} task instances for pages", extra=extra)

                # Create TaskParameters for each page
                return self._create_task_parameters_for_pages(pipeline_params, next_task, pages)

            else:
                # No post-processing, create single task
                LOGGER.debug("Creating single task instance (no post-processing)", extra=extra)
                task_params_next = TaskParameters.from_pipeline_parameters(pipeline_params, next_task)
                return [task_params_next]

        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Error determining next tasks: {str(e)}", extra=extra)
            return []

    def _find_task_index(self, tasks: List[TaskConfig], task_id: str) -> int:
        """
        Find the index of a task in the task list by its ID.

        Args:
            tasks: List of Task objects
            task_id: ID of the task to find

        Returns:
            Index of the task, or -1 if not found
        """
        for i, task in enumerate(tasks):
            if task.id == task_id:
                return i
        return -1

    def _extract_pages_from_results(self, task_results: TaskResults) -> List[Dict[str, Any]]:
        """
        Extract page information from task results.

        Args:
            task_results: Results from the task

        Returns:
            List of page dictionaries with page information
        """
        try:
            if not task_results.success:
                LOGGER.warning("Task failed, cannot extract pages")
                return []

            results = task_results.results
            if not results:
                LOGGER.warning("No results in task")
                return []

            # Handle both Dict and List[Dict] formats for results
            pages = []
            if isinstance(results, dict):
                # Single dict - extract pages field
                pages = results.get("pages", [])
            elif isinstance(results, list):
                # List of dicts - look for pages field in first dict, or treat each item as a page
                if results and isinstance(results[0], dict):
                    first_result = results[0]
                    pages = first_result.get("pages", [])
                    if not pages:
                        # If no "pages" field found, treat each item in the list as a page
                        LOGGER.debug("No 'pages' field found in list results, treating each result as a page")
                        pages = results
            else:
                LOGGER.warning(f"Unexpected results type: {type(results)}")
                return []

            if not isinstance(pages, list):
                LOGGER.warning(f"Pages field is not a list, got {type(pages)}")
                return []

            LOGGER.debug(f"Extracted {len(pages)} pages from task results")
            return pages

        except Exception as e:
            LOGGER.error(f"Error extracting pages from task results: {str(e)}")
            return []

    def _create_task_parameters_for_pages(self, 
                                        pipeline_params: PipelineParameters, 
                                        task_config: TaskConfig, 
                                        pages: List[Dict[str, Any]]) -> List[TaskParameters]:
        """
        Create TaskParameters for each page.

        Args:
            pipeline_params: Base pipeline parameters
            task_config: Configuration for the next task
            pages: List of page information dictionaries

        Returns:
            List of TaskParameters, one for each page
        """
        task_params_list = []

        for page in pages:
            try:
                # Extract page information
                page_number = page.get("page_number")
                if page_number is None:
                    LOGGER.warning(f"Page missing page_number: {page}")
                    continue

                # Create TaskParameters for this page
                task_params = TaskParameters.from_pipeline_parameters(pipeline_params, task_config)
                task_params.page_number = page_number

                # Add page-specific context
                if not task_params.context:
                    task_params.context = {}
                
                task_params.context.update({
                    "page_info": page,
                    "page_storage_uri": page.get("storage_uri"),
                    "total_pages": page.get("total_pages")
                })

                task_params_list.append(task_params)

                LOGGER.debug(f"Created TaskParameters for page {page_number}")

            except Exception as e:
                LOGGER.error(f"Error creating TaskParameters for page {page}: {str(e)}")
                continue

        return task_params_list

    async def _execute_task(self, task_params: TaskParameters, task_type: TaskType, extra: Dict[str, Any]) -> TaskResults:
        """
        Execute the main task logic based on task type.
        
        Args:
            task_params: Parameters for the task to run
            task_type: Type of task to execute
            extra: Extra logging context
            
        Returns:
            TaskResults from the executed task
        """
        if task_type == TaskType.MODULE:
            LOGGER.debug(f"Invoking module task: {task_params.task_config.module.type}", extra=extra)
            invoker = ModuleInvoker()
            return await invoker.run(task_params)            
        elif task_type == TaskType.PROMPT:
            LOGGER.debug(f"Invoking {task_params.task_config.type.value} task", extra=extra)
            invoker = PromptInvoker()
            return await invoker.run(task_params)            
        elif task_type == TaskType.PIPELINE:
            LOGGER.debug(f"Invoking {task_params.task_config.type.value} task", extra=extra)
            invoker = PipelinesInvoker()
            return await invoker.run(task_params)
        elif task_type == TaskType.REMOTE:
            LOGGER.debug(f"Invoking {task_params.task_config.type.value} task", extra=extra)
            invoker = RemoteInvoker()
            return await invoker.run(task_params)
        elif task_type == TaskType.PUBLISH_CALLBACK:
            LOGGER.debug(f"Invoking {task_params.task_config.type.value} task", extra=extra)
            invoker = PublishCallbackInvoker()
            return await invoker.run(task_params)
        else:
            LOGGER.error(f"Unknown task type: {task_type}", extra=extra)
            raise ValueError(f"Unknown task type: {task_type}")

    async def _handle_task_failure(self, task_params: TaskParameters, error: Exception, extra: Dict[str, Any]) -> TaskResults:
        """
        Handle task failure with retry logic and exponential backoff.
        
        Args:
            task_params: Parameters for the failed task
            error: The exception that caused the failure
            extra: Extra logging context
            
        Returns:
            TaskResults indicating failure
        """
        extra.update({
            "error": exceptionToMap(error),
            "task_iteration": task_params.task_iteration,
            "max_retry_count": task_params.task_retry_count,
            "retry_factor": task_params.task_retry_factor
        })
        
        LOGGER.error(f"Task {self.task_name} failed on iteration {task_params.task_iteration}: {str(error)}", extra=extra)
        
        # Check if we should retry
        if task_params.task_iteration < task_params.task_retry_count:
            LOGGER.info(f"Retrying task {self.task_name} (attempt {task_params.task_iteration + 1}/{task_params.task_retry_count})", extra=extra)
            await self._retry_task(task_params, error, extra)
            
            # Return a result indicating retry was initiated
            return TaskResults(
                success=False,
                error_message=f"Task failed, retry initiated (attempt {task_params.task_iteration + 1})",
                metadata={
                    "retry_initiated": True,
                    "retry_attempt": task_params.task_iteration + 1,
                    "original_error": str(error)
                }
            )
        else:
            LOGGER.error(f"Max retry attempts ({task_params.task_retry_count}) exceeded for task {self.task_name}", extra=extra)
            await self._mark_pipeline_failed(task_params, error, extra)
            
            # Return a result indicating final failure
            return TaskResults(
                success=False,
                error_message=f"Task failed after {task_params.task_retry_count} retry attempts: {str(error)}",
                metadata={
                    "max_retries_exceeded": True,
                    "final_attempt": task_params.task_iteration,
                    "pipeline_marked_failed": True,
                    "original_error": str(error)
                }
            )

    async def _retry_task(self, task_params: TaskParameters, error: Exception, extra: Dict[str, Any]) -> None:
        """
        Retry a failed task by incrementing the iteration count and resubmitting via CloudTask with exponential backoff.
        
        Args:
            task_params: Parameters for the task to retry
            error: The exception that caused the failure
            extra: Extra logging context
        """
        try:
            # Create new task parameters with incremented iteration
            retry_task_params = TaskParameters(
                app_id=task_params.app_id,
                tenant_id=task_params.tenant_id,
                patient_id=task_params.patient_id,
                document_id=task_params.document_id,
                page_number=task_params.page_number,
                page_count=task_params.page_count,
                priority=task_params.priority,
                pipeline_scope=task_params.pipeline_scope,
                pipeline_key=task_params.pipeline_key,
                pipeline_start_date=task_params.pipeline_start_date,
                run_id=task_params.run_id,
                subject=task_params.subject,
                params=task_params.params,
                context=task_params.context,
                entities=task_params.entities,
                task_config=task_params.task_config,
                task_queue_date=task_params.task_queue_date,
                task_iteration=task_params.task_iteration + 1,  # Increment retry count
                task_retry_count=task_params.task_retry_count,
                task_retry_factor=task_params.task_retry_factor
            )
            
            # Calculate exponential backoff delay
            schedule_time = None
            if task_params.task_retry_factor > 0:
                # Exponential backoff: factor * (2 ^ attempt)
                delay_seconds = task_params.task_retry_factor * (2 ** task_params.task_iteration)
                schedule_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
                
                extra.update({
                    "exponential_backoff_enabled": True,
                    "delay_seconds": delay_seconds,
                    "schedule_time": schedule_time.isoformat()
                })
                
                LOGGER.info(f"Scheduling retry task {self.task_name} with exponential backoff delay of {delay_seconds} seconds", extra=extra)
            else:
                extra.update({
                    "exponential_backoff_enabled": False,
                    "immediate_retry": True
                })
                
                LOGGER.info(f"Scheduling immediate retry task {self.task_name} (no exponential backoff)", extra=extra)
            
            # Submit retry task via CloudTask with optional scheduling
            cloud_task_adapter = CloudTaskAdapter()
            try:
                if schedule_time:
                    # Use CloudTask scheduling for delayed execution
                    response = await cloud_task_adapter.create_task_for_next_step(
                        task_id=self.task_name,
                        task_parameters=retry_task_params,
                        schedule_time=schedule_time
                    )
                else:
                    # Immediate execution
                    response = await cloud_task_adapter.create_task_for_next_step(
                        task_id=self.task_name,
                        task_parameters=retry_task_params
                    )
                
                LOGGER.info(f"Successfully submitted retry task {self.task_name} (attempt {retry_task_params.task_iteration})", extra={
                    **extra,
                    "retry_cloud_task_response": response,
                    "retry_attempt": retry_task_params.task_iteration
                })
                
            finally:
                await cloud_task_adapter.close()
                
        except Exception as retry_error:
            extra.update({"retry_error": exceptionToMap(retry_error)})
            LOGGER.error(f"Failed to submit retry task for {self.task_name}: {str(retry_error)}", extra=extra)
            # If retry submission fails, mark pipeline as failed
            await self._mark_pipeline_failed(task_params, retry_error, extra)

    async def _mark_pipeline_failed(self, task_params: TaskParameters, error: Exception, extra: Dict[str, Any]) -> None:
        """
        Mark the pipeline as failed in the DJT service.
        
        Args:
            task_params: Parameters for the failed task
            error: The exception that caused the failure
            extra: Extra logging context
        """
        try:
            djt_client = get_djt_client()
            
            # Create pipeline status update for failure
            pipeline_status_update = PipelineStatusUpdate(
                id=f"{task_params.pipeline_scope}.{task_params.pipeline_key}",
                status=PipelineStatus.FAILED,
                page_number=task_params.page_number,
                metadata={
                    "failed_task_id": task_params.task_config.id,
                    "failure_reason": str(error),
                    "task_iteration": task_params.task_iteration,
                    "max_retries_exceeded": True,
                    "pipeline_failure_reason": "task_max_retries_exceeded"
                },
                app_id=task_params.app_id,
                tenant_id=task_params.tenant_id,
                patient_id=task_params.patient_id,
                document_id=task_params.document_id,
                pages=task_params.page_count or 1
            )
            
            # Call DJT service to update pipeline status to failed
            djt_response = await djt_client.pipeline_status_update(
                job_id=task_params.run_id,
                pipeline_id=f"{task_params.pipeline_scope}:{task_params.pipeline_key}",
                pipeline_data=pipeline_status_update
            )
            
            LOGGER.error(f"Successfully updated DJT pipeline status to FAILED for {task_params.pipeline_scope}.{task_params.pipeline_key}", extra={
                **extra,
                "djt_response": djt_response
            })
            
        except Exception as djt_error:
            # Log DJT error but don't fail further
            LOGGER.error(f"Failed to update DJT pipeline failure status for {task_params.pipeline_scope}.{task_params.pipeline_key}: {str(djt_error)}", extra={
                **extra,
                "djt_error": exceptionToMap(djt_error)
            })

    async def _update_status(self, task_params: TaskParameters, results: TaskResults, extra: Dict[str, Any]) -> None:
        """
        Update pipeline status to COMPLETED in DJT service.
        
        Args:
            task_params: Parameters for the completed task
            results: Results from the completed task
            extra: Extra logging context
        """
        try:
            djt_client = get_djt_client()
            
            # Create pipeline status update for completion
            # Serialize results to JSON-compatible format to avoid datetime serialization issues
            final_task_results = None
            if results.success:
                try:
                    final_task_results = JsonUtil.loads(JsonUtil.dumps(results.model_dump()))
                    # Remove context and entities as it is large and not needed in DJT metadata
                    del final_task_results["context"]
                    del final_task_results["entities"]
                except Exception as e:
                    LOGGER.warning(f"Failed to serialize task results for DJT metadata: {str(e)}", extra=extra)
                    final_task_results = {"serialization_error": str(e)}
            
            pipeline_status_update = PipelineStatusUpdate(
                id=f"{task_params.pipeline_scope}.{task_params.pipeline_key}",
                status=PipelineStatus.COMPLETED,
                page_number=task_params.page_number,
                metadata={
                    "final_task_id": task_params.task_config.id,
                    "final_task_results": final_task_results,
                    "pipeline_completion_reason": "no_next_tasks"
                },
                app_id=task_params.app_id,
                tenant_id=task_params.tenant_id,
                patient_id=task_params.patient_id,
                document_id=task_params.document_id,
                pages=task_params.page_count or 1
            )
            
            # Call DJT service to update pipeline status to completed
            djt_response = await djt_client.pipeline_status_update(
                job_id=task_params.run_id,
                pipeline_id=f"{task_params.pipeline_scope}:{task_params.pipeline_key}",
                pipeline_data=pipeline_status_update
            )

            # If this was a page-level task, also log the document level is complete
            if task_params.page_number:
                # Create pipeline status update for completion (document level)
                # Use the same serialized results to maintain consistency
                pipeline_status_update = PipelineStatusUpdate(
                    id=f"{task_params.pipeline_scope}.{task_params.pipeline_key}",
                    status=PipelineStatus.COMPLETED,
                    page_number=None,
                    metadata={
                        "final_task_id": task_params.task_config.id,
                        "final_task_results": final_task_results,
                        "pipeline_completion_reason": "no_next_tasks"
                    },
                    app_id=task_params.app_id,
                    tenant_id=task_params.tenant_id,
                    patient_id=task_params.patient_id,
                    document_id=task_params.document_id,
                    pages=task_params.page_count or 1
                )
                
                # Call DJT service to update pipeline status to completed
                djt_response = await djt_client.pipeline_status_update(
                    job_id=task_params.run_id,
                    pipeline_id=f"{task_params.pipeline_scope}:{task_params.pipeline_key}",
                    pipeline_data=pipeline_status_update
                )
            
            LOGGER.info(f"Successfully updated DJT pipeline status to COMPLETED for {task_params.pipeline_scope}.{task_params.pipeline_key}", extra={
                **extra,
                "djt_response": djt_response
            })
            
        except Exception as djt_error:
            # Log DJT error but don't fail the task completion
            extra.update({"error": exceptionToMap(djt_error)})
            LOGGER.error(f"Failed to update DJT pipeline completion status for {task_params.pipeline_scope}.{task_params.pipeline_key}: {str(djt_error)}", extra=extra)

    async def _on_pipeline_complete(self, task_params: TaskParameters, results: TaskResults, extra: Dict[str, Any]) -> None:
        """
        Handle pipeline completion logic.
        
        Args:
            task_params: Parameters for the completed task
            results: Results from the completed task
            extra: Extra logging context
        """
        LOGGER.info(f"Pipeline execution complete for {task_params.pipeline_scope}.{task_params.pipeline_key}", extra={
            **extra,
            "pipeline_id": f"{task_params.pipeline_scope}.{task_params.pipeline_key}",
            "final_task_id": task_params.task_config.id,
            "run_id": task_params.run_id,
            "document_id": task_params.document_id,
            "page_number": task_params.page_number,
            "task_success": results.success if results else False
        })
        
        # Send pipeline page complete metric if this is a page-level pipeline
        if task_params.page_number is not None and results.success:
            pipeline_metric_metadata = {
                "pipeline_scope": task_params.pipeline_scope,
                "pipeline_key": task_params.pipeline_key,
                "pipeline_id": f"{task_params.pipeline_scope}.{task_params.pipeline_key}",
                "run_id": task_params.run_id,
                "app_id": task_params.app_id,
                "tenant_id": task_params.tenant_id,
                "patient_id": task_params.patient_id,
                "document_id": task_params.document_id,
                "page_number": task_params.page_number,
                "final_task_id": task_params.task_config.id,
                "pipeline_start_date": task_params.pipeline_start_date.isoformat() if task_params.pipeline_start_date else None,
                "event": "pipeline_page_execution_complete"
            }
            
            Metric.send(Metric.MetricType.PIPELINE_PAGE_COMPLETE, pipeline_metric_metadata)
        
        # Publish entities to paperglass
        await self._publish_entities(task_params, extra)

    async def _publish_entities(self, task_params: TaskParameters, extra: Dict[str, Any]) -> None:
        """
        Publish entities to paperglass POST /api/v5/entities endpoint via Cloud Tasks.
        
        Args:
            task_params: Parameters for the completed task
            extra: Extra logging context
        """
        try:
            # Check if there are any entities to publish
            if not task_params.entities:
                LOGGER.debug("No entities to publish", extra=extra)
                return
            
            # Extract EntityWrapper objects from the entities structure
            entity_wrappers = []
            for scope_key, scope_data in task_params.entities.items():
                for pipeline_key, pipeline_data in scope_data.items():
                    for task_id, entity_data in pipeline_data.items():
                        if isinstance(entity_data, EntityWrapper):
                            entity_wrappers.append(entity_data)
                        elif isinstance(entity_data, dict):
                            # Try to reconstruct EntityWrapper from dict
                            try:
                                entity_wrapper = EntityWrapper(**entity_data)
                                entity_wrappers.append(entity_wrapper)
                            except Exception as e:
                                LOGGER.warning(f"Failed to reconstruct EntityWrapper from dict for task {task_id}: {str(e)}", extra={
                                    **extra,
                                    "task_id": task_id,
                                    "entity_data_keys": list(entity_data.keys()) if isinstance(entity_data, dict) else None
                                })
            
            if not entity_wrappers:
                LOGGER.debug("No EntityWrapper objects found to publish", extra=extra)
                return
            
            extra.update({
                "entity_wrappers_count": len(entity_wrappers),
                "operation": "publish_entities"
            })
            
            LOGGER.info(f"Publishing {len(entity_wrappers)} EntityWrapper objects to paperglass", extra=extra)
            
            # Create Cloud Task for each EntityWrapper
            cloud_task_adapter = CloudTaskAdapter()
            try:
                for i, entity_wrapper in enumerate(entity_wrappers):
                    # Build the paperglass API URL
                    paperglass_url = f"{settings.PAPERGLASS_API_URL}/api/v5/entities"
                    
                    # Generate unique task name
                    import uuid
                    task_name = f"publish-entities-{task_params.run_id}-{i}-{uuid.uuid4().hex[:8]}"
                    
                    # Prepare headers with service account authentication
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    entity_extra = {
                        **extra,
                        "entity_wrapper_index": i,
                        "schema_ref": entity_wrapper.schema_ref,
                        "entity_count": len(entity_wrapper.entities) if isinstance(entity_wrapper.entities, list) else 1,
                        "is_entity_list": entity_wrapper.is_entity_list,
                        "paperglass_url": paperglass_url,
                        "task_name": task_name
                    }
                    
                    LOGGER.debug(f"Creating Cloud Task to publish EntityWrapper {i+1}/{len(entity_wrappers)}", extra=entity_extra)
                    
                    # Create the task using the medication extraction status check queue
                    response = await cloud_task_adapter.create_task(
                        location=settings.GCP_LOCATION_2,
                        queue=settings.MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME,
                        url=paperglass_url,
                        payload=entity_wrapper.model_dump(),
                        task_name=task_name,
                        headers=headers,
                        service_account_email=settings.SERVICE_ACCOUNT_EMAIL
                    )
                    
                    LOGGER.debug(f"Successfully created Cloud Task for EntityWrapper {i+1}/{len(entity_wrappers)}", extra={
                        **entity_extra,
                        "cloud_task_response": response
                    })
                    
            finally:
                await cloud_task_adapter.close()
                
            LOGGER.info(f"Successfully submitted {len(entity_wrappers)} EntityWrapper publishing tasks to Cloud Tasks", extra=extra)
            
        except Exception as e:
            # Log error but don't fail pipeline completion
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error(f"Failed to publish entities to paperglass: {str(e)}", extra=extra)
