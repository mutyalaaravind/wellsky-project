import pytest
import sys
import os
import json
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.pipeline_config import (
    PipelineConfig, TaskConfig, TaskType, ModuleConfig, PipelineReference,
    PostProcessing, PromptConfig, RemoteConfig,
    create_document_prep_pipeline, create_remote_processing_pipeline,
    validate_pipeline_config, pipeline_config_to_dict
)


def test_document_prep_pipeline_creation():
    """Test creating a document preparation pipeline."""
    pipeline = create_document_prep_pipeline()
    
    assert pipeline.key == "start"
    assert len(pipeline.id) == 32  # UUID4 hex length
    assert pipeline.version == "1.0"
    assert pipeline.name == "Document Prep Pipeline"
    assert pipeline.scope == "default"
    assert len(pipeline.tasks) == 2
    
    # Test first task
    split_task = pipeline.tasks[0]
    assert split_task.id == "SPLIT_PAGES"
    assert split_task.type == TaskType.MODULE
    assert split_task.module.type == "split_pages"
    assert split_task.post_processing.for_each == "page"
    
    # Test second task
    med_task = pipeline.tasks[1]
    assert med_task.id == "MEDICATION_EXTRACTION"
    assert med_task.type == TaskType.PIPELINE
    assert len(med_task.pipelines) == 1
    assert med_task.pipelines[0].id == "medication_extraction"


def test_pipeline_config_validation():
    """Test validating pipeline configuration from dictionary."""
    config_dict = {
        "key": "test_pipeline",
        "version": "1.0",
        "name": "Test Pipeline",
        "scope": "test",
        "tasks": [
            {
                "id": "TEST_TASK",
                "type": "module",
                "module": {
                    "type": "test_module"
                }
            }
        ]
    }
    
    pipeline = validate_pipeline_config(config_dict)
    assert pipeline.key == "test_pipeline"
    assert len(pipeline.id) == 32  # UUID4 hex length
    assert pipeline.tasks[0].type == TaskType.MODULE


def test_pipeline_config_to_dict():
    """Test converting pipeline configuration to dictionary."""
    pipeline = create_document_prep_pipeline()
    config_dict = pipeline_config_to_dict(pipeline)
    
    assert isinstance(config_dict, dict)
    assert config_dict["key"] == "start"
    assert len(config_dict["id"]) == 32  # UUID4 hex length
    assert config_dict["version"] == "1.0"
    assert len(config_dict["tasks"]) == 2


def test_prompt_config():
    """Test prompt configuration."""
    prompt = PromptConfig(
        model="test-model",
        system_instructions=["instruction1", "instruction2"],
        prompt="test prompt",
        max_output_tokens=1024,
        temperature=0.5
    )
    
    assert prompt.model == "test-model"
    assert len(prompt.system_instructions) == 2
    assert prompt.prompt == "test prompt"
    assert prompt.max_output_tokens == 1024
    assert prompt.temperature == 0.5


def test_task_types():
    """Test different task types."""
    # Module task
    module_task = TaskConfig(
        id="MODULE_TASK",
        type=TaskType.MODULE,
        module=ModuleConfig(type="test_module")
    )
    assert module_task.type == TaskType.MODULE
    assert module_task.module.type == "test_module"
    
    # Pipeline task
    pipeline_task = TaskConfig(
        id="PIPELINE_TASK",
        type=TaskType.PIPELINE,
        pipelines=[PipelineReference(id="test_pipeline")]
    )
    assert pipeline_task.type == TaskType.PIPELINE
    assert pipeline_task.pipelines[0].id == "test_pipeline"
    
    # Prompt task
    prompt_task = TaskConfig(
        id="PROMPT_TASK",
        type=TaskType.PROMPT,
        prompt=PromptConfig(model="test-model", prompt="test prompt")
    )
    assert prompt_task.type == TaskType.PROMPT
    assert prompt_task.prompt.model == "test-model"
    
    # Remote task
    remote_task = TaskConfig(
        id="REMOTE_TASK",
        type=TaskType.REMOTE,
        remote=RemoteConfig(url="https://api.example.com/test")
    )
    assert remote_task.type == TaskType.REMOTE
    assert remote_task.remote.url == "https://api.example.com/test"
    assert remote_task.remote.method == "POST"  # Default value
    assert remote_task.remote.timeout == 30  # Default value


