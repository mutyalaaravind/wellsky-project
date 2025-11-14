import contextvars
import json
import logging
from typing import List
import uuid
import time
from functools import wraps

from util.date_utils import now_utc
import coloredlogs

try:
    from google.cloud.logging_v2.handlers import StructuredLogHandler
    has_structured_logging = True
except ImportError:
    logging.warning('google-cloud-logging is not installed, structured logging will not be available')
    has_structured_logging = False

# Import settings - will need to be adapted based on distributed_job_tracking's settings
try:
    from settings import DEBUG, CLOUD_PROVIDER, STAGE
    LOGGING_CHATTY_LOGGERS = getattr(__import__('settings'), 'LOGGING_CHATTY_LOGGERS', [])
except ImportError:
    # Default values if settings not available
    DEBUG = True
    CLOUD_PROVIDER = 'local'
    STAGE = 'development'
    LOGGING_CHATTY_LOGGERS = []

# Simple DateTimeEncoder for JSON serialization
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

# Default to INFO level for everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s[%(process)d] [%(levelname)s] %(message)s',
    # https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
    # Let's kindly ask AWS (and other systems that want to poke their nose everywhere) to go screw themselves:
    force=True,
)

# Install coloredlogs
coloredlogs.install(level='DEBUG')

# Suppress debug logging for urllib3.connectionpool
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

# Use DEBUG level for our code
logging_level = logging.DEBUG if DEBUG else logging.INFO
logging.getLogger('distributed_job_tracking').setLevel(logging_level)

for logger_name in LOGGING_CHATTY_LOGGERS:
    logging.getLogger(logger_name).setLevel(logging_level)

if has_structured_logging and CLOUD_PROVIDER == 'google':
    # Use GCP log handler that formats messages into structured JSON logs
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(StructuredLogHandler())


def labels(**kwargs):
    """
    Convenience function to labels to log entries.

    >>> from collections import namedtuple
    >>> stuff = namedtuple('Stuff', 'id')(id=42)
    >>> getLogger(__name__).info('Got stuff, id = %s', stuff.id, extra=labels(stuff_id=stuff.id))
    """
    return {
        'labels': kwargs,
    }

def command_to_extra(command):
    
    if not command:
        return {}
    
    return command.dict()    


LOGGING_INJECT_GLOBAL_CONTEXT_ENABLED = True

class Context:

    user = contextvars.ContextVar('user', default=None)
    baseAggregate = contextvars.ContextVar('baseAggregate', default=None)   
    trace = contextvars.ContextVar('trace', default=None)
    opentelemetry = contextvars.ContextVar('opentelementry', default=None)
    traceId = contextvars.ContextVar('traceId', default=None)
    tracer = contextvars.ContextVar('tracer', default=None)
    job_context = contextvars.ContextVar('job_context', default=None)

    def __init__(self):
        tid = str(uuid.uuid4())
        self.traceId.set(tid)
        pass

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
            return self.user.get()["username"]

   
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
        job_context = self.get_job_context()

        loggingContext = {}
        if baseAggregate:
            loggingContext = baseAggregate.copy()
            
        # Add job context data
        if job_context:
            loggingContext.update(job_context)
            
        loggingContext["traceId"] = traceId
        loggingContext["username"] = username
        loggingContext["env"] = STAGE
        
        return loggingContext


    async def getTrace(self):
        return self.trace.get()


    async def setTrace(self, trace):
        self.trace.set(trace)


    async def getTraceId(self):
        return self.async_getTraceId()


    def sync_getTraceId(self):
        if self.traceId is not None and self.traceId.get() is not None:            
            return self.traceId.get()
        else:
            return None


    async def setOpenTelemetry(self, opentelemetry_traceparent: str, openetelemetry_tracestate: str, opentelemetry_baggage: str):
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
    
    def set_job_context(self, run_id=None, job_id=None, job_type=None, 
                       status=None, queue_name=None, worker_id=None,
                       task_id=None, **kwargs):
        """
        Set job context data that will be automatically injected into all log statements.
        
        Args:
            run_id: Job run ID
            job_id: Job ID
            job_type: Type of job
            status: Current job status
            queue_name: Queue name
            worker_id: Worker ID processing the job
            task_id: Current task ID
            **kwargs: Additional context data
        """
        context_data = {}
        
        # Add all non-None values to context
        if run_id is not None:
            context_data["run_id"] = run_id
        if job_id is not None:
            context_data["job_id"] = job_id
        if job_type is not None:
            context_data["job_type"] = job_type
        if status is not None:
            context_data["status"] = status
        if queue_name is not None:
            context_data["queue_name"] = queue_name
        if worker_id is not None:
            context_data["worker_id"] = worker_id
        if task_id is not None:
            context_data["task_id"] = task_id
            
        # Add any additional context data
        context_data.update(kwargs)
        
        self.job_context.set(context_data)
    
    def get_job_context(self):
        """Get the current job context data."""
        return self.job_context.get() or {}
    
    def clear_job_context(self):
        """Clear the job context data."""
        self.job_context.set(None)

    def extractCommand(self, command):        
        context_keys = [
            "run_id",
            "app_id",
            "tenant_id", 
            "patient_id",
            "document_id",
            "name",
            "pages",
        ]
        
        if not command:
            return {}            
        
        o = command.dict()
        
        context_obj = {}
        for key in context_keys:
            if key in o:
                context_obj[key] = o[key]   

        self.setBaseAggregate_sync(context_obj)
        return o

