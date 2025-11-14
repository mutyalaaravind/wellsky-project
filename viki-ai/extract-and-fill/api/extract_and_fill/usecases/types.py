from dataclasses import dataclass, field
from typing import List


@dataclass
class Sentence:
    speaker_tag: int
    words: List[str] = field(default_factory=list)


class StreamEvent:
    @property
    def type(self) -> str:
        raise NotImplementedError()


@dataclass
class RecognitionEvent(StreamEvent):
    is_final: bool
    transcript: str
    type: str = 'recognition'


@dataclass
class DiarizationEvent(StreamEvent):
    sentences: list[Sentence]
    type: str = 'diarization'
