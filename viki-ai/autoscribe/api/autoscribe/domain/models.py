from typing import Dict, List
from datetime import datetime
from random import choice
import string

from pydantic import BaseModel, Field
from autoscribe.domain.time import now_utc
from autoscribe.domain.types import UTCDatetime
from autoscribe.domain.values import Section
from autoscribe.usecases.types import Sentence, TextSentence


class TransactionError(Exception):
    pass


class Transaction(BaseModel):
    id: str
    created: UTCDatetime = Field(default_factory=now_utc)
    sections: Dict[str, Section] = Field(default_factory=dict)
    last_updated_section: str = Field(default='')

    @classmethod
    def create(cls, id: str):
        return cls(id=id)

    def update_section(self, section_id: str, sentences: List[Sentence], text_sentences: List[TextSentence]):
        try:
            section = self.sections[section_id]
        except KeyError:
            section = Section()

        self.sections[section_id] = section.copy(update={'sentences': sentences, 'text_sentences': text_sentences})
        self.last_updated_section = section_id

    def set_section_backend(self, section_id: str, backend: str):
        if section_id not in self.sections:
            raise TransactionError(f'Section {section_id} not found')
        self.sections[section_id] = self.sections[section_id].copy(update={'backend': backend})
        self.last_updated_section = section_id

    def finalize_section(self, section_id: str, text_sentences: List[TextSentence]):
        if section_id not in self.sections:
            raise TransactionError(f'Section {section_id} not found')
        self.last_updated_section = section_id
        self.sections[section_id] = self.sections[section_id].copy(
            update={
                'text_sentences': text_sentences,
                'is_finalized': True,
                'version': self.sections[section_id].version + 1,
            }
        )
