import logging
import json
from typing import Any, Dict
from .json_utils import DateTimeEncoder


class CustomLogger:
    """
    Custom logger for cloudtask-emulator with structured logging support.
    Simplified version based on paperglass CustomLogger.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _format_message_with_extra(self, msg: str, args: tuple, kwargs: Dict[str, Any]) -> tuple[str, bool]:
        """
        Format log messages with extra data for better readability.
        Returns (formatted_message, should_use_formatted) tuple.
        """
        if 'extra' in kwargs and kwargs['extra']:
            try:
                extra_data = kwargs['extra']
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

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        formatted_msg, use_formatted = self._format_message_with_extra(msg, args, kwargs)
        if use_formatted:
            self.logger.info(formatted_msg)
        else:
            self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        formatted_msg, use_formatted = self._format_message_with_extra(msg, args, kwargs)
        if use_formatted:
            self.logger.warning(formatted_msg)
        else:
            self.logger.warning(msg, *args, **kwargs)
        
    def warn(self, msg: str, *args, **kwargs):
        self.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        formatted_msg, use_formatted = self._format_message_with_extra(msg, args, kwargs)
        if use_formatted:
            self.logger.error(formatted_msg)
        else:
            self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        formatted_msg, use_formatted = self._format_message_with_extra(msg, args, kwargs)
        if use_formatted:
            self.logger.critical(formatted_msg)
        else:
            self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
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
