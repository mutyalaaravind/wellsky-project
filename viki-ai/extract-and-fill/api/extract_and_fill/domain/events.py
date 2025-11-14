from typing import Optional
from pydantic import BaseModel

class Event(BaseModel):
    pass

class TranscriptUpdatedEvent(Event):
    transcript_id: str
    transcript_text: str
    autoscribe_transcript_id: str
    autoscribe_transcript_version: str