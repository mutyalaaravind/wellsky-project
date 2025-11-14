from collections import defaultdict
from difflib import SequenceMatcher
import json
from typing import Any, Dict, List, Tuple

from paperglass.usecases.configuration import get_config
from paperglass.domain.models import Document, DocumentOperation, ExtractedMedication, Medication, MedicationProfile
from paperglass.domain.values import Configuration, DocumentOperationType, ExtractedMedicationReference, MedicationPageProfile, MedicationStatus, MedicationValue, MedispanMedicationValue, ReconcilledMedication, Origin, MedispanStatus, ResolvedReconcilledMedication
from paperglass.infrastructure.ports import IPromptAdapter, IQueryPort
from kink import inject

from ..log import getLogger
LOGGER = getLogger(__name__)

async def group_medications_by_patient(patient_id: str, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped_medications = defaultdict(lambda: {
        "name": None,
        "dosage": None,
        "route": None,
        "records": set()
    })

    for med in medications:
        if med.get("patient_id") == patient_id:
            key = (med.get("name"), med.get("dosage"), med.get("route"))
            group = grouped_medications[key]
            group["name"] = med.get("name")
            group["dosage"] = med.get("dosage")
            group["route"] = med.get("route")
            group["id"] = med.get("id")
            group['created_by'] = med.get("created_by")
            record = (
                med.get("document_id"),
                med.get("page_id"),
                med.get("name"),
                frozenset((frozenset(evidence.items()) for evidence in med.get("evidences"))),
                med.get("page_number"),
                med.get("created_by")
            )
            group["records"].add(record)

    # Convert sets to lists for JSON serialization compatibility
    for group in grouped_medications.values():
        group["records"] = [
            {"document_id": r[0], "page_id": r[1], "name": r[2],"page_number":r[4],"created_by":r[5],"evidences": [dict(evidence) for evidence in r[3]]} for r in group["records"]
        ]

    return list(grouped_medications.values())

async def get_medications_by_document(document_ids: List[str], query:IQueryPort) -> List[Dict[str, Any]]:
    document_ids = document_ids.split(",") if document_ids else []
    # if page_id is not provided based on page_number we can get the active page_id
    medication_result = []

    if document_ids:
        for document_id in document_ids:
            existing_document_medication_profiles = await query.list_document_medication_profile_by_document(document_id=document_id)
            doc = await query.get_document(document_id)
            medications = await query.get_medications_by_document(document_id)
            evidences_aggregates = await query.get_evidences_by_document(document_id,doc.get("execution_id"))
            if medications:
                for medication in medications:
                    LOGGER.debug("Medication: %s", json.dumps(medication, indent=2))
                    medication["evidences"] = []
                    medication["medication_status"] = None
                    medication["medication_status_reason"] = None
                    medication["medication_status_reason_explaination"] = None
                    mapped_doc_medication_profile = [{}]
                    if existing_document_medication_profiles:
                        mapped_doc_medication_profile= [m for m in existing_document_medication_profiles if medication.get("key") and medication.get("key") == m.get("key")]
                        #medication["profile"] = mapped_doc_medication_profile[0] if mapped_doc_medication_profile else {}
                        medication["medication_status"] = mapped_doc_medication_profile[0].get("medication_status") if mapped_doc_medication_profile else None
                        medication["medication_status_reason"] = mapped_doc_medication_profile[0].get("medication_status_reason") if mapped_doc_medication_profile else None
                        medication["medication_status_reason_explaination"] = mapped_doc_medication_profile[0].get("medication_status_reason_explaination") if mapped_doc_medication_profile else None
                    evidence_aggregate = [e for e in evidences_aggregates if e.get("page_id") == medication.get("page_id")]
                    if evidence_aggregate:
                        evidences = evidence_aggregate[0].get("evidences")
                        for evidence in evidences:
                            evidence_text = evidence.get("text")
                            if evidence_text and (medication.get("name") in evidence_text or SequenceMatcher(None,evidence_text.lower(), medication.get("name").lower()).ratio() > 0.4):
                                medication["evidences"].append(evidence)
                medication_result.extend(medications)
    return medication_result

async def get_resolved_reconcilled_medications(document_ids: List[str], patient_id:str, query:IQueryPort) -> List[ResolvedReconcilledMedication]:
    document_ids = document_ids.split(",") if document_ids else []

    LOGGER.debug("Medications:  get_medication_profile_by_documents: %s", document_ids)

    # get active operation_instance_id for a document
    doc_operations:List[DocumentOperation] = []
    for document_id in document_ids:
        # additional check to ensure deactivated document is not included in the query
        doc = await query.get_document(document_id)
        if doc.get("active") == False:
            continue

        doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(document_id=document_id,operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value)

        if doc_operation:
            doc_operations.append(doc_operation)

    # get medication profile
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id=patient_id)
    if medication_profile:
        return medication_profile.get_resolved_reconcilled_medications(doc_operations)
    return []

