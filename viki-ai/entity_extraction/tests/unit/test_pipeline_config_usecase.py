"""
Test the pipeline configuration usecase.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, patch, Mock

from usecases.pipeline_config import increment_version, create_or_update_pipeline_config, PipelineConfigResult


class TestIncrementVersion:
    """Test the increment_version function."""

    def test_increment_version_simple(self):
        """Test incrementing a simple version."""
        result = increment_version("1.0.0")
        assert result == "1.0.1"

    def test_increment_version_two_parts(self):
        """Test incrementing a two-part version."""
        result = increment_version("2.5")
        assert result == "2.6"

    def test_increment_version_single_part(self):
        """Test incrementing a single-part version."""
        result = increment_version("3")
        assert result == "4"

    def test_increment_version_large_number(self):
        """Test incrementing a version with large numbers."""
        result = increment_version("1.2.99")
        assert result == "1.2.100"

    def test_increment_version_zero(self):
        """Test incrementing from zero."""
        result = increment_version("1.0.0")
        assert result == "1.0.1"

    def test_increment_version_non_numeric_last_component(self):
        """Test error when last component is not numeric."""
        with pytest.raises(ValueError) as exc_info:
            increment_version("1.0.alpha")
        assert "Cannot increment version '1.0.alpha': last component 'alpha' is not numeric" in str(exc_info.value)

    def test_increment_version_empty_string(self):
        """Test error with empty version string."""
        with pytest.raises(ValueError) as exc_info:
            increment_version("")
        # Empty string results in empty list after split, so last component is empty string
        assert "Cannot increment version '': last component '' is not numeric" in str(exc_info.value)

    def test_increment_version_mixed_components(self):
        """Test error when last component is not numeric but others are."""
        with pytest.raises(ValueError) as exc_info:
            increment_version("1.2.beta")
        assert "Cannot increment version '1.2.beta': last component 'beta' is not numeric" in str(exc_info.value)

    def test_increment_version_large_number(self):
        """Test incrementing version with large number."""
        result = increment_version("1.0.999")
        assert result == "1.0.1000"

    def test_increment_version_negative_number(self):
        """Test incrementing version with negative number."""
        result = increment_version("1.0.-5")
        assert result == "1.0.-4"

    def test_increment_version_single_dot(self):
        """Test incrementing version with single dot."""
        with pytest.raises(ValueError) as exc_info:
            increment_version(".")
        assert "Cannot increment version '.': last component '' is not numeric" in str(exc_info.value)


class TestCreateOrUpdatePipelineConfig:
    """Test the create_or_update_pipeline_config function."""

    @pytest.fixture
    def sample_config_data(self):
        """Sample pipeline configuration data for testing."""
        return {
            "id": "test-config-001",
            "name": "Test Pipeline Configuration",
            "description": "A test configuration for unit testing",
            "version": "1.0.0",
            "active": True,
            "tasks": [
                {
                    "id": "task-1",
                    "name": "Test Task",
                    "type": "prompt",
                    "prompt": {
                        "model": "gemini-1.5-flash-002",
                        "prompt": "Extract entities from the following text: {text}",
                        "system_instructions": ["You are a helpful assistant."],
                        "response_format": "json",
                        "max_output_tokens": 4096,
                        "temperature": 0.5,
                        "top_p": 0.8
                    }
                }
            ]
        }

    @patch('usecases.pipeline_config.search_pipeline_config_no_cache')
    @patch('usecases.pipeline_config.save_pipeline_config')
    @patch('usecases.pipeline_config.validate_pipeline_config')
    @patch('usecases.pipeline_config.invalidate_pipeline_config_cache')
    async def test_create_new_config(self, mock_invalidate, mock_validate, mock_save, mock_search, sample_config_data):
        """Test creating a new pipeline configuration."""
        # Mock validation and save
        from models.pipeline_config import PipelineConfig
        mock_config = PipelineConfig(**{**sample_config_data, "scope": "test-scope", "key": "test-key", "id": "test-scope.test-key"})
        mock_validate.return_value = mock_config
        mock_save.return_value = "doc-123"
        
        # Mock search to return None first (no existing config), then return the saved config for verification
        mock_search.side_effect = [None, mock_config]
        
        # Call the function
        result = await create_or_update_pipeline_config("test-scope", "test-key", sample_config_data)
        
        # Verify result
        assert isinstance(result, PipelineConfigResult)
        assert result.operation == "created"
        assert result.document_id == "doc-123"
        assert result.archived_config_id is None
        assert result.config == mock_config
        
        # Verify mocks were called
        assert mock_search.call_count == 2  # Once for checking existing, once for verification
        mock_validate.assert_called_once()
        mock_save.assert_called_once_with(mock_config)
        mock_invalidate.assert_called_once_with("test-scope", "test-key")
        
        # Verify the ID was synthesized correctly in the config data passed to validate
        validate_call_args = mock_validate.call_args[0][0]
        assert validate_call_args["id"] == "test-scope.test-key-1.0.0"
        assert validate_call_args["scope"] == "test-scope"
        assert validate_call_args["key"] == "test-key"
        

    @patch('usecases.pipeline_config.search_pipeline_config_no_cache')
    @patch('usecases.pipeline_config.save_pipeline_config')
    @patch('usecases.pipeline_config.archive_pipeline_config')
    @patch('usecases.pipeline_config.validate_pipeline_config')
    @patch('usecases.pipeline_config.invalidate_pipeline_config_cache')
    async def test_update_existing_config_same_version_auto_increment(self, mock_invalidate, mock_validate, mock_archive, mock_save, mock_search, sample_config_data):
        """Test updating an existing configuration with the same version (auto-increment)."""
        # Mock existing config found
        existing_config_data = {**sample_config_data, "scope": "test-scope", "key": "test-key", "id": "test-scope.test-key", "version": "1.0.0"}
        from models.pipeline_config import PipelineConfig
        existing_config = PipelineConfig(**existing_config_data)
        
        # Mock new config with same version (should be auto-incremented)
        new_config_data = {**sample_config_data, "version": "1.0.0"}
        incremented_config = PipelineConfig(**{**new_config_data, "scope": "test-scope", "key": "test-key", "id": "test-scope.test-key", "version": "1.0.1"})
        mock_validate.return_value = incremented_config
        mock_archive.return_value = "archive-456"
        mock_save.return_value = "doc-789"
        
        # Mock search to return existing config first, then incremented config for verification
        mock_search.side_effect = [existing_config, incremented_config]
        
        # Call the function
        result = await create_or_update_pipeline_config("test-scope", "test-key", new_config_data)
        
        # Verify result
        assert result.operation == "updated"
        assert result.document_id == "doc-789"
        assert result.archived_config_id == "archive-456"
        
        # Verify the version was incremented on the returned config object
        # The implementation increments the version AFTER validation, not before
        assert result.config.version == "1.0.1"
        mock_invalidate.assert_called_once_with("test-scope", "test-key")

    @patch('usecases.pipeline_config.search_pipeline_config_no_cache')
    async def test_update_existing_config_same_version_cannot_increment(self, mock_search, sample_config_data):
        """Test updating an existing configuration with same version that cannot be incremented."""
        # Mock existing config found with non-numeric version component
        existing_config_data = {**sample_config_data, "scope": "test-scope", "key": "test-key", "id": "test-scope.test-key", "version": "1.0.alpha"}
        from models.pipeline_config import PipelineConfig
        existing_config = PipelineConfig(**existing_config_data)
        mock_search.return_value = existing_config
        
        # Mock new config with same version
        new_config_data = {**sample_config_data, "version": "1.0.alpha"}
        
        # Call the function and expect ValueError
        with pytest.raises(ValueError) as exc_info:
            await create_or_update_pipeline_config("test-scope", "test-key", new_config_data)
        
        assert "Cannot update configuration" in str(exc_info.value)
        assert "last component 'alpha' is not numeric" in str(exc_info.value)

    @patch('usecases.pipeline_config.search_pipeline_config_no_cache')
    @patch('usecases.pipeline_config.validate_pipeline_config')
    async def test_validation_error(self, mock_validate, mock_search, sample_config_data):
        """Test handling of validation errors."""
        # Mock no existing config
        mock_search.return_value = None
        
        # Mock validation failure
        mock_validate.side_effect = ValueError("Invalid configuration")
        
        # Call the function and expect ValueError
        with pytest.raises(ValueError) as exc_info:
            await create_or_update_pipeline_config("test-scope", "test-key", sample_config_data)
        
        assert "Invalid configuration" in str(exc_info.value)

    @patch('usecases.pipeline_config.search_pipeline_config_no_cache')
    @patch('usecases.pipeline_config.validate_pipeline_config')
    @patch('usecases.pipeline_config.save_pipeline_config')
    async def test_save_error(self, mock_save, mock_validate, mock_search, sample_config_data):
        """Test handling of save errors."""
        # Mock no existing config
        mock_search.return_value = None
        
        # Mock successful validation
        from models.pipeline_config import PipelineConfig
        mock_config = PipelineConfig(**{**sample_config_data, "scope": "test-scope", "key": "test-key", "id": "test-scope.test-key"})
        mock_validate.return_value = mock_config
        
        # Mock save failure
        mock_save.side_effect = Exception("Database error")
        
        # Call the function and expect Exception
        with pytest.raises(Exception) as exc_info:
            await create_or_update_pipeline_config("test-scope", "test-key", sample_config_data)
        
        assert "Error processing pipeline configuration" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)
