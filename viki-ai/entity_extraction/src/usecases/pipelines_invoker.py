from models.general import TaskParameters, TaskResults, PipelineParameters
from adapters.cloud_tasks import CloudTaskAdapter
from adapters.djt_client import get_djt_client
from models.djt_models import PipelineStatusUpdate, PipelineStatus
from util.custom_logger import getLogger
from util.exception import exceptionToMap
import settings

LOGGER = getLogger(__name__)


class PipelinesInvoker:
    """Invoker for pipeline-type tasks."""
    
    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Run a pipelines task with the given parameters.
        
        :param task_params: The parameters for the pipelines task to run.
        :return: The task results after running the pipelines.
        """
        extra = {
            "task_params": task_params.dict(),
        }

        try:
            pipeline_refs = task_params.task_config.pipelines
            LOGGER.info(f"Running pipelines task with {len(pipeline_refs)} pipeline(s)", extra=extra)
            
            # Collect pipeline names in the format {scope}.{pipeline_key}
            pipeline_names = [f"{pipeline_ref.scope}.{pipeline_ref.id}" for pipeline_ref in pipeline_refs]
            pipeline_names_list = ",".join(pipeline_names)
            
            pipeline_results = []
            cloud_task_adapter = CloudTaskAdapter()
            
            try:
                for pipeline_ref in pipeline_refs:

                    pipeline_scope = pipeline_ref.scope 
                    pipeline_id = pipeline_ref.id

                    extra.update({
                        "pipeline_scope": pipeline_scope,
                        "pipeline_id": pipeline_id,
                        "pipeline_ref": pipeline_ref.dict()
                    })

                    LOGGER.debug(f"Invoking pipeline scope: {pipeline_scope} pipeline: {pipeline_id}", extra=extra)
                    
                    # Create PipelineParameters for the sub-pipeline
                    # Merge context from the pipeline reference with existing context
                    merged_context = task_params.context.copy() if task_params.context else {}
                    if pipeline_ref.context:
                        merged_context.update(pipeline_ref.context)
                    
                    pipeline_params = PipelineParameters(
                        app_id=task_params.app_id,
                        tenant_id=task_params.tenant_id,
                        patient_id=task_params.patient_id,
                        document_id=task_params.document_id,
                        page_number=task_params.page_number,
                        pipeline_scope=pipeline_scope,
                        pipeline_key=pipeline_ref.id,
                        pipeline_start_date=task_params.pipeline_start_date,
                        run_id=task_params.run_id,
                        subject=task_params.subject,
                        context=merged_context
                    )
                    
                    # Build the target URL for the start_pipeline endpoint
                    base_url = pipeline_ref.host or settings.SELF_API_URL
                    url = f"{base_url}/api/pipeline/{pipeline_scope}/{pipeline_id}/start"
                    
                    # Create a cloud task to invoke the pipeline
                    response = await cloud_task_adapter.create_task(
                        location=settings.GCP_LOCATION_2,
                        queue=pipeline_ref.queue or settings.DEFAULT_TASK_QUEUE,
                        url=url,
                        payload=pipeline_params.dict(),
                        task_name=f"pipeline-{pipeline_ref.id}-{task_params.run_id}",
                        service_account_email=settings.SERVICE_ACCOUNT_EMAIL
                    )
                    
                    LOGGER.info(f"Successfully queued pipeline {pipeline_ref.id}", extra={
                        **extra,
                        "pipeline_id": pipeline_ref.id,
                        "cloud_task_response": response
                    })
                    
                    # Update pipeline status in DJT service
                    try:
                        djt_client = get_djt_client()
                        
                        # Create pipeline status update
                        pipeline_status_update = PipelineStatusUpdate(
                            id=f"{pipeline_scope}.{pipeline_id}",
                            status=PipelineStatus.IN_PROGRESS,
                            page_number=task_params.page_number,
                            metadata={
                                "cloud_task_response": response,
                                "queue": pipeline_ref.queue or settings.DEFAULT_TASK_QUEUE,
                                "url": url,
                                "pipeline_scope": pipeline_scope
                            },
                            app_id=task_params.app_id,
                            tenant_id=task_params.tenant_id,
                            patient_id=task_params.patient_id,
                            document_id=task_params.document_id,
                            pages=task_params.page_count or 1
                        )
                        
                        # Call DJT service to update pipeline status
                        djt_response = await djt_client.pipeline_status_update(
                            job_id=task_params.run_id,
                            pipeline_id=f"{pipeline_scope}:{pipeline_id}",
                            pipeline_data=pipeline_status_update
                        )
                        
                        LOGGER.info(f"Successfully updated DJT pipeline status for {pipeline_ref.id}", extra={
                            **extra,
                            "djt_response": djt_response
                        })
                        
                    except Exception as djt_error:
                        # Log DJT error but don't fail the entire pipeline operation
                        LOGGER.warning(f"Failed to update DJT pipeline status for {pipeline_ref.id}: {str(djt_error)}", extra={
                            **extra,
                            "djt_error": exceptionToMap(djt_error)
                        })
                    
                    pipeline_results.append({
                        "pipeline_id": pipeline_ref.id,
                        "status": "queued",
                        "message": f"Pipeline {pipeline_ref.id} queued successfully",
                        "cloud_task_response": response
                    })
                    
            finally:
                await cloud_task_adapter.close()
            
            LOGGER.info("Pipelines task completed")
            
            return TaskResults(
                success=True,
                results=None,
                metadata={
                    "invoker_type": "pipelines",
                    "pipeline_count": len(pipeline_refs),                    
                    "pipelines_executed": pipeline_names_list,
                    "pipeline_results": pipeline_results
                }
            )
            
        except Exception as e:
            extra.update({
                "error": exceptionToMap(e),
                "task_params": task_params.dict()
            })
            LOGGER.error(f"Error running pipelines task: {str(e)}", extra=extra)
            return TaskResults(
                success=False,
                error_message=str(e),
                results=None,
                metadata={
                    "invoker_type": "pipelines",
                    "error": exceptionToMap(e)
                }
            )