def test_remote_config():
    """Test remote configuration."""
    remote = RemoteConfig(
        url="https://api.example.com/analyze",
        method="POST",
        headers={"Authorization": "Bearer token"},
        timeout=60,
        context={"analysis_type": "document"}
    )
    
    assert remote.url == "https://api.example.com/analyze"
    assert remote.method == "POST"
    assert remote.headers["Authorization"] == "Bearer token"
    assert remote.timeout == 60
    assert remote.context["analysis_type"] == "document"


def test_remote_processing_pipeline_creation():
    """Test creating a remote processing pipeline."""
    pipeline = create_remote_processing_pipeline()
    
    assert pipeline.key == "remote_processing"
    assert pipeline.version == "1.0"
    assert pipeline.name == "Remote Processing Pipeline"
    assert pipeline.scope == "default"
    assert len(pipeline.tasks) == 2
    
    # Test first task (remote)
    remote_task = pipeline.tasks[0]
    assert remote_task.id == "DOCUMENT_ANALYSIS"
    assert remote_task.type == TaskType.REMOTE
    assert remote_task.remote.url == "https://api.example.com/analyze"
    assert remote_task.remote.method == "POST"
    assert remote_task.remote.timeout == 60
    assert "Authorization" in remote_task.remote.headers
    assert remote_task.remote.context["analysis_type"] == "document"
    
    # Test second task (module)
    module_task = pipeline.tasks[1]
    assert module_task.id == "PROCESS_RESULTS"
    assert module_task.type == TaskType.MODULE
    assert module_task.module.type == "result_processor"


def test_remote_task_json_config():
    """Test remote task configuration from JSON."""
    remote_task_json = {
        "key": "remote_test",
        "version": "1.0",
        "name": "Remote Test Pipeline",
        "scope": "test",
        "tasks": [
            {
                "id": "CALL_EXTERNAL_API",
                "type": "remote",
                "remote": {
                    "url": "https://external-api.com/process",
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json",
                        "X-API-Key": "secret-key"
                    },
                    "timeout": 45,
                    "context": {
                        "service": "external_processor",
                        "version": "v2"
                    }
                }
            }
        ]
    }
    
    pipeline = validate_pipeline_config(remote_task_json)
    assert pipeline.key == "remote_test"
    assert len(pipeline.tasks) == 1
    
    remote_task = pipeline.tasks[0]
    assert remote_task.type == TaskType.REMOTE
    assert remote_task.remote.url == "https://external-api.com/process"
    assert remote_task.remote.method == "POST"
    assert remote_task.remote.headers["X-API-Key"] == "secret-key"
    assert remote_task.remote.timeout == 45
    assert remote_task.remote.context["service"] == "external_processor"


def test_task_config_discriminator_fields():
    """Test that discriminator fields are properly excluded in model_dump."""
    # Remote task should only include remote field
    remote_task = TaskConfig(
        id="REMOTE_TASK",
        type=TaskType.REMOTE,
        remote=RemoteConfig(url="https://api.example.com/test")
    )
    
    task_dict = remote_task.model_dump()
    assert "remote" in task_dict
    assert "module" not in task_dict
    assert "pipelines" not in task_dict
    assert "prompt" not in task_dict
    
    # Module task should only include module field
    module_task = TaskConfig(
        id="MODULE_TASK",
        type=TaskType.MODULE,
        module=ModuleConfig(type="test_module")
    )
    
    task_dict = module_task.model_dump()
    assert "module" in task_dict
    assert "remote" not in task_dict
    assert "pipelines" not in task_dict
    assert "prompt" not in task_dict


def test_json_serialization():
    """Test that pipeline configs can be serialized to JSON."""
    pipeline = create_document_prep_pipeline()
    config_dict = pipeline_config_to_dict(pipeline)
    
    # Should be able to serialize to JSON
    json_str = json.dumps(config_dict)
    assert isinstance(json_str, str)
    
    # Should be able to deserialize back
    parsed_dict = json.loads(json_str)
    reconstructed_pipeline = validate_pipeline_config(parsed_dict)
    assert reconstructed_pipeline.id == pipeline.id
    assert reconstructed_pipeline.name == pipeline.name


