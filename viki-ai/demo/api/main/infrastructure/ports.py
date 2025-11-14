from abc import ABC, abstractmethod

from main.domain.models import Patient


class IFormRepositoryPort(ABC):
    @abstractmethod
    async def get_form_instance(self, id: str) -> dict:
        pass

    @abstractmethod
    async def save_form_instance(self, id: str, data: dict):
        pass

class IPatientRepositoryPort(ABC):

    @abstractmethod
    async def get_all_patients(self):
        pass

    @abstractmethod
    async def get_patient_by_id(self,  patient_id:str):
        pass

    @abstractmethod
    async def create_patient(self, patient:Patient):
        pass

class IMedicationRepositoryPort(ABC):

    @abstractmethod
    async def get_meds(self, tenant_id:str, patient_id:str):
        pass

    @abstractmethod
    async def save_med(self, tenant_id:dict, patient_id:str, data:dict):
        pass

class IAttachmentsRepositoryPort(ABC):

    @abstractmethod
    async def get_attach(self, tenant_id:str, patient_id:str):
        pass


class IEntityRepositoryPort(ABC):

    @abstractmethod
    async def save_entities(self, entity_id: str, entities_data: list):
        pass