class CustomLogger:
    # Class variable to track if we've already logged the structured logging warning
    _structured_logging_warning_logged = False
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def _wrap_extra(self, kwargs):        
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
            #self.logger.debug("Not converting to jsonPayload because no extra dict provided") 
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

            if contextData and CLOUD_PROVIDER == 'local':
                # self.logger.debug("Logging extra for next statement: %s", json.dumps(contextData, cls=DateTimeEncoder))
                pass

        else:
            # Only log this warning once per class
            if not CustomLogger._structured_logging_warning_logged:
                self.logger.warning("Structured logging is not enabled")
                CustomLogger._structured_logging_warning_logged = True
        return kwargs

    def debug(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.warning(msg, *args, **kwargs)
        
    def warn(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        
        # If structured logging is not available, append extra data as JSON to error messages
        if not has_structured_logging and 'extra' in kwargs and kwargs['extra']:
            try:
                # Extract the json_fields from the extra data
                extra_data = kwargs['extra'].get('json_fields', kwargs['extra'])
                if extra_data:
                    json_str = json.dumps(extra_data, indent=2, cls=DateTimeEncoder)
                    # Append JSON to the message
                    if args:
                        # If there are format args, format the message first
                        formatted_msg = msg % args
                        self.logger.error(f"{formatted_msg}\nExtra Data: {json_str}")
                        return
                    else:
                        # No format args, just append to message
                        self.logger.error(f"{msg}\nExtra Data: {json_str}")
                        return
            except Exception as e:
                # If JSON formatting fails, fall back to normal logging
                print(f"Error formatting extra data for error log: {e}")
        
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
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
        """
        Add custom labels to the log entry.
        """
        return labels(**kwargs)


getLogger = CustomLogger

# Global context instance for convenience functions
_context_instance = Context()

def set_job_context(run_id=None, job_id=None, job_type=None, 
                   status=None, queue_name=None, worker_id=None,
                   task_id=None, **kwargs):
    """
    Convenience function to set job context data that will be automatically injected into all log statements.
    
    Args:
        run_id: Job run ID
        job_id: Job ID
        job_type: Type of job
        status: Current job status
        queue_name: Queue name
        worker_id: Worker ID processing the job
        task_id: Current task ID
        **kwargs: Additional context data
    """
    _context_instance.set_job_context(
        run_id=run_id,
        job_id=job_id,
        job_type=job_type,
        status=status,
        queue_name=queue_name,
        worker_id=worker_id,
        task_id=task_id,
        **kwargs
    )

def get_job_context():
    """Convenience function to get the current job context data."""
    return _context_instance.get_job_context()

def clear_job_context():
    """Convenience function to clear the job context data."""
    _context_instance.clear_job_context()

# Simplified log_elapsed_time decorator for distributed job tracking
def log_elapsed_time(step_id: str, arg_types: List[type] = None):
    """
    Decorator to log elapsed time for function execution.
    Simplified version for distributed_job_tracking.
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
