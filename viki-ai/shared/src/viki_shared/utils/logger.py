import contextvars
import json
import logging
from typing import List, Dict, Any, Optional
import uuid
import time
from functools import wraps

from .date_utils import now_utc
from .exceptions import exceptionToMap
from .json_utils import DateTimeEncoder
import coloredlogs

try:
    from google.cloud.logging_v2.handlers import StructuredLogHandler
    has_structured_logging = True
except ImportError:
    logging.warning('google-cloud-logging is not installed, structured logging will not be available')
    has_structured_logging = False


def get_settings_with_defaults():
    """Get settings with fallback defaults if not available."""
    try:
        from settings import DEBUG, CLOUD_PROVIDER, STAGE
        LOGGING_CHATTY_LOGGERS = getattr(__import__('settings'), 'LOGGING_CHATTY_LOGGERS', [])
        return DEBUG, CLOUD_PROVIDER, STAGE, LOGGING_CHATTY_LOGGERS
    except ImportError:
        # Default values if settings not available
        return True, 'local', 'development', []


# Get settings
DEBUG, CLOUD_PROVIDER, STAGE, LOGGING_CHATTY_LOGGERS = get_settings_with_defaults()

# Default to INFO level for everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s[%(process)d] [%(levelname)s] %(message)s',
    force=True,
)

# Install coloredlogs
coloredlogs.install(level='DEBUG')

# Suppress debug logging for urllib3.connectionpool
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

# Suppress debug and info logging for httpcore (chatty HTTP client logs)
logging.getLogger('httpcore').setLevel(logging.WARNING)

# Use DEBUG level for our code
logging_level = logging.DEBUG if DEBUG else logging.INFO

for logger_name in LOGGING_CHATTY_LOGGERS:
    logging.getLogger(logger_name).setLevel(logging_level)

if has_structured_logging and CLOUD_PROVIDER == 'google':
    # Use GCP log handler that formats messages into structured JSON logs
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(StructuredLogHandler())


def labels(**kwargs):
    """
    Convenience function to add labels to log entries.
    """
    return {
        'labels': kwargs,
    }


def command_to_extra(command):
    """Convert command object to extra dict for logging."""
    if not command:
        return {}
    
    if hasattr(command, 'dict'):
        return command.dict()
    elif hasattr(command, 'model_dump'):
        return command.model_dump()
    else:
        return {}


LOGGING_INJECT_GLOBAL_CONTEXT_ENABLED = True