async def get_v3_extracted_medications(document_ids:List[str],doc_operations:List[DocumentOperation], query:IQueryPort) -> List[ExtractedMedication]:

    LOGGER.debug("Medications:  get_resolved_reconcilled_medications_v3: %s", document_ids)
    
    extracted_medications:List[ExtractedMedication] = []
    doc_operations = await get_document_operations(document_ids,query)
    for doc_ops in doc_operations:
        extracted_medications.extend(await query.get_extracted_medications_by_operation_instance_id(doc_ops.document_id,doc_ops.active_document_operation_instance_id))

    return extracted_medications

async def get_document_operations(document_ids:List[str],query:IQueryPort) -> List[DocumentOperation]:
    # get active operation_instance_id for a document
    doc_operations:List[DocumentOperation] = []
    for document_id in document_ids:
        # additional check to ensure deactivated document is not included in the query
        doc = await query.get_document(document_id)
        if doc.get("active") == False:
            continue

        doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(document_id=document_id,operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value)

        if doc_operation:
            doc_operations.append(doc_operation)
    return doc_operations

async def get_resolved_reconcilled_medications_v3(document_ids: List[str], patient_id:str, app_id: str, tenant_id: str, query:IQueryPort) -> List[ResolvedReconcilledMedication]:
    document_ids = document_ids.split(",") if document_ids else []
    config:Configuration = await get_config(app_id,tenant_id,query)
    doc_operations:List[DocumentOperation] = await get_document_operations(document_ids,query)
    extracted_medications = await get_v3_extracted_medications(document_ids,doc_operations,query)
    
    # get medication profile
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id=patient_id)
    if medication_profile:
        return medication_profile.get_resolved_reconcilled_medications_merged_with_extracted_medications(doc_operations,extracted_medications,config)
    return []

async def get_document_filter_profile(document_id:str,patient_id:str, query:IQueryPort) -> List[MedicationPageProfile]:
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id=patient_id)
    doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(document_id=document_id,operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value)
    if medication_profile:
        return medication_profile.get_page_profiles(document_id, doc_operation)
    return []

async def get_document_filter_profile_v3(document_id:str,patient_id:str, app_id: str, tenant_id: str, query:IQueryPort) -> List[MedicationPageProfile]:
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id=patient_id)
    doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(document_id=document_id,operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value)
    config:Configuration = await get_config(app_id,tenant_id,query)
    extracted_medications:List[ExtractedMedication] = []
    document:Document = Document(**await query.get_document(document_id))
    
    if doc_operation and doc_operation.active_document_operation_instance_id:
        extracted_medications.extend(await query.get_extracted_medications_by_operation_instance_id(document_id,doc_operation.active_document_operation_instance_id))

    if medication_profile:
        return medication_profile.get_page_profiles_merged_with_extracted_medications(document_id, doc_operation, extracted_medications, config)

    return []

