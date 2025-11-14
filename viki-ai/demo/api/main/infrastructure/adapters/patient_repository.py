from typing import List, Optional
from main.domain.models import Patient
from google.cloud.firestore import AsyncClient

from main.infrastructure.ports import IPatientRepositoryPort


class PatientRepository(IPatientRepositoryPort):
    def __init__(self,db_name:str):
        self.client = AsyncClient(database=db_name)
        self.patients_ref = self.client.collection('demo_patients')

    async def get_all_patients(self) -> List[Patient]:
        ref = self.patients_ref.where('active', '==', True).order_by('created_at')
        return [Patient(**doc.to_dict()) for doc in await ref.get()]

    async def create_patient(self, patient:Patient):
        ref = self.patients_ref.document(patient.id)
        await ref.set(patient.dict())
        return patient
    
    async def get_patient_by_id(self,  patient_id:str):
        patient = await self.patients_ref.document(patient_id).get()
        return Patient(**patient.to_dict()) if patient else None
