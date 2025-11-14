from abc import ABC, abstractproperty
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FormField:
    name: str
    question: str


@dataclass
class FormValue:
    name: str
    value: str


@dataclass
class CompleteFormResult:
    error: Optional[str]
    form_values: List[FormValue]
