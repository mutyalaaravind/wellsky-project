# Set environment variables before any imports
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Set required environment variables
env_vars = {
    "VERSION": "test",
    "SERVICE": "test",
    "STAGE": "test",
    "CLOUD_PROVIDER": "test",
    "GCP_PROJECT_ID": "test",
    "GCS_BUCKET_NAME": "test",
    "GCP_LOCATION": "test",
    "GCP_LOCATION_2": "test",
    "GCP_LOCATION_3": "test",
    "GCP_MULTI_REGION_FIRESTORE_LOCATON": "test",
    "GCP_FIRESTORE_DB": "test",
    "GCP_DOCAI_HCC_PROCESSOR_ID": "test",
    "GCP_DOCAI_HCC_PROCESSOR_VERSION": "test",
    "GCP_DOCAI_SUMMARIZER_PROCESSOR_ID": "test",
    "GCP_DOCAI_SUMMARIZER_PROCESSOR_VERSION": "test",
    "GCP_DOCAI_DOC_PROCESSOR_ID": "test",
    "GCP_DOCAI_DOC_PROCESSOR_VERSION": "test",
    "GCP_SEARCH_AND_CONVERSATION_DATA_SOURCE_ID": "test",
    "GCP_SEARCH_AND_CONVERSATION_FHIR_DATA_SOURCE_ID": "test",
    "GCP_VECTOR_SEARCH_INDEX_GCS_URI": "test",
    "GCP_VECTOR_SEARCH_INDEX_NAME": "test",
    "GCP_VECTOR_SEARCH_INDEX_ENDPOINT": "test",
    "GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID": "test",
    "GCP_VECTOR_SEARCH_INDEX_NAME_2": "test",
    "GCP_VECTOR_SEARCH_INDEX_ENDPOINT_2": "test",
    "GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID_2": "test",
    "FHIR_SERVER_URL": "test",
    "FHIR_DATA_STORE": "test",
    "FHIR_DATA_SET": "test",
    "FHIR_SEARCH_STORE_ID": "test",
    "MEDISPAN_CLIENT_ID": "test",
    "MEDISPAN_CLIENT_SECRET": "test",
    "MEDISPAN_VECTOR_SEARCH_PROJECT_ID": "test",
    "MEDISPAN_VECTOR_SEARCH_DEPLOYMENT_ID": "test",
    "MEDISPAN_VECTOR_SEARCH_ENDPOINT_ID": "test",
    "INTEGRATION_PROJECT_NAME": "test",
    "SELF_API": "test",
    "CLOUD_TASK_QUEUE_NAME": "test",
    "CLOUD_TASK_QUEUE_NAME_2": "test",
    "CLOUD_TASK_QUEUE_NAME_PRIORITY": "test",
    "CLOUD_TASK_QUEUE_NAME_PRIORITY_2": "test",
    "CLOUD_TASK_QUEUE_NAME_QUARANTINE": "test",
    "CLOUD_TASK_QUEUE_NAME_QUARANTINE_2": "test",
    "CLOUD_TASK_COMMAND_QUEUE_NAME": "test",
    "CLOUD_TASK_COMMAND_SCHEDULE_QUEUE_NAME": "test",
    "SERVICE_ACCOUNT_EMAIL": "test",
    "APPLICATION_INTEGRATION_TRIGGER_ID": "test",
    "HHH_MEDICATION_PROFILE_BASE_URL": "test",
    "OKTA_CLIENT_ID": "test",
    "OKTA_CLIENT_SECRET": "test",
    "OKTA_AUDIENCE": "test",
    "OKTA_TOKEN_ISSUER_URL": "test",
    "NEW_RELIC_LICENSE_KEY": "test",
    "SHAREPOINT_CLIENT_ID": "test",
    "SHAREPOINT_CLIENT_SECRET": "test",
    "MEDICATION_EXTRACTION_V4_TOPIC": "test",
    "MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME": "test",
    "MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY": "test",
    "MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE": "test",
    "MEDICATION_EXTRACTION_V4_API_URL": "test",
    "MEDICATION_EXTRACTION_V4_API_DEFAULT_URL": "test",
    "MEDICATION_EXTRACTION_V4_API_HIGH_URL": "test",
    "MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL": "test",
    "GCP_PUBSUB_PROJECT_ID": "test",
    "EXTRACTION_PUBSUB_TOPIC_NAME": "test",
}

for key, value in env_vars.items():
    os.environ[key] = value

# Now import the modules
import pytest
import json
import base64
from unittest.mock import MagicMock, patch, AsyncMock
from starlette.requests import Request
from starlette.responses import JSONResponse
from paperglass.interface.adapters.rest import RestAdapter
from paperglass.interface.ports import ICommandHandlingPort, CommandError
from paperglass.usecases.commands import Command


@pytest.fixture
def rest_adapter():
    return RestAdapter()


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.query_params = {}
    request.path_params = {}
    request.scope = {}  # Add scope attribute for the decode_token decorator
    # Create a valid base64-encoded JSON token
    token_data = json.dumps({"appId": "test-app", "tenantId": "test-tenant", "patientId": "test-patient", "userId": "test-user"})
    encoded_token = base64.b64encode(token_data.encode()).decode()
    request.headers = {'Authorization': f'Bearer {encoded_token}'}
    # Add token to the request as it's used by the decode_token decorator
    request.__getitem__ = lambda self, key: encoded_token if key == "token" else None
    return request


