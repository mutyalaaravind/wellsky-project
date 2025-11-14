from pydantic import BaseModel
from enum import Enum
from typing import Dict, Any, Union

from util.custom_logger import getLogger
from util.json_utils import JsonUtil

LOGGER = getLogger(__name__)


class Metric(BaseModel):
    class MetricType(str, Enum):
        HEARTBEAT = "Heartbeat"
        
        # Task execution metrics
        TASK_START = "TASK::START"
        TASK_COMPLETE = "TASK::COMPLETE"
        TASK_ERROR = "TASK::ERROR"
        
        # Entity extraction metrics
        ENTITY_EXTRACTION_START = "ENTITY_EXTRACTION::START"
        ENTITY_EXTRACTION_COMPLETE = "ENTITY_EXTRACTION::COMPLETE"
        ENTITY_EXTRACTION_ERROR = "ENTITY_EXTRACTION::ERROR"
        
        # Callback metrics
        CALLBACK_PUBLISH_START = "CALLBACK::PUBLISH_START"
        CALLBACK_PUBLISH_COMPLETE = "CALLBACK::PUBLISH_COMPLETE"
        CALLBACK_PUBLISH_ERROR = "CALLBACK::PUBLISH_ERROR"
        
        # LLM metrics
        LLM_REQUEST_START = "LLM::REQUEST_START"
        LLM_REQUEST_COMPLETE = "LLM::REQUEST_COMPLETE"
        LLM_REQUEST_ERROR = "LLM::REQUEST_ERROR"
        LLM_TOKEN_USAGE = "LLM::TOKEN_USAGE"
        
        # Pipeline metrics
        PIPELINE_START = "PIPELINE::START"
        PIPELINE_PAGE_START = "PIPELINE::PAGE::START"
        PIPELINE_COMPLETE = "PIPELINE::COMPLETE"
        PIPELINE_PAGE_COMPLETE = "PIPELINE::PAGE::COMPLETE"
        PIPELINE_ERROR = "PIPELINE::ERROR"
        PIPELINE_PAGE_ERROR = "PIPELINE::PAGE::ERROR"
        
    @classmethod
    def send(cls, metricType: Union[str, MetricType], tags: Dict[str, Any], branch: str = None):
        """
        Send a metric event with the specified type and tags.
        
        :param metricType: The metric type (string or MetricType enum)
        :param tags: Dictionary of tags/metadata for the metric
        :param branch: Optional branch identifier to append to the metric type
        """
        mt = None
        if isinstance(metricType, Metric.MetricType):
            mt = metricType.value
        else:
            mt = str(metricType)

        if branch:
            tags["branch"] = branch
            mt = f"{mt}:{branch}"

        # Clean the tags to ensure they are JSON serializable
        clean_tags = JsonUtil.clean(tags)
        
        LOGGER.info(f"METRIC::{mt}", extra=clean_tags)
