from kink import inject

from main.infrastructure.ports import IPatientRepositoryPort
from main.domain.models import Patient
from typing import List


@inject
@inject
def get_all_patients(patient_repo: IPatientRepositoryPort) -> List[Patient]:
    return patient_repo.get_all_patients()


@inject
async def get_patient_by_id(patient_id: str, patient_repo: IPatientRepositoryPort) -> Patient:
    return await patient_repo.get_patient_by_id(patient_id)


@inject
def create_patient(patient: Patient,patient_repo: IPatientRepositoryPort) -> Patient:
    return patient_repo.create_patient(patient)


@inject
def update_patient(patient_repo: IPatientRepositoryPort, patient_id: str, patient: Patient) -> Patient:
    return patient_repo.update_patient(patient_id, patient)


@inject
def delete_patient(patient_repo: IPatientRepositoryPort, patient_id: str) -> None:
    patient_repo.delete_patient(patient_id)
