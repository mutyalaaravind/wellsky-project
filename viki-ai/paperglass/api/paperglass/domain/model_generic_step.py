from uuid import uuid1
from datetime import datetime
from typing import Dict, List, Literal, Optional, Union, Any

from pydantic import BaseModel, Extra, Field

from .models import Aggregate, OperationMeta
from .time import now_utc

class OperationMetrics(BaseModel):
    start_time: datetime
    end_time: datetime
    elapsed_time: float

class GenericPromptStep(Aggregate):
    id: str = Field(default_factory=lambda: str(uuid1().hex))    
    operation: OperationMeta
    parameters: Dict[str, str]
    status: str
    response: Optional[Any] = None
    metrics: Optional[OperationMetrics] = None    
    errors: Optional[Any] = None

    @classmethod
    def create(cls, app_id:str, 
               tenant_id:str, 
               patient_id:str, 
               operation: OperationMeta,
               parameters: Dict[str, str],
               status: str,
               response: Optional[Any] = None,
               metrics: Optional[OperationMetrics] = None,
               errors: Optional[Any] = None
               ) -> 'DocumentFilterState':
        id = uuid1().hex
        return cls(id=id, 
                app_id=app_id, 
                tenant_id=tenant_id, 
                patient_id=patient_id, 
                operation=operation,
                parameters=parameters,
                status=status,
                response=response,
                metrics=metrics,
                errors=errors
                )

   
