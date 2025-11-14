from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from util.date_utils import now_utc
from util.uuid_utils import generate_id


class AggBase(BaseModel):
    """
    Base class for aggregation models.
    """
    
    id: str = Field(default_factory=lambda: str(generate_id()))
    created_at: datetime = Field(default_factory=now_utc)
    modified_at: datetime = Field(default_factory=now_utc)
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    active: Optional[bool] = True
