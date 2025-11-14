from typing import Optional, List, Dict
from datetime import datetime
import base64
import json
from jsonpath_ng import parse # type: ignore

from pydantic import BaseModel, Field

class GenericMessage():
    message: str
    details: str

    def __init__(self, message, details=None):
        self.message = message
        self.details = details

    def to_dict(self):
        return {
            "message": self.message,
            "details": self.details
        }


class Code(BaseModel):
    code: str
    value: str
    description: Optional[str] = None

    @classmethod
    def create(cls, codekey, value, description=None):
        return cls(code=codekey, value=value, description=description)

class ReferenceCodes(BaseModel):
    id: str
    category: str
    list: str
    codes: List[Code]
    cached_on: Optional[datetime] = None
    events: List = Field(default_factory=list)

    @classmethod
    def create(cls, category, list, codes):
        return cls(id=category + ":" + list, category=category, list=list, codes=codes)


class MessageContainer(BaseModel):
    version: str
    message_type: str    
    metadata: Optional[Dict] = None
    data: Optional[Dict] = None

class PubSubMessage(BaseModel):
    data: str
    messageId: str
    message_id: str
    publishTime: str
    publish_time: str    

class PubSubEnvelope(BaseModel):
    message: PubSubMessage
    subscription: str

    def get_data(self):
        decoded_data = base64.b64decode(self.message.data)
        data_str = decoded_data.decode("utf-8")
        data = json.loads(data_str)
        return data

class EntityFilterCriterion(BaseModel):
        entity_name: str
        values: List[str]

        def create(self, entity_name, values):
            return EntityFilterCriterion(entity_name=entity_name, values=values)

class EntityFilter(BaseModel):
    filterCriterion: List[EntityFilterCriterion]    

    def append(self, entity_name, values):
        self.filterCriterion.append(EntityFilterCriterion.create(entity_name, values))

    def filter(self, entities: List[Dict]):
        filtered_entities = []
        for entity in entities:
            original_entity = entity
            if isinstance(entity, BaseModel):
                entity = entity.dict()
            elif not isinstance(entity, dict):
                raise Exception("Entity must be a dict or a Pydantic BaseModel")
            
            criteria_met = []
            for criterion in self.filterCriterion:
                
                attribute_path = criterion.entity_name
                if not attribute_path.startswith("$"):
                    attribute_path = "$." + attribute_path

                jsonpath_expr = parse(attribute_path)                
                if jsonpath_expr.find(entity):                    
                    if any(match.value in criterion.values for match in jsonpath_expr.find(entity)):                        
                        criteria_met.append(True)
                    else:                        
                        criteria_met.append(False)
            
            if all(criteria_met):
                filtered_entities.append(original_entity)

        return filtered_entities

class NotFoundException(Exception):
    def __init__(self, message):
        self.message = message

class OrchestrationException(Exception):
    def __init__(self, message):
        self.message = message

class UnsupportedFileTypeException(Exception):
    def __init__(self, message):
        self.message = message

class WindowClosedException(Exception):
    def __init__(self, message):
        self.message = message

class TimeoutException(Exception):
    def __init__(self, message):
        self.message = message
        
class OrchestrationExceptionWithContext(OrchestrationException):
    def __init__(self, message, context):
        self.context = context
        super(OrchestrationExceptionWithContext,self).__init__(message)

class InvalidStateException(Exception):
    def __init__(self, message):
        self.message = message
    