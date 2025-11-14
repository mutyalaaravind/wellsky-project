import json
from datetime import datetime
from pydantic import BaseModel

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
    
class JsonUtil():
    @classmethod
    def dumps(cls, obj):
        return json.dumps(obj, cls=DateTimeEncoder)

    @classmethod
    def loads(cls, s):
        return json.loads(s)
    
    @classmethod
    def clean(cls, obj):
        if not obj:
            return obj
        
        def prune_non_serializable(o):
            if isinstance(o, dict):
                return {k: prune_non_serializable(v) for k, v in o.items() if cls.is_serializable(v)}
            elif isinstance(o, list):
                return [prune_non_serializable(i) for i in o if cls.is_serializable(i)]
            elif isinstance(o, BaseModel):
                return prune_non_serializable(o.dict())
            return o

        pruned = prune_non_serializable(obj)
        return json.loads(json.dumps(pruned, cls=DateTimeEncoder))
    
    @staticmethod
    def is_serializable(value):
        try:
            json.dumps(value, cls=DateTimeEncoder)
            return True
        except (TypeError, ValueError):
            return False        