class Context:
    """Global context manager for logging and tracing."""

    user = contextvars.ContextVar('user', default=None)
    baseAggregate = contextvars.ContextVar('baseAggregate', default=None)   
    trace = contextvars.ContextVar('trace', default=None)
    opentelemetry = contextvars.ContextVar('opentelementry', default=None)
    traceId = contextvars.ContextVar('traceId', default=None)
    tracer = contextvars.ContextVar('tracer', default=None)
    application_context = contextvars.ContextVar('application_context', default=None)

    def __init__(self):
        tid = str(uuid.uuid4())
        self.traceId.set(tid)

    async def getUser(self):
        return self.user.get()

    async def getUsername(self):
        return self.sync_getUsername()
        
    def sync_getUsername(self):
        if self.user is None:        
            return "unknown"
        elif self.user.get() is None:
            return "unknown"
        else:
            user_data = self.user.get()
            if isinstance(user_data, dict):
                return user_data.get("username", "unknown")
            return "unknown"

    async def setUser(self, user):
        self.user.set(user)

    def getBaseAggregate(self):
        return self.baseAggregate.get()
    
    async def setBaseAggregate(self, baseAggregate):
        self.baseAggregate.set(baseAggregate)

    def setBaseAggregate_sync(self, baseAggregate):
        self.baseAggregate.set(baseAggregate)

    def getLoggingContext(self):
        traceId = self.traceId.get()
        username = self.sync_getUsername()
        baseAggregate = self.getBaseAggregate() if self.baseAggregate is not None else {}
        app_context = self.get_application_context()

        loggingContext = {}
        if baseAggregate:
            loggingContext = baseAggregate.copy()
            
        # Add application context data
        if app_context:
            loggingContext.update(app_context)
            
        loggingContext["traceId"] = traceId
        loggingContext["username"] = username
        loggingContext["env"] = STAGE
        
        return loggingContext

    async def getTrace(self):
        return self.trace.get()

    async def setTrace(self, trace):
        self.trace.set(trace)

    async def getTraceId(self):
        return self.sync_getTraceId()

    def sync_getTraceId(self):
        if self.traceId is not None and self.traceId.get() is not None:            
            return self.traceId.get()
        else:
            return None

    async def setOpenTelemetry(self, opentelemetry_traceparent: str, 
                             openetelemetry_tracestate: str, opentelemetry_baggage: str):
        o = {
            "parenttrace": opentelemetry_traceparent,
            "tracestate": openetelemetry_tracestate,
            "baggage": opentelemetry_baggage
        }
        self.opentelemetry.set(o)

    async def getOpenTelemetry(self):
        return self.opentelemetry.get()

    def getTracer(self):
        return self.tracer.get()
    
    def setTracer(self, tracer):
        self.tracer.set(tracer)
    
    def update_trace_context(self):
        """Update trace context with OpenTelemetry trace information."""
        try:
            # This would need to be implemented based on specific tracing setup
            pass
        except Exception:
            # Don't fail if tracing update fails
            pass
    
    def set_application_context(self, **kwargs):
        """
        Set application context data that will be automatically injected into all log statements.
        
        Args:
            **kwargs: Context data (app_id, tenant_id, patient_id, document_id, etc.)
        """
        context_data = {k: v for k, v in kwargs.items() if v is not None}
        self.application_context.set(context_data)
    
    def get_application_context(self):
        """Get the current application context data."""
        return self.application_context.get() or {}
    
    def clear_application_context(self):
        """Clear the application context data."""
        self.application_context.set(None)

    def extractCommand(self, command):        
        """Extract context information from command object."""
        context_keys = [
            "app_id", "tenant_id", "patient_id", "user_id", "document_id",
            "document_operation_definition_id", "document_operation_instance_id",
            "page_number", "run_id", "job_id", "pipeline_scope", "pipeline_key",
            "task_id", "name", "pages"
        ]
        
        if not command:
            return {}            
        
        o = command_to_extra(command)
        
        context_obj = {}
        for key in context_keys:
            if key in o:
                context_obj[key] = o[key]   

        self.setBaseAggregate_sync(context_obj)
        return o


