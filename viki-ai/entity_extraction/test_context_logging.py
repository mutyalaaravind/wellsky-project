"""Test context-aware logging implementation in both local and GCP modes."""
import sys
import os
import importlib
from unittest.mock import patch
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from util.custom_logger import (
    getLogger,
    set_pipeline_context,
    get_pipeline_context,
    clear_pipeline_context,
    Context,
    _context_instance
)
import settings

def test_basic_logging():
    """Test basic logging functionality."""
    print("=== Testing Basic Logging ===")
    logger = getLogger(__name__)

    logger.info("This is a basic info message")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")

def test_context_setting_and_logging():
    """Test setting pipeline context and automatic injection."""
    print("\n=== Testing Context Setting and Logging ===")
    logger = getLogger(__name__)

    # Clear any existing context
    clear_pipeline_context()

    # Set pipeline context
    set_pipeline_context(
        app_id="test_app",
        tenant_id="tenant_123",
        patient_id="patient_456",
        document_id="doc_789",
        page_number="page_number 1",
        run_id="run_abc123",
        pipeline_scope="medication_extraction",
        pipeline_key="extract_medications",
        task_id="task_001"
    )

    # Verify context is set
    context = get_pipeline_context()
    print(f"Set context: {context}")

    # Test logging with automatic context injection
    logger.info("Processing started with automatic context injection")
    logger.error("An error occurred", extra={"error_code": "ERR_001", "retry_count": 3})
    logger.debug("Debug information", extra={"step": "validation", "items_processed": 42})

def test_additional_context():
    """Test adding additional context data."""
    print("\n=== Testing Additional Context Data ===")
    logger = getLogger(__name__)

    # Add additional context
    set_pipeline_context(
        app_id="test_app",
        tenant_id="tenant_123",
        patient_id="patient_456",
        document_id="doc_789",
        page_number="page_number 1",
        run_id="run_abc123",
        pipeline_scope="medication_extraction",
        pipeline_key="extract_medications",
        task_id="task_001"
    )

    logger.info("Processing page with additional context")
    logger.warning(
        "Validation warning",
        extra={"validation_type": "schema", "field": "medication_name"}
    )

def test_context_clearing():
    """Test context clearing."""
    print("\n=== Testing Context Clearing ===")
    logger = getLogger(__name__)

    # Clear context
    clear_pipeline_context()

    logger.info("This message should have minimal context")

    # Verify context is cleared
    context = get_pipeline_context()
    print(f"Cleared context: {context}")

def test_gcp_mode():
    """Test logging in GCP mode with structured logging."""
    print("\n=== Testing GCP Mode Logging ===")

    # Save original values
    original_cloud_provider = getattr(settings, 'CLOUD_PROVIDER', 'local')

    try:
        # Mock GCP environment
        with patch.object(settings, 'CLOUD_PROVIDER', 'google'):
            # Force reload of custom_logger to pick up new settings
            from util import custom_logger
            importlib.reload(custom_logger)

            # Get fresh logger instance
            logger = custom_logger.getLogger(__name__)

            print("Testing with CLOUD_PROVIDER = 'google'")

            # Set context for GCP testing
            custom_logger.set_pipeline_context(
                app_id="gcp_test_app",
                tenant_id="gcp_tenant_123",
                patient_id="gcp_patient_456",
                document_id="gcp_doc_789",
                page_number="gcp_page_number",
                run_id="gcp_run_abc123",
                pipeline_scope="gcp_medication_extraction",
                pipeline_key="gcp_extract_medications",
                task_id="gcp_task_id"
            )

            # Test various log levels in GCP mode
            logger.info("GCP Info message with context injection")
            logger.warning(
                "GCP Warning message",
                extra={"warning_type": "validation", "field": "dosage"}
            )
            logger.error(
                "GCP Error message",
                extra={"error_code": "GCP_ERR_001", "retry_count": 2}
            )
            logger.debug(
                "GCP Debug message",
                extra={"step": "gcp_processing", "items": 10}
            )

            # Test with complex extra data
            complex_extra = {
                "nested_data": {
                    "medications": ["aspirin", "ibuprofen"],
                    "dosages": [100, 200]
                },
                "metadata": {
                    "source": "gcp_test",
                    "version": "1.0"
                }
            }
            logger.info("GCP message with complex extra data", extra=complex_extra)

            print("GCP mode testing completed - check structured logs")

    except Exception as exc:
        print(f"Error during GCP mode testing: {exc}")
    finally:
        # Restore original settings
        settings.CLOUD_PROVIDER = original_cloud_provider
        # Reload custom_logger to restore original behavior
        from util import custom_logger
        importlib.reload(custom_logger)
        print("Restored original CLOUD_PROVIDER setting")

