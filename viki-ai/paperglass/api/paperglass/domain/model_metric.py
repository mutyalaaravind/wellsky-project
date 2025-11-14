from pydantic import BaseModel
from enum import Enum
from typing import Dict, Any
import json

from paperglass.log import CustomLogger
from paperglass.domain.util_json import DateTimeEncoder, JsonUtil
LOGGER = CustomLogger(__name__)

class Metric(BaseModel):
    class MetricType(str, Enum):
        HEARTBEAT = "Heartbeat"

        HHH_MEDICATIONS_GET = "HHH::MEDICATIONS_GET"
        HHH_MEDICATIONS_ADD = "HHH::MEDICATIONS_ADD"
        HHH_MEDICATIONS_FREEFORM_ADD = "HHH::MEDICATIONS_FREEFORM_ADD"
        HHH_MEDICATIONS_UPDATE = "HHH::MEDICATIONS_UPDATE"
        HHH_MEDICATIONS_DELETE = "HHH::MEDICATIONS_DELETE"
        HHH_ATTACHMENTS_GET = "HHH::ATTACHMENTS_GET"
        HHH_ATTACHMENT_ACCEPTED = "HHH::ATTACHMENT_ACCEPTED"
        HHH_ATTACHMENT_SKIPPED = "HHH::ATTACHMENT_SKIPPED"
        HHH_CLASSIFICATION_GET = "HHH::CLASSIFICATION_GET"
        HHH_ATTACHMENT_METADATA_GET = "HHH::ATTACHMENT_METADATA_GET"
        HHH_ATTACHMENT_METADATA_MISSING = "HHH::ATTACHMENT_METADATA_MISSING"
        HHH_AUTH = "HHH::AUTH"

        
    @classmethod
    def send(cls, metricType: str|MetricType, tags: Dict[str, Any], branch: str = None):
        mt = None
        if isinstance(metricType, Metric.MetricType):
            mt = metricType.value
        else:
            mt = str(metricType)

        if branch:
            tags["branch"] = branch
            mt = f"{mt}:{branch}"

        LOGGER.info(f"METRIC::{mt}", extra=JsonUtil.clean(tags))