async def get_medication_profile_by_documents(document_ids: List[str],patient_id:str, query:IQueryPort) -> List[Dict[str, Any]]:
    medication_result = []
    document_ids = document_ids.split(",") if document_ids else []

    LOGGER.debug("Medications:  get_medication_profile_by_documents: %s", document_ids)

    # get active operation_instance_id for a document
    doc_operation_instances = {}
    for document_id in document_ids:
        # additional check to ensure deactivated document is not included in the query
        doc = await query.get_document(document_id)
        if doc.get("active") == False:
            continue

        doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(document_id=document_id,operation_type=DocumentOperationType.MEDICATION_EXTRACTION.value)

        if doc_operation:
            doc_operation_instances[document_id]=doc_operation.active_document_operation_instance_id

    # get medication profile
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id=patient_id)
    #LOGGER.debug("MedicationProfile: %s", json.dumps(json.loads(medication_profile.json()), indent=2))
    if medication_profile:
        medications = medication_profile.medications
        for medication in medications:
            reconcilled_medication:ReconcilledMedication = medication
            extracted_medication_records = []
            is_medication_associated_with_given_documents = False

            for document_id in document_ids:
                if document_id in medication.document_references:
                    is_medication_associated_with_given_documents = True
                    for extracted_medication in medication.extracted_medication_reference:
                        extracted_medication:ExtractedMedicationReference = extracted_medication
                        if extracted_medication.document_id == document_id and \
                            extracted_medication.document_operation_instance_id == doc_operation_instances.get(document_id):

                            extracted_medication_dict = extracted_medication.dict()
                            # extracted_medication_dict["evidences"] = matched_evidence_record
                            extracted_medication_records.append({
                                    "documentId":extracted_medication.document_id,
                                    "extractedMedicationId":extracted_medication.extracted_medication_id,
                                    "documentOperationInstanceId":extracted_medication.document_operation_instance_id,
                                    "pageNumber": extracted_medication.page_number,
                                })
                            # some edge case where a given reconcilled medcication has more than one extracted medication with same
                            #  extracted_medication_id, operation_instance_id and document_id
                            # we don't want this duplicate to show in the UI
                            # break will ensure we end up with only one extracted medication record for a given reconcilled medication record
                            # ToDo: investigate medication extraction command handler to avoid this duplicate
                            break

            if not reconcilled_medication.imported_medication and not reconcilled_medication.user_entered_medication and not extracted_medication_records:
                # this extracted medication doesn't have required doc operation instance id
                continue

            if is_medication_associated_with_given_documents and extracted_medication_records and not reconcilled_medication.user_entered_medication and not reconcilled_medication.imported_medication:
                # filter out medications without dosage for now

                if not reconcilled_medication.medication.strength and not reconcilled_medication.medication.route:
                    continue

            if is_medication_associated_with_given_documents or reconcilled_medication.imported_medication:
                medication_dict =  reconcilled_medication.medication.dict()

                medication_dict["extractedMedications"] = extracted_medication_records
                medication_dict["startDate"] = reconcilled_medication.latest_start_date
                medication_dict["endDate"] = reconcilled_medication.latest_end_date
                medication_dict["discontinuedDate"] = reconcilled_medication.latest_discontinued_date
                medication_dict["deleted"] = reconcilled_medication.deleted #ToDo: get from user entered medication or imported medication data model
                medication_dict["id"] = medication.id

                if reconcilled_medication.medispan_id and reconcilled_medication.medispan_id != "0":
                    medication_dict["medispan_id"] = reconcilled_medication.medispan_id.removesuffix(".0")
                    LOGGER.debug("+medication_dict: %s", medication_dict)
                    LOGGER.debug("+reconcilled_medication: %s", reconcilled_medication)
                    medication_dict["medispanMatchStatus"] = "MATCHED"
                    medication_dict["isUnlisted"] = False
                else:
                    LOGGER.debug("-medication_dict: %s", medication_dict)
                    LOGGER.debug("-reconcilled_medication: %s", reconcilled_medication)
                    medication_dict["medispanMatchStatus"] = "UNMATCHED"
                    medication_dict["isUnlisted"] = True
                medication_dict["medispanMatchStatus"] = reconcilled_medication.medispan_status
                medication_dict["medicationStatus"] = {"status":None,"statusReason":None,"statusReasonExplaination":None}
                medication_dict["modifiedBy"] = None
                medication_dict["origin"] = Origin.EXTRACTED
                medication_dict["medicationType"] = "extracted"  # Deprecated in favor of origin
                medication_dict["isSynced"] = False
                if reconcilled_medication.host_medication_sync_status:
                    medication_dict["host_medication_sync_status"] = {
                        "host_medication_unique_identifier": reconcilled_medication.host_medication_sync_status.host_medication_unique_identifier,
                        "last_synced_at": reconcilled_medication.host_medication_sync_status.last_synced_at.isoformat()
                    }
                    medication_dict["isSynced"] = True
                if reconcilled_medication.user_entered_medication:
                    LOGGER.debug("user_entered_medication %s: %s", reconcilled_medication.id, reconcilled_medication.user_entered_medication)
                    medication_dict["name"] = reconcilled_medication.user_entered_medication.medication.name
                    medication_dict["route"] = reconcilled_medication.user_entered_medication.medication.route
                    medication_dict["strength"] = reconcilled_medication.user_entered_medication.medication.strength
                    medication_dict["dosage"] = reconcilled_medication.user_entered_medication.medication.dosage
                    medication_dict["form"] = reconcilled_medication.user_entered_medication.medication.form
                    medication_dict["frequency"] = reconcilled_medication.user_entered_medication.medication.frequency
                    medication_dict["instructions"] = reconcilled_medication.user_entered_medication.medication.instructions
                    if reconcilled_medication.user_entered_medication.change_sets and reconcilled_medication.user_entered_medication.change_sets.changes:
                        medication_dict["change_sets"] = json.loads(json.dumps([x.dict() for x in reconcilled_medication.user_entered_medication.change_sets.changes],indent=4, sort_keys=True, default=str))
                    if reconcilled_medication.user_entered_medication.medication.medispan_id and reconcilled_medication.user_entered_medication.medication.medispan_id != 0:
                        medication_dict["medispanMatchStatus"] = MedispanStatus.MATCHED
                        medication_dict["isUnlisted"] = False
                    else:
                        medication_dict["medispanMatchStatus"] = MedispanStatus.UNMATCHED
                        medication_dict["isUnlisted"] = True
                    medication_dict["medicationStatus"] = {"status":reconcilled_medication.user_entered_medication.medication_status.status,
                                                            "statusReason":reconcilled_medication.user_entered_medication.medication_status.status_reason,
                                                            "statusReasonExplaination":reconcilled_medication.user_entered_medication.medication_status.status_reason_explaination}
                    medication_dict["modifiedBy"] = reconcilled_medication.user_entered_medication.modified_by
                    medication_dict["startDate"] = reconcilled_medication.user_entered_medication.medication.start_date
                    medication_dict["discontinuedDate"] = reconcilled_medication.user_entered_medication.medication.discontinued_date
                    medication_dict["origin"] = Origin.USER_ENTERED
                    medication_dict["medispan_id"] = reconcilled_medication.user_entered_medication.medication.medispan_id
                    medication_dict["medicationType"] = "user_entered"  # Deprecated in favor of origin
                    medication_dict["classification"]   = reconcilled_medication.user_entered_medication.medication.classification
                if reconcilled_medication.imported_medication:
                    LOGGER.debug("imported_medication %s: %s", reconcilled_medication.id, reconcilled_medication.imported_medication)
                    medication_dict["name"] = reconcilled_medication.imported_medication.medication.name
                    medication_dict["route"] = reconcilled_medication.imported_medication.medication.route
                    medication_dict["strength"] = reconcilled_medication.imported_medication.medication.strength
                    medication_dict["dosage"] = reconcilled_medication.imported_medication.medication.dosage
                    medication_dict["form"] = reconcilled_medication.imported_medication.medication.form
                    medication_dict["frequency"] = reconcilled_medication.imported_medication.medication.frequency
                    medication_dict["instructions"] = reconcilled_medication.imported_medication.medication.instructions
                    if reconcilled_medication.imported_medication.medispan_id and reconcilled_medication.imported_medication.medispan_id != "0":
                        medication_dict["medispanMatchStatus"] = MedispanStatus.MATCHED
                        medication_dict["isUnlisted"] = False
                    else:
                        LOGGER.debug("MedispanMatchStatus UNMATCHED: %s", reconcilled_medication.imported_medication.medication)
                        LOGGER.debug("MedispanMatchStatus UNMATCHED reconcilledMed: %s", reconcilled_medication)
                        medication_dict["medispanMatchStatus"] = MedispanStatus.UNMATCHED
                        medication_dict["isUnlisted"] = True
                    medication_dict["modifiedBy"] = reconcilled_medication.imported_medication.modified_by
                    medication_dict["startDate"] = reconcilled_medication.imported_medication.medication.start_date
                    medication_dict["discontinuedDate"] = reconcilled_medication.imported_medication.medication.discontinued_date
                    medication_dict["origin"] = Origin.IMPORTED
                    medication_dict["medispan_id"] = reconcilled_medication.imported_medication.medispan_id
                    medication_dict["medicationType"] = "imported" # Deprecated in favor of origin
                    medication_dict["isSynced"] = True

                medication_dict["evidences"] = []
                medication_result.append(medication_dict)

    # get extracted medications by operation_instance_id


    # get evidences
    return medication_result