def test_gcp_vs_local_comparison():
    """Compare logging output between GCP and local modes."""
    print("\n=== Testing GCP vs Local Mode Comparison ===")

    original_cloud_provider = getattr(settings, 'CLOUD_PROVIDER', 'local')

    try:
        # Test Local Mode
        print("\n--- LOCAL MODE ---")
        with patch.object(settings, 'CLOUD_PROVIDER', 'local'):
            from util import custom_logger
            importlib.reload(custom_logger)

            logger = custom_logger.getLogger(__name__)
            custom_logger.set_pipeline_context(
                app_id="comparison_app",
                tenant_id="comparison_tenant",
                patient_id="comparison_patient",
                document_id="comparison_doc_id",
                page_number="comparison_page_number",
                run_id="comparison_run_123",
                pipeline_scope="comparison_medication_extraction",
                pipeline_key="comparison_extract_medications",
                task_id="comparison_task_id"
            )

            logger.info("Local mode: Context should appear in 'Extra Data' section")
            logger.error(
                "Local mode: Error with extra data",
                extra={"error_type": "comparison_test"}
            )

        # Test GCP Mode
        print("\n--- GCP MODE ---")
        with patch.object(settings, 'CLOUD_PROVIDER', 'google'):
            from util import custom_logger
            importlib.reload(custom_logger)

            logger = custom_logger.getLogger(__name__)
            custom_logger.set_pipeline_context(
                app_id="comparison_app",
                tenant_id="comparison_tenant",
                patient_id="comparison_patient",
                document_id="comparison_doc_id",
                page_number="comparison_page_number",
                run_id="comparison_run_123",
                pipeline_scope="comparison_medication_extraction",
                pipeline_key="comparison_extract_medications",
                task_id="comparison_task_id"
            )

            logger.info("GCP mode: Context should be in structured jsonPayload")
            logger.error(
                "GCP mode: Error with extra data",
                extra={"error_type": "comparison_test"}
            )

        print("\nComparison completed - observe the different output formats")

    except Exception as exc:
        print(f"Error during comparison testing: {exc}")
    finally:
        # Restore original settings
        settings.CLOUD_PROVIDER = original_cloud_provider
        from util import custom_logger
        importlib.reload(custom_logger)

def test_direct_context_access():
    """Test accessing context data directly through Context class."""
    print("\n=== Testing Direct Context Access ===")

    # Clear any existing context
    clear_pipeline_context()

    # Create context instance
    context = Context()

    # Set some pipeline context
    set_pipeline_context(
        app_id="direct_test_app",
        tenant_id="direct_tenant_123",
        patient_id="direct_patient_456",
        document_id="direct_doc_789",
        run_id="direct_run_abc123",
        pipeline_scope="direct_extraction",
        pipeline_key="direct_extract",
        task_id="direct_task_001"
    )

    # Test getting all logging context
    full_context = context.getLoggingContext()
    print(f"Full logging context: {full_context}")

    # Test getting base aggregate (should be empty since we didn't set it)
    base_aggregate = context.getBaseAggregate()
    print(f"Base aggregate: {base_aggregate}")

    # Test getting pipeline context specifically
    pipeline_context = context.get_pipeline_context()
    print(f"Pipeline context: {pipeline_context}")

    # Test getting trace ID
    trace_id = context.sync_getTraceId()
    print(f"Trace ID: {trace_id}")

    # Test accessing via global instance
    global_context = _context_instance.getLoggingContext()
    print(f"Global context instance: {global_context}")

    # Test accessing specific values
    app_id = _context_instance.get_pipeline_context().get('app_id')
    tenant_id = _context_instance.get_pipeline_context().get('tenant_id')
    print(f"Specific values - app_id: {app_id}, tenant_id: {tenant_id}")

