from kink import inject

from main.infrastructure.ports import IAttachmentsRepositoryPort
from main.domain.models import Attachment
from typing import List


@inject
def get_attach(tenant_id:str, patient_id:str, attach_repo: IAttachmentsRepositoryPort) -> List[Attachment]:
    return attach_repo.get_attach(tenant_id, patient_id)
