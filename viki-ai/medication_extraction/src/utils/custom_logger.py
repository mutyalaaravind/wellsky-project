import contextvars
import json
import logging
from typing import List
import uuid
import time
from functools import wraps

from utils.date import now_utc
from utils.json import DateTimeEncoder

from settings import DEBUG, CLOUD_PROVIDER, STAGE, LOGGING_CHATTY_LOGGERS

import coloredlogs
# import os
# import json

# import coloredlogs

# from paperglass.settings import (
#     CLOUD_PROVIDER,  # type: ignore
# )
# from context import Context
# from util_json import DateTimeEncoder

try:
    from google.cloud.logging_v2.handlers import StructuredLogHandler

    has_structured_logging = True
except ImportError:
    logging.warning('google-cloud-logging is not installed, structured logging will not be available')
    has_structured_logging = False

# Default to INFO level for everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s[%(process)d] [%(levelname)s] %(message)s',
    # https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
    # Let's kindly ask AWS (and other systems that want to poke their nose everywhere) to go screw themselves:
    force=True,
)
coloredlogs.install(level='DEBUG')

# Suppress debug logging for urllib3.connectionpool
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

# Use DEBUG level for our code
logging_level = logging.DEBUG if DEBUG else logging.INFO
logging.getLogger('medication_extraction').setLevel(logging_level)

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
            return "unkwown"
        elif self.user.get() is None:
            return "unkwown"
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

        loggingContext = {}
        if baseAggregate:
            loggingContext = baseAggregate.copy()
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

    def extractCommand(self, command):        
        context_keys = [
            "app_id",
            "tenant_id",
            "patient_id",
            "user_id",
            "document_id",
            "document_operation_definition_id",
            "document_operation_instance_id",
            "page_number",
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
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def _format_message_with_extra(self, msg, args, kwargs):
        """
        Utility function to format log messages with extra data when structured logging is not available.
        Returns (formatted_message, should_use_formatted) tuple.
        """
        if not has_structured_logging and 'extra' in kwargs and kwargs['extra']:
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
                print(f"Error formatting extra data for log: {e}")
        
        return msg, False

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
                # Don't log extra data for non-extra cases to reduce chattiness
                pass

        else:
            pass
            #self.logger.debug("Structured logging is not enabled")
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
        
        # Use utility function to format message with extra data for errors when structured logging is not available
        formatted_msg, use_formatted = self._format_message_with_extra(msg, args, kwargs)
        if use_formatted:
            self.logger.error(formatted_msg)
        else:
            self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs = self._wrap_extra(kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
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
        """
        Add custom labels to the log entry.
        """
        return labels(**kwargs)


getLogger = CustomLogger #logging.getLogger
# if LOGGING_USE_CUSTOM_LOGGER:
#     getLogger = CustomLogger

from models import DocumentOperationStep

def log_elapsed_time(step_id:DocumentOperationStep|str, arg_types:List[type]):
    from typing import List
    from datetime import datetime
    from pydantic import BaseModel
    from utils.json import JsonUtil
    from utils.exception import exceptionToMap
    from model_metric import Metric

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = getLogger(__name__)
            start_time = now_utc()

            result = await func(*args, **kwargs)
            
            elapsed_time = now_utc() - start_time
            extra = {
                "elapsed_time": elapsed_time.total_seconds(),                
            }
            if isinstance(result, List):
                extra["result_count"] = len(result)            

            auto_parameters = {
                "keys": list(kwargs.keys()),
                "primitive": {},
                "null": {},
                "BaseModel": {},
                "ignored": {},
                "exceptions": {}
            }

            arguments = {}

            for key, arg in kwargs.items():    
                arguments[key] = arg

            for i, arg in enumerate(args):
                key = type(arg).__name__.lower()
                if key in arguments:
                    key = f"{key}_{i}"
                arguments[key] = arg

            for key, arg in arguments.items():
                # All primitive type kwargs will be logged
                if isinstance(arg, (str, int, float, bool)):
                    extra[key] = arg
                    auto_parameters["primitive"][key] = arg
                elif arg is None:
                    extra[key] = arg
                    auto_parameters["null"][key] = arg
                elif type(arg) in arg_types:
                    try:
                        o = arg
                        if isinstance(arg, BaseModel):
                            logger.debug("Converting BaseModel to dict for metric: %s", key)
                            o = arg.model_dump()
                            auto_parameters["BaseModel"][key] = o
                            auto_parameters["BaseModel"][key + "_clean"] = JsonUtil.clean(o)
                        else:
                            logger.debug("Converting type(%s) to dict for metric: %s", type(arg), key)
                            auto_parameters["BaseModel"][key] = o
                            auto_parameters["BaseModel"][key + "_clean"] = JsonUtil.clean(o)

                        extra[key] = JsonUtil.clean(o)

                    except Exception as e:
                        extra2 = {
                            "error": exceptionToMap(e),
                            "object": str(arg)
                        }
                        extra2.update(extra)
                        logger.error("Exception converting object to clean json for metric", extra=extra2)

                        auto_parameters["exceptions"][key] = exceptionToMap(e)
                else:
                    logger.info("Ignoring non-primitive type key '%s': %s", key, arg)
                    auto_parameters["ignored"][key] = str(arg)
                        
                if key == "wait_time_start" and arg:
                    try:
                        wait_time_start_s = arg
                        wait_time_start = datetime.fromisoformat(wait_time_start_s)
                        extra["wait_time"] = (start_time - wait_time_start).total_seconds()
                    except Exception as e:
                        extra2 = {
                            "error": exceptionToMap(e),
                            "object": str(arg)
                        }
                        extra2.update(extra)
                        logger.error("Error calculating wait time for metric", extra=extra2)

            logger.debug("auto_parameters: %s", auto_parameters, extra=auto_parameters)

            step_name = step_id
            if isinstance(step_id, DocumentOperationStep):
                step_name = "STEP." + step_id.value
                extra.update({"step_id": step_id.value})

            extra.update({
                "function": func.__name__,
            })

            metric_type = Metric.MetricType.MEDICATIONEXTRACTION_STEP_PREFIX + step_name
            Metric.send(metric_type, tags=extra)                
            
            return result
        return wrapper
    return decorator
