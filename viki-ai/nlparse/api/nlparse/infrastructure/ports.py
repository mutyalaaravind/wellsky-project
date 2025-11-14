from abc import ABC, abstractmethod
from enum import Enum
from typing import AsyncIterator, List, Optional, Tuple

from nlparse.usecases.types import Entity, Mention, Relationship


class IHealthcareNLPPort(ABC):
    @abstractmethod
    async def extract(self, text: str) -> Tuple[List[Entity], List[Mention], List[Relationship]]:
        pass
