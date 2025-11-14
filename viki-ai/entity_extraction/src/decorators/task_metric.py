import functools
import time
from datetime import datetime
from typing import Callable, Any

from util.exception import exceptionToMap
from models.general import TaskParameters, TaskResults
from models.metric import Metric
from util.custom_logger import getLogger

LOGGER = getLogger(__name__)


def task_metric(func: Callable) -> Callable:
    """
    Decorator to calculate elapsed time and log metric events for task execution.
    
    This decorator logs the start and end of task processes with metadata from TaskParameters.
    It calculates the elapsed time and includes it in the logging metrics.
    
    :param func: The function to decorate (should be a run method that takes TaskParameters)
    :return: The decorated function
    """
    @functools.wraps(func)
    async def wrapper(self, task_params: TaskParameters) -> TaskResults:
        start_time = time.time()
        start_datetime = datetime.now()
        
        # Extract metadata from TaskParameters for logging
        metric_metadata = {
            "task_id": task_params.task_config.id,
            "task_type": task_params.task_config.type.value if hasattr(task_params.task_config.type, 'value') else str(task_params.task_config.type),
            "pipeline_scope": task_params.pipeline_scope,
            "pipeline_key": task_params.pipeline_key,
            "run_id": task_params.run_id,
            "app_id": task_params.app_id,
            "tenant_id": task_params.tenant_id,
            "patient_id": task_params.patient_id,
            "document_id": task_params.document_id,
            "invoker_class": self.__class__.__name__,
            "function_name": func.__name__,
            "start_time": start_datetime.isoformat()
        }
        
        # Send task start metric
        Metric.send(Metric.MetricType.TASK_START, {
            **metric_metadata,
            "event": "task_execution_start"
        })
        
        try:
            # Execute the original function
            result = await func(self, task_params)
            
            # Calculate elapsed time
            end_time = time.time()
            elapsed_time = float(end_time - start_time)
            elapsed_time_ms = int((end_time - start_time) * 1000)
            end_datetime = datetime.now()
            
            # Update result with elapsed time if not already set
            if hasattr(result, 'execution_time_ms') and result.execution_time_ms is None:
                result.execution_time_ms = elapsed_time_ms
            
            # Send task completion metric
            error_message = getattr(result, 'error_message', None)
            completion_metadata = {
                **metric_metadata,
                "event": "task_execution_complete",
                "end_time": end_datetime.isoformat(),
                "elapsed_time": elapsed_time,
                "success": result.success if hasattr(result, 'success') else True                
            }

            if not error_message:
                Metric.send(Metric.MetricType.TASK_COMPLETE, completion_metadata)
            else:                                
                completion_metadata.update({
                    "error_message": getattr(result, 'error_message', None),
                    "error": result.get('error', None) if isinstance(result, dict) else None
                })
                Metric.send(Metric.MetricType.TASK_ERROR, completion_metadata)
            
            return result
            
        except Exception as e:
            # Calculate elapsed time for failed execution
            end_time = time.time()
            elapsed_time = float(end_time - start_time)
            elapsed_time_ms = int((end_time - start_time) * 1000)
            end_datetime = datetime.now()
            
            # Send task failure metric
            failure_metadata = {
                **metric_metadata,
                "event": "task_execution_error",
                "end_time": end_datetime.isoformat(),
                "elapsed_time": elapsed_time,
                "success": False,
                "error_message": str(e),
                "error": exceptionToMap(e),                
            }
            
            Metric.send(Metric.MetricType.TASK_ERROR, failure_metadata)
            
            # Re-raise the exception
            raise
    
    return wrapper
