from kink import inject

from main.infrastructure.ports import IMedicationRepositoryPort
from main.domain.models import Medication
from typing import List


@inject
def get_meds(tenant_id:str, patient_id:str, med_repo: IMedicationRepositoryPort) -> List[Medication]:
    return med_repo.get_meds(tenant_id, patient_id)

@inject
def save_med(tenant_id:str, patient_id:str, data:dict, med_repo: IMedicationRepositoryPort) -> List[Medication]:
    return med_repo.save_med(tenant_id, patient_id, data)
