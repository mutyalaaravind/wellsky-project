"""
Unit tests for entity ID preservation from Paperglass.

Tests that entity IDs created in Paperglass are preserved when
entities are saved in AdminUI via the document processing callback.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from domain.models.entity import Entity, EntityCallbackData
from application.commands.entity_commands import (
    EntityCommandHandler,
    ProcessDocumentCallbackCommand
)


class TestEntityIdPreservation:
    """Test suite for entity ID preservation from Paperglass."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock entity repository."""
        repository = Mock()
        repository.save_entities_batch = AsyncMock(return_value=["id1", "id2", "id3"])
        return repository
    
    @pytest.fixture
    def entity_command_handler(self, mock_repository):
        """Create an entity command handler with mock repository."""
        return EntityCommandHandler(entity_repository=mock_repository)
    
    @pytest.fixture
    def sample_callback_data_with_ids(self):
        """Sample callback data with Paperglass entity IDs."""
        return EntityCallbackData(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc",
            source_id="test_source",
            status="completed",
            timestamp="2025-10-31T10:00:00Z",
            run_id="test_run",
            metadata={"test": "metadata"},
            entities_data=[
                {
                    "id": "paperglass_entity_1",  # Paperglass ID
                    "entity_type": "insurance",
                    "name": "Test Insurance",
                    "policy_number": "12345"
                },
                {
                    "id": "paperglass_entity_2",  # Paperglass ID
                    "entity_type": "insurance",
                    "name": "Another Insurance",
                    "policy_number": "67890"
                },
                {
                    "id": "paperglass_entity_3",  # Paperglass ID
                    "entity_type": "medication",
                    "drug_name": "Aspirin",
                    "dosage": "100mg"
                }
            ]
        )
    
    @pytest.fixture
    def sample_callback_data_without_ids(self):
        """Sample callback data without Paperglass entity IDs."""
        return EntityCallbackData(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc",
            source_id="test_source",
            status="completed",
            timestamp="2025-10-31T10:00:00Z",
            run_id="test_run",
            metadata={"test": "metadata"},
            entities_data=[
                {
                    "entity_type": "insurance",
                    "name": "Test Insurance",
                    "policy_number": "12345"
                },
                {
                    "entity_type": "medication",
                    "drug_name": "Aspirin",
                    "dosage": "100mg"
                }
            ]
        )
    
    @pytest.mark.asyncio
    async def test_entity_ids_preserved_from_paperglass(
        self, 
        entity_command_handler, 
        sample_callback_data_with_ids,
        mock_repository
    ):
        """Test that entity IDs from Paperglass are preserved."""
        # Arrange
        command = ProcessDocumentCallbackCommand(
            callback_data=sample_callback_data_with_ids
        )
        
        # Act
        result = await entity_command_handler.handle_process_document_callback(command)
        
        # Assert
        assert result["entities_received"] == 3
        assert result["entities_saved"] == 3
        
        # Verify save_entities_batch was called
        mock_repository.save_entities_batch.assert_called_once()
        
        # Get the entities that were passed to save_entities_batch
        saved_entities = mock_repository.save_entities_batch.call_args[0][0]
        
        # Verify all entities have their Paperglass IDs
        assert len(saved_entities) == 3
        assert saved_entities[0].id == "paperglass_entity_1"
        assert saved_entities[1].id == "paperglass_entity_2"
        assert saved_entities[2].id == "paperglass_entity_3"
        
        # Verify entity_data does NOT contain duplicate 'id' field
        for entity in saved_entities:
            assert "id" not in entity.entity_data
    
    @pytest.mark.asyncio
    async def test_entity_ids_generated_when_not_provided(
        self, 
        entity_command_handler, 
        sample_callback_data_without_ids,
        mock_repository
    ):
        """Test that entity IDs are auto-generated when not provided by Paperglass."""
        # Arrange
        command = ProcessDocumentCallbackCommand(
            callback_data=sample_callback_data_without_ids
        )
        
        # Act
        result = await entity_command_handler.handle_process_document_callback(command)
        
        # Assert
        assert result["entities_received"] == 2
        assert result["entities_saved"] == 2
        
        # Get the entities that were passed to save_entities_batch
        saved_entities = mock_repository.save_entities_batch.call_args[0][0]
        
        # Verify all entities have IDs (even if auto-generated)
        assert len(saved_entities) == 2
        assert saved_entities[0].id is not None
        assert saved_entities[1].id is not None
        assert len(saved_entities[0].id) > 0
        assert len(saved_entities[1].id) > 0
        
        # IDs should be different from each other
        assert saved_entities[0].id != saved_entities[1].id
    
    @pytest.mark.asyncio
    async def test_entity_attributes_preserved(
        self, 
        entity_command_handler, 
        sample_callback_data_with_ids,
        mock_repository
    ):
        """Test that entity attributes are correctly preserved."""
        # Arrange
        command = ProcessDocumentCallbackCommand(
            callback_data=sample_callback_data_with_ids
        )
        
        # Act
        await entity_command_handler.handle_process_document_callback(command)
        
        # Get the entities that were passed to save_entities_batch
        saved_entities = mock_repository.save_entities_batch.call_args[0][0]
        
        # Verify first entity (insurance)
        entity1 = saved_entities[0]
        assert entity1.id == "paperglass_entity_1"
        assert entity1.entity_type == "insurance"
        assert entity1.app_id == "test_app"
        assert entity1.tenant_id == "test_tenant"
        assert entity1.patient_id == "test_patient"
        assert entity1.document_id == "test_doc"
        assert entity1.run_id == "test_run"
        assert entity1.entity_data["name"] == "Test Insurance"
        assert entity1.entity_data["policy_number"] == "12345"
        assert "id" not in entity1.entity_data  # ID should not be duplicated
        
        # Verify third entity (medication)
        entity3 = saved_entities[2]
        assert entity3.id == "paperglass_entity_3"
        assert entity3.entity_type == "medication"
        assert entity3.entity_data["drug_name"] == "Aspirin"
        assert entity3.entity_data["dosage"] == "100mg"
    
    @pytest.mark.asyncio
    async def test_entities_grouped_by_type(
        self, 
        entity_command_handler, 
        sample_callback_data_with_ids,
        mock_repository
    ):
        """Test that entities are correctly grouped by type."""
        # Arrange
        command = ProcessDocumentCallbackCommand(
            callback_data=sample_callback_data_with_ids
        )
        
        # Act
        await entity_command_handler.handle_process_document_callback(command)
        
        # Get the entities that were passed to save_entities_batch
        saved_entities = mock_repository.save_entities_batch.call_args[0][0]
        
        # Group entities by type
        insurance_entities = [e for e in saved_entities if e.entity_type == "insurance"]
        medication_entities = [e for e in saved_entities if e.entity_type == "medication"]
        
        # Verify grouping
        assert len(insurance_entities) == 2
        assert len(medication_entities) == 1
        
        # Verify IDs are preserved in both groups
        assert insurance_entities[0].id == "paperglass_entity_1"
        assert insurance_entities[1].id == "paperglass_entity_2"
        assert medication_entities[0].id == "paperglass_entity_3"
    
    def test_entity_creation_with_explicit_id(self):
        """Test that Entity can be created with an explicit ID."""
        # Arrange
        explicit_id = "my_custom_id"
        
        # Act
        entity = Entity(
            id=explicit_id,
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc",
            entity_data={"test": "data"}
        )
        
        # Assert
        assert entity.id == explicit_id
        assert entity.app_id == "test_app"
        assert entity.entity_data == {"test": "data"}
    
    def test_entity_creation_without_explicit_id(self):
        """Test that Entity auto-generates ID when not provided."""
        # Act
        entity = Entity(
            app_id="test_app",
            tenant_id="test_tenant",
            patient_id="test_patient",
            document_id="test_doc",
            entity_data={"test": "data"}
        )
        
        # Assert
        assert entity.id is not None
        assert len(entity.id) > 0
        assert entity.app_id == "test_app"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
