import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.context import Context
import uuid

@pytest.fixture
def context():
    return Context()

@pytest.mark.asyncio
async def test_get_set_user(context):
    test_user = {"username": "testuser", "id": "123"}
    await context.setUser(test_user)
    assert await context.getUser() == test_user
    assert await context.getUsername() == "testuser"

@pytest.mark.asyncio
async def test_get_username_when_none(context):
    assert await context.getUsername() == "unknown"
    await context.setUser(None)
    assert await context.getUsername() == "unknown"

@pytest.mark.asyncio
async def test_base_aggregate(context):
    test_aggregate = {"key": "value"}
    await context.setBaseAggregate(test_aggregate)
    assert context.getBaseAggregate() == test_aggregate
    
    # Test sync version
    new_aggregate = {"key2": "value2"}
    context.setBaseAggregate_sync(new_aggregate)
    assert context.getBaseAggregate() == new_aggregate

def test_get_logging_context(context):
    test_aggregate = {"key": "value"}
    context.setBaseAggregate_sync(test_aggregate)
    logging_context = context.getLoggingContext()
    
    assert "traceId" in logging_context
    assert "env" in logging_context
    assert "username" in logging_context
    assert logging_context["key"] == "value"
    assert logging_context["username"] == "unknown"

@pytest.mark.asyncio
async def test_trace_management(context):
    test_trace = "test-trace"
    await context.setTrace(test_trace)
    assert await context.getTrace() == test_trace

def test_trace_id(context):
    trace_id = context.sync_getTraceId()
    assert isinstance(trace_id, str)
    assert uuid.UUID(trace_id)  # Verify it's a valid UUID

@pytest.mark.asyncio
async def test_opentelemetry(context):
    parent_trace = "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
    trace_state = "rojo=00f067aa0ba902b7"
    baggage = "username=test"
    
    await context.setOpenTelemetry(parent_trace, trace_state, baggage)
    telemetry = await context.getOpenTelemetry()
    
    assert telemetry["parenttrace"] == parent_trace
    assert telemetry["tracestate"] == trace_state
    assert telemetry["baggage"] == baggage

def test_tracer(context):
    test_tracer = {"name": "test-tracer"}
    context.setTracer(test_tracer)
    assert context.getTracer() == test_tracer

def test_extract_command(context):
    class MockCommand:
        def dict(self):
            return {
                "app_id": "123",
                "tenant_id": "456",
                "patient_id": "789",
                "user_id": "012",
                "document_id": "345",
                "document_operation_definition_id": "678",
                "document_operation_instance_id": "901",
                "page_number": 1,
                "other_field": "value"
            }
    
    command = MockCommand()
    result = context.extractCommand(command)
    
    # Check if relevant fields are extracted and set in baseAggregate
    base_aggregate = context.getBaseAggregate()
    assert base_aggregate["app_id"] == "123"
    assert base_aggregate["tenant_id"] == "456"
    assert base_aggregate["patient_id"] == "789"
    assert base_aggregate["user_id"] == "012"
    assert base_aggregate["document_id"] == "345"
    assert base_aggregate["document_operation_definition_id"] == "678"
    assert base_aggregate["document_operation_instance_id"] == "901"
    assert base_aggregate["page_number"] == 1
    
    # Check if original command dict is returned
    assert result["other_field"] == "value"

def test_extract_command_empty(context):
    context.setBaseAggregate_sync({})  # Reset the base aggregate
    result = context.extractCommand(None)
    assert result == {}
    assert context.getBaseAggregate() == {}