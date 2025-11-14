from abc import ABC, abstractmethod
from typing import Optional, AsyncIterable


class IQNAPort(ABC):
    class IQNAModel(ABC):
        @abstractmethod
        async def query(self, question: str) -> str:
            pass

    @abstractmethod
    async def build_model(self, text: str) -> IQNAModel:
        pass
    
class ExtractPort(ABC):
    
    @abstractmethod
    async def get_medical_record(self, statement: str) -> str:
        pass
    
    @abstractmethod
    async def get_health_info(self, statement: str, question: str) -> str:
        pass