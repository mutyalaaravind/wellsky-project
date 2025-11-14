from pydantic import BaseModel
from enum import Enum
from typing import Dict, Any
import json

from utils.custom_logger import CustomLogger
from utils.json import DateTimeEncoder, JsonUtil
LOGGER = CustomLogger(__name__)

class Metric(BaseModel):
    class MetricType(str, Enum):
        HEARTBEAT = "Heartbeat"

        DOCUMENT_CREATED = "DOCUMENT::CREATED"
        DOCUMENT_PAGE_CREATED = "DOCUMENTPAGE::CREATED"

        MEDICATIONEXTRACTION_STEP_PREFIX = "PIPELINE::MEDICATIONEXTRACTION::"
        PIPELINE_CLOUDTASK_PREFIX = "PIPELINE::CLOUDTASK::"
        

        
    @classmethod
    def send(cls, metricType: str|MetricType, tags: Dict[str, Any]={}, branch: str = None):
        mt = None
        if isinstance(metricType, Metric.MetricType):
            mt = metricType.value
        else:
            mt = str(metricType)

        if branch:
            tags.update({"branch": branch})            
            mt = f"{mt}:{branch}"
        
        extra = JsonUtil.clean(tags)        
        LOGGER.info(f"METRIC::{mt}", extra=extra)
