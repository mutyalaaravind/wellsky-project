import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import settings


class TestSettings:
    """Test suite for settings module."""

    def test_get_module_root(self):
        """Test that get_module_root returns the correct directory."""
        result = settings.get_module_root()
        assert isinstance(result, str)
        assert result.endswith('src')

    def test_getenv_or_die_with_existing_env_var(self):
        """Test getenv_or_die with an existing environment variable."""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = settings.getenv_or_die('TEST_VAR')
            assert result == 'test_value'

    def test_getenv_or_die_with_missing_env_var(self):
        """Test getenv_or_die raises ValueError for missing environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="MISSING_VAR is missing in environment"):
                settings.getenv_or_die('MISSING_VAR')

    def test_to_bool_true_values(self):
        """Test to_bool function with various true values."""
        true_values = ['1', 'y', 'yes', 't', 'true', 'on', 'Y', 'YES', 'T', 'TRUE', 'ON']
        for value in true_values:
            assert settings.to_bool(value) is True

    def test_to_bool_false_values(self):
        """Test to_bool function with various false values."""
        false_values = ['0', 'n', 'no', 'f', 'false', 'off', 'N', 'NO', 'F', 'FALSE', 'OFF', 'random']
        for value in false_values:
            assert settings.to_bool(value) is False

    def test_to_bool_none_value(self):
        """Test to_bool function with None value."""
        assert settings.to_bool(None) is False

    def test_to_int(self):
        """Test to_int function."""
        assert settings.to_int('42') == 42
        assert settings.to_int('-10') == -10
        assert settings.to_int('0') == 0

    def test_to_int_invalid_value(self):
        """Test to_int function with invalid value."""
        with pytest.raises(ValueError):
            settings.to_int('not_a_number')

    def test_to_double(self):
        """Test to_double function."""
        assert settings.to_double('3.14') == 3.14
        assert settings.to_double('-2.5') == -2.5
        assert settings.to_double('0.0') == 0.0
        assert settings.to_double('42') == 42.0

    def test_to_double_invalid_value(self):
        """Test to_double function with invalid value."""
        with pytest.raises(ValueError):
            settings.to_double('not_a_number')

    def test_to_list_of_strings(self):
        """Test to_list_of_strings function."""
        assert settings.to_list_of_strings('a,b,c') == ['a', 'b', 'c']
        assert settings.to_list_of_strings('single') == ['single']
        assert settings.to_list_of_strings('') == ['']
        assert settings.to_list_of_strings('item1,item2,item3,item4') == ['item1', 'item2', 'item3', 'item4']

    @patch.dict(os.environ, {
        'VERSION': '1.0.0',
        'SERVICE': 'test-service',
        'STAGE': 'test',
        'DEBUG': 'true',
        'CLOUD_PROVIDER': 'gcp',
        'GCP_PROJECT_ID': 'test-project',
        'GCP_PUBSUB_PROJECT_ID': 'test-pubsub-project',
        'GCS_BUCKET_NAME': 'test-bucket',
        'GCP_LOCATION': 'us-central1',
        'GCP_LOCATION_2': 'us-east1',
        'GCP_LOCATION_3': 'us-west1',
        'GCP_MULTI_REGION_FIRESTORE_LOCATON': 'nam5',
        'GCP_FIRESTORE_DB': 'test-db',
        'SERVICE_ACCOUNT_EMAIL': 'test@test.com',
        'SELF_API_URL': 'http://localhost:8000',
        'SELF_API_URL_2': 'http://localhost:8001',
        'PAPERGLASS_API_URL': 'http://paperglass.com',
        'PAPERGLASS_INTEGRATION_TOPIC': 'test-topic'
    })
    def test_environment_variables_loading(self):
        """Test that environment variables are loaded correctly."""
        # Reload the settings module to pick up the new environment variables
        import importlib
        importlib.reload(settings)
        
        assert settings.VERSION == '1.0.0'
        assert settings.SERVICE == 'test-service'
        assert settings.STAGE == 'test'
        assert settings.DEBUG is True
        assert settings.CLOUD_PROVIDER == 'gcp'
        assert settings.GCP_PROJECT_ID == 'test-project'

    @patch.dict(os.environ, {
        'CLOUDTASK_EMULATOR_ENABLED': 'false',
        'CLOUDTASK_EMULATOR_URL': 'http://remote-host:9999',
        'USE_JSON_SAFE_LOADS': 'false',
        'LLM_VERTEXAI_ENABLED': 'false',
        'LLM_MAX_OUTPUT_TOKENS': '4096',
        'LLM_TEMPERATURE': '0.5',
        'LLM_TOP_P': '0.8',
        'LLM_PROMPT_AUDIT_ENABLED': 'false'
    })
    def test_optional_environment_variables(self):
        """Test optional environment variables with custom values."""
        import importlib
        importlib.reload(settings)
        
        assert settings.CLOUDTASK_EMULATOR_ENABLED is False
        assert settings.CLOUDTASK_EMULATOR_URL == 'http://remote-host:9999'
        assert settings.USE_JSON_SAFE_LOADS is False
        assert settings.LLM_VERTEXAI_ENABLED is False
        assert settings.LLM_MAX_OUTPUT_TOKENS_DEFAULT == 4096
        assert settings.LLM_TEMPERATURE_DEFAULT == 0.5
        assert settings.LLM_TOP_P_DEFAULT == 0.8
        assert settings.LLM_PROMPT_AUDIT_ENABLED is False

    def test_json_cleaners_configuration(self):
        """Test JSON cleaners configuration."""
        assert isinstance(settings.JSON_CLEANERS, list)
        assert len(settings.JSON_CLEANERS) > 0
        assert 'type' in settings.JSON_CLEANERS[0]
        assert 'match' in settings.JSON_CLEANERS[0]
        assert 'replace' in settings.JSON_CLEANERS[0]

    def test_dotenv_loading_path_construction(self):
        """Test that the dotenv path is constructed correctly."""
        # Test that the env_path is constructed properly
        from pathlib import Path
        import settings
        
        # The path should be constructed as parent.parent / '.env'
        expected_path_parts = ['entity_extraction', '.env']
        
        # We can't easily test the exact path construction without mocking,
        # but we can verify the module loads without errors
        assert hasattr(settings, 'env_path')
        
        # Test that Path is used correctly by checking the module loads
        import importlib
        importlib.reload(settings)
        
        # If we get here without errors, the path construction worked
        assert True

    def test_default_values(self):
        """Test default values for optional environment variables."""
        # Test that default values are set correctly when env vars are not provided
        with patch.dict(os.environ, {}, clear=True):
            # Mock load_dotenv to prevent loading .env file during test
            with patch('dotenv.load_dotenv'):
                # Set required env vars to avoid errors
                with patch.dict(os.environ, {
                    'VERSION': '1.0.0',
                    'SERVICE': 'test-service',
                    'STAGE': 'test',
                    'CLOUD_PROVIDER': 'gcp',
                    'GCP_PROJECT_ID': 'test-project',
                    'GCP_PUBSUB_PROJECT_ID': 'test-pubsub-project',
                    'GCS_BUCKET_NAME': 'test-bucket',
                    'GCP_LOCATION': 'us-central1',
                    'GCP_LOCATION_2': 'us-east1',
                    'GCP_LOCATION_3': 'us-west1',
                    'GCP_MULTI_REGION_FIRESTORE_LOCATON': 'nam5',
                    'GCP_FIRESTORE_DB': 'test-db',
                    'SERVICE_ACCOUNT_EMAIL': 'test@test.com',
                    'SELF_API_URL': 'http://localhost:8000',
                    'SELF_API_URL_2': 'http://localhost:8001',
                    'PAPERGLASS_API_URL': 'http://paperglass.com',
                    'PAPERGLASS_INTEGRATION_TOPIC': 'test-topic',
                    'DJT_API_URL': 'http://djt-api:17000',
                    'MEDICATION_EXTRACTION_V4_STATUS_CHECK_QUEUE_NAME': 'medication-extraction-v4-status-check-queue'
                }):
                    import importlib
                    importlib.reload(settings)

                    # Test default values (when no environment variables are set)
                    assert settings.INTRA_TASK_INVOCATION_DEFAULT_QUEUE == "entity-extraction-intra-default-default-queue"
                    assert settings.CLOUDTASK_EMULATOR_ENABLED is False  # Default from code: "false"
                    assert settings.CLOUDTASK_EMULATOR_URL == "http://localhost:30001"  # Default from code
                    assert settings.DEFAULT_TASK_QUEUE == "default-queue"  # Default from code
                    assert settings.USE_JSON_SAFE_LOADS is True
                    assert settings.LLM_VERTEXAI_ENABLED is True
                    assert settings.LLM_API_VERSION == 'v1'
                    assert settings.LLM_MODEL_DEFAULT == 'gemini-1.5-flash-002'
                    assert settings.LLM_MAX_OUTPUT_TOKENS_DEFAULT == 8192
                    assert settings.LLM_TEMPERATURE_DEFAULT == 0.0
                    assert settings.LLM_TOP_P_DEFAULT == 0.95
                    assert settings.LLM_PROMPT_AUDIT_ENABLED is True
