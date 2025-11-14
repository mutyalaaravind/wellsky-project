import traceback 

def exceptionToMap(exception) -> dict:
    return {
        'message': str(exception),
        'type': exception.__class__.__name__,
        'details': getStacktraceList(exception)
    }

def getStacktrace(exception):
    tb = traceback.extract_tb(exception.__traceback__)
    return traceback.format_list(tb)

def getStacktraceList(exception):
    return traceback.format_exception(type(exception), exception, exception.__traceback__)

def getTrimmedStacktrace(exception):
    tb = traceback.extract_tb(exception.__traceback__)
    trimmed_tb = tb[-12:]  # Select the last 12 entries
    return traceback.format_list(trimmed_tb)

def getTrimmedStacktraceAsString(exception):
    return '\n'.join(getTrimmedStacktrace(exception))

class UnAuthorizedException(Exception):
    pass

class OrchestrationException(Exception):
    def __init__(self, message):
        self.message = message

class UnsupportedFileTypeException(Exception):
    def __init__(self, message):
        self.message = message

class WindowClosedException(Exception):
    def __init__(self, message):
        self.message = message
        
class OrchestrationExceptionWithContext(OrchestrationException):
    def __init__(self, message, context):
        self.context = context
        super(OrchestrationExceptionWithContext,self).__init__(message)
        
class JobException(Exception):
    def __init__(self, message):
        self.message = message
