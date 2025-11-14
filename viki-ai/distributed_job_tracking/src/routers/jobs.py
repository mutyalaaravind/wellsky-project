from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any

from models.simple_job import SimpleJobCreate, SimpleJobResponse, SimpleJobUpdate
from models.pipeline import PipelineStatusUpdate, PipelineResponse, PipelineListResponse
from usecases.simple_job_service import SimpleJobService
from usecases.pipeline_service import PipelineService

from util.custom_logger import getLogger
from util.exception import exceptionToMap

LOGGER = getLogger(__name__)

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


def get_simple_job_service() -> SimpleJobService:
    """Dependency to get simple job service instance"""
    return SimpleJobService()


def get_pipeline_service() -> PipelineService:
    """Dependency to get pipeline service instance"""
    return PipelineService()


@router.post("/", response_model=SimpleJobResponse)
async def create_job(
    job_data: SimpleJobCreate,
    job_service: SimpleJobService = Depends(get_simple_job_service)
):
    """
    Create a new job entry.
    
    This endpoint creates a job with the following structure and stores it in Redis
    as a hash with key "djt::{run_id}" and hashkey "job".
    """
    try:
        # Check if job with this run_id already exists
        if await job_service.job_exists(job_data.run_id):
            LOGGER.warning(f"Job with run_id '{job_data.run_id}' already exists")
            raise HTTPException(
                status_code=409, 
                detail=f"Job with run_id '{job_data.run_id}' already exists"
            )        
        job = await job_service.create_job(job_data)
        return SimpleJobResponse(job=job, message="Job created successfully")
    except HTTPException as e:
        LOGGER.warning(f"HTTPException occurred: {str(e)}", extra={"error": exceptionToMap(e)})
        raise
    except Exception as e:
        LOGGER.error(f"Error occurred while creating job: {str(e)}", extra={"error": exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")
    finally:
        await job_service.close()


@router.get("/{run_id}", response_model=SimpleJobResponse)
async def get_job(
    run_id: str,
    job_service: SimpleJobService = Depends(get_simple_job_service)
):
    """Get a job by run_id"""
    try:
        job = await job_service.get_job(run_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return SimpleJobResponse(job=job, message="Job retrieved successfully")
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error occurred while getting job: {str(e)}", extra={"error": exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")
    finally:
        await job_service.close()


@router.put("/{run_id}", response_model=SimpleJobResponse)
async def update_job(
    run_id: str,
    job_update: SimpleJobUpdate,
    job_service: SimpleJobService = Depends(get_simple_job_service)
):
    """Update a job by run_id"""
    try:
        job = await job_service.update_job(run_id, job_update)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return SimpleJobResponse(job=job, message="Job updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error occurred while updating job: {str(e)}", extra={"error": exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")
    finally:
        await job_service.close()


@router.delete("/{run_id}")
async def delete_job(
    run_id: str,
    job_service: SimpleJobService = Depends(get_simple_job_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Delete a job and all associated data by run_id.
    
    This endpoint deletes:
    - The job data from djt::{run_id} hash
    - The pipeline list from djt::{run_id}:pipeline_list set
    - All pipeline status data from djt::{run_id}:pipelines:{pipeline_id} hashes
    """
    try:
        # Check if job exists first
        job_exists = await job_service.job_exists(run_id)
        if not job_exists:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Delete all pipeline data first
        pipelines_deleted = await pipeline_service.delete_all_pipelines_for_run(run_id)
        
        # Delete the job
        job_deleted = await job_service.delete_job(run_id)
        
        if not job_deleted:
            # This shouldn't happen since we checked existence, but handle it
            raise HTTPException(status_code=404, detail="Job not found")
        
        LOGGER.info("Job and associated data deleted successfully", extra={
            "run_id": run_id,
            "job_deleted": job_deleted,
            "pipelines_deleted": pipelines_deleted,
            "operation": "delete_job_and_data"
        })
        
        return JSONResponse(
            content={
                "message": "Job and all associated data deleted successfully",
                "job_deleted": job_deleted,
                "pipelines_deleted": pipelines_deleted
            },
            status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error occurred while deleting job and data: {str(e)}", extra={"error": exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to delete job and data: {str(e)}")
    finally:
        await job_service.close()
        await pipeline_service.close()


@router.get("/{job_id}/pipelines", response_model=PipelineListResponse)
async def list_pipelines(
    job_id: str,
    request: Request,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    List all pipelines for a job.
    
    This endpoint retrieves all pipelines for the given job_id (used as run_id).
    It first pulls the set of pipeline_ids from Redis using key djt::{run_id}:pipelines.
    Then it retrieves each pipeline status from Redis using hgetall with key djt::{run_id}:pipelines:{pipeline_id}.
    
    Returns a PipelineListResponse with:
    - status: Overall status of all pipelines (failed > processing > complete)
    - pipeline_count: Number of pipelines in this run_id
    - pipeline_ids: List of pipeline_ids in this run_id
    - elapsed_time: Elapsed time since earliest pipeline creation
    - pipelines: List of individual pipeline statuses with metadata
    """
    try:
        pipelines_data = await pipeline_service.list_pipelines_for_run(job_id)
        return pipelines_data
    except Exception as e:
        LOGGER.error(f"Error occurred while listing pipelines: {str(e)}", extra={"error": exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to list pipelines: {str(e)}")
    finally:
        await pipeline_service.close()
        

@router.post("/{job_id}/pipelines/{pipeline_id}/status", response_model=PipelineResponse)
async def update_pipeline_status(
    job_id: str,
    pipeline_id: str,
    pipeline_data: PipelineStatusUpdate,
    request: Request,
    pipeline_service: PipelineService = Depends(get_pipeline_service)
):
    """
    Update pipeline status for a job.
    
    This endpoint updates a pipeline with the provided data structure and uses a Redis pipeline to:
    a) Add the pipeline_id to a set at djt::{run_id}:pipeline_list
    b) Create a hash at key djt::{run_id}:pipelines:{pipeline_id} with a hash key of "{page_number}" or "document" if page_number is null
    
    The job_id parameter is used as the run_id for Redis key generation.
    The page_number field is optional - if null, "document" will be used as the hash key.
    
    If the job doesn't exist, it will be auto-created using the job creation fields in the pipeline data.
    """
    try:
        pipeline = await pipeline_service.update_pipeline_status(job_id, pipeline_id, pipeline_data)
        return PipelineResponse(pipeline=pipeline, message="Pipeline status updated successfully")
    except HTTPException as e:
        LOGGER.warning(f"HTTPException occurred: {str(e)}", extra={"error": exceptionToMap(e)})
        raise
    except Exception as e:
        LOGGER.error(f"Error occurred while updating pipeline status: {str(e)}", extra={"error": exceptionToMap(e)})
        raise HTTPException(status_code=500, detail=f"Failed to update pipeline status: {str(e)}")
    finally:
        await pipeline_service.close()
