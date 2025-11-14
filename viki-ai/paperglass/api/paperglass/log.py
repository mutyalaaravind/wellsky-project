import logging
import os
import json

import coloredlogs

from paperglass.settings import (
    DEBUG,
    CLOUD_PROVIDER,  # type: ignore
    LOGGING_USE_CUSTOM_LOGGER,
    LOGGING_INJECT_GLOBAL_CONTEXT_ENABLED,
    LOGGING_CHATTY_LOGGERS,
)
from paperglass.domain.context import Context
from paperglass.domain.util_json import DateTimeEncoder

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

# Use DEBUG level for our code
logging_level = logging.DEBUG if DEBUG else logging.INFO
logging.getLogger('paperglass').setLevel(logging_level)

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
    

class CustomLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def _format_message_with_extra(self, msg, args, kwargs):
        """
        Utility function to format log messages with extra data when running locally.
        Returns (formatted_message, should_use_formatted) tuple.
        """
        # Format extra data when running locally (regardless of structured logging availability)
        # or when structured logging is not available
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
                    # Try to convert datetime objects to strings before giving up
                    try:
                        contextData = json.loads(json.dumps(contextData, cls=DateTimeEncoder, default=str))
                    except Exception as e2:
                        print(f"Error converting extra to json (even with str conversion): {e2}")
                        # Keep the original data but convert problematic types to strings
                        contextData = {k: str(v) if hasattr(v, '__dict__') else v for k, v in contextData.items()}
                kwargs['extra'] = {"json_fields": contextData}
            
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


getLogger = logging.getLogger
if LOGGING_USE_CUSTOM_LOGGER:
    getLogger = CustomLogger
