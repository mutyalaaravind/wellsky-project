import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Optional, Dict, Any

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from adapters.firestore import (
    FirestoreAdapter, get_firestore_adapter, get_pipeline_config,
    search_pipeline_config, list_pipeline_configs, list_active_pipeline_configs,
    save_pipeline_config, FIRESTORE_SINGLETON_ENABLE
)
from models.pipeline_config import PipelineConfig, TaskConfig, TaskType, ModuleConfig


class TestFirestoreAdapter:
    """Test suite for FirestoreAdapter class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a sample pipeline config for testing
        self.sample_config_dict = {
            "id": "test-config-123",
            "key": "test_pipeline",
            "version": "1.0",
            "name": "Test Pipeline",
            "scope": "test",
            "active": True,
            "tasks": [
                {
                    "id": "TEST_TASK",
                    "type": "module",
                    "module": {
                        "type": "test_module",
                        "context": {}
                    }
                }
            ]
        }
        
        self.sample_config = PipelineConfig(**self.sample_config_dict)

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.FIRESTORE_EMULATOR_HOST', None)
    def test_init_with_parameters(self, mock_client):
        """Test FirestoreAdapter initialization with custom parameters."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        adapter = FirestoreAdapter(project_id="custom-project", database="custom-db")
        
        assert adapter.project_id == "custom-project"
        assert adapter.database == "custom-db"
        assert adapter.collection_name == "entity_extraction_config"
        mock_client.assert_called_once_with(project="custom-project", database="custom-db")

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.FIRESTORE_EMULATOR_HOST', 'localhost:8080')
    def test_init_with_emulator(self, mock_client):
        """Test FirestoreAdapter initialization with emulator."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        adapter = FirestoreAdapter()
        
        # When using emulator, only project parameter is passed (emulator project)
        mock_client.assert_called_once_with(project="google-cloud-firestore-emulator")

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.GCP_PROJECT_ID', 'default-project')
    @patch('adapters.firestore.GCP_FIRESTORE_DB', 'default-db')
    def test_init_with_defaults(self, mock_client):
        """Test FirestoreAdapter initialization with default settings."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        adapter = FirestoreAdapter()
        
        assert adapter.project_id == 'default-project'
        assert adapter.database == 'default-db'

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_get_pipeline_config_success(self, mock_validate, mock_client):
        """Test successful retrieval of pipeline config by ID."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.sample_config_dict
        mock_query.stream.return_value = [mock_doc]
        
        mock_validate.return_value = self.sample_config
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_pipeline_config("test-config-123")
        
        # Assertions
        assert result == self.sample_config
        mock_collection.where.assert_called_once()
        mock_validate.assert_called_once_with(self.sample_config_dict)

    @patch('adapters.firestore.firestore.Client')
    async def test_get_pipeline_config_not_found(self, mock_client):
        """Test pipeline config retrieval when no document is found."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.stream.return_value = []  # No documents found
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_pipeline_config("nonexistent-id")
        
        # Assertions
        assert result is None

    @patch('adapters.firestore.firestore.Client')
    async def test_get_pipeline_config_exception(self, mock_client):
        """Test pipeline config retrieval with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.where.side_effect = Exception("Firestore error")
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.get_pipeline_config("test-id")
        
        assert "Error retrieving pipeline config for ID 'test-id'" in str(exc_info.value)

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    @patch('adapters.firestore.LOGGER')
    async def test_search_pipeline_config_success(self, mock_logger, mock_validate, mock_client):
        """Test successful search for pipeline config by scope and key."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.sample_config_dict
        mock_query2.stream.return_value = [mock_doc]
        
        mock_validate.return_value = self.sample_config
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.search_pipeline_config("test", "test_pipeline")
        
        # Assertions
        assert result == self.sample_config
        assert mock_collection.where.call_count == 1
        assert mock_query1.where.call_count == 1
        mock_validate.assert_called_once_with(self.sample_config_dict)
        mock_logger.debug.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    @patch('adapters.firestore.exceptionToMap')
    async def test_search_pipeline_config_exception(self, mock_exception_map, mock_logger, mock_client):
        """Test search pipeline config with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.where.side_effect = Exception("Firestore error")
        
        mock_exception_map.return_value = {"error": "mapped_error"}
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.search_pipeline_config("test", "test_pipeline")
        
        assert "Error searching pipeline config for scope 'test' and key 'test_pipeline'" in str(exc_info.value)
        mock_logger.error.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_list_pipeline_configs_with_scope(self, mock_validate, mock_client):
        """Test listing pipeline configs with scope filter."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.sample_config_dict
        mock_query.stream.return_value = [mock_doc]
        
        mock_validate.return_value = self.sample_config
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_pipeline_configs(scope="test")
        
        # Assertions
        assert len(result) == 1
        assert result[0] == self.sample_config
        mock_collection.where.assert_called_once()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_list_pipeline_configs_no_scope(self, mock_validate, mock_client):
        """Test listing all pipeline configs without scope filter."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.sample_config_dict
        mock_collection.stream.return_value = [mock_doc]
        
        mock_validate.return_value = self.sample_config
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_pipeline_configs()
        
        # Assertions
        assert len(result) == 1
        assert result[0] == self.sample_config
        mock_collection.where.assert_not_called()
        mock_collection.stream.assert_called_once()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    @patch('builtins.print')
    async def test_list_pipeline_configs_with_invalid_doc(self, mock_print, mock_validate, mock_client):
        """Test listing pipeline configs with one invalid document."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc1 = Mock()
        mock_doc1.to_dict.return_value = self.sample_config_dict
        mock_doc1.id = "valid-doc"
        
        mock_doc2 = Mock()
        mock_doc2.to_dict.return_value = {"invalid": "data"}
        mock_doc2.id = "invalid-doc"
        
        mock_collection.stream.return_value = [mock_doc1, mock_doc2]
        
        # First call succeeds, second call fails
        mock_validate.side_effect = [self.sample_config, Exception("Validation error")]
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_pipeline_configs()
        
        # Assertions
        assert len(result) == 1
        assert result[0] == self.sample_config
        mock_print.assert_called_once()
        assert "Warning: Failed to parse pipeline config from document invalid-doc" in mock_print.call_args[0][0]

    @patch('adapters.firestore.firestore.Client')
    async def test_list_pipeline_configs_exception(self, mock_client):
        """Test list pipeline configs with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.stream.side_effect = Exception("Firestore error")
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.list_pipeline_configs()
        
        assert "Error listing pipeline configs for scope 'None'" in str(exc_info.value)

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    @patch('builtins.print')
    async def test_list_active_pipeline_configs_success(self, mock_print, mock_validate, mock_client):
        """Test listing active pipeline configs."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        # Create active config
        active_config_dict = self.sample_config_dict.copy()
        active_config_dict["active"] = True
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = active_config_dict
        mock_query.stream.return_value = [mock_doc]
        
        active_config = PipelineConfig(**active_config_dict)
        mock_validate.return_value = active_config
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_active_pipeline_configs()
        
        # Assertions
        assert len(result) == 1
        assert result[0] == active_config
        mock_collection.where.assert_called_once()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_list_active_pipeline_configs_filter_inactive(self, mock_validate, mock_client):
        """Test that inactive configs are filtered out."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        # Create inactive config
        inactive_config_dict = self.sample_config_dict.copy()
        inactive_config_dict["active"] = False
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = inactive_config_dict
        mock_query.stream.return_value = [mock_doc]
        
        # Create mock config with active=False
        inactive_config = Mock()
        inactive_config.active = False
        mock_validate.return_value = inactive_config
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_active_pipeline_configs()
        
        # Assertions - should be empty since config is inactive
        assert len(result) == 0

    @patch('adapters.firestore.firestore.Client')
    async def test_save_pipeline_config_with_document_id(self, mock_client):
        """Test saving pipeline config with specific document ID."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.save_pipeline_config(self.sample_config, "custom-doc-id")
        
        # Assertions
        assert result == "custom-doc-id"
        mock_collection.document.assert_called_once_with("custom-doc-id")
        mock_doc_ref.set.assert_called_once()

    @patch('adapters.firestore.firestore.Client')
    async def test_save_pipeline_config_auto_generate_id(self, mock_client):
        """Test saving pipeline config with auto-generated document ID."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc_ref = Mock()
        mock_saved_doc = Mock()
        mock_saved_doc.exists = True
        mock_doc_ref.get.return_value = mock_saved_doc
        mock_collection.document.return_value = mock_doc_ref
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.save_pipeline_config(self.sample_config)
        
        # The implementation generates ID as {scope}.{key}-{version}
        expected_id = f"{self.sample_config.scope}.{self.sample_config.key}-{self.sample_config.version}"
        assert result == expected_id
        mock_collection.document.assert_called_once_with(expected_id)
        mock_doc_ref.set.assert_called_once()

    @patch('adapters.firestore.firestore.Client')
    async def test_save_pipeline_config_exception(self, mock_client):
        """Test save pipeline config with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc_ref = Mock()
        mock_doc_ref.set.side_effect = Exception("Firestore error")
        mock_collection.document.return_value = mock_doc_ref
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.save_pipeline_config(self.sample_config)
        
        assert "Error saving pipeline config 'test_pipeline'" in str(exc_info.value)

    @patch('adapters.firestore.firestore.Client')
    async def test_delete_pipeline_config_success(self, mock_client):
        """Test successful deletion of pipeline config."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        
        mock_doc = Mock()
        mock_doc_ref = Mock()
        mock_doc.reference = mock_doc_ref
        mock_query2.stream.return_value = [mock_doc]
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.delete_pipeline_config("test", "test_pipeline")
        
        # Assertions
        assert result is True
        mock_doc_ref.delete.assert_called_once()

    @patch('adapters.firestore.firestore.Client')
    async def test_delete_pipeline_config_not_found(self, mock_client):
        """Test deletion when no matching document is found."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        mock_query2.stream.return_value = []  # No documents found
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.delete_pipeline_config("test", "test_pipeline")
        
        # Assertions
        assert result is False

    @patch('adapters.firestore.firestore.Client')
    async def test_delete_pipeline_config_exception(self, mock_client):
        """Test delete pipeline config with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.where.side_effect = Exception("Firestore error")
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.delete_pipeline_config("test", "test_pipeline")
        
        assert "Error deleting pipeline config for scope 'test' and key 'test_pipeline'" in str(exc_info.value)


class TestFirestoreSingleton:
    """Test suite for Firestore singleton functionality."""

    def setup_method(self):
        """Reset singleton state before each test."""
        import adapters.firestore
        adapters.firestore._firestore_adapter = None

    @patch('adapters.firestore.FIRESTORE_SINGLETON_ENABLE', True)
    @patch('adapters.firestore.FirestoreAdapter')
    def test_get_firestore_adapter_singleton_enabled_first_call(self, mock_adapter_class):
        """Test singleton behavior on first call."""
        mock_adapter_instance = Mock()
        mock_adapter_class.return_value = mock_adapter_instance
        
        result = get_firestore_adapter()
        
        assert result == mock_adapter_instance
        mock_adapter_class.assert_called_once()

    @patch('adapters.firestore.FIRESTORE_SINGLETON_ENABLE', True)
    @patch('adapters.firestore.FirestoreAdapter')
    def test_get_firestore_adapter_singleton_enabled_subsequent_call(self, mock_adapter_class):
        """Test singleton behavior on subsequent calls."""
        mock_adapter_instance = Mock()
        mock_adapter_class.return_value = mock_adapter_instance
        
        # First call
        result1 = get_firestore_adapter()
        # Second call
        result2 = get_firestore_adapter()
        
        assert result1 == result2 == mock_adapter_instance
        mock_adapter_class.assert_called_once()  # Should only be called once

    @patch('adapters.firestore.FIRESTORE_SINGLETON_ENABLE', False)
    @patch('adapters.firestore.FirestoreAdapter')
    @patch('adapters.firestore.GCP_PROJECT_ID', 'test-project')
    @patch('adapters.firestore.GCP_FIRESTORE_DB', 'test-db')
    def test_get_firestore_adapter_singleton_disabled(self, mock_adapter_class):
        """Test behavior when singleton is disabled."""
        mock_adapter_instance = Mock()
        mock_adapter_class.return_value = mock_adapter_instance
        
        result = get_firestore_adapter()
        
        assert result == mock_adapter_instance
        mock_adapter_class.assert_called_once_with(
            project_id='test-project',
            database='test-db'
        )


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    @patch('adapters.firestore.get_firestore_adapter')
    async def test_get_pipeline_config_convenience(self, mock_get_adapter):
        """Test convenience function for getting pipeline config."""
        mock_adapter = Mock()
        mock_adapter.get_pipeline_config = AsyncMock(return_value="test_result")
        mock_get_adapter.return_value = mock_adapter
        
        result = await get_pipeline_config("test-id")
        
        assert result == "test_result"
        mock_adapter.get_pipeline_config.assert_called_once_with("test-id")

    @patch('adapters.firestore.get_firestore_adapter')
    async def test_search_pipeline_config_convenience(self, mock_get_adapter):
        """Test convenience function for searching pipeline config."""
        mock_adapter = Mock()
        mock_adapter.search_pipeline_config = AsyncMock(return_value="test_result")
        mock_get_adapter.return_value = mock_adapter
        
        result = await search_pipeline_config("test_scope", "test_key")
        
        assert result == "test_result"
        mock_adapter.search_pipeline_config.assert_called_once_with("test_scope", "test_key")

    @patch('adapters.firestore.get_firestore_adapter')
    async def test_list_pipeline_configs_convenience(self, mock_get_adapter):
        """Test convenience function for listing pipeline configs."""
        mock_adapter = Mock()
        mock_adapter.list_pipeline_configs = AsyncMock(return_value=["test_result"])
        mock_get_adapter.return_value = mock_adapter
        
        result = await list_pipeline_configs("test_scope")
        
        assert result == ["test_result"]
        mock_adapter.list_pipeline_configs.assert_called_once_with("test_scope")

    @patch('adapters.firestore.get_firestore_adapter')
    async def test_list_active_pipeline_configs_convenience(self, mock_get_adapter):
        """Test convenience function for listing active pipeline configs."""
        mock_adapter = Mock()
        mock_adapter.list_active_pipeline_configs = AsyncMock(return_value=["test_result"])
        mock_get_adapter.return_value = mock_adapter
        
        result = await list_active_pipeline_configs()
        
        assert result == ["test_result"]
        mock_adapter.list_active_pipeline_configs.assert_called_once()

    @patch('adapters.firestore.get_firestore_adapter')
    async def test_save_pipeline_config_convenience(self, mock_get_adapter):
        """Test convenience function for saving pipeline config."""
        mock_adapter = Mock()
        mock_adapter.save_pipeline_config = AsyncMock(return_value="doc-id")
        mock_get_adapter.return_value = mock_adapter
        
        mock_config = Mock()
        result = await save_pipeline_config(mock_config, "test-doc-id")
        
        assert result == "doc-id"
        mock_adapter.save_pipeline_config.assert_called_once_with(mock_config, "test-doc-id")


class TestFirestoreIntegration:
    """Integration tests for Firestore adapter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_config_dict = {
            "id": "integration-test-123",
            "key": "integration_pipeline",
            "version": "1.0",
            "name": "Integration Test Pipeline",
            "scope": "integration",
            "active": True,
            "tasks": [
                {
                    "id": "INTEGRATION_TASK",
                    "type": "module",
                    "module": {
                        "type": "integration_module",
                        "context": {"test": "data"}
                    }
                }
            ]
        }

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_full_crud_workflow(self, mock_validate, mock_client):
        """Test complete CRUD workflow."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        # Mock save operation - the implementation uses document().set() not add()
        mock_doc_ref = Mock()
        mock_saved_doc = Mock()
        mock_saved_doc.exists = True
        mock_doc_ref.get.return_value = mock_saved_doc
        mock_collection.document.return_value = mock_doc_ref
        
        # Mock search operation
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.sample_config_dict
        mock_query2.stream.return_value = [mock_doc]
        
        config = PipelineConfig(**self.sample_config_dict)
        mock_validate.return_value = config
        
        # Mock delete operation
        mock_doc.reference = Mock()
        
        # Test workflow
        adapter = FirestoreAdapter()
        
        # 1. Save config - the implementation generates ID as {scope}.{key}-{version}
        doc_id = await adapter.save_pipeline_config(config)
        expected_id = f"{config.scope}.{config.key}-{config.version}"
        assert doc_id == expected_id
        
        # 2. Search for config
        found_config = await adapter.search_pipeline_config("integration", "integration_pipeline")
        assert found_config == config
        
        # 3. Delete config
        deleted = await adapter.delete_pipeline_config("integration", "integration_pipeline")
        assert deleted is True

    @patch('adapters.firestore.firestore.Client')
    async def test_error_handling_chain(self, mock_client):
        """Test error handling across multiple operations."""
        # Setup mocks to fail
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.where.side_effect = Exception("Connection error")
        
        adapter = FirestoreAdapter()
        
        # Test that all operations properly handle and re-raise exceptions
        with pytest.raises(Exception):
            await adapter.get_pipeline_config("test-id")
        
        with pytest.raises(Exception):
            await adapter.search_pipeline_config("test", "test")
        
        with pytest.raises(Exception):
            await adapter.list_pipeline_configs()
        
        with pytest.raises(Exception):
            await adapter.delete_pipeline_config("test", "test")

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_document_data_variations(self, mock_validate, mock_client):
        """Test handling of various document data scenarios."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        # Test with None document data
        mock_doc_none = Mock()
        mock_doc_none.to_dict.return_value = None
        
        # Test with empty document data
        mock_doc_empty = Mock()
        mock_doc_empty.to_dict.return_value = {}
        
        # Test with valid document data
        mock_doc_valid = Mock()
        mock_doc_valid.to_dict.return_value = self.sample_config_dict
        
        mock_query.stream.return_value = [mock_doc_none, mock_doc_empty, mock_doc_valid]
        
        config = PipelineConfig(**self.sample_config_dict)
        mock_validate.return_value = config
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_pipeline_config("test-id")
        
        # Should only return the valid config, skipping None and empty docs
        assert result == config
        mock_validate.assert_called_once_with(self.sample_config_dict)

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_list_active_pipeline_configs_missing_active_field(self, mock_validate, mock_client):
        """Test that configs with missing active field default to True."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        # Create config without active field
        config_dict_no_active = self.sample_config_dict.copy()
        if 'active' in config_dict_no_active:
            del config_dict_no_active['active']
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = config_dict_no_active
        mock_query.stream.return_value = [mock_doc]
        
        # Create mock config without active attribute (defaults to True)
        config_no_active = Mock()
        # Don't set active attribute, so getattr will return True as default
        mock_validate.return_value = config_no_active
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_active_pipeline_configs()
        
        # Should include config since active defaults to True
        assert len(result) == 1
        assert result[0] == config_no_active

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    @patch('builtins.print')
    async def test_list_active_pipeline_configs_with_invalid_doc(self, mock_print, mock_validate, mock_client):
        """Test list_active_pipeline_configs with invalid document."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {"invalid": "data"}
        mock_doc.id = "invalid-active-doc"
        mock_query.stream.return_value = [mock_doc]
        
        mock_validate.side_effect = Exception("Validation error")
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_active_pipeline_configs()
        
        # Should return empty list and print warning
        assert len(result) == 0
        mock_print.assert_called_once()
        assert "Warning: Failed to parse pipeline config from document invalid-active-doc" in mock_print.call_args[0][0]

    @patch('adapters.firestore.firestore.Client')
    async def test_list_active_pipeline_configs_exception(self, mock_client):
        """Test list_active_pipeline_configs with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.where.side_effect = Exception("Firestore error")
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.list_active_pipeline_configs()
        
        assert "Error listing active pipeline configs" in str(exc_info.value)


class TestFirestoreAdapterAdditionalCoverage:
    """Additional tests to increase firestore adapter coverage."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_config_dict = {
            "id": "test-config-123",
            "key": "test_pipeline",
            "version": "1.0",
            "name": "Test Pipeline",
            "scope": "test",
            "active": True,
            "tasks": [
                {
                    "id": "TEST_TASK",
                    "type": "module",
                    "module": {
                        "type": "test_module",
                        "context": {}
                    }
                }
            ]
        }
        self.sample_config = PipelineConfig(**self.sample_config_dict)

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.now_utc')
    @patch('adapters.firestore.LOGGER')
    async def test_archive_pipeline_config_success(self, mock_logger, mock_now_utc, mock_client):
        """Test successful archiving of pipeline config."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc_ref = Mock()
        mock_saved_doc = Mock()
        mock_saved_doc.exists = True
        mock_saved_doc.to_dict.return_value = {"archived": True}
        mock_doc_ref.get.return_value = mock_saved_doc
        mock_collection.document.return_value = mock_doc_ref
        
        from datetime import datetime
        mock_now_utc.return_value = datetime(2024, 1, 1, 12, 0, 0)
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.archive_pipeline_config(self.sample_config)
        
        # Assertions
        assert result == self.sample_config.id
        mock_doc_ref.set.assert_called_once()
        
        # Verify archive metadata was added
        set_call_args = mock_doc_ref.set.call_args[0][0]
        assert "archived_at" in set_call_args
        assert "original_scope" in set_call_args
        assert "original_key" in set_call_args
        assert set_call_args["original_scope"] == self.sample_config.scope
        assert set_call_args["original_key"] == self.sample_config.key

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    @patch('adapters.firestore.exceptionToMap')
    async def test_archive_pipeline_config_exception(self, mock_exception_map, mock_logger, mock_client):
        """Test archive pipeline config with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc_ref = Mock()
        mock_doc_ref.set.side_effect = Exception("Archive error")
        mock_collection.document.return_value = mock_doc_ref
        
        mock_exception_map.return_value = {"error": "mapped_error"}
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.archive_pipeline_config(self.sample_config)
        
        assert "Error archiving pipeline config 'test_pipeline'" in str(exc_info.value)
        mock_logger.error.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_mark_pipeline_config_inactive_success(self, mock_logger, mock_client):
        """Test successful marking of pipeline config as inactive."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        mock_doc = Mock()
        mock_doc_ref = Mock()
        mock_doc.reference = mock_doc_ref
        mock_doc.id = "test-doc-id"
        mock_query.stream.return_value = [mock_doc]
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.mark_pipeline_config_inactive(self.sample_config)
        
        # Assertions
        assert result is True
        mock_doc_ref.update.assert_called_once_with({"active": False})
        mock_logger.info.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_mark_pipeline_config_inactive_not_found(self, mock_logger, mock_client):
        """Test marking pipeline config as inactive when not found."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.stream.return_value = []  # No documents found
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.mark_pipeline_config_inactive(self.sample_config)
        
        # Assertions
        assert result is False
        mock_logger.warning.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    @patch('adapters.firestore.exceptionToMap')
    async def test_mark_pipeline_config_inactive_exception(self, mock_exception_map, mock_logger, mock_client):
        """Test mark pipeline config inactive with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.where.side_effect = Exception("Update error")
        
        mock_exception_map.return_value = {"error": "mapped_error"}
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.mark_pipeline_config_inactive(self.sample_config)
        
        assert "Error marking pipeline config 'test_pipeline'" in str(exc_info.value)
        mock_logger.error.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_delete_inactive_pipeline_configs_success(self, mock_logger, mock_client):
        """Test successful deletion of inactive pipeline configs."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_query3 = Mock()
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        mock_query2.where.return_value = mock_query3
        
        mock_doc1 = Mock()
        mock_doc1.to_dict.return_value = {"version": "1.0"}
        mock_doc1.reference = Mock()
        mock_doc1.id = "doc1"
        
        mock_doc2 = Mock()
        mock_doc2.to_dict.return_value = {"version": "2.0"}
        mock_doc2.reference = Mock()
        mock_doc2.id = "doc2"
        
        mock_query3.stream.return_value = [mock_doc1, mock_doc2]
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.delete_inactive_pipeline_configs("test", "test_pipeline")
        
        # Assertions
        assert result == 2
        mock_doc1.reference.delete.assert_called_once()
        mock_doc2.reference.delete.assert_called_once()
        mock_logger.info.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    @patch('adapters.firestore.exceptionToMap')
    async def test_delete_inactive_pipeline_configs_exception(self, mock_exception_map, mock_logger, mock_client):
        """Test delete inactive pipeline configs with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        mock_collection.where.side_effect = Exception("Delete error")
        
        mock_exception_map.return_value = {"error": "mapped_error"}
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.delete_inactive_pipeline_configs("test", "test_pipeline")
        
        assert "Error deleting inactive pipeline configs for scope 'test' and key 'test_pipeline'" in str(exc_info.value)
        mock_logger.error.assert_called()

    @patch('adapters.firestore.firestore.Client')
    async def test_save_pipeline_config_document_not_saved(self, mock_client):
        """Test save pipeline config when document verification fails."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_doc_ref = Mock()
        mock_saved_doc = Mock()
        mock_saved_doc.exists = False  # Document was not saved
        mock_doc_ref.get.return_value = mock_saved_doc
        mock_collection.document.return_value = mock_doc_ref
        
        # Test
        adapter = FirestoreAdapter()
        
        with pytest.raises(Exception) as exc_info:
            await adapter.save_pipeline_config(self.sample_config, "test-doc-id")
        
        assert "Document test-doc-id was not saved successfully" in str(exc_info.value)

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_list_active_pipeline_configs_with_app_id_filter(self, mock_validate, mock_client):
        """Test listing active pipeline configs with app_id filter."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        
        # Create config with app_id
        config_dict = self.sample_config_dict.copy()
        config_dict["app_id"] = "test-app"
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = config_dict
        mock_query2.stream.return_value = [mock_doc]
        
        config_with_app_id = PipelineConfig(**config_dict)
        mock_validate.return_value = config_with_app_id
        
        # Test
        adapter = FirestoreAdapter()
        result = await adapter.list_active_pipeline_configs(app_id="test-app")
        
        # Assertions
        assert len(result) == 1
        assert result[0] == config_with_app_id
        # Verify app_id filter was applied
        assert mock_query1.where.call_count == 1

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_list_active_pipeline_configs_with_labels_filter(self, mock_validate, mock_client):
        """Test listing active pipeline configs with labels filter."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        # Create config with labels
        config_dict = self.sample_config_dict.copy()
        config_dict["labels"] = ["label1", "label2"]
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = config_dict
        mock_query.stream.return_value = [mock_doc]
        
        # Create mock config with labels
        config_with_labels = Mock()
        config_with_labels.active = True
        config_with_labels.labels = ["label1", "label2"]
        mock_validate.return_value = config_with_labels
        
        # Test with matching labels
        adapter = FirestoreAdapter()
        result = await adapter.list_active_pipeline_configs(labels=["label1"])
        
        # Assertions - should include config since it has label1
        assert len(result) == 1
        assert result[0] == config_with_labels

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.validate_pipeline_config')
    async def test_list_active_pipeline_configs_labels_not_match(self, mock_validate, mock_client):
        """Test listing active pipeline configs with labels that don't match."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection
        
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        
        mock_doc = Mock()
        mock_doc.to_dict.return_value = self.sample_config_dict
        mock_query.stream.return_value = [mock_doc]
        
        # Create mock config without matching labels
        config_without_labels = Mock()
        config_without_labels.active = True
        config_without_labels.labels = ["other_label"]
        mock_validate.return_value = config_without_labels
        
        # Test with non-matching labels
        adapter = FirestoreAdapter()
        result = await adapter.list_active_pipeline_configs(labels=["required_label"])

        # Assertions - should be empty since labels don't match
        assert len(result) == 0


class TestFirestoreAppConfigCache:
    """Test app config cache functionality in FirestoreAdapter."""

    @pytest.fixture
    def sample_app_config_cache(self):
        """Sample app config cache for testing."""
        from models.app_config import AppConfigCache
        from datetime import datetime, timezone, timedelta

        return AppConfigCache(
            app_id="test-app-123",
            cached_at=datetime.now(timezone.utc),
            ttl_seconds=3600,
            config={"key": "value", "settings": {"enabled": True}}
        )

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_get_app_config_cache_success(self, mock_logger, mock_client, sample_app_config_cache):
        """Test successful retrieval of app config cache."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref

        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_app_config_cache.to_firestore_dict()
        mock_doc_ref.get.return_value = mock_doc

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_app_config_cache("test-app-123")

        # Assertions
        assert result is not None
        assert result.app_id == "test-app-123"
        assert result.config == {"key": "value", "settings": {"enabled": True}}
        mock_logger.debug.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_get_app_config_cache_not_found(self, mock_logger, mock_client):
        """Test app config cache not found."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref

        mock_doc = Mock()
        mock_doc.exists = False
        mock_doc_ref.get.return_value = mock_doc

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_app_config_cache("test-app-123")

        # Assertions
        assert result is None
        mock_logger.debug.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_get_app_config_cache_empty_document(self, mock_logger, mock_client):
        """Test app config cache with empty document."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref

        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = None
        mock_doc_ref.get.return_value = mock_doc

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_app_config_cache("test-app-123")

        # Assertions
        assert result is None
        mock_logger.warning.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_get_app_config_cache_expired(self, mock_logger, mock_client):
        """Test app config cache that is expired."""
        from models.app_config import AppConfigCache
        from datetime import datetime, timezone, timedelta

        # Create expired cache
        expired_cache = AppConfigCache(
            app_id="test-app-123",
            cached_at=datetime.now(timezone.utc) - timedelta(hours=2),  # 2 hours ago
            ttl_seconds=3600,  # 1 hour TTL
            config={"key": "value"}
        )

        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref

        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = expired_cache.to_firestore_dict()
        mock_doc_ref.get.return_value = mock_doc

        # Mock delete operation
        mock_doc_ref.delete = Mock()

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_app_config_cache("test-app-123")

        # Assertions
        assert result is None
        mock_logger.info.assert_called()
        mock_doc_ref.delete.assert_called_once()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_get_app_config_cache_exception(self, mock_logger, mock_client):
        """Test app config cache retrieval with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.side_effect = Exception("Firestore error")

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.get_app_config_cache("test-app-123")

        # Assertions
        assert result is None
        mock_logger.error.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_save_app_config_cache_success(self, mock_logger, mock_client, sample_app_config_cache):
        """Test successful saving of app config cache."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.set = Mock()

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.save_app_config_cache(sample_app_config_cache)

        # Assertions
        assert result is True
        mock_doc_ref.set.assert_called_once()
        mock_logger.debug.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_save_app_config_cache_exception(self, mock_logger, mock_client, sample_app_config_cache):
        """Test saving app config cache with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.set.side_effect = Exception("Firestore error")

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.save_app_config_cache(sample_app_config_cache)

        # Assertions
        assert result is False
        mock_logger.error.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_delete_app_config_cache_success(self, mock_logger, mock_client):
        """Test successful deletion of app config cache."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.delete = Mock()

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.delete_app_config_cache("test-app-123")

        # Assertions
        assert result is True
        mock_doc_ref.delete.assert_called_once()
        mock_logger.debug.assert_called()

    @patch('adapters.firestore.firestore.Client')
    @patch('adapters.firestore.LOGGER')
    async def test_delete_app_config_cache_exception(self, mock_logger, mock_client):
        """Test deletion of app config cache with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance

        mock_collection = Mock()
        mock_client_instance.collection.return_value = mock_collection

        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.delete.side_effect = Exception("Firestore error")

        # Test
        adapter = FirestoreAdapter()
        result = await adapter.delete_app_config_cache("test-app-123")

        # Assertions
        assert result is False
        mock_logger.error.assert_called()
