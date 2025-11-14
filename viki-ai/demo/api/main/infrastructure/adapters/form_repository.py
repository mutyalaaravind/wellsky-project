from typing import Optional
from google.cloud.firestore import AsyncClient

from main.infrastructure.ports import IFormRepositoryPort


class FormRepository(IFormRepositoryPort):
    def __init__(self, db_name):
        self.client = AsyncClient()
        self.form_instances_ref = self.client.collection('demo_form_instances')

    async def get_form_instance(self, id: str) -> Optional[dict]:
        ref = self.form_instances_ref.document(id)
        doc = await ref.get()
        if not doc.exists:
            return None
        return doc.to_dict()

    async def save_form_instance(self, id: str, data: dict):
        ref = self.form_instances_ref.document(id)
        await ref.set(data)
