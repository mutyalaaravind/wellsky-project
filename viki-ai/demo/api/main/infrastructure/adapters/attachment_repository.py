from typing import List, Optional
from main.domain.models import Attachment
from google.cloud.firestore import AsyncClient

from main.infrastructure.ports import IAttachmentsRepositoryPort


class AttachmentRepository(IAttachmentsRepositoryPort):
    def __init__(self,db_name:str):
        self.client = AsyncClient(database=db_name)
        self.attachments_ref = self.client.collection('demo_attachments')

    async def get_attach(self, tenant_id:str, patient_id:str):
        # data = {
        #     'appId': 'ltc',
        #     'tenantId': tenant_id,
        #     'patientId': patient_id,
        #     'hostFileId': 12333455,
        #     'fileId': '12333455',
        #     'fileName': 'test-file.pdf',
        #     'fileType': 'application/pdf',
        #     'createdOn': '2025-04-15T10:00:00Z',
        #     'updatedOn': '2025-04-15T10:00:00Z',
        #     'sha256': 'jhbvjgvasdchbkjhbjasuvdkjchbksjdhvckyghcvhj',
        #     'metadata': {
        #         'catagory': 'medication_profile',
        #     },
        #     'active': True,
        #     'repositoryType': 'api',
        #     'api': {
        #         'method': 'GET',
        #         'url': 'https://api.example.com/attachments/12333455',
        #         'headers': {
        #             'X-Custom-Token': 'xyxyxyxyxyxyxyxyxyxyxy',
        #         },
        #         'body': None
        #     }
        # }
        # ref = self.attachments_ref.document(patient_id)
        # await ref.set(data)

        ref = self.attachments_ref.where('tenantId', '==', tenant_id).where('patientId', '==', patient_id)
        docs = await ref.get()
        return [Attachment(**doc.to_dict()) for doc in docs]

    # async def save_med(self, tenant_id:str, patient_id:str, data:dict):
    #     ref = self.meds_ref.document(patient_id)
    #     await ref.set(data)
    #     ref = self.meds_ref.where('tenantId', '==', tenant_id).where('patientId', '==', patient_id).where('id', '==', data["id"])
    #     docs = await ref.get()
    #     return Medication(**docs[0].to_dict())
