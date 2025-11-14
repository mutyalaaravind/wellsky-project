from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any, Union, List
from datetime import datetime
import uuid

from util.date_utils import now_utc
from util.uuid_utils import generate_id
from util.uri_utils import DocumentUriGenerator

from models.pipeline_config import TaskConfig
from models.base import AggBase
import settings


def generate_run_id() -> str:
    """
    Generate a run ID with date/time prefix in format: YYYYMMDDTHHmmss-UUID
    
    Returns:
        Formatted run ID string
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%dT%H%M%S")
    uuid_part = str(generate_id())
    return f"{timestamp}-{uuid_part}"


class PipelineParameters(BaseModel):
    """
    Base parameters for pipeline operations.
    """
    business_unit: Optional[str] = "unknown"
    solution_code: Optional[str] = "unknown"
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    page_number: Optional[int] = None
    page_count: Optional[int] = None
    priority: Optional[str] = "default"
    pipeline_scope: Optional[str] = None
    pipeline_key: Optional[str] = None
    pipeline_start_date: Optional[datetime] = Field(default_factory=now_utc)
    run_id: str = Field(default_factory=generate_run_id)
    subject: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)    
    context: dict = Field(default_factory=dict)    
    entities: Optional[dict] = Field(default_factory=dict)
    task_retry_count: int = Field(default_factory=lambda: settings.TASK_RETRY_COUNT_DEFAULT)
    task_retry_factor: int = Field(default_factory=lambda: settings.TASK_RETRY_FACTOR_DEFAULT)

class TaskParameters(PipelineParameters):
    """
    Parameters for module tasks in the entity extraction pipeline.
    """        
    task_config: TaskConfig
    task_queue_date: datetime = Field(default_factory=now_utc)
    task_iteration: int = 0

    @property
    def subject_uri(self) -> str:
        """
        Generate the subject URI based on whether a page number is set.
        
        Returns:
            Document-level URI if page_number is None, otherwise page-level URI.
        """
        return DocumentUriGenerator.generate_subject_uri(
            app_id=self.app_id,
            tenant_id=self.tenant_id,
            patient_id=self.patient_id,
            document_id=self.document_id,
            page_number=self.page_number
        )

    @classmethod
    def from_pipeline_parameters(cls, pipeline_params: PipelineParameters, task_config: TaskConfig):
        """
        Create TaskParameters from PipelineParameters.
        
        :param pipeline_params: The base pipeline parameters.
        :return: TaskParameters instance.
        """
        return cls(
            app_id=pipeline_params.app_id,
            tenant_id=pipeline_params.tenant_id,
            patient_id=pipeline_params.patient_id,
            document_id=pipeline_params.document_id,
            page_number=pipeline_params.page_number,
            page_count=pipeline_params.page_count,
            priority=pipeline_params.priority,
            pipeline_scope=pipeline_params.pipeline_scope,
            pipeline_key=pipeline_params.pipeline_key,                        
            pipeline_start_date=pipeline_params.pipeline_start_date,
            run_id=pipeline_params.run_id,            
            task_config=task_config,
            subject=pipeline_params.subject,
            context=pipeline_params.context,
            entities=pipeline_params.entities,
            task_retry_count=pipeline_params.task_retry_count,
            task_retry_factor=pipeline_params.task_retry_factor
        )

    

class TaskResults(BaseModel):
    """
    Results returned by module tasks in the entity extraction pipeline.
    """
    
    success: bool = True    
    results: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    error_message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityWrapper(BaseModel):
    """
    Wrapper for entity extraction results.
    
    Attributes:
        entity_id: Unique identifier for the entity
        entity_type: Type of the entity (e.g., "medication", "procedure")
        entity_data: The extracted data for the entity
        timestamp: Timestamp of when the entity was extracted
    """
    schema_ref: str
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    page_number: Optional[int] = None
    run_id: str = Field(default_factory=generate_run_id)
    is_entity_list: bool = False
    entities: Union[Dict[str, Any], List[Dict[str, Any]]]

    @field_validator('entities')
    @classmethod
    def validate_entities(cls, v):
        """
        Validate that entities field contains proper data structure.
        
        Args:
            v: The entities value to validate
            
        Returns:
            The validated entities value
            
        Raises:
            ValueError: If entities structure is invalid
        """
        if isinstance(v, list):
            # Ensure all items in list are dictionaries
            if not all(isinstance(item, dict) for item in v):
                raise ValueError("All items in entity list must be dictionaries")
        elif not isinstance(v, dict):
            raise ValueError("Entities must be either a dictionary or a list of dictionaries")
        
        return v

    def add_entities(self, entity_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        Add extracted entity(ies) and set is_entity_list based on the data type.
        
        Args:
            entity_data: The extracted entity data, either a single dict or list of dicts
        """
        self.entities = entity_data
        self.is_entity_list = isinstance(entity_data, list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