@inject
async def get_medications_grouped_by_patient(patient_id: str, document_ids: str,  query:IQueryPort) -> List[Dict[str, Any]]:
    medications = await get_medications_by_document(document_ids,  query)
    return await group_medications_by_patient(patient_id, medications)

"""
for every extracted medication, we need to find matched medsipan medication using LLM
"""
@inject
async def find_matching_medispan_medication_with_llm(medication_value:MedicationValue,
                                            medispan_medications:List[MedispanMedicationValue],
                                            prompt_adapter:IPromptAdapter):

    opMeta:OperationMeta = OperationMeta(
        type = "adhoc",
        step = "medications.find_matching_medispan_medication_with_llm",
    )

    if medication_value and medispan_medications:
        prompt_text = f"""
        You are a medical professional that is trying to find medication record from medispan medications that
        match the provided medication record.
        input_medication_record: {medication_value.dict()}
        medispan_medications: {[x.dict() for x in medispan_medications]}
        Please return the best matched medispan medication record as json.
        """
        result = await prompt_adapter.multi_modal_predict([prompt_text], metadata=opMeta.dict())
        result = result.replace('**', '').replace('##', '').replace('```', '').replace('json', '')
        result = eval(result.replace("\\n",""))
        if result and result.get("name"):
            return MedispanMedicationValue(**result)
    return None

"""
for every extracted medication, we need to find matched medsipan medication using python logic
"""
@inject
async def find_matching_medispan_medication_with_logic(medication_value:MedicationValue,
                                            medispan_medications:List[MedispanMedicationValue],
                                            prompt_adapter:IPromptAdapter) -> Tuple[MedispanMedicationValue, float]:
    winning_score = 0
    winning_medication = None
    for medispan_medication in medispan_medications:
        match_score = medication_value.match_score(medispan_medication)
        if match_score > winning_score:
            winning_score = match_score
            winning_medication = medispan_medication
    return (winning_medication, winning_score)

async def get_best_match_of_medispan_results(search_term, medispan_medications: List[MedispanMedicationValue]):
    # LLM will sort results based on best match at the top
    score = None
    winning_medication = None
    if medispan_medications and len(medispan_medications) > 0:
        LOGGER.debug("Best match to medispan for search_term '%s': %s", search_term, medispan_medications[0])
        winning_medication = medispan_medications[0]
        score = 1.0
    return (winning_medication, score)
