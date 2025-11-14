import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict, List
import uuid


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.usecases.configuration import get_config
from paperglass.domain.models import Document, DocumentOperation, DocumentOperationDefinition, ExtractedClinicalData, PageLabel
from paperglass.infrastructure.ports import IQueryPort
from paperglass.domain.values import ClinicalData, DocumentOperationStep, DocumentOperationType
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.usecases.commands import CreateClinicalData, ExtractClinicalData
from paperglass.usecases.clinical_data import get_extracted_clinical_data
from kink import inject

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)


app_id="007"
tenant_id="54321"
patient_id="abc1"
document_id = "dummy"
document_operation_instance_id = "dummy"
page_id="dummy"
page_number=1

@inject
async def create_immunizations(commands: ICommandHandlingPort):
    clinical_data=[{"name":"Flu","status":"yes","date":"01/01/2022"},{"name":"TB","status":"no","date":""}]
    await commands.handle_command(CreateClinicalData(
        app_id=app_id,
        tenant_id=tenant_id,
        patient_id=patient_id,
        document_id=document_id,
        document_operation_instance_id=document_operation_instance_id,
        clinical_data_type="immunization",
        clinical_data  = clinical_data
    ))

@inject
async def create_allergies(commands: ICommandHandlingPort):
    clinical_data=[
        {
            "substance": "advil",
            "reaction": "nose itch"
        },
        {
            "substance": "tylnol",
            "reaction": "rash on head"
        }
    ]
    await commands.handle_command(CreateClinicalData(
        app_id=app_id,
        tenant_id=tenant_id,
        patient_id=patient_id,
        document_id=document_id,
        document_operation_instance_id=document_operation_instance_id,
        clinical_data_type=PageLabel.ALLERGIES.value,
        clinical_data  = clinical_data,
        page_id=page_id,
        page_number=page_number
    ))

@inject
async def extract_allergies(query:IQueryPort, command_handler: ICommandHandlingPort):
    doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)
    doc_operation_definition = doc_operation_definitions[0]
    extracted_allergies:List[ExtractedClinicalData] = await command_handler.handle_command(ExtractClinicalData(app_id=app_id, 
                                                                                                                        tenant_id=tenant_id,
                                                                                                                        patient_id="10b1b438d8694fb7bcf50edf07bc286d",
                                                                                                                        document_operation_instance_id="6eca00b66adc11efa3353e3297f4bd07",
                                                                                                                        document_operation_definition_id="bda2081860f611ef91b73e3297f4bd07",
                                                                                                                        document_id="a06b0b7e6ad211efb1df42004e494300", 
                                                                                                                        page_id="a06b0b7e6ad211efb1df42004e494300",
                                                                                                                        page_number=3, 
                                                                                                                        labelled_content=["ALL SULFA; LEVOFLOXACIN; TERBUTALINE"],
                                                                                                                        prompt=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("prompt"),
                                                                                                                        model=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("model"),
                                                                                                                        clinical_data_type = PageLabel.ALLERGIES.value
                                                                                                                        ))
    

@inject
async def extract(document_id: str, page_id: str, page_number:int, query:IQueryPort, command_handler: ICommandHandlingPort):
    classified_page = await query.get_classified_page(page_id=page_id)
    config = await get_config(app_id, tenant_id, query)
    document:Document = Document(**await query.get_document(document_id))
    document_operation_definitions:List[DocumentOperationDefinition] = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)
    doc_operation_definition = document_operation_definitions[0]
    document_operation:DocumentOperation = query.get_document_operation_by_document_id(document_id, DocumentOperationType.MEDICATION_EXTRACTION.value)
    

    document_operation_instance_id = document_operation.active_document_operation_instance_id
    document_operation_definition_id = document_operation.active_document_operation_definition_id
    
    if config and config.extract_allergies and classified_page:
        label_allergies = PageLabel.ALLERGIES.value
        labelled_content_allergies = [x.get(label_allergies) for x in classified_page.labels if x and x.get(label_allergies) and label_allergies in x.keys()]
        
        if labelled_content_allergies:
            
            step_id_in_progress = DocumentOperationStep.ALLERGIES_EXTRACTION
            extracted_allergies:List[ExtractedClinicalData] = await command_handler.handle_command(ExtractClinicalData(app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id, 
                                                                                                page_id=page_id,
                                                                                                page_number=page_number, 
                                                                                                labelled_content=labelled_content_allergies,
                                                                                                prompt=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("prompt"),
                                                                                                model=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("model"),
                                                                                                clinical_data_type = PageLabel.ALLERGIES.value
                                                                                                ))
            
    if config and config.extract_immunizations and classified_page:
        label_immunizations = PageLabel.IMMUNIZATIONS.value
        labelled_content_immunizations = [x.get(label_immunizations) for x in classified_page.labels if x and x.get(label_immunizations) and label_immunizations in x.keys()]
        
        if labelled_content_allergies:
            
            step_id_in_progress = DocumentOperationStep.IMMUNIZATIONS_EXTRACTION
            extracted_immunizations:List[ExtractedClinicalData] = await command_handler.handle_command(ExtractClinicalData(app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id, 
                                                                                                page_id=page_id,
                                                                                                page_number=page_number, 
                                                                                                labelled_content=labelled_content_immunizations,
                                                                                                prompt=doc_operation_definition.step_config.get(DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value).get("prompt"),
                                                                                                model=doc_operation_definition.step_config.get(DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value).get("model"),
                                                                                                clinical_data_type = PageLabel.IMMUNIZATIONS.value
                                                                                                ))

@inject
async def get_allergies(document_id, query:IQueryPort):
    extracted_allergies:List[ExtractedClinicalData] = await get_extracted_clinical_data(clinical_data_type=PageLabel.ALLERGIES.value, document_ids=[document_id],query=query)
    print(extracted_allergies)

@inject
async def get_immunizations(query:IQueryPort):
    extracted_immunizations:List[ExtractedClinicalData] = await get_extracted_clinical_data(clinical_data_type="immunization", document_ids=[document_id],query=query)
    print(extracted_immunizations)

if __name__ == "__main__":
    # asyncio.run(create_immunizations())    
    # asyncio.run(create_allergies())   
    #asyncio.run(get_immunizations()) 
    #asyncio.run(extract_allergies())
    asyncio.run(get_allergies("b696ce346c7011ef9b9842004e494300")) 