def test_example_json_configs():
    """Test that the example JSON configurations from the requirements work."""
    # Document prep pipeline example
    doc_prep_json = {
        "key": "start",
        "version": "1.0",
        "name": "Document Prep Pipeline",
        "scope": "default",
        "tasks": [
            {
                "id": "SPLIT_PAGES",
                "type": "module",
                "module": {
                    "type": "split_pages"
                },
                "post_processing": {
                    "for_each": "page"
                }
            },
            {
                "id": "MEDICATION_EXTRACTION",
                "type": "pipeline",
                "pipelines": [
                    {
                        "id": "medication_extraction",
                        "queue": "entry_med_extract_{app_id}_{priority}_queue"
                    }
                ]
            }
        ]
    }
    
    pipeline = validate_pipeline_config(doc_prep_json)
    assert pipeline.key == "start"
    assert len(pipeline.id) == 32  # UUID4 hex length
    assert len(pipeline.tasks) == 2
    
    # Medication extraction pipeline example
    med_extract_json = {
        "key": "medication_extraction",
        "version": "1.0",
        "name": "Medication Extraction Pipeline",
        "scope": "default",
        "output_entity": "medication",
        "tasks": [
            {
                "id": "EXTRACT_MEDICATION",
                "type": "prompt",
                "prompt": {
                    "model": "gemini-1.5-flash-002",
                    "system_instructions": [],
                    "prompt": "",
                    "max_output_tokens": 8192,
                    "temperature": 0.0,
                    "top_p": 0.95,
                    "safety_settings": {
                        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE"
                    }
                }
            },
            {
                "id": "MATCH_MEDICATION",
                "type": "module",
                "module": {
                    "type": "match_medication",
                    "params": {
                        "prompt": {
                            "model": "gemini-1.5-flash-002",
                            "system_instructions": [],
                            "prompt": "",
                            "max_output_tokens": 8192,
                            "temperature": 0.0,
                            "top_p": 0.95,
                            "safety_settings": {
                                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE"
                            }
                        }
                    }
                }
            }
        ]
    }
    
    pipeline = validate_pipeline_config(med_extract_json)
    assert pipeline.key == "medication_extraction"
    assert len(pipeline.id) == 32  # UUID4 hex length
    assert pipeline.output_entity == "medication"
    assert len(pipeline.tasks) == 2


def test_pipeline_config_with_labels_and_app_id():
    """Test pipeline configuration with labels and app_id fields."""
    config_dict = {
        "key": "test_pipeline",
        "version": "1.0",
        "name": "Test Pipeline",
        "scope": "test",
        "labels": ["development", "medical", "high-priority"],
        "app_id": "app_12345",
        "tasks": [
            {
                "id": "TEST_TASK",
                "type": "module",
                "module": {
                    "type": "test_module"
                }
            }
        ]
    }
    
    pipeline = validate_pipeline_config(config_dict)
    assert pipeline.key == "test_pipeline"
    assert pipeline.labels == ["development", "medical", "high-priority"]
    assert pipeline.app_id == "app_12345"
    
    # Test serialization includes the new fields
    config_dict_output = pipeline_config_to_dict(pipeline)
    assert config_dict_output["labels"] == ["development", "medical", "high-priority"]
    assert config_dict_output["app_id"] == "app_12345"


def test_pipeline_config_with_empty_labels():
    """Test pipeline configuration with empty labels (default)."""
    config_dict = {
        "key": "test_pipeline",
        "version": "1.0", 
        "name": "Test Pipeline",
        "scope": "test",
        "tasks": [
            {
                "id": "TEST_TASK",
                "type": "module",
                "module": {
                    "type": "test_module"
                }
            }
        ]
    }
    
    pipeline = validate_pipeline_config(config_dict)
    assert pipeline.labels == []  # Default empty list
    assert pipeline.app_id is None  # Default None


def test_pipeline_config_labels_filtering_logic():
    """Test the logic that would be used for filtering by labels."""
    # Test config with multiple labels
    config_with_labels = {
        "labels": ["development", "medical", "high-priority", "ml-pipeline"]
    }
    
    # Test filtering scenarios
    test_cases = [
        # (required_labels, config_labels, should_match)
        (["development"], ["development", "medical"], True),
        (["development", "medical"], ["development", "medical", "high-priority"], True),
        (["development", "medical"], ["development"], False),  # Missing "medical"
        (["nonexistent"], ["development", "medical"], False),
        ([], ["development", "medical"], True),  # No filter means all match
        (["development", "medical", "high-priority"], ["development", "medical", "high-priority", "ml-pipeline"], True),
    ]
    
    for required_labels, config_labels, expected_match in test_cases:
        # This mimics the filtering logic from the Firestore adapter
        if required_labels:
            matches = all(label in config_labels for label in required_labels)
        else:
            matches = True
        
        assert matches == expected_match, f"Failed for required_labels={required_labels}, config_labels={config_labels}"
