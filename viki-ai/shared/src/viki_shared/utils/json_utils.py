import json
import re
from datetime import datetime
from pydantic import BaseModel
from typing import Any, Dict, List, Union


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that converts datetime objects to ISO format strings."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


class JsonUtil:
    """Utility class for JSON operations with datetime support."""
    
    @classmethod
    def dumps(cls, obj: Any) -> str:
        """Serialize object to JSON string with datetime support."""
        return json.dumps(obj, cls=DateTimeEncoder)

    @classmethod
    def loads(cls, s: str) -> Any:
        """Deserialize JSON string to object."""
        return json.loads(s)
    
    @classmethod
    def clean(cls, obj: Any) -> Any:
        """
        Clean an object by converting datetime objects to ISO strings and removing non-serializable values.
        This ensures the object can be safely serialized to JSON.
        """
        if not obj:
            return obj
        
        def prune_non_serializable(o):
            if isinstance(o, dict):
                result = {}
                for k, v in o.items():
                    processed_v = prune_non_serializable(v)
                    if processed_v is not None:
                        result[k] = processed_v
                return result
            elif isinstance(o, list):
                return [prune_non_serializable(i) for i in o if prune_non_serializable(i) is not None]
            elif isinstance(o, BaseModel):
                # Use the model_dump() method for Pydantic v2 compatibility
                try:
                    return prune_non_serializable(o.model_dump())
                except AttributeError:
                    # Fallback to dict() for older Pydantic versions
                    return prune_non_serializable(o.dict())
            elif cls.is_serializable(o):
                return o
            else:
                return None

        pruned = prune_non_serializable(obj)
        return json.loads(json.dumps(pruned, cls=DateTimeEncoder))
    
    @staticmethod
    def is_serializable(value: Any) -> bool:
        """Check if a value can be serialized to JSON."""
        try:
            json.dumps(value, cls=DateTimeEncoder)
            return True
        except (TypeError, ValueError):
            return False


def convertToJson(serializedJson: str) -> Any:
    """
    Convert serialized JSON string to object, handling code block formatting.
    """
    serializedJson = serializedJson.strip()    
    if serializedJson.startswith("```json") and serializedJson.endswith("```"):
        cleanjson = serializedJson[7:]
        cleanjson = cleanjson[:-3]        
        return json.loads(cleanjson)
    else:
        return json.loads(serializedJson)


def safe_loads(jsonStr: str, index: int = -1, cleaners: List[Dict[str, str]] = None) -> Any:
    """
    Safely load JSON string with fallback cleaning strategies.
    
    Args:
        jsonStr: JSON string to parse
        index: Index of cleaner to try (-1 for raw parsing)
        cleaners: List of regex cleaning patterns
    """
    if cleaners is None:
        cleaners = []
        
    try:
        if jsonStr.startswith("```json") and jsonStr.endswith("```"):            
            cleanjson = jsonStr[7:]
            cleanjson = cleanjson[:-3]
            jsonStr = cleanjson

        if index < 0:
            return json.loads(jsonStr)
        elif index < len(cleaners):
            cleaner = cleaners[index]
            clean_str = re.sub(cleaner.get("match", ""), cleaner.get("replace", ""), jsonStr)
            return json.loads(clean_str)
        else:
            return None
    except json.JSONDecodeError:
        index += 1
        return safe_loads(jsonStr, index, cleaners)