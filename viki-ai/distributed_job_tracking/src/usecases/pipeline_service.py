import json
from datetime import datetime
from typing import Optional
import redis.asyncio as redis
from models.pipeline import Pipeline, PipelineStatusUpdate, PipelineListResponse, PipelineListItem, PipelineStatus
from models.metric import Metric
import settings
from util.custom_logger import getLogger, set_job_context
from util.date_utils import now_utc
from util.json_utils import JsonUtil

from util.exception import exceptionToMap


class PipelineService:
    """Service for handling pipeline operations with Redis storage"""
    
    def __init__(self):
        self.logger = getLogger(__name__)
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    
    async def close(self):
        """Close Redis connection"""
        await self.redis_client.aclose()
    
    def _get_pipeline_list_key(self, run_id: str) -> str:
        """Generate Redis key for pipeline list"""
        return f"djt::{run_id}:pipeline_list"
    
    def _get_pipelines_hash_key(self, run_id: str, pipeline_id: str) -> str:
        """Generate Redis key for pipelines hash"""
        return f"djt::{run_id}:pipelines:{pipeline_id}"
    
    def _get_pipeline_hash_field(self, page_number: Optional[int]) -> str:
        """Generate hash field for pipeline data"""
        if page_number is None:
            return "document"
        return str(page_number)
    
    async def update_pipeline_status(self, run_id: str, pipeline_id: str, pipeline_data: PipelineStatusUpdate) -> Pipeline:
        """Update pipeline status using Redis pipeline for atomic operations. Auto-creates job if it doesn't exist."""
        # Set job context for logging
        set_job_context(run_id=run_id, job_type="pipeline", status="updating")
        
        page_display = pipeline_data.page_number if pipeline_data.page_number is not None else "document"
        
        # Check if job exists, and create it if it doesn't
        await self._ensure_job_exists(run_id, pipeline_data)
        
        # Check if this is the first status for this run
        is_first_status = await self._is_first_status_for_run(run_id)
        
        # Check if pipeline already exists
        pipelines_hash_key = self._get_pipelines_hash_key(run_id, pipeline_id)
        pipeline_hash_field = self._get_pipeline_hash_field(pipeline_data.page_number)
        existing_pipeline_json = await self.redis_client.hget(pipelines_hash_key, pipeline_hash_field)
        
        if existing_pipeline_json:
            # Pipeline exists - update status and updated_at only
            self.logger.info("Updating existing pipeline status with run_id: %s, pipeline_id: %s, page: %s", 
                            run_id, pipeline_id, page_display)
            
            # Parse existing pipeline data
            existing_pipeline_data = json.loads(existing_pipeline_json)
            existing_pipeline = Pipeline(**existing_pipeline_data)
            
            # Update only status and updated_at
            existing_pipeline.status = pipeline_data.status
            existing_pipeline.updated_at = now_utc()
            
            # Store updated pipeline with TTL
            updated_pipeline_json = existing_pipeline.model_dump_json()
            await self.redis_client.hset(pipelines_hash_key, pipeline_hash_field, updated_pipeline_json)
            await self.redis_client.expire(pipelines_hash_key, settings.DJT_REDIS_TTL_DEFAULT)
            
            self.logger.info("Pipeline status updated successfully", extra={
                "run_id": run_id,
                "pipeline_id": pipeline_id,
                "page_number": pipeline_data.page_number,
                "old_status": existing_pipeline_data.get("status"),
                "new_status": pipeline_data.status,
                "operation": "update_pipeline_status"
            })
            
            # Check overall run status after update
            await self._check_and_publish_run_completion(run_id)
            
            return existing_pipeline
        else:
            # Pipeline doesn't exist - create new one
            self.logger.info("Creating new pipeline with run_id: %s, pipeline_id: %s, page: %s", 
                            run_id, pipeline_id, page_display)
            
            # Create pipeline with timestamps
            pipeline_data.id = pipeline_id
            pipeline = Pipeline(
                **pipeline_data.model_dump(),
                created_at=now_utc(),
                updated_at=now_utc()
            )
            
            # Use Redis pipeline for atomic operations
            redis_pipeline = self.redis_client.pipeline()
            
            # a) Add pipeline_id to set at djt::{run_id}:pipeline_list
            pipeline_list_key = self._get_pipeline_list_key(run_id)
            redis_pipeline.sadd(pipeline_list_key, pipeline_id)
            redis_pipeline.expire(pipeline_list_key, settings.DJT_REDIS_TTL_DEFAULT)
            
            # b) Create hash at key djt::{run_id}:pipelines:{pipeline_id} with hash key {page_number} or "document"
            pipeline_json = pipeline.model_dump_json()
            redis_pipeline.hset(pipelines_hash_key, pipeline_hash_field, pipeline_json)
            redis_pipeline.expire(pipelines_hash_key, settings.DJT_REDIS_TTL_DEFAULT)
            
            # Execute the pipeline
            await redis_pipeline.execute()
            
            self.logger.info("Pipeline created successfully using keys '%s' and '%s'", 
                            pipeline_list_key, pipelines_hash_key, extra={
                "run_id": run_id,
                "pipeline_id": pipeline_id,
                "page_number": pipeline_data.page_number,
                "status": pipeline_data.status,
                "operation": "create_pipeline"
            })
            
            # If this is the first status for the run, notify paperglass
            if is_first_status:
                await self._publish_first_status(run_id, pipeline_data)
            
            # Check overall run status after creation
            await self._check_and_publish_run_completion(run_id)
            
            return pipeline
    
    async def get_pipeline(self, run_id: str, pipeline_id: str, page_number: Optional[int]) -> Optional[Pipeline]:
        """Get a pipeline by run_id, pipeline_id, and page_number"""
        set_job_context(run_id=run_id)
        
        self.logger.debug("Retrieving pipeline", extra={
            "run_id": run_id,
            "pipeline_id": pipeline_id,
            "page_number": page_number,
            "operation": "get_pipeline"
        })
        
        pipelines_hash_key = self._get_pipelines_hash_key(run_id, pipeline_id)
        pipeline_hash_field = self._get_pipeline_hash_field(page_number)
        pipeline_json = await self.redis_client.hget(pipelines_hash_key, pipeline_hash_field)
        
        if not pipeline_json:
            self.logger.warning("Pipeline not found", extra={
                "run_id": run_id,
                "pipeline_id": pipeline_id,
                "page_number": page_number,
                "operation": "get_pipeline"
            })
            return None
        
        pipeline_data = json.loads(pipeline_json)
        pipeline = Pipeline(**pipeline_data)
        
        self.logger.debug("Pipeline retrieved successfully", extra={
            "run_id": run_id,
            "pipeline_id": pipeline_id,
            "page_number": page_number,
            "status": pipeline.status,
            "operation": "get_pipeline"
        })
        
        return pipeline
    
    async def pipeline_exists(self, run_id: str, pipeline_id: str, page_number: Optional[int]) -> bool:
        """Check if a pipeline exists"""
        pipelines_hash_key = self._get_pipelines_hash_key(run_id, pipeline_id)
        pipeline_hash_field = self._get_pipeline_hash_field(page_number)
        return await self.redis_client.hexists(pipelines_hash_key, pipeline_hash_field)
    
    async def get_pipeline_list(self, run_id: str) -> list[str]:
        """Get list of pipeline IDs for a run"""
        pipeline_list_key = self._get_pipeline_list_key(run_id)
        pipeline_ids = await self.redis_client.smembers(pipeline_list_key)
        return list(pipeline_ids)
    
    async def get_all_pipelines_for_run(self, run_id: str) -> dict[str, Pipeline]:
        """Get all pipelines for a run"""
        pipelines_hash_key = self._get_pipelines_hash_key(run_id)
        all_pipeline_data = await self.redis_client.hgetall(pipelines_hash_key)
        
        pipelines = {}
        for hash_field, pipeline_json in all_pipeline_data.items():
            pipeline_data = json.loads(pipeline_json)
            pipeline = Pipeline(**pipeline_data)
            pipelines[hash_field] = pipeline
        
        return pipelines
    
    async def list_pipelines_for_run(self, run_id: str) -> PipelineListResponse:
        """
        List all pipelines for a run_id.
        
        First checks if the job exists. If not, returns NOT_STARTED status.
        Then pulls the set of pipeline_ids from Redis using key djt::{run_id}:pipelines.
        Then retrieves each pipeline status from Redis using hgetall with key djt::{run_id}:pipelines:{pipeline_id}.
        Returns a PipelineListResponse with status, pipeline_count, pipeline_ids, and pipelines list.
        """
        set_job_context(run_id=run_id)
        
        self.logger.debug("Listing pipelines for run", extra={
            "run_id": run_id,
            "operation": "list_pipelines_for_run"
        })
        
        # Check if job exists first
        job_key = f"djt::{run_id}"
        job_exists = await self.redis_client.hexists(job_key, "job")
        
        if not job_exists:
            self.logger.info("Job does not exist for run", extra={
                "run_id": run_id,
                "operation": "list_pipelines_for_run"
            })
            return PipelineListResponse(
                status=PipelineStatus.NOT_STARTED,  # Job doesn't exist, so not started
                pipeline_count=0,
                pipeline_ids=[],
                elapsed_time=None,
                pipelines=[]
            )
        
        # First get the set of pipeline_ids from djt::{run_id}:pipelines
        pipelines_set_key = self._get_pipeline_list_key(run_id) 
        pipeline_ids = await self.redis_client.smembers(pipelines_set_key)
        
        if not pipeline_ids:
            self.logger.info("No pipeline IDs found for run", extra={
                "run_id": run_id,
                "operation": "list_pipelines_for_run"
            })
            return PipelineListResponse(
                status=PipelineStatus.COMPLETED,  # Default status when no pipelines but job exists
                pipeline_count=0,
                pipeline_ids=[],
                elapsed_time=None,
                pipelines=[]
            )
        
        # Then retrieve each pipeline status using hgetall
        pipelines = []
        pipeline_statuses = []
        earliest_created_at = None
        
        for pipeline_id in pipeline_ids:
            pipeline_hash_key = f"djt::{run_id}:pipelines:{pipeline_id}"
            pipeline_data = await self.redis_client.hgetall(pipeline_hash_key)
            
            if pipeline_data:
                # Convert the hash data to a proper JSON structure
                tasks = {}
                pipeline_task_statuses = []
                pipeline_created_at = None
                pipeline_order = None
                has_numeric_keys = False
                
                for field, value in pipeline_data.items():
                    try:
                        # Try to parse as JSON first (for nested objects)
                        parsed_value = json.loads(value)
                        tasks[field] = parsed_value
                        
                        # If this task has a status, collect it for aggregate status
                        if isinstance(parsed_value, dict) and "status" in parsed_value:
                            pipeline_task_statuses.append(parsed_value["status"])
                        
                        # Extract created_at for elapsed time calculation
                        if isinstance(parsed_value, dict) and "created_at" in parsed_value:
                            try:
                                created_at_str = parsed_value["created_at"]
                                if isinstance(created_at_str, str):
                                    pipeline_created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                                elif isinstance(created_at_str, datetime):
                                    pipeline_created_at = created_at_str
                            except (ValueError, TypeError):
                                pass
                        
                        # Extract order for sorting (stored at pipeline level)
                        if isinstance(parsed_value, dict) and "order" in parsed_value:
                            try:
                                pipeline_order = int(parsed_value["order"])
                            except (ValueError, TypeError):
                                pass
                    except (json.JSONDecodeError, TypeError):
                        # If not JSON, store as string
                        tasks[field] = value
                    
                    # Check if the field key is numeric (indicates page-level processing)
                    if field.isdigit():
                        has_numeric_keys = True
                
                # Determine aggregate status for this pipeline based on its tasks
                if has_numeric_keys:
                    # For page-level pipelines, we need to check if all pages are accounted for
                    pipeline_aggregate_status = await self._determine_page_level_status(pipeline_task_statuses, tasks, run_id)
                else:
                    # For document-level pipelines, use standard status determination
                    pipeline_aggregate_status = self._determine_overall_status(pipeline_task_statuses)
                
                # Calculate elapsed time for this pipeline
                pipeline_elapsed_time = None
                if pipeline_created_at:
                    current_time = now_utc()
                    if pipeline_created_at.tzinfo is None:
                        # Assume UTC if no timezone info
                        pipeline_created_at = pipeline_created_at.replace(tzinfo=current_time.tzinfo)
                    pipeline_elapsed_time = (current_time - pipeline_created_at).total_seconds()
                    
                    # Track earliest created_at for overall elapsed time
                    if earliest_created_at is None or pipeline_created_at < earliest_created_at:
                        earliest_created_at = pipeline_created_at
                
                # Create the structured pipeline object
                pipeline_item = PipelineListItem(
                    id=pipeline_id,
                    status=pipeline_aggregate_status,
                    elapsed_time=pipeline_elapsed_time,
                    is_page_level=has_numeric_keys,
                    order=pipeline_order,
                    tasks=tasks
                )
                
                pipelines.append(pipeline_item)
                
                # Collect status for determining overall run status
                pipeline_statuses.append(pipeline_aggregate_status)
            else:
                self.logger.warning("Pipeline data not found", extra={
                    "run_id": run_id,
                    "pipeline_id": pipeline_id,
                    "operation": "list_pipelines_for_run"
                })
        
        # Sort pipelines by order field (ascending) for consistent display
        # Pipelines without order will be placed at the end
        def get_sort_order(pipeline_item: PipelineListItem) -> tuple:
            """Get sort key for pipeline. Returns (order, pipeline_id) for stable sorting."""
            order = pipeline_item.order if pipeline_item.order is not None else float('inf')
            return (order, pipeline_item.id)
        
        sorted_pipelines = sorted(pipelines, key=get_sort_order)
        
        self.logger.debug("Sorted pipelines by order field", extra={
            "run_id": run_id,
            "pipeline_count": len(pipelines),
            "sorted_order": [(p.id, p.order) for p in sorted_pipelines],
            "operation": "list_pipelines_for_run"
        })
        
        # Determine overall status (least status: failed > processing > complete)
        overall_status = self._determine_overall_status(pipeline_statuses)
        
        # Calculate overall elapsed time based on earliest pipeline
        overall_elapsed_time = None
        if earliest_created_at:
            current_time = now_utc()
            overall_elapsed_time = (current_time - earliest_created_at).total_seconds()
        
        result = PipelineListResponse(
            status=overall_status,
            pipeline_count=len(pipeline_ids),
            pipeline_ids=list(pipeline_ids),
            elapsed_time=overall_elapsed_time,
            pipelines=sorted_pipelines
        )
        
        self.logger.info("Retrieved pipelines for run", extra={
            "run_id": run_id,
            "pipeline_count": len(pipeline_ids),
            "overall_status": overall_status,
            "operation": "list_pipelines_for_run"
        })
        
        return result
    
    async def _get_total_pages_for_run(self, run_id: str) -> int:
        """Get the total number of pages for a run from the job data."""
        try:
            job_key = f"djt::{run_id}"
            job_json = await self.redis_client.hget(job_key, "job")
            if job_json:
                job_data = json.loads(job_json)
                return job_data.get("pages", 0)
        except Exception as e:
            self.logger.warning("Could not retrieve page count for run", extra={
                "run_id": run_id,
                "error": str(e),
                "operation": "_get_total_pages_for_run"
            })
        return 0

    async def _determine_page_level_status(self, pipeline_task_statuses: list[str], tasks: dict, run_id: str) -> PipelineStatus:
        """
        Determine status for page-level pipelines with smarter logic.
        For page-level pipelines, COMPLETED status is only returned if all pages from the job are accounted for.
        """
        # First check for high-priority statuses that override page completion logic
        if PipelineStatus.FAILED in pipeline_task_statuses or "FAILED" in pipeline_task_statuses:
            return PipelineStatus.FAILED
        
        if PipelineStatus.IN_PROGRESS in pipeline_task_statuses or "IN_PROGRESS" in pipeline_task_statuses:
            return PipelineStatus.IN_PROGRESS
        
        if PipelineStatus.QUEUED in pipeline_task_statuses or "QUEUED" in pipeline_task_statuses:
            return PipelineStatus.QUEUED
        
        if PipelineStatus.NOT_STARTED in pipeline_task_statuses or "NOT_STARTED" in pipeline_task_statuses:
            return PipelineStatus.NOT_STARTED
        
        # For COMPLETED status, we need to check if all pages from the job are accounted for
        if PipelineStatus.COMPLETED in pipeline_task_statuses or "COMPLETED" in pipeline_task_statuses:
            # Get the total pages from the job
            total_pages = await self._get_total_pages_for_run(run_id)
            
            if total_pages > 0:
                # Get the numeric page keys from tasks
                page_numbers = set()
                for field in tasks.keys():
                    if field.isdigit():
                        page_numbers.add(int(field))
                
                if page_numbers:
                    # Check if we have all pages from 1 to total_pages
                    expected_pages = set(range(1, total_pages + 1))
                    
                    if page_numbers == expected_pages:
                        # All pages from job are accounted for
                        # Check if all accounted pages are COMPLETED
                        all_completed = True
                        for page_num in page_numbers:
                            page_key = str(page_num)
                            if page_key in tasks:
                                task_data = tasks[page_key]
                                if isinstance(task_data, dict):
                                    task_status = task_data.get("status", "")
                                    if task_status not in [PipelineStatus.COMPLETED, "COMPLETED"]:
                                        all_completed = False
                                        break
                        
                        if all_completed:
                            self.logger.debug("Page-level pipeline completed - all job pages accounted for", extra={
                                "run_id": run_id,
                                "pages_processed": sorted(page_numbers),
                                "total_pages": total_pages,
                                "operation": "_determine_page_level_status"
                            })
                            return PipelineStatus.COMPLETED
                        else:
                            # Some pages are not completed yet
                            return PipelineStatus.IN_PROGRESS
                    else:
                        # Missing pages from the job - still in progress
                        missing_pages = expected_pages - page_numbers
                        self.logger.debug("Page-level pipeline incomplete - missing pages from job", extra={
                            "run_id": run_id,
                            "pages_processed": sorted(page_numbers),
                            "missing_pages": sorted(missing_pages),
                            "total_pages": total_pages,
                            "operation": "_determine_page_level_status"
                        })
                        return PipelineStatus.IN_PROGRESS
                else:
                    # No pages processed yet, but job has pages - still in progress
                    self.logger.debug("Page-level pipeline incomplete - no pages processed yet", extra={
                        "run_id": run_id,
                        "total_pages": total_pages,
                        "operation": "_determine_page_level_status"
                    })
                    return PipelineStatus.IN_PROGRESS
            else:
                # No total pages info or zero pages - treat as document level
                return PipelineStatus.COMPLETED
        
        # If no COMPLETED status found, return IN_PROGRESS for page-level pipelines
        # since they should be actively processing
        return PipelineStatus.IN_PROGRESS

    def _determine_overall_status(self, pipeline_statuses: list[str]) -> PipelineStatus:
        """
        Determine the overall status based on individual pipeline statuses.
        Priority: FAILED > IN_PROGRESS > QUEUED > NOT_STARTED > COMPLETED > UNKNOWN
        """
        if not pipeline_statuses:
            return PipelineStatus.COMPLETED
        
        # Check for failed status first (highest priority)
        if PipelineStatus.FAILED in pipeline_statuses or "FAILED" in pipeline_statuses:
            return PipelineStatus.FAILED
        
        # Check for in progress status (high priority)
        if PipelineStatus.IN_PROGRESS in pipeline_statuses or "IN_PROGRESS" in pipeline_statuses:
            return PipelineStatus.IN_PROGRESS
        
        # Check for queued status (medium priority)
        if PipelineStatus.QUEUED in pipeline_statuses or "QUEUED" in pipeline_statuses:
            return PipelineStatus.QUEUED
        
        # Check for not started status (medium priority)
        if PipelineStatus.NOT_STARTED in pipeline_statuses or "NOT_STARTED" in pipeline_statuses:
            return PipelineStatus.NOT_STARTED
        
        # Check for completed status
        if PipelineStatus.COMPLETED in pipeline_statuses or "COMPLETED" in pipeline_statuses:
            return PipelineStatus.COMPLETED
        
        # Default to unknown for any unrecognized statuses
        return PipelineStatus.UNKNOWN
    
    async def _check_and_publish_run_completion(self, run_id: str) -> None:
        """
        Check if the overall run is complete and publish status if needed.
        """
        try:
            # Get the overall status of all pipelines for this run
            run_status_data = await self.list_pipelines_for_run(run_id)
            overall_status = run_status_data.status

            self.logger.debug("Checked overall run status", extra={
                "run_id": run_id,
                "overall_status": overall_status,
                "pipeline_count": run_status_data.pipeline_count
            })
            
            # Publish status for both COMPLETED and FAILED final states
            if overall_status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
                await self.publish_status(run_id, overall_status, run_status_data)
        except Exception as e:
            self.logger.error("Error checking run completion status", extra={
                "run_id": run_id,
                "error": exceptionToMap(e),
                "operation": "_check_and_publish_run_completion"
            })
    
    async def delete_all_pipelines_for_run(self, run_id: str) -> bool:
        """
        Delete all pipeline data for a run including pipeline list and individual pipeline hashes.
        Returns True if any data was deleted, False if no data existed.
        """
        set_job_context(run_id=run_id)
        
        self.logger.info("Deleting all pipeline data for run", extra={
            "run_id": run_id,
            "operation": "delete_all_pipelines_for_run"
        })
        
        try:
            # Get the list of pipeline IDs first
            pipeline_list_key = self._get_pipeline_list_key(run_id)
            pipeline_ids = await self.redis_client.smembers(pipeline_list_key)
            
            if not pipeline_ids:
                self.logger.info("No pipeline data found to delete", extra={
                    "run_id": run_id,
                    "operation": "delete_all_pipelines_for_run"
                })
                return False
            
            # Use Redis pipeline for atomic deletion
            redis_pipeline = self.redis_client.pipeline()
            
            # Delete the pipeline list set
            redis_pipeline.delete(pipeline_list_key)
            
            # Delete each pipeline hash
            for pipeline_id in pipeline_ids:
                pipeline_hash_key = self._get_pipelines_hash_key(run_id, pipeline_id)
                redis_pipeline.delete(pipeline_hash_key)
            
            # Execute all deletions
            results = await redis_pipeline.execute()
            
            # Count how many keys were actually deleted
            deleted_count = sum(1 for result in results if result > 0)
            
            self.logger.info("Pipeline data deletion completed", extra={
                "run_id": run_id,
                "pipeline_count": len(pipeline_ids),
                "keys_deleted": deleted_count,
                "operation": "delete_all_pipelines_for_run"
            })
            
            return deleted_count > 0
            
        except Exception as e:
            self.logger.error("Error deleting pipeline data", extra={
                "run_id": run_id,
                "error": str(e),
                "operation": "delete_all_pipelines_for_run"
            })
            raise

    async def _is_first_status_for_run(self, run_id: str) -> bool:
        """
        Check if this is the first status being posted for a run.
        Returns True if no pipelines exist yet for this run.
        """
        try:
            pipeline_list_key = self._get_pipeline_list_key(run_id)
            pipeline_count = await self.redis_client.scard(pipeline_list_key)
            
            # If no pipelines exist yet, this is the first status
            is_first = pipeline_count == 0
            
            self.logger.debug("Checked if first status for run", extra={
                "run_id": run_id,
                "pipeline_count": pipeline_count,
                "is_first_status": is_first,
                "operation": "_is_first_status_for_run"
            })
            
            return is_first
            
        except Exception as e:
            self.logger.error("Error checking if first status for run", extra={
                "run_id": run_id,
                "error": str(e),
                "operation": "_is_first_status_for_run"
            })
            # Default to False to avoid duplicate notifications
            return False

    async def _publish_first_status(self, run_id: str, pipeline_data: PipelineStatusUpdate) -> None:
        """
        Publish first status notification to paperglass to inform it of the runid.
        This is called when the first pipeline status is posted for a run.
        Only sends callbacks for entity_extraction and medication_extraction operations.
        """
        try:
            # Get job data
            job_key = f"djt::{run_id}"
            job_json = await self.redis_client.hget(job_key, "job")
            
            if not job_json:
                self.logger.warning("Job data not found for first status publication", extra={
                    "run_id": run_id,
                    "operation": "_publish_first_status"
                })
                return
            
            job_data = json.loads(job_json)
            
            # Read operation_type from job data
            operation_type = job_data.get("operation_type")
            if not operation_type:
                self.logger.warning("No operation_type found in job data, defaulting to entity_extraction", extra={
                    "run_id": run_id,
                    "job_data_keys": list(job_data.keys()),
                    "operation": "_publish_first_status"
                })
                operation_type = "entity_extraction"
            
            self.logger.info("Publishing first status notification to paperglass", extra={
                "run_id": run_id,
                "status": pipeline_data.status.value,
                "operation_type": operation_type,
                "operation": "_publish_first_status"
            })
            
            # Only send callbacks to PaperGlass for entity_extraction and medication_extraction operations
            if operation_type in ["entity_extraction", "medication_extraction"]:
                # Prepare initial status update payload
                status_payload = {
                    "app_id": job_data.get("app_id"),
                    "tenant_id": job_data.get("tenant_id"),
                    "patient_id": job_data.get("patient_id"),
                    "document_id": job_data.get("document_id"),                
                    "run_id": run_id,
                    "status": "IN_PROGRESS",  # First status is always IN_PROGRESS
                    "elapsed_time": 0,  # Just started
                    "pipelines": [],  # No pipeline details needed for first status
                }
                
                # Create CloudTask to post initial status update to paperglass
                from adapters.cloud_tasks import CloudTaskAdapter
                cloud_task_adapter = CloudTaskAdapter()
                
                try:
                    # Build the target URL for paperglass status update
                    url = f"{settings.PAPERGLASS_API_URL}/api/v5/status_update/{operation_type}"
                    
                    # Generate unique task name
                    import uuid
                    task_name = f"first-status-update-{operation_type}-{uuid.uuid4().hex[:8]}"

                    response = await cloud_task_adapter.create_task(
                        location=settings.GCP_LOCATION_2,
                        queue=settings.DEFAULT_TASK_QUEUE,
                        url=url,
                        payload=status_payload,
                        task_name=task_name,
                        service_account_email=settings.SERVICE_ACCOUNT_EMAIL
                    )
                    
                    self.logger.info("Successfully created first status update task for paperglass", extra={
                        "run_id": run_id,
                        "operation_type": operation_type,
                        "url": url,
                        "task_name": task_name,
                        "cloud_task_response": response,
                        "operation": "_publish_first_status"
                    })
                    
                finally:
                    await cloud_task_adapter.close()
            else:
                self.logger.info("Skipping PaperGlass callback for non-extraction operation", extra={
                    "run_id": run_id,
                    "operation_type": operation_type,
                    "status": pipeline_data.status.value,
                    "reason": "operation_type_not_extraction",
                    "operation": "_publish_first_status"
                })
                
        except Exception as e:
            self.logger.error("Error publishing first status notification", extra={
                "run_id": run_id,
                "error": str(e),
                "operation": "_publish_first_status"
            })
            # Don't re-raise the exception as first status publication failure shouldn't fail the main operation

    async def _ensure_job_exists(self, run_id: str, pipeline_data: PipelineStatusUpdate) -> None:
        """
        Ensure that a job exists for the given run_id. If not, create it using the pipeline data.
        """
        job_key = f"djt::{run_id}"
        job_exists = await self.redis_client.hexists(job_key, "job")
        
        if not job_exists:
            self.logger.info("Job does not exist, auto-creating job", extra={
                "run_id": run_id,
                "operation": "_ensure_job_exists"
            })
            
            # Create job data from pipeline data
            from models.simple_job import SimpleJob
            
            job = SimpleJob(
                app_id=pipeline_data.app_id,
                tenant_id=pipeline_data.tenant_id,
                patient_id=pipeline_data.patient_id,
                document_id=pipeline_data.document_id,
                run_id=run_id,
                name=f"Auto-created job for {run_id}",  # Default job name
                pages=pipeline_data.pages,
                metadata=pipeline_data.metadata,  # Use pipeline metadata for job metadata
                created_at=now_utc(),
                updated_at=now_utc()
            )
            
            # Store job in Redis with TTL
            job_json = job.model_dump_json()
            await self.redis_client.hset(job_key, "job", job_json)
            await self.redis_client.expire(job_key, settings.DJT_REDIS_TTL_DEFAULT)
            
            self.logger.info("Job auto-created successfully", extra={
                "run_id": run_id,
                "job_name": job.name,
                "operation": "_ensure_job_exists"
            })

    async def publish_status(self, run_id: str, status: PipelineStatus, run_data: PipelineListResponse) -> None:
        """
        Publish status notification when run is complete.
        Posts status update to paperglass API via Cloud Task.
        """
        self.logger.info("Run completed - publishing status notification", extra={
            "run_id": run_id,
            "status": status.value,
            "pipeline_count": run_data.pipeline_count,
            "elapsed_time": run_data.elapsed_time,
            "operation": "publish_status"
        })

        try:
            # Get job data to extract pipeline_id for operation_type
            job_key = f"djt::{run_id}"
            job_json = await self.redis_client.hget(job_key, "job")
            
            if not job_json:
                self.logger.warning("Job data not found for status publication", extra={
                    "run_id": run_id,
                    "operation": "publish_status"
                })
                return
            
            job_data = json.loads(job_json)
            
            # Calculate total pipeline elapsed time from start to completion
            total_pipeline_elapsed_time = None
            if run_data.elapsed_time is not None:
                # run_data.elapsed_time is already the total elapsed time from pipeline start
                total_pipeline_elapsed_time = run_data.elapsed_time
            
            # Send pipeline completion or error metric based on status
            pipeline_metric_metadata = {
                "run_id": run_id,
                "status": status.value,
                "pipeline_count": run_data.pipeline_count,
                "elapsed_time": run_data.elapsed_time,
                "total_pipeline_elapsed_time": total_pipeline_elapsed_time,
                "app_id": job_data.get("app_id"),
                "tenant_id": job_data.get("tenant_id"),
                "patient_id": job_data.get("patient_id"),
                "document_id": job_data.get("document_id"),
                "operation_type": "entity_extraction",
                "pipeline_ids": run_data.pipeline_ids,
            }
            
            if status == PipelineStatus.COMPLETED:
                pipeline_metric_metadata["event"] = "pipeline_execution_complete"
                Metric.send(Metric.MetricType.PIPELINE_COMPLETE, pipeline_metric_metadata)
            elif status == PipelineStatus.FAILED:
                pipeline_metric_metadata["event"] = "pipeline_execution_error"
                Metric.send(Metric.MetricType.PIPELINE_ERROR, pipeline_metric_metadata)
            
            # Read operation_type from job data
            operation_type = job_data.get("operation_type")
            if not operation_type:
                self.logger.warning("No operation_type found in job data, defaulting to entity_extraction", extra={
                    "run_id": run_id,
                    "job_data_keys": list(job_data.keys()),
                    "operation": "publish_status"
                })
                operation_type = "entity_extraction"
            
            # Clean pipelines data to ensure datetime objects are properly serialized
            cleaned_pipelines = []
            for pipeline in run_data.pipelines:
                pipeline_dict = pipeline.model_dump()
                cleaned_pipeline = JsonUtil.clean(pipeline_dict)
                cleaned_pipelines.append(cleaned_pipeline)
            
            # Prepare status update payload
            status_payload = {
                "app_id": job_data.get("app_id"),
                "tenant_id": job_data.get("tenant_id"),
                "patient_id": job_data.get("patient_id"),
                "document_id": job_data.get("document_id"),                
                "run_id": run_id,
                "status": status.value,                
                "elapsed_time": run_data.elapsed_time,
                "pipelines": cleaned_pipelines,
            }
            
            # Only send callbacks to PaperGlass for entity_extraction operations
            if operation_type == "entity_extraction":
                # Create CloudTask to post status update to paperglass
                from adapters.cloud_tasks import CloudTaskAdapter
                cloud_task_adapter = CloudTaskAdapter()
                
                try:
                    # Build the target URL for paperglass status update
                    url = f"{settings.PAPERGLASS_API_URL}/api/v5/status_update/{operation_type}"
                    
                    # Generate unique task name
                    import uuid
                    task_name = f"status-update-{operation_type}-{uuid.uuid4().hex[:8]}"
                    
                    response = await cloud_task_adapter.create_task(
                        location=settings.GCP_LOCATION_2,
                        queue=settings.DEFAULT_TASK_QUEUE,
                        url=url,
                        payload=status_payload,
                        task_name=task_name,
                        service_account_email=settings.SERVICE_ACCOUNT_EMAIL
                    )

                    self.logger.info("Successfully created status update task for paperglass", extra={
                        "run_id": run_id,
                        "operation_type": operation_type,
                        "url": url,
                        "task_name": task_name,
                        "cloud_task_response": response,
                        "operation": "publish_status"
                    })
                
                finally:
                    await cloud_task_adapter.close()
            else:
                self.logger.info("Skipping PaperGlass callback for non-entity-extraction operation", extra={
                    "run_id": run_id,
                    "operation_type": operation_type,
                    "status": status.value,
                    "reason": "operation_type_not_entity_extraction"
                })
                
        except Exception as e:
            self.logger.error("Error publishing status notification", extra={
                "run_id": run_id,
                "error": str(e),
                "operation": "publish_status"
            })
            # Don't re-raise the exception as status publication failure shouldn't fail the main operation

        # Update all keys to update their expiry so they will exist for the next few minutes.  
        # If we immediately delete, there is a window of time where a status won't exist in paperglass or here.
        try:
            # Get the list of pipeline IDs and update their TTL
            pipeline_list_key = self._get_pipeline_list_key(run_id)
            pipeline_ids = await self.redis_client.smembers(pipeline_list_key)
            
            # Update TTL for pipeline list
            await self.redis_client.expire(pipeline_list_key, settings.STATUS_POST_COMPLETE_TTL)  
            
            # Update TTL for each pipeline hash
            for pipeline_id in pipeline_ids:
                pipeline_hash_key = self._get_pipelines_hash_key(run_id, pipeline_id)
                await self.redis_client.expire(pipeline_hash_key,  settings.STATUS_POST_COMPLETE_TTL) 
            
            # Update TTL for job data
            job_key = f"djt::{run_id}"
            await self.redis_client.expire(job_key,  settings.STATUS_POST_COMPLETE_TTL)  
            
            self.logger.debug("Updated TTL for pipeline data after status publication", extra={
                "run_id": run_id,
                "pipeline_count": len(pipeline_ids),
                "ttl_seconds":  settings.STATUS_POST_COMPLETE_TTL,
                "operation": "publish_status"
            })
            
        except Exception as e:
            self.logger.error("Error updating TTL for pipeline data", extra={
                "run_id": run_id,
                "error": str(e),
                "operation": "publish_status"
            })
