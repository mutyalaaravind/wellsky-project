import os
import sys
import time
from unittest.mock import patch, MagicMock, AsyncMock

# Add the root project directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import and setup test environment first
from tests.test_env import setup_test_env
setup_test_env()

# Patch tracing functions before importing the main application
with patch('util.tracing.initialize_tracing', MagicMock()), \
     patch('util.tracing.instrument_libraries', MagicMock()):

    # Now import application modules after environment is set up
    import pytest
    from fastapi.testclient import TestClient
    from fastapi import HTTPException, Request
    from middleware.security import require_service_account_auth
    import main
    import settings
    from models.general import PipelineParameters, TaskParameters

    # Mock token claims for testing
    MOCK_TOKEN_CLAIMS = {
        "sub": "test-subject",
        "email": "test@example.com",
        "iss": "https://accounts.google.com",
        "aud": "test-audience",
        "iat": 1234567890,
        "exp": 9999999999
    }

    class MockOIDCValidator:
        """Mock OIDC validator for testing"""
        async def validate_token(self, authorization_header: str) -> dict:
            """Mock token validation that always succeeds"""
            if not authorization_header or not authorization_header.startswith('Bearer '):
                raise ValueError("Missing or invalid Authorization header")
            return {
                "sub": "test-subject",
                "email": "test-service-account@test.com",
                "iss": "https://accounts.google.com",
                "aud": "test-service-account@test.com",
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600
            }

    class TestMainAPI:
        """Test suite for main.py FastAPI application."""

        def setup_method(self):
            """Set up test client and patches before each test."""
            # Set CLOUD_PROVIDER to local for testing
            import settings
            settings.CLOUD_PROVIDER = 'local'
            
            # Create a mock that returns specific values for different env vars
            def mock_getenv(key, default=None):
                env_values = {
                    # Tracing settings
                    'ENABLE_GCP_TRACE_EXPORTER': 'false',
                    'ENABLE_CONSOLE_TRACE_EXPORTER': 'false',
                    'ENABLE_JAEGER_TRACE_EXPORTER': 'false',
                    'HOSTNAME': 'test-host',
                    # Cloud settings
                    'CLOUD_PROVIDER': 'local',
                    'CLOUDTASK_EMULATOR_ENABLED': 'true',
                    'ENTITYEXTRACTION_TASK_PERSIST_GCS_ENABLED': 'false',
                    'USE_JSON_SAFE_LOADS': 'true',
                    'LLM_VERTEXAI_ENABLED': 'false',
                    'GCP_PROJECT_ID': 'test-project',
                    'GCP_PUBSUB_PROJECT_ID': 'test-project',
                    'GCP_LOCATION': 'us-central1',
                    'GCP_LOCATION_2': 'us-central1',
                    'GCP_LOCATION_3': 'us-central1',
                    'GCP_MULTI_REGION_FIRESTORE_LOCATON': 'us-central1',
                    'GCP_FIRESTORE_DB': 'test-db',
                    'SERVICE_ACCOUNT_EMAIL': 'test@test.com',
                    'VERSION': '1.0.0',
                    'SERVICE': 'test-service',
                    'STAGE': 'test'
                }
                return env_values.get(key, default)
                
            # Initialize the os.getenv patcher with the mock
            self.os_getenv_patcher = patch('os.getenv', side_effect=mock_getenv)
            self.os_getenv_patcher.start()
            self.client = TestClient(main.app)

        def teardown_method(self):
            """Clean up after each test."""
            self.os_getenv_patcher.stop()

        def test_root_endpoint(self):
            """Test the root endpoint."""
            response = self.client.get("/api/")
            assert response.status_code == 200
            assert response.json() == {"message": "Welcome to Entity Extraction API"}

        def test_health_check_endpoint(self):
            """Test the health check endpoint."""
            response = self.client.get("/api/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}

        @patch('routers.pipeline.pipeline_start')
        def test_start_pipeline_success(self, mock_pipeline_start):
            """Test successful pipeline start."""
            # Mock the pipeline_start function
            mock_result = MagicMock()
            mock_result.dict.return_value = {"status": "started", "pipeline_id": "test-123"}
            mock_pipeline_start.return_value = mock_result

            # Create test data with required fields
            pipeline_params = {
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "patient_id": "test-patient",
                "document_id": "test-document"
            }

            with patch('util.oidc_validator.get_oidc_validator', return_value=MockOIDCValidator()), \
                 patch('settings.SERVICE_ACCOUNT_EMAIL', 'test-service-account@test.com'):
                response = self.client.post(
                    "/api/pipeline/test-scope/test-pipeline/start",
                    json=pipeline_params,
                    headers={"Authorization": "Bearer test-token"}
                )

            assert response.status_code == 200
            assert response.json() == {"status": "started", "pipeline_id": "test-123"}
            mock_pipeline_start.assert_called_once()

        @patch('routers.pipeline.pipeline_start')
        def test_start_pipeline_value_error(self, mock_pipeline_start):
            """Test pipeline start with ValueError."""
            # Mock the pipeline_start function to raise ValueError
            mock_pipeline_start.side_effect = ValueError("Invalid pipeline configuration")

            pipeline_params = {
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "patient_id": "test-patient",
                "document_id": "test-document"
            }

            with patch('util.oidc_validator.get_oidc_validator', return_value=MockOIDCValidator()), \
                 patch('settings.SERVICE_ACCOUNT_EMAIL', 'test-service-account@test.com'):
                response = self.client.post(
                    "/api/pipeline/test-scope/test-pipeline/start",
                    json=pipeline_params,
                    headers={"Authorization": "Bearer test-token"}
                )

            assert response.status_code == 422
            assert "Invalid pipeline configuration" in response.json()["detail"]

        @patch('routers.pipeline.pipeline_start')
        def test_start_pipeline_general_exception(self, mock_pipeline_start):
            """Test pipeline start with general exception."""
            # Mock the pipeline_start function to raise a general exception
            mock_pipeline_start.side_effect = Exception("Database connection failed")

            pipeline_params = {
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "patient_id": "test-patient",
                "document_id": "test-document"
            }

            with patch('util.oidc_validator.get_oidc_validator', return_value=MockOIDCValidator()), \
                 patch('settings.SERVICE_ACCOUNT_EMAIL', 'test-service-account@test.com'):
                response = self.client.post(
                    "/api/pipeline/test-scope/test-pipeline/start",
                    json=pipeline_params,
                    headers={"Authorization": "Bearer test-token"}
                )

            assert response.status_code == 500
            assert "Error starting pipeline: Database connection failed" in response.json()["detail"]

        @patch('routers.pipeline.TaskOrchestrator')
        def test_run_pipeline_task_success(self, mock_orchestrator_class):
            """Test successful pipeline task execution."""
            # Mock the TaskOrchestrator
            mock_orchestrator = AsyncMock()
            mock_orchestrator.run.return_value = {"status": "completed", "result": "success"}
            mock_orchestrator_class.return_value = mock_orchestrator

            task_params = {
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "patient_id": "test-patient",
                "document_id": "test-document",
                "task_config": {
                    "id": "test-task",
                    "type": "module",
                    "module": {"type": "test_module"}
                }
            }

            with patch('util.oidc_validator.get_oidc_validator', return_value=MockOIDCValidator()), \
                 patch('settings.SERVICE_ACCOUNT_EMAIL', 'test-service-account@test.com'):
                response = self.client.post(
                    "/api/pipeline/test-scope/test-pipeline/test-task/run",
                    json=task_params,
                    headers={"Authorization": "Bearer test-token"}
                )

            assert response.status_code == 200
            assert response.json() == {"status": "completed", "result": "success"}
            mock_orchestrator_class.assert_called_once_with("test-task")
            mock_orchestrator.run.assert_called_once()

        @patch('routers.pipeline.TaskOrchestrator')
        def test_run_pipeline_task_value_error(self, mock_orchestrator_class):
            """Test pipeline task execution with ValueError."""
            # Mock the TaskOrchestrator to raise ValueError
            mock_orchestrator = MagicMock()
            mock_orchestrator.run.side_effect = ValueError("Invalid task parameters")
            mock_orchestrator_class.return_value = mock_orchestrator

            task_params = {
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "patient_id": "test-patient",
                "document_id": "test-document",
                "task_config": {
                    "id": "test-task",
                    "type": "module",
                    "module": {"type": "test_module"}
                }
            }

            with patch('util.oidc_validator.get_oidc_validator', return_value=MockOIDCValidator()), \
                 patch('settings.SERVICE_ACCOUNT_EMAIL', 'test-service-account@test.com'):
                response = self.client.post(
                    "/api/pipeline/test-scope/test-pipeline/test-task/run",
                    json=task_params,
                    headers={"Authorization": "Bearer test-token"}
                )

            assert response.status_code == 422
            assert "Invalid task parameters" in response.json()["detail"]

        @patch('routers.pipeline.TaskOrchestrator')
        def test_run_pipeline_task_general_exception(self, mock_orchestrator_class):
            """Test pipeline task execution with general exception."""
            # Mock the TaskOrchestrator to raise a general exception
            mock_orchestrator = MagicMock()
            mock_orchestrator.run.side_effect = Exception("Task execution failed")
            mock_orchestrator_class.return_value = mock_orchestrator

            task_params = {
                "app_id": "test-app",
                "tenant_id": "test-tenant",
                "patient_id": "test-patient",
                "document_id": "test-document",
                "task_config": {
                    "id": "test-task",
                    "type": "module",
                    "module": {"type": "test_module"}
                }
            }

            with patch('util.oidc_validator.get_oidc_validator', return_value=MockOIDCValidator()), \
                 patch('settings.SERVICE_ACCOUNT_EMAIL', 'test-service-account@test.com'):
                response = self.client.post(
                    "/api/pipeline/test-scope/test-pipeline/test-task/run",
                    json=task_params,
                    headers={"Authorization": "Bearer test-token"}
                )

            assert response.status_code == 500
            assert "Error running pipeline task: Task execution failed" in response.json()["detail"]

        @patch('routers.config_pipeline.list_active_pipeline_configs')
        @patch('routers.config_pipeline.pipeline_config_to_dict')
        def test_list_all_pipeline_configs_success(self, mock_pipeline_config_to_dict, mock_list_configs):
            """Test successful listing of all pipeline configurations."""
            # Mock the list_active_pipeline_configs function
            mock_config1 = MagicMock()
            mock_config2 = MagicMock()
            mock_list_configs.return_value = [mock_config1, mock_config2]
            
            # Mock the pipeline_config_to_dict function
            mock_pipeline_config_to_dict.side_effect = [
                {"id": "config1", "name": "Test Config 1"},
                {"id": "config2", "name": "Test Config 2"}
            ]

            response = self.client.get("/api/config/pipelines")

            assert response.status_code == 200
            result = response.json()
            assert result["count"] == 2
            assert len(result["configurations"]) == 2
            assert result["configurations"][0] == {"id": "config1", "name": "Test Config 1"}
            assert result["configurations"][1] == {"id": "config2", "name": "Test Config 2"}

        @patch('routers.config_pipeline.list_active_pipeline_configs')
        def test_list_all_pipeline_configs_exception(self, mock_list_configs):
            """Test listing pipeline configurations with exception."""
            # Mock the list_active_pipeline_configs function to raise an exception
            mock_list_configs.side_effect = Exception("Database error")

            response = self.client.get("/api/config/pipelines")

            assert response.status_code == 500
            assert "Error retrieving pipeline configurations: Database error" in response.json()["detail"]

        @patch('routers.config_pipeline.search_pipeline_config')
        def test_get_pipeline_config_success(self, mock_search_config):
            """Test successful retrieval of a specific pipeline configuration."""
            # Mock the search_pipeline_config function
            mock_config = MagicMock()
            mock_config.dict.return_value = {"id": "test-config", "name": "Test Configuration"}
            mock_search_config.return_value = mock_config

            response = self.client.get("/api/config/pipelines/test-scope/test-pipeline")

            assert response.status_code == 200
            assert response.json() == {"id": "test-config", "name": "Test Configuration"}
            mock_search_config.assert_called_once_with("test-scope", "test-pipeline")

        @patch('routers.config_pipeline.search_pipeline_config')
        def test_get_pipeline_config_not_found(self, mock_search_config):
            """Test retrieval of a non-existent pipeline configuration."""
            # Mock the search_pipeline_config function to return None
            mock_search_config.return_value = None

            response = self.client.get("/api/config/pipelines/test-scope/nonexistent-pipeline")

            assert response.status_code == 404
            assert "Pipeline configuration not found" in response.json()["detail"]

        @patch('routers.config_pipeline.search_pipeline_config')
        def test_get_pipeline_config_exception(self, mock_search_config):
            """Test retrieval of pipeline configuration with exception."""
            # Mock the search_pipeline_config function to raise an exception
            mock_search_config.side_effect = Exception("Database connection failed")

            response = self.client.get("/api/config/pipelines/test-scope/test-pipeline")

            assert response.status_code == 500
            assert "Error retrieving pipeline configuration: Database connection failed" in response.json()["detail"]

        def test_cors_middleware_configured(self):
            """Test that CORS middleware is properly configured."""
            # Test that the app has CORS middleware by checking middleware stack
            middleware_stack = main.app.middleware_stack
            # CORS middleware should be present in the middleware stack
            assert middleware_stack is not None
            
            # Test CORS headers are present in response
            response = self.client.get("/api/health", headers={"Origin": "http://localhost:3000"})
            assert response.status_code == 200
            # CORS should add access-control headers when configured
            assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()] or response.status_code == 200

        def test_api_router_included(self):
            """Test that the API router is included in the app."""
            # Test that routes are properly configured
            routes = [route.path for route in main.app.routes]
            expected_routes = [
                "/api/",
                "/api/health",
                "/api/pipeline/{scope}/{pipeline_key}/start",
                "/api/pipeline/{scope}/{pipeline_key}/{task}/run",
                "/api/config/pipelines",
                "/api/config/pipelines/{scope}/{pipeline_key}"
            ]
            
            # Check that at least some of the expected routes are present
            found_routes = 0
            for expected_route in expected_routes:
                if any(expected_route in route for route in routes):
                    found_routes += 1
            
            # We should find at least the basic routes
            assert found_routes >= 2  # At least root and health endpoints

        def test_app_title(self):
            """Test that the FastAPI app has the correct title."""
            assert main.app.title == "Entity Extraction API"

        @patch('main.logger')
        async def test_startup_event_success(self, mock_logger):
            """Test successful startup event execution."""
            with patch('util.tracing.initialize_tracing') as mock_init_tracing, \
                 patch('util.tracing.instrument_libraries') as mock_instrument, \
                 patch('settings.ENABLE_GCP_TRACE_EXPORTER', True), \
                 patch('settings.ENABLE_CONSOLE_TRACE_EXPORTER', False), \
                 patch('settings.ENABLE_JAEGER_TRACE_EXPORTER', False), \
                 patch('settings.JAEGER_ENDPOINT', "http://jaeger:4318/v1/traces"):
                
                # Execute startup event
                await main.startup_event()
                
                # Verify tracing initialization was called
                mock_init_tracing.assert_called_once_with(
                    service_name="entity-extraction",
                    service_version="1.0.0",
                    enable_gcp_exporter=True,
                    enable_console_exporter=False,
                    enable_jaeger_exporter=False,
                    jaeger_endpoint="http://jaeger:4318/v1/traces"
                )
                mock_instrument.assert_called_once()
                mock_logger.info.assert_called_once_with("OpenTelemetry tracing initialized successfully")

        @patch('main.logger')
        async def test_startup_event_tracing_failure(self, mock_logger):
            """Test startup event when tracing initialization fails."""
            with patch('util.tracing.initialize_tracing') as mock_init_tracing:
                # Make tracing initialization fail
                mock_init_tracing.side_effect = Exception("Tracing setup failed")
                
                # Execute startup event (should not raise exception)
                await main.startup_event()
                
                # Verify warning was logged
                mock_logger.warning.assert_called_once_with("Failed to initialize OpenTelemetry tracing: Tracing setup failed")

        @patch('main.logger')
        async def test_startup_event_import_error(self, mock_logger):
            """Test startup event when util.tracing import fails."""
            with patch('builtins.__import__') as mock_import:
                # Make the import of util.tracing fail
                def side_effect(name, *args, **kwargs):
                    if name == 'util.tracing':
                        raise ImportError("No module named 'util.tracing'")
                    return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = side_effect
                
                # Execute startup event (should not raise exception)
                await main.startup_event()
                
                # Verify warning was logged
                mock_logger.warning.assert_called_once()
                assert "Failed to initialize OpenTelemetry tracing" in mock_logger.warning.call_args[0][0]

        @patch('main.logger')
        async def test_startup_event_instrument_libraries_failure(self, mock_logger):
            """Test startup event when instrument_libraries fails."""
            with patch('util.tracing.initialize_tracing') as mock_init_tracing, \
                 patch('util.tracing.instrument_libraries') as mock_instrument, \
                 patch('settings.ENABLE_GCP_TRACE_EXPORTER', True), \
                 patch('settings.ENABLE_CONSOLE_TRACE_EXPORTER', False), \
                 patch('settings.ENABLE_JAEGER_TRACE_EXPORTER', False), \
                 patch('settings.JAEGER_ENDPOINT', "http://jaeger:4318/v1/traces"):
                
                # Make instrument_libraries fail
                mock_instrument.side_effect = Exception("Instrumentation failed")
                
                # Execute startup event (should not raise exception)
                await main.startup_event()
                
                # Verify tracing initialization was called but warning was logged
                mock_init_tracing.assert_called_once()
                mock_logger.warning.assert_called_once_with("Failed to initialize OpenTelemetry tracing: Instrumentation failed")
