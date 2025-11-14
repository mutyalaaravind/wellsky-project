
from typing import List

from paperglass.domain.values import DocumentOperationType, ExtractedClinicalDataReference
from paperglass.domain.models import DocumentOperation, ExtractedClinicalData, ExtractedClinicalDataDeduped, PageLabel
from paperglass.infrastructure.ports import IQueryPort


async def get_extracted_clinical_data(clinical_data_type: str, document_ids:List[str], query:IQueryPort):
    extracted_clinical_data:List[ExtractedClinicalData] = []
    extracted_clinical_deduped_data:List[ExtractedClinicalDataDeduped] = []
    for doc_id in document_ids:
        doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(doc_id, DocumentOperationType.MEDICATION_EXTRACTION.value)
        if doc_operation:
            extracted_clinical_data.extend(await query.get_extracted_clinical_data_by_type_doc_id_and_doc_operation_instance_id(
                clinical_data_type, doc_id, doc_operation.active_document_operation_instance_id))

    
    for extracted_clinical_records in extracted_clinical_data:
        
        for extracted_clinical_record in extracted_clinical_records.clinical_data:
            if extracted_clinical_records.clinical_data_type == PageLabel.ALLERGIES.value:
                deduped_clinical_records:List[ExtractedClinicalDataDeduped] = [x for x in extracted_clinical_deduped_data 
                                                                               if x.clinical_data_type == PageLabel.ALLERGIES.value and 
                x.clinical_data.get("substance") == extracted_clinical_record.get("substance") and 
                x.clinical_data.get("reaction") == extracted_clinical_record.get("reaction")]
                
                if deduped_clinical_records:
                    deduped_clinical_record = deduped_clinical_records[0]
                    deduped_clinical_record_references = [x for x in deduped_clinical_record.references 
                                                            if x.document_id == extracted_clinical_records.document_id and
                                                            x.document_operation_instance_id == extracted_clinical_records.document_operation_instance_id and
                                                            x.page_number == extracted_clinical_records.page_number and 
                                                            x.extracted_clinical_data_id == extracted_clinical_records.id]
                    if not deduped_clinical_record_references:
                        deduped_clinical_record.references.append(ExtractedClinicalDataReference(
                            document_id=extracted_clinical_records.document_id,
                            document_operation_instance_id=extracted_clinical_records.document_operation_instance_id,
                            page_number=extracted_clinical_records.page_number,
                            extracted_clinical_data_id=extracted_clinical_records.id
                        ))
                else:
                    extracted_clinical_deduped_data.append(ExtractedClinicalDataDeduped(
                        id = extracted_clinical_records.id,
                        app_id = extracted_clinical_records.app_id,
                        tenant_id = extracted_clinical_records.tenant_id,
                        patient_id = extracted_clinical_records.patient_id,
                        clinical_data_type=extracted_clinical_records.clinical_data_type,
                        clinical_data = extracted_clinical_record,
                        references=[ExtractedClinicalDataReference(
                            document_id=extracted_clinical_records.document_id,
                            document_operation_instance_id=extracted_clinical_records.document_operation_instance_id,
                            page_number=extracted_clinical_records.page_number,
                            extracted_clinical_data_id=extracted_clinical_records.id
                        )]
                    ))

            if extracted_clinical_records.clinical_data_type == PageLabel.IMMUNIZATIONS.value:
                if extracted_clinical_record.get("status") == "unknown":
                    continue
                deduped_clinical_records:List[ExtractedClinicalDataDeduped] = [x for x in extracted_clinical_deduped_data 
                                                                            if x.clinical_data_type == PageLabel.IMMUNIZATIONS.value and 
                                                                                x.clinical_data.get("name") == extracted_clinical_record.get("name") and 
                                                                                x.clinical_data.get("status") == extracted_clinical_record.get("status")
                                                                            ]
                
                if deduped_clinical_records:
                    deduped_clinical_record = deduped_clinical_records[0]
                    deduped_clinical_record_references = [x for x in deduped_clinical_record.references 
                                                            if x.document_id == extracted_clinical_records.document_id and
                                                            x.document_operation_instance_id == extracted_clinical_records.document_operation_instance_id and
                                                            x.page_number == extracted_clinical_records.page_number and 
                                                            x.extracted_clinical_data_id == extracted_clinical_records.id]
                    if not deduped_clinical_record_references:
                        deduped_clinical_record.references.append(ExtractedClinicalDataReference(
                            document_id=extracted_clinical_records.document_id,
                            document_operation_instance_id=extracted_clinical_records.document_operation_instance_id,
                            page_number=extracted_clinical_records.page_number,
                            extracted_clinical_data_id=extracted_clinical_records.id
                        ))
                else:
                    extracted_clinical_deduped_data.append(ExtractedClinicalDataDeduped(
                        id = extracted_clinical_records.id,
                        app_id = extracted_clinical_records.app_id,
                        tenant_id = extracted_clinical_records.tenant_id,
                        patient_id = extracted_clinical_records.patient_id,
                        clinical_data_type=extracted_clinical_records.clinical_data_type,
                        clinical_data = extracted_clinical_record,
                        references=[ExtractedClinicalDataReference(
                            document_id=extracted_clinical_records.document_id,
                            document_operation_instance_id=extracted_clinical_records.document_operation_instance_id,
                            page_number=extracted_clinical_records.page_number,
                            extracted_clinical_data_id=extracted_clinical_records.id
                        )]
                    ))
            
    #return extracted_clinical_data
    return extracted_clinical_deduped_data
