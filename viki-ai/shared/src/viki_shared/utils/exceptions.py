import traceback 
from typing import Dict, List


def exceptionToMap(exception: Exception) -> Dict[str, any]:
    """Convert exception to dictionary representation."""
    return {
        'message': str(exception),
        'type': exception.__class__.__name__,
        'details': getStacktraceList(exception)
    }


def getStacktrace(exception: Exception) -> List[str]:
    """Get formatted stacktrace from exception."""
    tb = traceback.extract_tb(exception.__traceback__)
    return traceback.format_list(tb)


def getStacktraceList(exception: Exception) -> List[str]:
    """Get complete formatted exception traceback."""
    return traceback.format_exception(type(exception), exception, exception.__traceback__)


def getTrimmedStacktrace(exception: Exception) -> List[str]:
    """Get trimmed stacktrace (last 12 entries)."""
    tb = traceback.extract_tb(exception.__traceback__)
    trimmed_tb = tb[-12:]  # Select the last 12 entries
    return traceback.format_list(trimmed_tb)


def getTrimmedStacktraceAsString(exception: Exception) -> str:
    """Get trimmed stacktrace as single string."""
    return '\n'.join(getTrimmedStacktrace(exception))


# Common exception classes
class UnAuthorizedException(Exception):
    """Raised when authentication fails."""
    pass


class OrchestrationException(Exception):
    """Base exception for orchestration errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedFileTypeException(Exception):
    """Raised when file type is not supported."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class WindowClosedException(Exception):
    """Raised when operation window is closed."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class OrchestrationExceptionWithContext(OrchestrationException):
    """Orchestration exception with additional context."""
    
    def __init__(self, message: str, context: Dict):
        self.context = context
        super().__init__(message)


class JobException(Exception):
    """Raised when job processing fails."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)