def test_extract_command():
    """Test the extractCommand method functionality."""
    print("\n=== Testing extractCommand Method ===")

    # Clear any existing context
    clear_pipeline_context()

    # Create a mock command object with the expected attributes
    class MockCommand:
        def __init__(self, **kwargs):
            self._data = kwargs

        def dict(self):
            return self._data

    # Create context instance
    context = Context()

    # Test with valid command containing all expected keys
    command_data = {
        "app_id": "extract_app_123",
        "tenant_id": "extract_tenant_456",
        "patient_id": "extract_patient_789",
        "user_id": "extract_user_abc",
        "document_id": "extract_doc_def",
        "document_operation_definition_id": "extract_def_ghi",
        "document_operation_instance_id": "extract_inst_jkl",
        "page_number": "extract_page_1",
        "run_id": "extract_run_mno",
        "pipeline_scope": "extract_scope",
        "pipeline_key": "extract_key",
        "extra_field": "should_not_be_extracted"
    }

    mock_command = MockCommand(**command_data)

    # Test extractCommand
    result = context.extractCommand(mock_command)
    print(f"extractCommand result: {result}")

    # Verify that base aggregate was set with only the expected keys
    base_aggregate = context.getBaseAggregate()
    print(f"Base aggregate after extractCommand: {base_aggregate}")

    # Verify that extra_field was not included in base aggregate
    assert "extra_field" not in base_aggregate, "extra_field should not be in base aggregate"
    assert "app_id" in base_aggregate, "app_id should be in base aggregate"

    # Test with None command
    result_none = context.extractCommand(None)
    print(f"extractCommand with None: {result_none}")
    assert result_none == {}, "extractCommand should return empty dict for None"

    # Test with command missing some keys
    partial_command_data = {
        "app_id": "partial_app",
        "tenant_id": "partial_tenant",
        "missing_other_keys": "value"
    }
    partial_command = MockCommand(**partial_command_data)
    result_partial = context.extractCommand(partial_command)
    print(f"extractCommand with partial data: {result_partial}")

    base_aggregate_partial = context.getBaseAggregate()
    print(f"Base aggregate after partial command: {base_aggregate_partial}")

def test_specific_context_values():
    """Test retrieving specific context values and manipulating context."""
    print("\n=== Testing Specific Context Value Retrieval ===")

    # Clear any existing context
    clear_pipeline_context()

    # Create context instance
    context = Context()

    # Set initial pipeline context
    set_pipeline_context(
        app_id="specific_app",
        tenant_id="specific_tenant",
        patient_id="specific_patient",
        document_id="specific_doc",
        page_number="specific_page_1",
        run_id="specific_run_123"
    )

    # Test getting specific values via convenience function
    pipeline_data = get_pipeline_context()
    print(f"Pipeline context via convenience function: {pipeline_data}")

    # Test accessing individual values
    app_id = pipeline_data.get('app_id')
    tenant_id = pipeline_data.get('tenant_id')
    non_existent = pipeline_data.get('non_existent_key', 'default_value')

    print(f"Individual values:")
    print(f"  app_id: {app_id}")
    print(f"  tenant_id: {tenant_id}")
    print(f"  non_existent_key: {non_existent}")

    # Test setting base aggregate directly
    base_data = {
        "custom_field": "custom_value",
        "operation_id": "op_456"
    }
    context.setBaseAggregate_sync(base_data)

    # Test retrieving base aggregate
    retrieved_base = context.getBaseAggregate()
    print(f"Set and retrieved base aggregate: {retrieved_base}")

    # Test full logging context with both pipeline and base aggregate
    full_context = context.getLoggingContext()
    print(f"Full context with both pipeline and base data: {full_context}")

    # Test context clearing
    clear_pipeline_context()
    after_clear = get_pipeline_context()
    print(f"Pipeline context after clearing: {after_clear}")

    # Base aggregate should still be there
    base_after_clear = context.getBaseAggregate()
    print(f"Base aggregate after pipeline clear: {base_after_clear}")

    # Test setting additional context via kwargs
    set_pipeline_context(
        app_id="kwargs_app",
        custom_param="custom_value",
        nested_data={"key": "value"}
    )

    kwargs_context = get_pipeline_context()
    print(f"Context with kwargs: {kwargs_context}")

def main():
    """Run all tests."""
    print("Testing Context-Aware Logging Implementation")
    print("=" * 50)

    test_basic_logging()
    test_context_setting_and_logging()
    test_additional_context()
    test_direct_context_access()
    test_extract_command()
    test_specific_context_values()
    # test_context_clearing()
    test_gcp_mode()
    test_gcp_vs_local_comparison()

    print("\n=== Test Complete ===")
    print("Check the logs above to verify context injection is working.")
    print("In GCP environments, context will appear in jsonPayload.")
    print("In local environments, context will appear as 'Extra Data' sections.")
    print("\nGCP mode tests completed - compare the output formats.")


if __name__ == "__main__":
    main()