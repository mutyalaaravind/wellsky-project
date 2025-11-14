from paperglass.domain.values import DocumentSettings
from paperglass.infrastructure.ports import ISettingsPort
from google.cloud.firestore import AsyncClient as AsyncFirestoreClient

class SettingsAdapter(ISettingsPort):

    def __init__(self, db_name) -> None:
        self.db = AsyncFirestoreClient(database=db_name)

    async def get_document_settings(self, patient_id: str) -> DocumentSettings:
        doc_settings = await self.db.collection(u"paperglass_settings").document(patient_id).get()
        doc_settings = doc_settings.to_dict()
        if doc_settings:
            doc_settings =  DocumentSettings(**doc_settings)
        if not doc_settings:
            return DocumentSettings(patient_id=patient_id)
        return doc_settings

    async def save_document_settings(self, settings: DocumentSettings) -> None:
        await self.db.collection(u"paperglass_settings").document(settings.patient_id).set(settings.dict())