class CustomLogger:
    """Enhanced logger with structured logging and context injection."""
    
    # Class variable to track if we've already logged the structured logging warning
    _structured_logging_warning_logged = False
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _format_message_with_extra(self, msg: str, args: tuple, kwargs: dict):
        """
        Utility function to format log messages with extra data when running locally.
        Returns (formatted_message, should_use_formatted) tuple.
        """
        # Format extra data when running locally or when structured logging is not available
        if (CLOUD_PROVIDER == 'local' or not has_structured_logging) and 'extra' in kwargs and kwargs['extra']:
            try:
                # Extract the json_fields from the extra data
                extra_data = kwargs['extra'].get('json_fields', kwargs['extra'])
                if extra_data:
                    json_str = json.dumps(extra_data, indent=2, cls=DateTimeEncoder)
                    # Format the message with extra data
                    if args:
                        # If there are format args, format the message first
                        formatted_msg = msg % args
                        return f"{formatted_msg}\nExtra Data: {json_str}", True
                    else:
                        # No format args, just append to message
                        return f"{msg}\nExtra Data: {json_str}", True
            except Exception as e:
                # If JSON formatting fails, fall back to normal logging
                error = {"error": exceptionToMap(e)}
                print(f"Error formatting extra data for log: {e}")
                print(f"Error details: {json.dumps(error, indent=2)}")
        
        return msg, False

    def _wrap_extra(self, kwargs: dict) -> dict:
        """Wrap kwargs with context and structured logging support."""
        if has_structured_logging and "extra" in kwargs:
            baseContext = {}
            if LOGGING_INJECT_GLOBAL_CONTEXT_ENABLED:
                try:
                    baseContext = Context().getLoggingContext()
                except Exception as e:
                    # If the exception is logged, a blackhole will be created
                    print("Error getting logging context: %s", e)     
                
            contextData = kwargs['extra'] if 'extra' in kwargs else {}            

            if baseContext and contextData:
                contextData.update(baseContext)
            elif baseContext:
                contextData = baseContext
            elif not contextData:
                contextData = {
                    "global": "No global context data to inject"
                }
                
            if contextData:
                try:
                    contextData = json.loads(json.dumps(contextData, cls=DateTimeEncoder))
                except Exception as e:
                    print("Error converting extra to json: ", str(e), " ", contextData)
                    contextData = {}
                kwargs['extra'] = {"json_fields": contextData}

            if contextData and CLOUD_PROVIDER == 'local':
                self.logger.debug("Logging extra for next statement: %s", json.dumps(contextData, cls=DateTimeEncoder))
                
        elif "extra" not in kwargs:
            contextData = {}

            if LOGGING_INJECT_GLOBAL_CONTEXT_ENABLED:
                try:
                    contextData = Context().getLoggingContext()
                except Exception as e:
                    # If the exception is logged, a blackhole will be created
                    print("Error getting logging context for non extra: %s", e)     

            if contextData:
                try:
                    contextData = json.loads(json.dumps(contextData, cls=DateTimeEncoder))
                except Exception as e:
                    print("Error converting extra to json: %s", contextData)
                    contextData = {}
                kwargs['extra'] = {"json_fields": contextData}

        else:
            # Only log this warning once per class
            if not CustomLogger._structured_logging_warning_logged:
                self.logger.warning("Structured logging is not enabled")
                CustomLogger._structured_logging_warning_logged = True
        return kwargs

    def debug(self, msg: str, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.warning(msg, *args, **kwargs)
        
    def warn(self, msg: str, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        
        # Use utility function to format message with extra data for errors when structured logging is not available
        formatted_msg, use_formatted = self._format_message_with_extra(msg, args, kwargs)
        if use_formatted:
            self.logger.error(formatted_msg)
        else:
            self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        
        # Use utility function to format message with extra data for exceptions when structured logging is not available
        formatted_msg, use_formatted = self._format_message_with_extra(msg, args, kwargs)
        if use_formatted:
            self.logger.exception(formatted_msg)
        else:
            self.logger.exception(msg, *args, **kwargs)

    def addHandler(self, handler):
        self.logger.addHandler(handler)

    def removeHandler(self, handler):
        self.logger.removeHandler(handler)

    def setLevel(self, level):
        self.logger.setLevel(level)

    def getEffectiveLevel(self):
        return self.logger.getEffectiveLevel()

    def isEnabledFor(self, level):
        return self.logger.isEnabledFor(level)

    def addLabels(self, **kwargs):
        """Add custom labels to the log entry."""
        return labels(**kwargs)


# Main logger factory function
def getLogger(name: str) -> CustomLogger:
    """Get a CustomLogger instance for the given name."""
    return CustomLogger(name)


# Global context instance for convenience functions
_context_instance = Context()


def set_application_context(**kwargs):
    """
    Convenience function to set application context data that will be automatically injected into all log statements.
    
    Args:
        **kwargs: Context data (app_id, tenant_id, patient_id, document_id, etc.)
    """
    _context_instance.set_application_context(**kwargs)


def get_application_context() -> Dict[str, Any]:
    """Convenience function to get the current application context data."""
    return _context_instance.get_application_context()


def clear_application_context():
    """Convenience function to clear the application context data."""
    _context_instance.clear_application_context()


def log_elapsed_time(step_id: str, arg_types: Optional[List[type]] = None):
    """
    Decorator to log elapsed time for function execution.
    """
    if arg_types is None:
        arg_types = []
        
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = getLogger(__name__)
            start_time = now_utc()

            result = await func(*args, **kwargs)
            
            elapsed_time = now_utc() - start_time
            extra = {
                "elapsed_time": elapsed_time.total_seconds(),
                "function": func.__name__,
                "step_id": step_id,
            }
            
            if isinstance(result, List):
                extra["result_count"] = len(result)

            logger.info("Function %s completed in %s seconds", func.__name__, elapsed_time.total_seconds(), extra=extra)
            
            return result
        return wrapper
    return decorator