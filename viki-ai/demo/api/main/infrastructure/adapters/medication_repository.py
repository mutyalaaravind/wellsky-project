from typing import List, Optional
from main.domain.models import Medication
from google.cloud.firestore import AsyncClient

from main.infrastructure.ports import IMedicationRepositoryPort


class MedicationRepository(IMedicationRepositoryPort):
    def __init__(self,db_name:str):
        self.client = AsyncClient(database=db_name)
        self.meds_ref = self.client.collection('demo_medications')

    async def get_meds(self, tenant_id:str, patient_id:str):
        ref = self.meds_ref.where('tenantId', '==', tenant_id).where('patientId', '==', patient_id)
        docs = await ref.get()
        return [Medication(**doc.to_dict()) for doc in docs]
    
    async def save_med(self, tenant_id:str, patient_id:str, data:dict):
        ref = self.meds_ref.document(patient_id)
        await ref.set(data)
        ref = self.meds_ref.where('tenantId', '==', tenant_id).where('patientId', '==', patient_id).where('id', '==', data["id"])
        docs = await ref.get()
        return Medication(**docs[0].to_dict())