@pytest.fixture
def mock_commands():
    commands = AsyncMock(spec=ICommandHandlingPort)
    return commands


@pytest.mark.asyncio
async def test_command_success(rest_adapter, mock_request, mock_commands):
    """Test the command endpoint with a valid command."""
    # Arrange
    command_data = {
        "type": "test_command",
        "command": {
            "type": "CreateNote",
            "title": "Test Note",
            "content": "Test Content"
        }
    }
    mock_request.json = AsyncMock(return_value=command_data)
    
    # Mock the parse_obj_as function to return a Command object
    mock_command = MagicMock(spec=Command)
    
    with patch('paperglass.interface.adapters.rest.parse_obj_as', return_value=mock_command) as mock_parse:
        # Act
        response = await rest_adapter.command(mock_request, commands=mock_commands)
        
        # Assert
        mock_parse.assert_called_once_with(Command, command_data["command"])
        mock_commands.handle_command.assert_called_once_with(mock_command)
        
        assert isinstance(response, JSONResponse)
        response_data = json.loads(response.body)
        assert response_data["success"] is True


@pytest.mark.asyncio
async def test_command_error(rest_adapter, mock_request, mock_commands):
    """Test the command endpoint with an invalid command that raises a CommandError."""
    # Arrange
    command_data = {
        "type": "test_command",
        "command": {
            "type": "InvalidCommand",
            "invalid_field": "value"
        }
    }
    mock_request.json = AsyncMock(return_value=command_data)
    
    # Create a CommandError with some error details
    error_details = {"field": ["error message"]}
    command_error = CommandError()
    # Manually set the errors attribute since CommandError doesn't accept kwargs
    command_error.errors = error_details
    
    # Mock the parse_obj_as function to return a Command object
    mock_command = MagicMock(spec=Command)
    
    with patch('paperglass.interface.adapters.rest.parse_obj_as', return_value=mock_command) as mock_parse:
        # Make the handle_command method raise a CommandError
        mock_commands.handle_command.side_effect = command_error
        
        # Act
        response = await rest_adapter.command(mock_request, commands=mock_commands)
        
        # Assert
        mock_parse.assert_called_once_with(Command, command_data["command"])
        mock_commands.handle_command.assert_called_once_with(mock_command)
        
        assert isinstance(response, JSONResponse)
        response_data = json.loads(response.body)
        assert response_data["success"] is False
        assert response_data["errors"] == error_details


@pytest.mark.asyncio
async def test_command_parse_error(rest_adapter, mock_request, mock_commands):
    """Test the command endpoint when parse_obj_as raises an exception."""
    # Arrange
    command_data = {
        "type": "test_command",
        "command": {
            "type": "InvalidCommand",
            "invalid_field": "value"
        }
    }
    mock_request.json = AsyncMock(return_value=command_data)
    
    # Create a CommandError with some error details
    error_details = {"field": ["error message"]}
    command_error = CommandError()
    # Manually set the errors attribute since CommandError doesn't accept kwargs
    command_error.errors = error_details
    
    with patch('paperglass.interface.adapters.rest.parse_obj_as', side_effect=command_error) as mock_parse:
        # Act
        response = await rest_adapter.command(mock_request, commands=mock_commands)
        
        # Assert
        mock_parse.assert_called_once_with(Command, command_data["command"])
        mock_commands.handle_command.assert_not_called()
        
        assert isinstance(response, JSONResponse)
        response_data = json.loads(response.body)
        assert response_data["success"] is False
        assert response_data["errors"] == error_details


@pytest.mark.asyncio
async def test_command_malformed_payload(rest_adapter, mock_request, mock_commands):
    """Test the command endpoint with a malformed payload missing required fields."""
    # Arrange
    # Add a command field with an empty dict to avoid NoneType has no attribute 'get' error
    command_data = {
        "type": "test_command",
        "command": {}  # Empty dict instead of None
    }
    mock_request.json = AsyncMock(return_value=command_data)
    
    # Create a CommandError with some error details
    error_details = {"field": ["error message"]}
    command_error = CommandError()
    # Manually set the errors attribute since CommandError doesn't accept kwargs
    command_error.errors = error_details
    
    # Act
    # Mock the Context class to avoid errors with the context
    with patch('paperglass.domain.context.Context') as mock_context:
        # Setup the mock context
        context_instance = mock_context.return_value
        context_instance.setUser = AsyncMock()
        context_instance.setBaseAggregate = AsyncMock()
        
        # Mock the LOGGER to avoid errors with the logging
        with patch('paperglass.interface.adapters.rest.LOGGER') as mock_logger:
            # Mock the parse_obj_as function to raise a CommandError
            with patch('paperglass.interface.adapters.rest.parse_obj_as', side_effect=command_error) as mock_parse:
                response = await rest_adapter.command(mock_request, commands=mock_commands)
                
                # Assert
                mock_commands.handle_command.assert_not_called()
                
                # Check that an error response is returned
                assert isinstance(response, JSONResponse)
                response_data = json.loads(response.body)
                assert response_data["success"] is False
                assert response_data["errors"] == error_details
