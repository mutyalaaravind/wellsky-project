from kink import di

from .ports import IFormRepositoryPort,IPatientRepositoryPort, IMedicationRepositoryPort, IAttachmentsRepositoryPort, IEntityRepositoryPort
from .adapters.form_repository import FormRepository
from .adapters.patient_repository import PatientRepository
from .adapters.medication_repository import MedicationRepository
from .adapters.attachment_repository import AttachmentRepository
from .adapters.entity_repository import EntityRepository
from main.settings import FIRESTORE_EMULATOR_HOST, GCP_FIRESTORE_DB, GCP_PROJECT_ID

di[IFormRepositoryPort] = lambda _: FormRepository(GCP_PROJECT_ID)
di[IPatientRepositoryPort] = lambda _: PatientRepository(GCP_FIRESTORE_DB if not FIRESTORE_EMULATOR_HOST else '(default)')
di[IMedicationRepositoryPort] = lambda _: MedicationRepository(GCP_FIRESTORE_DB if not FIRESTORE_EMULATOR_HOST else '(default)')
di[IAttachmentsRepositoryPort] = lambda _: AttachmentRepository(GCP_FIRESTORE_DB if not FIRESTORE_EMULATOR_HOST else '(default)')
di[IEntityRepositoryPort] = lambda _: EntityRepository(GCP_FIRESTORE_DB if not FIRESTORE_EMULATOR_HOST else '(default)')
