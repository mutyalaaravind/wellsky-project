import logging
import os
import json

import coloredlogs

from main.settings import DEBUG

try:
    from google.cloud.logging_v2.handlers import StructuredLogHandler

    has_structured_logging = True
except ImportError:
    logging.error('google-cloud-logging is not installed, structured logging will not be available')
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
logging.getLogger('main').setLevel(logging_level)

# Make some modules less verbose
for name in ('urllib3', 'google', 'chromadb', 'grpc', 'clickhouse_connect', 'shapely', 'gcloud'):
    logging.getLogger(name).setLevel(logging.ERROR)

if has_structured_logging and os.getenv('CLOUD_PROVIDER') == 'google':
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

    def _wrap_extra(self, kwargs):        
        if has_structured_logging and "extra" in kwargs:
            baseContext = {}
                
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
                    contextData = json.loads(json.dumps(contextData, default=str))
                except Exception as e:
                    # Try to convert datetime objects to strings before giving up
                    try:
                        contextData = json.loads(json.dumps(contextData, default=str))
                    except Exception as e2:
                        print(f"Error converting extra to json (even with str conversion): {e2}")
                        # Keep the original data but convert problematic types to strings
                        contextData = {k: str(v) if hasattr(v, '__dict__') else v for k, v in contextData.items()}
                kwargs['extra'] = {"json_fields": contextData}

            if contextData and os.getenv('CLOUD_PROVIDER') == 'local':
                self.logger.debug("Logging extra: %s", json.dumps(contextData, default=str))
        elif "extra" not in kwargs:
            #self.logger.debug("Not converting to jsonPayload because no extra dict provided") 
            contextData = {}

            if contextData:
                try:
                    contextData = json.loads(json.dumps(contextData, default=str))
                except Exception as e:
                    print("Error converting extra to json: %s", contextData)
                    contextData = {}
                kwargs['extra'] = {"json_fields": contextData}

            if contextData and os.getenv('CLOUD_PROVIDER') == 'local':
                self.logger.debug("Logging extra: %s", json.dumps(contextData, default=str))

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


getLogger = logging.getLogger
# Always use custom logger for demo
getLogger = CustomLogger
