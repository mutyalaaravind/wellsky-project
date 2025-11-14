from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import uuid
import json
from datetime import datetime

from util.custom_logger import getLogger
from models.base import AggBase
import settings

LOGGER = getLogger(__name__)

class TaskType(str, Enum):
    MODULE = "module"
    PIPELINE = "pipeline"
    PROMPT = "prompt"
    REMOTE = "remote"
    PUBLISH_CALLBACK = "publish_callback"

class PromptConfig(BaseModel):
    model: str
    system_instructions: Optional[List[str]] = []
    prompt: str
    max_output_tokens: Optional[int] = settings.LLM_MAX_OUTPUT_TOKENS_DEFAULT
    temperature: Optional[float] = settings.LLM_TEMPERATURE_DEFAULT
    top_p: Optional[float] = settings.LLM_TOP_P_DEFAULT
    safety_settings: Optional[dict] = None
    context: Optional[Dict[str, Any]] = {}
    is_add_document_uri_to_context: Optional[bool] = True


class ModuleConfig(BaseModel):
    type: str
    context: Optional[Dict[str, Any]] = {}


class PipelineReference(BaseModel):
    scope: str = "default"
    id: str
    host: Optional[str] = None
    queue: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}


class RemoteConfig(BaseModel):
    url: str
    method: str = "POST"
    headers: Optional[Dict[str, str]] = {}
    timeout: Optional[int] = 30
    context: Optional[Dict[str, Any]] = {}


class EntitySchemaRef(BaseModel):
    schema_uri: str
    var_name: str

class PostProcessing(BaseModel):
    for_each: Optional[str] = None

class TaskInvocation(BaseModel):
    queue_name: Optional[str] = settings.INTRA_TASK_INVOCATION_DEFAULT_QUEUE

class PublishCallbackEndpoint(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = {}
    
    model_config = ConfigDict(extra='forbid')

class PublishCallbackConfig(BaseModel):
    enabled: bool
    entity_schema_ref: Optional[EntitySchemaRef] = None
    scope: Optional[str] = "default"
    pipeline_id: Optional[str] = None
    endpoint: PublishCallbackEndpoint
    
    model_config = ConfigDict(extra='ignore')

class TaskConfig(BaseModel):
    id: str
    type: TaskType
    invoke: Optional[TaskInvocation] = TaskInvocation()
    module: Optional[ModuleConfig] = None
    pipelines: Optional[List[PipelineReference]] = None
    prompt: Optional[PromptConfig] = None
    remote: Optional[RemoteConfig] = None
    callback: Optional[PublishCallbackConfig] = None
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Additional parameters for the pipeline
    post_processing: Optional[PostProcessing] = None
    entity_schema_ref: Optional[EntitySchemaRef] = None
    
    model_config = ConfigDict(extra='ignore')
    
    def model_dump(self, **kwargs):
        """Override model_dump method to exclude None values for discriminator fields."""
        # Get the base dict representation
        result = super().model_dump(**kwargs)
        
        # Remove None values for discriminator fields regardless of task type
        # This implements the discriminator pattern where only relevant fields are included
        discriminator_fields = ['module', 'pipelines', 'prompt', 'remote', 'callback']
        for field in discriminator_fields:
            if field in result and result[field] is None:
                del result[field]
        
        return result

    def dict(self, **kwargs):
        """Legacy dict method for backward compatibility."""
        return self.model_dump(**kwargs)


class PipelineConfig(AggBase):    
    key: str
    version: Optional[str] = None  # Expect semantic versioning format, e.g., "1.0.0"
    name: str
    description: Optional[str] = None  # Optional description of the pipeline's purpose and functionality
    scope: str = "default"
    output_entity: Optional[str] = None
    tasks: List[TaskConfig]    
    auto_publish_entities_enabled: Optional[bool] = True  # Most workflows will want to auto-pubish entities to paperglass.  This can be disabled for cases where intermediate entities are to be extracted for use in later tasks but the intermediates are not be be persisted to paperglass.
    labels: Optional[List[str]] = Field(default_factory=list)  # Array of string labels for filtering and categorization
    app_id: Optional[str] = None  # Application ID for filtering pipeline configurations
    
    def model_dump(self, **kwargs):
        """Override model_dump method to ensure Task objects use their custom model_dump method."""
        # Get the base dict representation
        result = super().model_dump(**kwargs)
        
        # Ensure tasks use their custom model_dump method
        if 'tasks' in result and result['tasks']:
            result['tasks'] = [task.model_dump(**kwargs) for task in self.tasks]
        
        return result

    def dict(self, **kwargs):
        """Legacy dict method for backward compatibility."""
        return self.model_dump(**kwargs)
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_encoders={
            # Custom encoders if needed
        }
    )


# Example usage and validation functions
def create_document_prep_pipeline() -> PipelineConfig:
    """Create the document preparation pipeline configuration."""
    return PipelineConfig(
        key="start",
        version="1.0",
        name="Document Prep Pipeline",
        scope="default",
        tasks=[
            TaskConfig(
                id="SPLIT_PAGES",
                type=TaskType.MODULE,
                module=ModuleConfig(type="split_pages"),
                post_processing=PostProcessing(for_each="page")
            ),
            TaskConfig(
                id="MEDICATION_EXTRACTION",
                type=TaskType.PIPELINE,
                pipelines=[
                    PipelineReference(
                        id="medication_extraction",
                        queue="entry_med_extract_{app_id}_{priority}_queue"
                    )
                ]
            )
        ]
    )


def create_remote_processing_pipeline() -> PipelineConfig:
    """Create a pipeline configuration that includes a remote task."""
    return PipelineConfig(
        key="remote_processing",
        version="1.0",
        name="Remote Processing Pipeline",
        scope="default",
        tasks=[
            TaskConfig(
                id="DOCUMENT_ANALYSIS",
                type=TaskType.REMOTE,
                remote=RemoteConfig(
                    url="https://api.example.com/analyze",
                    method="POST",
                    headers={
                        "Authorization": "Bearer token",
                        "Content-Type": "application/json"
                    },
                    timeout=60,
                    context={
                        "analysis_type": "document",
                        "include_metadata": True
                    }
                )
            ),
            TaskConfig(
                id="PROCESS_RESULTS",
                type=TaskType.MODULE,
                module=ModuleConfig(type="result_processor")
            )
        ]
    )

def validate_pipeline_config(config_dict: Dict[str, Any]) -> PipelineConfig:
    """Validate and parse a pipeline configuration from a dictionary."""
    LOGGER.debug("Validating pipeline configuration: %s", config_dict)

    return PipelineConfig(**config_dict)


def pipeline_config_to_dict(config: PipelineConfig) -> Dict[str, Any]:
    """Convert a pipeline configuration to a dictionary with JSON-serializable values."""
    config_dict = config.dict(exclude_none=True)
    
    # Convert datetime objects to ISO format strings for JSON serialization
    def convert_datetimes(obj):
        if isinstance(obj, dict):
            return {k: convert_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetimes(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    return convert_datetimes(config_dict)
