from typing import List
from autoscribe.domain.time import now_utc
from autoscribe.domain.types import UTCDatetime

from pydantic import BaseModel, Field


class Word(BaseModel):
    text: str
    start: float
    end: float


class Sentence(BaseModel):
    speaker_tag: int
    words: List[Word] = Field(default_factory=list)

    def as_text(self):
        speaker_abbrev = '?' if self.speaker_tag == 0 else chr(ord('A') + self.speaker_tag - 1)
        if len(self.words):
            start_timestamp = f'{int(self.words[0].start // 60):02}:{int(self.words[0].start % 60):02}'
        else:
            start_timestamp = '--:--'
        return f'{speaker_abbrev} [{start_timestamp}]: {" ".join(word.text for word in self.words)}'

    def get_start(self):
        return self.words[0].start if len(self.words) else 0

    def get_text(self):
        return " ".join(word.text for word in self.words)


class TextSentence(BaseModel):
    speaker_tag: int
    start: float
    text: str
    is_final: bool = False


class StreamEvent(BaseModel):
    type: str = 'unknown'


class StartEvent(StreamEvent):
    type: str = 'start'
    transaction_id: str


class ErrorEvent(StreamEvent):
    message: str
    type: str = 'error'


class RecognitionEvent(StreamEvent):
    transcript: str
    type: str = 'recognition'


class DiarizationEvent(StreamEvent):
    sentences: list[Sentence]
    type: str = 'diarization'
