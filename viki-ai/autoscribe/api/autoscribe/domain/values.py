from typing import List, Optional
from pydantic import BaseModel, Field

from autoscribe.usecases.types import Sentence, TextSentence


class Section(BaseModel, frozen=True):
    backend: Optional[str]
    sentences: List[Sentence] = Field(default_factory=list)
    text_sentences: List[TextSentence] = Field(default_factory=list)

    is_finalized: bool = False
    version: int = 0
