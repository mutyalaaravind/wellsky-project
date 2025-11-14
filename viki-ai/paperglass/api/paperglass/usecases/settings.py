from paperglass.infrastructure.ports import ISettingsPort
from paperglass.domain.values import DocumentSettings
from kink import inject


@inject
async def get_document_settings(self, patient_id: str,settings_adapter: ISettingsPort) -> DocumentSettings:
    settings_adapter.get(patient_id)

@inject
async def save_document_settings(self, patient_id: str, settings: DocumentSettings,settings_adapter: ISettingsPort) -> None:
    settings_adapter.set(patient_id, settings)