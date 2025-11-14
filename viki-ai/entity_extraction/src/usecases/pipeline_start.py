from typing import Dict, Any, Optional
import sys
import os
from datetime import datetime

# Add the adapters directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'adapters'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from adapters.firestore import search_pipeline_config
from models.pipeline_config import PipelineConfig
from models.general import TaskParameters, PipelineParameters
from models.djt_models import PipelineStatusUpdate, PipelineStatus
from models.metric import Metric
from adapters.djt_client import get_djt_client
from util.uuid_utils import generate_id, generate_timeprefixed_id
from util.date_utils import now_utc
from util.custom_logger import getLogger, set_pipeline_context
from util.exception import exceptionToMap
from util.tracing import trace_function, add_span_attributes, add_span_event
from adapters.firestore import search_pipeline_config
from usecases.task_orchestrator import TaskOrchestrator

import settings


logger = getLogger(__name__)


@trace_function(
    name="pipeline.start",
    attributes={
        "operation.type": "pipeline_start",
        "service.component": "entity_extraction"
    }
)
async def pipeline_start(scope: str, pipeline_key: str, pipeline_params: PipelineParameters = None) -> PipelineParameters:
    """
    Start a pipeline by retrieving its configuration and initiating the pipeline process.
    
    Args:
        scope: The scope of the pipeline (e.g., 'default', 'medical', etc.)
        pipeline_key: The key identifier of the pipeline
        request_body: The PipelineParameters containing pipeline parameters
        
    Returns:
        Dictionary containing pipeline start information and status
        
    Raises:
        ValueError: If pipeline configuration is not found
        Exception: For other errors during pipeline start
    """
    
    # Add span attributes for tracing
    add_span_attributes({
        "pipeline.scope": scope,
        "pipeline.key": pipeline_key,
        "pipeline.app_id": pipeline_params.app_id if pipeline_params else None,
        "pipeline.tenant_id": pipeline_params.tenant_id if pipeline_params else None,
        "pipeline.document_id": pipeline_params.document_id if pipeline_params else None,
        "pipeline.page_number": pipeline_params.page_number if pipeline_params else None
    })
    
    # Initialize extra dictionary with input parameters
    extra = {
        "scope": scope,
        "pipeline_key": pipeline_key,
        "operation": "pipeline_start"
    }

    if scope is None or scope.strip() == "" or pipeline_key is None or pipeline_key.strip() == "":
        extra.update({
            "error_type": "invalid_input",
            "operation_result": "failed"
        })
        add_span_event("validation_failed", {"error": "invalid_input_parameters"})
        logger.error("Invalid input parameters for pipeline start", extra=extra)
        raise ValueError(f"Scope '{scope}' and pipeline_key '{pipeline_key}' must be provided")
    
    add_span_event("pipeline_start_initiated")
    logger.info("Starting pipeline start process", extra=extra)
    
    try:
        # Retrieve the pipeline configuration
        logger.debug(f"Searching for pipeline configuration: scope '{scope}' pipeline '{pipeline_key}'", extra=extra)
        
        config = await search_pipeline_config(scope, pipeline_key)
        
        if config is None:
            extra.update({
                "error_type": "configuration_not_found",
                "operation_result": "failed"
            })
            logger.error("Pipeline configuration not found", extra=extra)
            raise ValueError(f"Pipeline configuration not found for scope '{scope}' and key '{pipeline_key}'")
        
        # Update extra with configuration details
        extra.update({
            "pipeline_id": config.id,
            "pipeline_name": config.name,
            "pipeline_version": config.version,
            "task_count": len(config.tasks) if config.tasks is not None else 0,
            "output_entity": config.output_entity
        })
        
        logger.debug("Pipeline configuration retrieved successfully", extra=extra)       

        
        if config.tasks is None or len(config.tasks) == 0:
            extra.update({
                "error_type": "no_tasks_defined",
                "operation_result": "failed"
            })
            import json
            from util.json_utils import DateTimeEncoder

            
            
            logger.error(f"Pipeline configuration: {json.dumps(config.dict(), indent=2, cls=DateTimeEncoder)}", extra=extra)
            logger.error("No tasks defined in pipeline configuration", extra=extra)
            raise ValueError("Pipeline configuration must define at least one task")        

        # Use the run_id passed in or generate run_id with date/time prefix: YYYYMMddTHHmmss-UUID
        run_id = pipeline_params.run_id or generate_timeprefixed_id()

        pipeline_params.pipeline_scope = scope
        pipeline_params.pipeline_key = pipeline_key
        pipeline_params.run_id = run_id
        pipeline_params.pipeline_start_date = now_utc()
        
        # Set pipeline context for logging
        set_pipeline_context(
            app_id=pipeline_params.app_id,
            tenant_id=pipeline_params.tenant_id,
            patient_id=pipeline_params.patient_id,
            document_id=pipeline_params.document_id,
            page_number=pipeline_params.page_number,
            run_id=run_id,
            pipeline_scope=scope,
            pipeline_key=pipeline_key
        )
        
        # Send pipeline start metric - conditional based on page_number
        pipeline_metric_metadata = {
            "pipeline_scope": scope,
            "pipeline_key": pipeline_key,
            "pipeline_id": f"{scope}.{pipeline_key}",
            "pipeline_name": config.name,
            "pipeline_version": config.version,
            "run_id": run_id,
            "app_id": pipeline_params.app_id,
            "tenant_id": pipeline_params.tenant_id,
            "patient_id": pipeline_params.patient_id,
            "document_id": pipeline_params.document_id,
            "page_number": pipeline_params.page_number,
            "task_count": len(config.tasks),
            "first_task_id": config.tasks[0].id,
            "pipeline_start_date": pipeline_params.pipeline_start_date.isoformat() if pipeline_params.pipeline_start_date else None,
        }
        
        if pipeline_params.page_number is None:
            # Document-level pipeline start
            pipeline_metric_metadata["event"] = "pipeline_execution_start"
            Metric.send(Metric.MetricType.PIPELINE_START, pipeline_metric_metadata)
        else:
            # Page-level pipeline start
            pipeline_metric_metadata["event"] = "pipeline_page_execution_start"
            Metric.send(Metric.MetricType.PIPELINE_PAGE_START, pipeline_metric_metadata)
        
        task_config = config.tasks[0]

        task_params: TaskParameters = TaskParameters.from_pipeline_parameters(pipeline_params, task_config=task_config)
        
        # Update pipeline status in distributed job tracking before starting execution
        try:
            djt_client = get_djt_client()
            pipeline_status_data = PipelineStatusUpdate(
                status=PipelineStatus.IN_PROGRESS,
                page_number=pipeline_params.page_number,
                metadata={
                    "pipeline_scope": scope,
                    "pipeline_key": pipeline_key,
                    "pipeline_name": config.name,
                    "pipeline_version": config.version,
                    "task_count": len(config.tasks),
                    "first_task": task_config.id,
                    "pipeline_start_date": pipeline_params.pipeline_start_date.isoformat() if pipeline_params.pipeline_start_date else None
                },
                app_id=pipeline_params.app_id,
                tenant_id=pipeline_params.tenant_id,
                patient_id=pipeline_params.patient_id,
                document_id=pipeline_params.document_id,
                pages=pipeline_params.page_count
            )
            
            await djt_client.pipeline_status_update(
                job_id=run_id,
                pipeline_id=f"{scope}:{pipeline_key}",
                pipeline_data=pipeline_status_data
            )
            
            logger.info(f"Updated DJT pipeline status to IN_PROGRESS for run_id: {run_id}", extra=extra)
            
        except Exception as djt_error:
            # Log the error but don't fail the pipeline start
            extra.update({"djt_error": exceptionToMap(djt_error)})
            logger.warning(f"Failed to update DJT pipeline status: {str(djt_error)}", extra=extra)
        
        # Use TaskOrchestrator to run the first task and handle the entire pipeline
        orchestrator = TaskOrchestrator(task_params.task_config.id)
        results = await orchestrator.invoke(task_params)

        # Prepare the response with pipeline information
        from util.json_utils import JsonUtil
        response = JsonUtil.clean(config.dict())
        
        # Update extra with final status
        extra.update({
            "status": "started",
            "operation_result": "success"
        })
        
        logger.info("Pipeline started successfully", extra=extra)

        return pipeline_params
        
    except ValueError as e:
        extra.update({
            "error": exceptionToMap(e),
            "operation_result": "failed"
        })
        logger.error("ValueError in pipeline_start", extra=extra)
        raise
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e),
            "operation_result": "failed"
        })
        logger.error(f"Unexpected error in pipeline_start: {str(e)}", extra=extra)
        raise
