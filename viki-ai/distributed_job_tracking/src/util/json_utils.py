import json
from datetime import datetime
from pydantic import BaseModel


class JsonUtil():
    @classmethod
    def dumps(cls, obj):
        return json.dumps(obj, cls=DateTimeEncoder)

    @classmethod
    def loads(cls, s):
        return json.loads(s)
    
    @classmethod
    def clean(cls, obj):
        """
        Clean an object by converting datetime objects to ISO strings and removing non-serializable values.
        This ensures the object can be safely serialized to JSON.
        """
        if not obj:
            return obj
        
        def prune_non_serializable(o):
            if isinstance(o, dict):
                return {k: prune_non_serializable(v) for k, v in o.items() if cls.is_serializable(v)}
            elif isinstance(o, list):
                return [prune_non_serializable(i) for i in o if cls.is_serializable(i)]
            elif isinstance(o, BaseModel):
                # Use the object's model_dump() method for Pydantic v2 compatibility
                try:
                    return prune_non_serializable(o.model_dump())
                except AttributeError:
                    # Fallback to dict() for older Pydantic versions
                    return prune_non_serializable(o.dict())
            return o

        pruned = prune_non_serializable(obj)
        return json.loads(json.dumps(pruned, cls=DateTimeEncoder))
    
    @staticmethod
    def is_serializable(value):
        """Check if a value can be serialized to JSON."""
        try:
            json.dumps(value, cls=DateTimeEncoder)
            return True
        except (TypeError, ValueError):
            return False
        

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that converts datetime objects to ISO format strings."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
