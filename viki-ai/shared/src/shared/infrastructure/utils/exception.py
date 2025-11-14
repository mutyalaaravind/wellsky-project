"""
Exception utilities for shared library.

This module provides utilities for handling and mapping exceptions
to structured data for logging and error reporting.
"""

import traceback 


def exceptionToMap(exception) -> dict:
    """
    Convert an exception to a structured dictionary for logging.
    
    Args:
        exception: The exception to convert
        
    Returns:
        dict: Structured exception data with message, type, and details
    """
    return {
        'message': str(exception),
        'type': exception.__class__.__name__,
        'details': getStacktraceList(exception)
    }


def getStacktrace(exception):
    """Get the stack trace from an exception as a formatted list."""
    tb = traceback.extract_tb(exception.__traceback__)
    return traceback.format_list(tb)


def getStacktraceList(exception):
    """Get the full stack trace from an exception."""
    return traceback.format_exception(type(exception), exception, exception.__traceback__)


def getTrimmedStacktrace(exception):
    """Get a trimmed stack trace (last 12 entries) from an exception."""
    tb = traceback.extract_tb(exception.__traceback__)
    trimmed_tb = tb[-12:]  # Select the last 12 entries
    return traceback.format_list(trimmed_tb)


def getTrimmedStacktraceAsString(exception):
    """Get a trimmed stack trace as a single string."""
    return '\n'.join(getTrimmedStacktrace(exception))