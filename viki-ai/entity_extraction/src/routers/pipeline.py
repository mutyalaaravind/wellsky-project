from fastapi import APIRouter, HTTPException, Request, Depends
from usecases.pipeline_start import pipeline_start
from usecases.task_orchestrator import TaskOrchestrator
from usecases.pipeline_config import create_or_update_pipeline_config
from util.custom_logger import getLogger
from util.exception import exceptionToMap
from models.general import PipelineParameters, TaskParameters
from models.pipeline_config import PipelineConfig, validate_pipeline_config, pipeline_config_to_dict
from typing import Dict, Any

LOGGER = getLogger(__name__)

# Create router for pipeline endpoints
router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.post("/{scope}/{pipeline_key}/start")
async def start_pipeline(
    scope: str,
    pipeline_key: str,
    pipeline_params: PipelineParameters,
    request: Request
):
    """Start a pipeline for the given scope and pipeline key."""
        
    extra = {
        "http_request": {
            "method": "POST",
            "url": f"/api/pipeline/{scope}/{pipeline_key}/start",
            "body": pipeline_params.model_dump(),
            "headers": dict(request.headers),
        }
    }
    
    try:
        # Get the request body        
        LOGGER.debug(f"Starting pipeline for scope: {scope}, pipeline: {pipeline_key} with params: {pipeline_params.model_dump()}", extra=extra)
        result = await pipeline_start(scope, pipeline_key, pipeline_params)
        return result.dict()
        
    except ValueError as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Value error in request", extra=extra)
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Error starting pipeline", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Error starting pipeline: {str(e)}"
        )

@router.post("/{scope}/{pipeline_key}/{task}/run")
async def run_pipeline_task(
    scope: str,
    pipeline_key: str,
    task: str,
    task_parameters: TaskParameters
):
    """Run a pipeline task with the given TaskParameters."""
    
    extra = {
        "http_request": {
            "method": "POST",
            "url": f"/api/pipeline/{scope}/{pipeline_key}/{task}/run",
            "body": task_parameters.model_dump(),
            "task_parameters": task_parameters.model_dump(),
        }
    }
    
    try:
        # Log the task execution
        LOGGER.info(f"Running pipeline task '{task}' for scope: {scope}, pipeline: {pipeline_key}", extra=extra)
        
        # Use TaskOrchestrator to run the task and handle next tasks automatically
        orchestrator = TaskOrchestrator(task)
        result = await orchestrator.run(task_parameters)
        
        return result
        
    except ValueError as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Value error in task execution", extra=extra)
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error("Error running pipeline task", extra=extra)
        raise HTTPException(
            status_code=500,
            detail=f"Error running pipeline task: {str(e)}"
        )
