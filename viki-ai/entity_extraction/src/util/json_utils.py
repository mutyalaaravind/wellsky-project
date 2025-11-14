import json
import re
from datetime import datetime
from pydantic import BaseModel

from settings import JSON_CLEANERS

def convertToJson(serializedJson):
    serializedJson = serializedJson.strip()    
    if serializedJson.startswith("```json") and serializedJson.endswith("```"):
        cleanjson = serializedJson[7:]
        cleanjson = cleanjson[:-3]        
        return json.loads(cleanjson)
    else:
        return json.loads(serializedJson)


def safe_loads(jsonStr, index=-1):
    try:

        if jsonStr.startswith("```json") and jsonStr.endswith("```"):            
            cleanjson = jsonStr[7:]
            cleanjson = cleanjson[:-3]
            jsonStr = cleanjson

        if index < 0:
            return json.loads(jsonStr)
        elif index < len(JSON_CLEANERS):
            cleaner = JSON_CLEANERS[index]
            extra = {
                "index": index,
                "cleaner": cleaner,
                "jsonStr": jsonStr
            }
            clean_str = re.sub(cleaner.get("match"), cleaner.get("replace"), jsonStr)
            return json.loads(clean_str)
        else:
            return None
    except json.JSONDecodeError as e:
        index += 1
        extra = {
            "index": index,
            "jsonStr": jsonStr,
            "error": str(e)
        }
        return safe_loads(jsonStr, index)
    

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
                # Use the object's dict() method which may be overridden for custom behavior
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
        
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)
