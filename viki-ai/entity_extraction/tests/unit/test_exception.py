import pytest
import traceback
import os
import sys

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from util.exception import (
    exceptionToMap,
    getStacktrace,
    getStacktraceList,
    getTrimmedStacktrace,
    getTrimmedStacktraceAsString,
    UnAuthorizedException,
    OrchestrationException,
    UnsupportedFileTypeException,
    WindowClosedException,
    OrchestrationExceptionWithContext,
    JobException
)


class TestExceptionUtilities:
    """Test suite for exception utility functions."""

    def test_exceptionToMap_basic_exception(self):
        """Test exceptionToMap with a basic exception."""
        try:
            raise ValueError("Test error message")
        except ValueError as e:
            result = exceptionToMap(e)
            
            assert result['message'] == "Test error message"
            assert result['type'] == "ValueError"
            assert isinstance(result['details'], list)
            assert len(result['details']) > 0
            assert any("Test error message" in detail for detail in result['details'])

    def test_exceptionToMap_custom_exception(self):
        """Test exceptionToMap with a custom exception."""
        try:
            raise OrchestrationException("Custom orchestration error")
        except OrchestrationException as e:
            result = exceptionToMap(e)
            
            assert result['message'] == "Custom orchestration error"
            assert result['type'] == "OrchestrationException"
            assert isinstance(result['details'], list)
            assert len(result['details']) > 0

    def test_exceptionToMap_exception_with_no_message(self):
        """Test exceptionToMap with an exception that has no message."""
        try:
            raise RuntimeError()
        except RuntimeError as e:
            result = exceptionToMap(e)
            
            assert result['message'] == ""
            assert result['type'] == "RuntimeError"
            assert isinstance(result['details'], list)

    def test_getStacktrace(self):
        """Test getStacktrace function."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            stacktrace = getStacktrace(e)
            
            assert isinstance(stacktrace, list)
            assert len(stacktrace) > 0
            assert any("ValueError" in line for line in stacktrace)

    def test_getStacktraceList(self):
        """Test getStacktraceList function."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            stacktrace_list = getStacktraceList(e)
            
            assert isinstance(stacktrace_list, list)
            assert len(stacktrace_list) > 0
            assert any("ValueError" in line for line in stacktrace_list)
            assert any("Test error" in line for line in stacktrace_list)

    def test_getTrimmedStacktrace(self):
        """Test getTrimmedStacktrace function."""
        def deep_function_call():
            def level1():
                def level2():
                    def level3():
                        raise ValueError("Deep error")
                    level3()
                level2()
            level1()
        
        try:
            deep_function_call()
        except ValueError as e:
            trimmed_stacktrace = getTrimmedStacktrace(e)
            
            assert isinstance(trimmed_stacktrace, list)
            assert len(trimmed_stacktrace) <= 12  # Should be trimmed to max 12 entries
            assert any("ValueError" in line for line in trimmed_stacktrace)

    def test_getTrimmedStacktraceAsString(self):
        """Test getTrimmedStacktraceAsString function."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            trimmed_stacktrace_string = getTrimmedStacktraceAsString(e)
            
            assert isinstance(trimmed_stacktrace_string, str)
            assert "ValueError" in trimmed_stacktrace_string
            assert "\n" in trimmed_stacktrace_string  # Should be joined with newlines

    def test_getTrimmedStacktrace_with_long_stack(self):
        """Test getTrimmedStacktrace with a very long stack trace."""
        def create_deep_stack(depth):
            if depth == 0:
                raise ValueError("Deep stack error")
            else:
                create_deep_stack(depth - 1)
        
        try:
            create_deep_stack(20)  # Create a stack deeper than 12
        except ValueError as e:
            trimmed_stacktrace = getTrimmedStacktrace(e)
            
            assert isinstance(trimmed_stacktrace, list)
            assert len(trimmed_stacktrace) <= 12  # Should be trimmed to exactly 12 or fewer


class TestCustomExceptions:
    """Test suite for custom exception classes."""

    def test_UnAuthorizedException(self):
        """Test UnAuthorizedException."""
        with pytest.raises(UnAuthorizedException):
            raise UnAuthorizedException("Unauthorized access")
        
        try:
            raise UnAuthorizedException("Unauthorized access")
        except UnAuthorizedException as e:
            assert str(e) == "Unauthorized access"
            assert isinstance(e, Exception)

    def test_OrchestrationException(self):
        """Test OrchestrationException."""
        message = "Orchestration failed"
        
        with pytest.raises(OrchestrationException):
            raise OrchestrationException(message)
        
        try:
            raise OrchestrationException(message)
        except OrchestrationException as e:
            assert e.message == message
            assert isinstance(e, Exception)

    def test_UnsupportedFileTypeException(self):
        """Test UnsupportedFileTypeException."""
        message = "Unsupported file type: .xyz"
        
        with pytest.raises(UnsupportedFileTypeException):
            raise UnsupportedFileTypeException(message)
        
        try:
            raise UnsupportedFileTypeException(message)
        except UnsupportedFileTypeException as e:
            assert e.message == message
            assert isinstance(e, Exception)

    def test_WindowClosedException(self):
        """Test WindowClosedException."""
        message = "Window was closed unexpectedly"
        
        with pytest.raises(WindowClosedException):
            raise WindowClosedException(message)
        
        try:
            raise WindowClosedException(message)
        except WindowClosedException as e:
            assert e.message == message
            assert isinstance(e, Exception)

    def test_OrchestrationExceptionWithContext(self):
        """Test OrchestrationExceptionWithContext."""
        message = "Orchestration failed with context"
        context = {"task_id": "123", "pipeline": "test_pipeline"}
        
        with pytest.raises(OrchestrationExceptionWithContext):
            raise OrchestrationExceptionWithContext(message, context)
        
        try:
            raise OrchestrationExceptionWithContext(message, context)
        except OrchestrationExceptionWithContext as e:
            assert e.message == message
            assert e.context == context
            assert isinstance(e, OrchestrationException)
            assert isinstance(e, Exception)

    def test_JobException(self):
        """Test JobException."""
        message = "Job execution failed"
        
        with pytest.raises(JobException):
            raise JobException(message)
        
        try:
            raise JobException(message)
        except JobException as e:
            assert e.message == message
            assert isinstance(e, Exception)

    def test_exception_inheritance(self):
        """Test that OrchestrationExceptionWithContext properly inherits from OrchestrationException."""
        message = "Test message"
        context = {"key": "value"}
        
        exception = OrchestrationExceptionWithContext(message, context)
        
        assert isinstance(exception, OrchestrationException)
        assert isinstance(exception, Exception)
        assert exception.message == message
        assert exception.context == context

    def test_custom_exceptions_with_exceptionToMap(self):
        """Test that custom exceptions work properly with exceptionToMap."""
        try:
            raise OrchestrationExceptionWithContext("Test error", {"context": "test"})
        except OrchestrationExceptionWithContext as e:
            result = exceptionToMap(e)
            
            # The string representation includes both message and context as a tuple
            assert "Test error" in result['message']
            assert result['type'] == "OrchestrationExceptionWithContext"
            assert isinstance(result['details'], list)
            assert len(result['details']) > 0


class TestExceptionIntegration:
    """Integration tests for exception utilities."""

    def test_full_exception_workflow(self):
        """Test the complete workflow of exception handling."""
        try:
            # Simulate a complex operation that fails
            def operation_that_fails():
                def nested_operation():
                    raise UnsupportedFileTypeException("Cannot process .unknown file")
                nested_operation()
            
            operation_that_fails()
        except UnsupportedFileTypeException as e:
            # Test all utility functions with the same exception
            exception_map = exceptionToMap(e)
            stacktrace = getStacktrace(e)
            stacktrace_list = getStacktraceList(e)
            trimmed_stacktrace = getTrimmedStacktrace(e)
            trimmed_string = getTrimmedStacktraceAsString(e)
            
            # Verify all functions return expected types and content
            assert exception_map['type'] == "UnsupportedFileTypeException"
            assert exception_map['message'] == "Cannot process .unknown file"
            
            assert isinstance(stacktrace, list)
            assert isinstance(stacktrace_list, list)
            assert isinstance(trimmed_stacktrace, list)
            assert isinstance(trimmed_string, str)
            
            # Verify content consistency
            assert len(stacktrace_list) >= len(stacktrace)
            assert len(trimmed_stacktrace) <= len(stacktrace)

    def test_exception_chaining(self):
        """Test exception handling with exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as original:
                raise OrchestrationException("Orchestration failed") from original
        except OrchestrationException as e:
            result = exceptionToMap(e)
            
            assert result['type'] == "OrchestrationException"
            assert result['message'] == "Orchestration failed"
            assert isinstance(result['details'], list)

    def test_exception_with_special_characters(self):
        """Test exception handling with special characters in messages."""
        special_message = "Error with special chars: àáâãäå ñ 中文 🚀"
        
        try:
            raise JobException(special_message)
        except JobException as e:
            result = exceptionToMap(e)
            
            assert result['message'] == special_message
            assert result['type'] == "JobException"
            
            trimmed_string = getTrimmedStacktraceAsString(e)
            assert isinstance(trimmed_string, str)

    def test_exception_with_empty_context(self):
        """Test OrchestrationExceptionWithContext with empty context."""
        message = "Error with empty context"
        context = {}
        
        try:
            raise OrchestrationExceptionWithContext(message, context)
        except OrchestrationExceptionWithContext as e:
            assert e.message == message
            assert e.context == context
            assert e.context == {}

    def test_exception_with_none_context(self):
        """Test OrchestrationExceptionWithContext with None context."""
        message = "Error with None context"
        context = None
        
        try:
            raise OrchestrationExceptionWithContext(message, context)
        except OrchestrationExceptionWithContext as e:
            assert e.message == message
            assert e.context is None
