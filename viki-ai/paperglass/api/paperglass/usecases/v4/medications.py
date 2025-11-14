import json
from logging import getLogger
import traceback
from typing import List
from paperglass.usecases.commands import CreateorUpdateMedicationProfile
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.usecases.configuration import get_config
from paperglass.domain.values import Configuration, DocumentOperationType, MedicationPageProfile, ResolvedReconcilledMedication
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.usecases.medications import get_document_filter_profile_v3, get_document_operations, get_v3_extracted_medications
from paperglass.log import CustomLogger
from paperglass.infrastructure.repositories.medications import MedicationsRepository
from paperglass.domain.models import Document, DocumentOperation, ExtractedMedication, MedicationProfile
from paperglass.infrastructure.ports import IQueryPort, IStoragePort
from kink import inject
from uuid import uuid4

LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)

async def get_medication(document_id:str, medication_id:str):
    extra = {
        "document_id": document_id,
        "medication_id": medication_id
    }
    try:
        medications_repo = MedicationsRepository()
        medication:ExtractedMedication = await medications_repo.get_medication(document_id,medication_id)
        return medication
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error reading medication {medication_id} from {document_id}: {traceback.format_exc()}", extra=extra)
        return None

async def list_medications(document_id:str, page_number: int) -> List[ExtractedMedication]:
    extra = {
        "document_id": document_id,
        "page_number": page_number
    }
    try:
        medications_repo = MedicationsRepository()
        medications:List[ExtractedMedication] = await medications_repo.list_medications(document_id, page_number)
        return medications
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error reading medications from {document_id}: {traceback.format_exc()}", extra=extra)
        return []

@inject()
async def create_medications(document_id:str,page_number:int, run_id:str,medications_storage_uri:str,storage:IStoragePort):
    
    extra={
        "document_id":document_id,
        "run_id":run_id,
        "medications_storage_uri":medications_storage_uri
    }
    medications_repo = MedicationsRepository()
    medications = await storage.get_external_document_raw(medications_storage_uri)
    medications = json.loads(medications)
    medications = [ExtractedMedication(**med) for med in medications]
    await medications_repo.batch_create_medications(document_id,page_number,run_id,medications)
    return medications

@inject()
async def get_resolved_reconcilled_medications(document_ids_with_orchestration_engine_version, patient_id,app_id, tenant_id, config,query:IQueryPort,command:ICommandHandlingPort) -> List[ResolvedReconcilledMedication]:
    try:
        # check if document id is processed by v3 or v4
        # v3 - pull medications from legacy medication
        # v4 - pull medications from new medications collection
        medication_repo = MedicationsRepository()
        medication_profile:MedicationProfile = None
        extracted_medications:List[ExtractedMedication] = []
        doc_operations = []
        v3_document_ids = []
        v4_document_ids = []
        for document_id, orchestration_version in document_ids_with_orchestration_engine_version.items():
            if orchestration_version == "v3":
                v3_document_ids.append(document_id)
            elif orchestration_version == "v4":
                v4_document_ids.append(document_id)
        
        medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id=patient_id)
        
        if medication_profile is None:
            # medication_profile = MedicationProfile(
            #     id = uuid4().hex,
            #     app_id=app_id,
            #     tenant_id=tenant_id,
            #     patient_id=patient_id,
            #     medications=[]
            # )
            medication_profile = await command.handle_command_with_explicit_transaction(CreateorUpdateMedicationProfile(
                app_id=app_id,
                tenant_id=tenant_id,
                patient_id=patient_id,
                document_id=document_id,
                document_operation_instance_id = "latest",
                document_operation_definition_id = "latest"
            ))
        
        if v3_document_ids:
            v3_doc_operations = await get_document_operations(v3_document_ids,query)
            v3_extracted_medications = await get_v3_extracted_medications(v3_document_ids,v3_doc_operations,query)
            doc_operations.extend(v3_doc_operations)
            extracted_medications.extend(v3_extracted_medications)
        if v4_document_ids:
            for document_id in v4_document_ids:
                doc_operation_instance_id = await medication_repo.get_latest_doc_operation_instance_id(document_id)
                v4_doc_operation = DocumentOperation(
                    id="dummy",
                    app_id=app_id,
                    tenant_id=tenant_id,
                    patient_id=patient_id,
                    document_id=document_id,
                    operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                    active_document_operation_definition_id = "medication_extraction",
                    active_document_operation_instance_id = doc_operation_instance_id
                )
                v4_extracted_medications = await medication_repo.get_medications_by_document_ids([document_id],doc_operation_instance_id)
                
                extracted_medications.extend(v4_extracted_medications)
                doc_operations.append(v4_doc_operation)

        reconciled_medications =  medication_profile.get_resolved_reconcilled_medications_merged_with_extracted_medications(
            doc_operations,
            extracted_medications,
            config
        )

        return reconciled_medications
    except Exception as e:
        LOGGER2.error(f"Error getting resolved reconcilled medications: {traceback.format_exc()}",extra={"patient_id":patient_id})
    return []


@inject()
async def get_document_filter_profile_v4(document_id:str,patient_id:str, app_id: str, tenant_id: str, query:IQueryPort, commands:ICommandHandlingPort) -> List[MedicationPageProfile]:
    
    LOGGER.debug(f"Getting document filter profile v4 for document_id: {document_id}, patient_id: {patient_id}, app_id: {app_id}, tenant_id: {tenant_id}")
    
    medication_repo = MedicationsRepository()
    doc_operation:DocumentOperation = None
    document:Document = Document(**await query.get_document(document_id))
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id=patient_id)
    extracted_medications:List[ExtractedMedication] = []
    config:Configuration = await get_config(app_id,tenant_id,query)
    
    if document.operation_status.get(DocumentOperationType.MEDICATION_EXTRACTION.value) and document.operation_status.get(DocumentOperationType.MEDICATION_EXTRACTION.value).orchestration_engine_version=="v4":
        if not medication_profile:
            # medication_profile = MedicationProfile(
            #     id = uuid4().hex,
            #     app_id=app_id,
            #     tenant_id=tenant_id,
            #     patient_id=patient_id,
            #     medications=[]
            # )
            LOGGER.debug(f"Command type is: {type(commands)}", extra={"patient_id": patient_id, "document_id": document_id})
            medication_profile = await commands.handle_command_with_explicit_transaction(CreateorUpdateMedicationProfile(
                app_id=app_id,
                tenant_id=tenant_id,
                patient_id=patient_id,
                document_id=document_id,
                document_operation_instance_id = "latest",
                document_operation_definition_id = "latest"
            ))
        doc_operation_instance_id = await medication_repo.get_latest_doc_operation_instance_id(document_id)
        doc_operation = DocumentOperation(
                id="dummy",
                app_id=app_id,
                tenant_id=tenant_id,
                patient_id=patient_id,
                document_id=document_id,
                operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                active_document_operation_definition_id = "medication_extraction",
                active_document_operation_instance_id = doc_operation_instance_id
            )
        extracted_medications.extend(await medication_repo.get_medications_by_document_ids([document_id],doc_operation_instance_id))
    else:
        # doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(document_id=document_id,operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value)
        # extracted_medications.extend(await query.get_extracted_medications_by_operation_instance_id(document_id,doc_operation.active_document_operation_instance_id))
        return await get_document_filter_profile_v3(document_id,patient_id,app_id,tenant_id,query)
        
    if medication_profile:
        return medication_profile.get_page_profiles_merged_with_extracted_medications(document_id, doc_operation, extracted_medications, config)

    return []