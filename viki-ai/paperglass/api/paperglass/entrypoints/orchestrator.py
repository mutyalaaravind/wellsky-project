import sys,os
import traceback
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import datetime
import time
from typing import Any, List, Dict
from kink import inject
from paperglass.domain.models import AppConfig, AppTenantConfig, ClassifiedPage, Document, DocumentOperation, DocumentOperationDefinition, DocumentOperationInstance, DocumentOperationInstanceLog, DocumentStatus, ExtractedClinicalData, ExtractedMedication, Medication,Page, PageLabel, MedicalCodingRawData
from paperglass.domain.model_toc import PageTOC, DocumentTOC
from paperglass.usecases.configuration import get_config
from paperglass.usecases.commands import (
    ClassifyPage,
    CreateAppConfiguration, 
    CreateDefaultMedicationDocumentOperationDefinition, 
    CreateOrUpdateDocumentOperation, 
    CreateDocumentOperationInstance, 
    CreateDocumentOperationInstanceLog, 
    CreateEvidence, 
    CreatePage, 
    CreateorUpdateMedicationProfile, 
    CreateorUpdateMedicationProfile, 
    ExecuteCustomPrompt,
    ExtractClinicalData, 
    ExtractMedication, 
    ExtractText, 
    GetDocument, 
    MedispanMatching,
    PerformOCR, 
    SplitPages, 
    AssembleTOC,
    ExtractConditionsData,
)
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.values import (
    Configuration, 
    DocumentOperationStatus, 
    DocumentOperationStep, 
    DocumentStatusType, 
    OrchestrationPriority,
    PageText, 
    Result
)
from paperglass.usecases.commands import ClassifyPage, CreateDefaultMedicationDocumentOperationDefinition, CreateOrUpdateDocumentOperation, CreateDocumentOperationInstance, CreateDocumentOperationInstanceLog, CreateEvidence, CreatePage, CreateorUpdateMedicationProfile, ExecuteCustomPrompt, ExtractMedication, ExtractText, GetDocument, PerformOCR, SplitPages, AssembleTOC, NormalizeMedications
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.values import DocumentOperationStatus, DocumentOperationStep, DocumentStatusType, DocumentOperationType
from paperglass.infrastructure.ports import IQueryPort, IStoragePort, IUnitOfWorkManagerPort

from paperglass.domain.models_common import OrchestrationException
from paperglass.domain.utils.exception_utils import exceptionToMap, getTrimmedStacktraceAsString

import asyncio
import argparse
import json

from paperglass.settings import STAGE,ORCHESTRATION_MEDICALEXTRACTION_STEP_NORMALIZATION_ENABLED

from paperglass.entrypoints.orchestrate_document_medication_grader import GraderOrchestrationAgent

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

SPAN_BASE: str = "CONTROLLER:orchestrator:"
from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils
from opentelemetry.trace.status import Status, StatusCode
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

CHECK_FOR_NEW_DOCUMENT_INTERVAL_IN_MINS = 30


documents_processed = []
async def check_for_new_document_and_trigger_orchestration(version):
    # Simulating the retrieval of documentId
    
    documents:List[Document] = await get_documents()
    LOGGER.info("found %s documents", len(documents))
    if documents:
        for document in documents:
            # Check if a new documentId is added
            if document and document.id not in documents_processed:
                # Execute the function when a new documentId is added
                LOGGER.info("New document found: %s", document.id)
                documents_processed.append(document.id)
                if version == "2":
                    await orchestrate_v2(document)

@inject
async def get_documents(query_adapter:IQueryPort):
    # Replace this with your logic to retrieve the documentId
    # For example, you can fetch it from a database or an API
    # Return None if no new documentId is available
    timestamp_to_check = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=CHECK_FOR_NEW_DOCUMENT_INTERVAL_IN_MINS)
    return await query_adapter.get_documents_by_created(timestamp_to_check.isoformat())

@inject
async def get_document(document_id:str,query_adapter:IQueryPort):
    doc = await query_adapter.get_document(document_id=document_id)
    
    return Document(**doc)

@inject
async def orchestrate_for_new_transaction(app_id:str,tenant_id:str,patient_id:str,document_id:str,command_handler:ICommandHandlingPort):
    document = await command_handler.handle_command(GetDocument(app_id=app_id,tenant_id=tenant_id,patient_id=patient_id, document_id=document_id))
    return await orchestrate_v2(document,command_handler)

@inject
async def orchestrate_with_default_document_operations(document:Document,command_handler:ICommandHandlingPort,query:IQueryPort):
    document_operation_instance:DocumentOperationInstance = None
    step_id_in_progress = None
    try:
        operation_context = {}
        # creating a default document operation definition if it doesnt' exist
        # this should be only for local dev, in cloud deployed version we will have this passed as argument to the orchestrator
        doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)
        doc_operation_definition = None
        doc_operation_definition_id = None
        if not doc_operation_definitions:
            doc_operation_definition:DocumentOperationDefinition = await command_handler.handle_command(CreateDefaultMedicationDocumentOperationDefinition(app_id=document.app_id, tenant_id=document.tenant_id))
            doc_operation_definition_id = doc_operation_definition.id
        else:
            doc_operation_definition = doc_operation_definitions[0]
            doc_operation_definition_id = doc_operation_definitions[0].id
            LOGGER.info("Found exiting definition: %s", doc_operation_definition_id)

        # create new DocumentOperationInstance
        document_operation_instance:DocumentOperationInstance = await command_handler.handle_command(CreateDocumentOperationInstance(app_id=document.app_id, 
                                                                                                                                     tenant_id=document.tenant_id,
                                                                                                                                     patient_id=document.patient_id,
                                                                                                                                     document_id=document.id,
                                                                                                                                     document_operation_definition_id=doc_operation_definition_id,
                                                                                                                                     status=DocumentOperationStatus.IN_PROGRESS
                                                                                                                                     ))
        
        # step_id_in_progress = DocumentOperationStep.SPLIT_PAGES
        # document:Document = await command_handler.handle_command(SplitPages(document_operation_instance_id=document_operation_instance.id, 
        #                                                                     document_operation_definition_id=doc_operation_definition_id,
        #                                                                     app_id=document.app_id, 
        #                                                                     tenant_id=document.tenant_id,
        #                                                                     patient_id=document.patient_id,
        #                                                                     document_id=document.id))
        
        # custom_prompt = """
        # As an expert transcriber, generate a table of contents for this document. For each entry in the table of contents, include metadata such as document type, section, page, number of medications in that section, and number of medical conditions referenced in that section.  

        # Document name is at the first page of the document at the top.  Document name should not include the patient's name, company name, or location.  A good candidate is a name near the word form.
        
        # Datetimes will be expressed in ISO-8601 format with the timezone component
        # Dates will be expressed in ISO-8601 format with only the date component
        # Discharge date may also be a date near DC Date.
        # Documents with a discharge date are likely to be a DischargeSummary document type
        # Do not include duplicate medication names in the same section
        
        # Output the data in JSON format of:
        
        # {
        # "docs": [
        #     {
        #     "name": "**Name of the source document",
        #     "date": "**Date of the document in ISO-8601 format",
        #     "discharged": "**Discharge date for the patient in ISO-8601 format",
        #     "type": "**Type of document using FHIR composition type",
        #     "section": [
        #         {
        #             "name': "**Section name",
        #             "pages": {
        #                 "s": "**Starting page for the section",
        #                 "e": "**Ending page for the section",
        #             },
        #             "meds": [
        #                     {
        #                     "name": "**Medication name only for medications referenced in this section. Do not include dosage in the name.",
        #                     "meta": {
        #                         "page": "**For evidence, the page number this medication was noted. This field should be an integer not a string"
        #                     }
        #                 }
        #             ]
        #         }
        #         ]
        #     }
        # ]
        # }
        # """
        # step_id_in_progress = DocumentOperationStep.CUSTOM_STEP
        # page:Page=await command_handler.handle_command(ExecuteCustomPrompt(app_id=document.app_id,
        #                                                             tenant_id=document.tenant_id,
        #                                                             patient_id=document.patient_id,
        #                                                             document_operation_instance_id=document_operation_instance.id,
        #                                                             document_operation_definition_id=doc_operation_definition_id,
        #                                                             document_id=document.id,
        #                                                             doc_storage_uri=document.storage_uri,
        #                                                             context={"prompt":custom_prompt},
        #                                                             step_id = DocumentOperationStep.CUSTOM_STEP,
        #                                                             prompt=doc_operation_definition.step_config.get(DocumentOperationStep.CUSTOM_STEP.value,{"prompt":custom_prompt}).get("prompt"),
        #                                                             model = doc_operation_definition.step_config.get(DocumentOperationStep.CUSTOM_STEP.value,{"model":"gemini-1.5-flash-001"}).get("model")
        #                                                             ))

        for document_page in document.pages:
            # we will process each page in the document in sequence and if something fails,
            # we will log the error and continue with the next page
            try:
                page_number = document_page.number
                LOGGER.debug("Processing page %s", page_number)

                # step_id_in_progress = DocumentOperationStep.CREATE_PAGE
                # page:Page=await command_handler.handle_command(CreatePage(document_operation_instance_id=document_operation_instance.id,
                #                                                             document_operation_definition_id=doc_operation_definition_id,
                #                                                             app_id=document.app_id, 
                #                                                             tenant_id=document.tenant_id,
                #                                                             patient_id=document.patient_id,
                #                                                             document_id=document.id,
                #                                                             page_number=page_number,
                #                                                             storage_uri=document_page.storage_uri))
                # #page:Page = Page(**await query_adapter.get_page(document_id=document.id, page_number=page_number))
                # step_id_in_progress = DocumentOperationStep.PERFORM_OCR
                # page:Page=await command_handler.handle_command(PerformOCR(document_operation_instance_id=document_operation_instance.id,
                #                                                         document_operation_definition_id=doc_operation_definition_id,
                #                                                         app_id=document.app_id, 
                #                                                         tenant_id=document.tenant_id,
                #                                                         patient_id=document.patient_id,
                #                                                         document_id=document.id, 
                #                                                         page_id=page.id))
                
                # step_id_in_progress = DocumentOperationStep.TEXT_EXTRACTION
                # page:Page=await command_handler.handle_command(ExtractText(app_id=document.app_id, 
                #                                                         tenant_id=document.tenant_id,
                #                                                         patient_id=document.patient_id,
                #                                                         document_operation_instance_id=document_operation_instance.id,
                #                                                         document_operation_definition_id=doc_operation_definition_id,
                #                                                         document_id=document.id, 
                #                                                         page_id=page.id, 
                #                                                         page_number=page_number,
                #                                                         prompt=doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION.value).get("prompt"),
                #                                                         model = doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION.value).get("model")
                #                                                         ))

                # step_id_in_progress = DocumentOperationStep.CLASSIFICATION
                # classified_page:ClassifiedPage = await command_handler.handle_command(ClassifyPage(app_id=document.app_id, 
                #                                                                                     tenant_id=document.tenant_id,
                #                                                                                     patient_id=document.patient_id,
                #                                                                                     document_operation_instance_id=document_operation_instance.id,
                #                                                                                     document_operation_definition_id=doc_operation_definition_id,
                #                                                                                     document_id=document.id, 
                #                                                                                     page_id=page.id,
                #                                                                                     page_text=page.text,
                #                                                                                     prompt=doc_operation_definition.step_config.get(DocumentOperationStep.CLASSIFICATION.value).get("prompt"),
                #                                                                                     model = doc_operation_definition.step_config.get(DocumentOperationStep.CLASSIFICATION.value).get("model")
                #                                                                                 ))
                step_id_in_progress = DocumentOperationStep.CLASSIFICATION
                page_dict = await query.get_page(document_id=document.id, page_number=page_number)
                if not page_dict:
                    continue
                page:Page = Page(**page_dict)
                classified_page = await query.get_classified_page(page_id=page.id)
                label = "medications"
                
                if classified_page:
                    labelled_content = [x.get(label) for x in classified_page.labels if x and label in x.keys()]
                    if labelled_content:
                        step_id_in_progress = DocumentOperationStep.MEDICATIONS_EXTRACTION
                        extracted_medications:List[ExtractedMedication] = await command_handler.handle_command(ExtractMedication(app_id=document.app_id, 
                                                                                                            tenant_id=document.tenant_id,
                                                                                                            patient_id=document.patient_id,
                                                                                                            document_operation_instance_id=document_operation_instance.id,
                                                                                                            document_operation_definition_id=doc_operation_definition_id,
                                                                                                            document_id=document.id, 
                                                                                                            page_id=page.id,
                                                                                                            page_number=page.number, 
                                                                                                            labelled_content=labelled_content,
                                                                                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.MEDICATIONS_EXTRACTION.value).get("prompt"),
                                                                                                            model=doc_operation_definition.step_config.get(DocumentOperationStep.MEDICATIONS_EXTRACTION.value).get("model")
                                                                                                            ))
                        if extracted_medications:
                            medications_to_search_for = []
                            for extracted_medication in extracted_medications:
                                # create or update medication profile
                                medication_string = f"""
                                "name":{extracted_medication.medication.name},
                                "dosage":{extracted_medication.medication.dosage},
                                "frequency":{extracted_medication.medication.frequency},
                                "route":{extracted_medication.medication.route},
                                "start_date":{extracted_medication.start_date},
                                "end_date":{extracted_medication.end_date},
                                "reason":{extracted_medication.reason}
                                """
                                
                                medications_to_search_for.append(medication_string)
                            step_id_in_progress = DocumentOperationStep.EVIDENCE_CREATION
                            evidences = await command_handler.handle_command(CreateEvidence(app_id=document.app_id, 
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_operation_instance_id=document_operation_instance.id,
                                                                                            document_operation_definition_id=doc_operation_definition_id,
                                                                                            document_id=document.id, 
                                                                                            page_id=page.id,
                                                                                            page_number=page.number, 
                                                                                            medications=medications_to_search_for,
                                                                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.EVIDENCE_CREATION.value).get("prompt"),
                                                                                            model=doc_operation_definition.step_config.get(DocumentOperationStep.EVIDENCE_CREATION.value).get("model")
                                                                                        ))
                            step_id_in_progress = DocumentOperationStep.MEDICATION_PROFILE_CREATION                                                          
                            medication_profile=await command_handler.handle_command(CreateorUpdateMedicationProfile(app_id=document.app_id,
                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                        patient_id=document.patient_id,
                                                                                                                        document_operation_instance_id=document_operation_instance.id,
                                                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                                                        document_id=document.id, 
                                                                                                                        extracted_medications=extracted_medications,
                                                                                                                        step_id = DocumentOperationStep.MEDICATION_PROFILE_CREATION
                                                                                                                        ))
            except Exception as e:
                LOGGER.error("Error occured in step %s (stack trace in DocumentOperationInstanceLog): %s", step_id_in_progress, str(e))
                if document:
                    operation_context['error'] = exceptionToMap(e)
                    if document_operation_instance and doc_operation_definition_id:
                        doc_operation_instance_log = await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                                                            step_id=step_id_in_progress,
                                                                                                                            description="Error occured during orchestration",
                                                                                                                            tenant_id=document.tenant_id,
                                                                                                                            patient_id=document.patient_id,
                                                                                                                            document_id=document.id, 
                                                                                                                            document_operation_instance_id=document_operation_instance.id,
                                                                                                                            document_operation_definition_id=doc_operation_definition_id,
                                                                                                                            status=DocumentOperationStatus.FAILED, 
                                                                                                                            context=operation_context))
                    else:
                        LOGGER.error("Whoops, no DocumentOperationInstanceLog for this operation.  Error occured during orchestration of step %s: %s :::: %s", step_id_in_progress, str(e), traceback.format_exc())
   
        # create/update DocumentOperation with above instance as active instance for the doc so that frontend can switch to this instance results
        document_operation:DocumentOperation = await command_handler.handle_command(CreateOrUpdateDocumentOperation(app_id=document.app_id, 
                                                                                                            tenant_id=document.tenant_id,
                                                                                                            patient_id=document.patient_id,
                                                                                                            document_id=document.id,
                                                                                                            active_document_operation_definition_id=doc_operation_definition_id,
                                                                                                            active_document_operation_instance_id=document_operation_instance.id,
                                                                                                            status = DocumentOperationStatus.COMPLETED
                                                                                                            ))
        LOGGER.info(f"Orchestration completed for document: {document.id}. please refer document operation instance id: {document_operation_instance.id}")
    except Exception as e:
        LOGGER.error("Error occured during orchestration for document %s: %s", document.id, str(e))
        if document:
            operation_context['error'] = exceptionToMap(e)
            if document_operation_instance and doc_operation_definition_id:
                doc_operation_instance_log = await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                                                    step_id=step_id_in_progress,
                                                                                                                    description="Error occured during orchestration",
                                                                                                                    tenant_id=document.tenant_id,
                                                                                                                    patient_id=document.patient_id,
                                                                                                                    document_id=document.id, 
                                                                                                                    document_operation_instance_id=document_operation_instance.id,
                                                                                                                    document_operation_definition_id=doc_operation_definition_id,
                                                                                                                    status=DocumentOperationStatus.FAILED, 
                                                                                                                    context=operation_context))
            else:
                LOGGER.error("Error occured during orchestration (with no documentOperationInstance and DocOperationDefinitionId): %s", getTrimmedStacktraceAsString(e))

@inject
async def orchestrate_for_custom_prompt(document:Document, command_handler:ICommandHandlingPort, query:IQueryPort):
    
    thisSpanName = "orchestrate_toc"
    with await opentelemetry.getSpan(thisSpanName) as span: 

        metric_starttime = time.time()
            
        LOGGER.debug("Entering orchestrate_for_custom_prompt...")

        model = "gemini-1.5-flash-001"
        
        document_operation_instance:DocumentOperationInstance = None
        operation_type = DocumentOperationType.TOC.value
        operation_name = "Table of Contents"
        operation_description = "Generates Table of Contents for the document"
        document_workflow_id = "toc"

        step_id_in_progress = None

        LOGGER.debug("Defining prompts...")
        system_prompt = """
        You are a document entity extraction specialist. Given a document, your task is to extract the values for user provided json schema.

        - The JSON schema must be followed during the extraction.
        - The values must only include text found in the document
        - Do not normalize any entity value.
        - If an entity is not found in the document, set the entity value to null.
        """

        custom_prompt = """
        As an expert medical transcriber, assess the PDF page extract the list of sections.  

        Rules:
        Internal page information can on the page in the form where internal page number} is separated from the internal page count by a slash (e.g. 1/4 is the first page in a four page document)
        The document name cannot include the patient name, company name, or location 
        Only extract medications if medications are in a list or a table
        Exclude medications if they are in an Administration or Diagnosis record
        Do not include the medication in the list of meds if it is missing the medication name.  If this occurs at the top of the page, it could indicate the section is a continuation from the prior section.

        For the page, output the following json: 
        {
            "doc": {
                "name": "Name of the document",
                "documentType": "FHIR Composition type for this document",        
                "internalPageNumber": "Internal page number printed on the page",
                "internalPageCount": "Internal page count printed on the page",
                "sections": [
                    {
                        "name": "Name of the section",
                        "isContinued": "Set to a boolean true if this section is a continuation from a previous page"
                        "meds": [
                            "name": "Name of the medication",
                            "dosage": "Dosage of the medication (e.g. 50 mg)",
                            "route": "Route of the medication (e.g. Oral, etc.)",
                            "form": "Form of the medication (e.g. Tab, Cap, etc.)"
                        ]
                    }        
                ]
            }    
        }
        """  

        try:        
            operation_context = {}
            # creating a default document operation definition if it doesnt' exist
            # this should be only for local dev, in cloud deployed version we will have this passed as argument to the orchestrator
            LOGGER.debug("Checking for existing DocumentOperationDefinition for %s operation type...", operation_type)
            doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = operation_type)
            doc_operation_definition = None
            doc_operation_definition_id = None

            if not doc_operation_definitions:
                LOGGER.info("No existing DocumentOperationDefinition found.  Creating new DocumentOperationDefinition...")
                
                step_config: Dict[str, Dict[str, str | Dict ] | Any] = {
                    DocumentOperationStep.TOC_SECTION_EXTRACTION.value: {
                        "model": model,
                        "system_prompts": [system_prompt],
                        "prompt": custom_prompt, 
                        "description":"Extract section data from the document page",
                    },
                    DocumentOperationStep.TOC_ASSEMBLY.value:{                    
                        "description":"Assemble page section information into document Table of Contents",
                    }
                }
                
                command = CreateDefaultMedicationDocumentOperationDefinition(
                        app_id=document.app_id, 
                        tenant_id=document.tenant_id,
                        document_workflow_id = document_workflow_id,
                        name = operation_name,
                        operation_type = operation_type,
                        operation_name = operation_name,
                        description = operation_description,
                        step_config = step_config
                )

                LOGGER.info("Creating new DocumentOperationDefinition: %s", command)
                doc_operation_definition:DocumentOperationDefinition = await command_handler.handle_command(command)
                doc_operation_definition_id = doc_operation_definition.id
                LOGGER.debug("Created new DocumentOperationDefinition with id: %s", doc_operation_definition_id)
            else:
                LOGGER.debug("Found existing definition for %s operation type", operation_type)
                doc_operation_definition = doc_operation_definitions[0]
                doc_operation_definition_id = doc_operation_definitions[0].id


            # create new DocumentOperationInstance
            LOGGER.debug("Creating DocumentOperationInstance for %s operation type...", operation_type)        
            command = CreateDocumentOperationInstance(app_id=document.app_id, 
                                                    tenant_id=document.tenant_id,
                                                    patient_id=document.patient_id,
                                                    document_id=document.id,
                                                    document_operation_definition_id=doc_operation_definition_id,
                                                    status=DocumentOperationStatus.IN_PROGRESS,
                                                    priority=OrchestrationPriority.DEFAULT
            )        
            document_operation_instance:DocumentOperationInstance = await command_handler.handle_command(command)
            LOGGER.debug("""Created DocumentOperationInstance with id: %s for document: %s""", document_operation_instance.id, document.id)        

            step_id_in_progress = DocumentOperationStep.TOC_SECTION_EXTRACTION

            doc_operation_instance_log = await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                                                step_id=step_id_in_progress,
                                                                                                                description="TOC orchestration began",
                                                                                                                tenant_id=document.tenant_id,
                                                                                                                patient_id=document.patient_id,
                                                                                                                document_id=document.id, 
                                                                                                                document_operation_instance_id=document_operation_instance.id,
                                                                                                                document_operation_definition_id=doc_operation_definition_id,
                                                                                                                status=DocumentOperationStatus.IN_PROGRESS, 
                                                                                                                context=operation_context))

            LOGGER.debug("Executing %s operation step %s for documentId %s:  Number of pages: %s", operation_type, step_id_in_progress, document.id, document.page_count)
            toc_pages: List[PageTOC] = []

            for page in document.pages:
                LOGGER.debug("Extracting TOC data for Document %s Page %s: %s", document.id, page.number, page)
                
                results = await command_handler.handle_command(ExecuteCustomPrompt(app_id=document.app_id,
                                                                        tenant_id=document.tenant_id,
                                                                        patient_id=document.patient_id,
                                                                        document_operation_instance_id=document_operation_instance.id,
                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                        document_id=document.id,
                                                                        page_number = page.number,
                                                                        doc_storage_uri=page.storage_uri,
                                                                        context={
                                                                            "prompt":custom_prompt,
                                                                            "system_prompt": system_prompt
                                                                        },
                                                                        step_id = DocumentOperationStep.TOC_SECTION_EXTRACTION,
                                                                        system_prompts = [system_prompt],
                                                                        prompt = doc_operation_definition.step_config.get(DocumentOperationStep.CUSTOM_STEP.value,{"prompt":custom_prompt}).get("prompt"),
                                                                        model = doc_operation_definition.step_config.get(DocumentOperationStep.CUSTOM_STEP.value,{"model":"gemini-1.5-flash-001"}).get("model")
                                                                        ))
                
                o:PageTOC = PageTOC(
                    id = str(uuid.uuid1()), 
                    document_id = document.id,
                    page_number = page.number,
                    page = page,
                    toc = results
                )    
                    
                toc_pages.append(o)

            
            # Assemble the TOC from page TOC data
            LOGGER.debug("Assembling TOC for Document %s with instance id %s", document.id, document_operation_instance.id)
            command = AssembleTOC(app_id=document.app_id,
                        tenant_id=document.tenant_id,
                        patient_id=document.patient_id,
                        document_id=document.id,
                        document_operation_instance_id=document_operation_instance.id,
                        document_operation_definition_id=doc_operation_definition_id,
                        pageTOCs=toc_pages,
                        context = {},
                        step_id = DocumentOperationStep.TOC_ASSEMBLY)
        
            LOGGER.debug("Executing %s operation step %s for documentId %s", operation_type, DocumentOperationStep.TOC_ASSEMBLY, document.id)
            await command_handler.handle_command(command)        
            LOGGER.debug("Completed %s operation step %s for documentId %s", operation_type, DocumentOperationStep.TOC_ASSEMBLY, document.id)

            # Set the document operation to current instance !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            LOGGER.debug("Create or Update DocumentOperation with active instance for documentId %s", document.id)
            doc_op: DocumentOperation = await command_handler.handle_command(CreateOrUpdateDocumentOperation(app_id=document.app_id, 
                                                                                tenant_id=document.tenant_id,
                                                                                patient_id=document.patient_id,
                                                                                document_id=document.id,
                                                                                operation_type=operation_type,
                                                                                active_document_operation_definition_id=doc_operation_definition_id,
                                                                                active_document_operation_instance_id=document_operation_instance.id,
                                                                                status = DocumentOperationStatus.COMPLETED
                                                                                ))
            LOGGER.debug("Completed TOC orchestration for documentId %s", document.id)

            metric_endtime = time.time()
            elapsed_time = metric_endtime - metric_starttime
            LOGGER.debug("METRIC:  Processing of document %s with %s pages took: %s seconds", document.id, document.page_count, elapsed_time)
            
            operation_context["elapsedtime"] = elapsed_time

            doc_operation_instance_log = await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                                                step_id=step_id_in_progress,
                                                                                                                description="TOC orchestration complete",
                                                                                                                tenant_id=document.tenant_id,
                                                                                                                patient_id=document.patient_id,
                                                                                                                document_id=document.id, 
                                                                                                                document_operation_instance_id=document_operation_instance.id,
                                                                                                                document_operation_definition_id=doc_operation_definition_id,
                                                                                                                status=DocumentOperationStatus.COMPLETED, 
                                                                                                                context=operation_context))

        except OrchestrationException as e:
            # Certain exceptions already have an instance_log created by the command handler.  Thie allows for us to log the error but not create duplicate instance log entries
            LOGGER.error("Error occured during TOC orchestration of documentId %s: %s", document.id, str(e))
            LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))
        except Exception as e:
            LOGGER.error("Error occurred running pipeline %s: %s", operation_type, e)
            if document:
                operation_context['error'] = exceptionToMap(e)
                if document_operation_instance and doc_operation_definition_id:
                    doc_operation_instance_log = await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                                                        step_id=step_id_in_progress,
                                                                                                                        description="Error occured during orchestration",
                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                        patient_id=document.patient_id,
                                                                                                                        document_id=document.id, 
                                                                                                                        document_operation_instance_id=document_operation_instance.id,
                                                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                                                        status=DocumentOperationStatus.FAILED, 
                                                                                                                        context=operation_context))
                else:
                    LOGGER.error("Error occured during TOC orchestration: %s", getTrimmedStacktraceAsString(e))


@inject
async def orchestrate(document:Document,command_handler:ICommandHandlingPort):
    try:
        # ToDo: chain pure functions with imperitive shells to complete the orchestration
        # in prod, we would be doing this via orchestrator tool such as integration tool
        execution_id = uuid.uuid4().hex
        #status = await command_handler.handle_command(LogDocumentStatus(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, status=DocumentStatusType.DOCUMENT_UPLOADED,message=""))
        document:Document = await command_handler.handle_command(SplitPages(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id))
        #document:Document = Document(**await query_adapter.get_document(document_id=document.id))
        for document_page in document.pages:
            page_number = document_page.number
            page:Page=await command_handler.handle_command(CreatePage(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, page_number=page_number,storage_uri=document_page.storage_uri))
            #page:Page = Page(**await query_adapter.get_page(document_id=document.id, page_number=page_number))
            page:Page=await command_handler.handle_command(PerformOCR(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, page_id=page.id))
            page:Page=await command_handler.handle_command(ExtractText(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, page_id=page.id, page_number=page_number))
            #page:Page = Page(**await query_adapter.get_page(document_id=document.id, page_number=page_number))
            classified_page:ClassifiedPage = await command_handler.handle_command(ClassifyPage(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, page_id=page.id,page_text=page.text,page_number=page_number))
            label = "medications"
            if classified_page:
                labelled_content = [x.get(label) for x in classified_page.labels if x and label in x.keys()]
                if labelled_content:
                    medications:List[Medication] = await command_handler.handle_command(ExtractMedication(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, page_id=page.id,page_number=page.number, labelled_content=labelled_content))
                    if medications:
                        medications_to_search_for = []
                        for medication in medications:
                            medication_string = f"""
                            "name":{medication.name},
                            "dosage":{medication.dosage},
                            "frequency":{medication.frequency},
                            "route":{medication.route},
                            "start_date":{medication.start_date},
                            "end_date":{medication.end_date},
                            "reason":{medication.reason}
                            """
                            
                            medications_to_search_for.append(medication_string)
                        evidences = await command_handler.handle_command(CreateEvidence(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, page_id=page.id,page_number=page.number, medications=medications_to_search_for))
        #status:DocumentStatus = await command_handler.handle_command(LogDocumentStatus(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, status=DocumentStatusType.COMPLETED, message=""))
        return execution_id
    except OrchestrationException as e:
        # Certain exceptions already have an instance_log created by the command handler.  Thie allows for us to log the error but not create duplicate instance log entries
        LOGGER.error("Error occured during TOC orchestration of documentId %s: %s", document.id, str(e))
        LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))
    except Exception as e:
        # TODO why is this being swallowed?
        if document:
            #status:DocumentStatus = await command_handler.handle_command(LogDocumentStatus(execution_id=execution_id,app_id=document.app_id, tenant_id=document.tenant_id,patient_id=document.patient_id,document_id=document.id, status=DocumentStatusType.FAILED, message=str(e)))
            pass
        return execution_id

@inject
async def orchestrate_v2(document:Document,command_handler:ICommandHandlingPort,query:IQueryPort):
    if 1==1:
        thisSpanName = "orchestrate_v2"
        with await opentelemetry.getSpan(thisSpanName) as span: 
            document_operation_instance:DocumentOperationInstance = None
            step_id_in_progress = None
            try:
                operation_context = {}
                # creating a default document operation definition if it doesnt' exist
                # this should be only for local dev, in cloud deployed version we will have this passed as argument to the orchestrator
                doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)
                doc_operation_definition = None
                doc_operation_definition_id = None
                if not doc_operation_definitions:
                    LOGGER.debug("No existing DocumentOperationDefinition found.  Creating new DocumentOperationDefinition...")
                    doc_operation_definition:DocumentOperationDefinition = await command_handler.handle_command(CreateDefaultMedicationDocumentOperationDefinition(app_id=document.app_id, tenant_id=document.tenant_id))
                    doc_operation_definition_id = doc_operation_definition.id
                else:
                    doc_operation_definition = doc_operation_definitions[0] #Future: pick the right one based on some logic
                    doc_operation_definition_id = doc_operation_definitions[0].id
                    LOGGER.debug("Found existing definition: %s", doc_operation_definition_id)

                # create new DocumentOperationInstance
                document_operation_instance:DocumentOperationInstance = await command_handler.handle_command(CreateDocumentOperationInstance(app_id=document.app_id, 
                                                                                                                                            tenant_id=document.tenant_id,
                                                                                                                                            patient_id=document.patient_id,
                                                                                                                                            document_id=document.id,
                                                                                                                                            document_operation_definition_id=doc_operation_definition_id,
                                                                                                                                            status=DocumentOperationStatus.IN_PROGRESS
                                                                                                                                            ))
                step_id_in_progress = DocumentOperationStep.SPLIT_PAGES

                # look for app or tenant config
                config:Configuration = await get_config(document.app_id, document.tenant_id)

                page_texts:List[PageText] = []
                
                if not config:
                    app_config:AppConfig = await command_handler.handle_command(CreateAppConfiguration(app_id=document.app_id))
                    config = app_config.config


                
                document:Document = await command_handler.handle_command(SplitPages(document_operation_instance_id=document_operation_instance.id, 
                                                                                    document_operation_definition_id=doc_operation_definition_id,
                                                                                    app_id=document.app_id, 
                                                                                    tenant_id=document.tenant_id,
                                                                                    patient_id=document.patient_id,
                                                                                    document_id=document.id))

                for document_page in document.pages:

                    page_number = document_page.number

                    

                    with await opentelemetry.getSpan(thisSpanName + ":page[" + str(page_number) + "]") as span1: 

                        # we will process each page in the document in sequence and if something fails,
                        # we will log the error and continue with the next page
                        try:
                            LOGGER.debug("Processing page %s", page_number)                            

                            step_id_in_progress = DocumentOperationStep.CREATE_PAGE
                            page:Page=await command_handler.handle_command(CreatePage(document_operation_instance_id=document_operation_instance.id,
                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_id=document.id,
                                                                                        page_number=page_number,
                                                                                        storage_uri=document_page.storage_uri))
                            #page:Page = Page(**await query_adapter.get_page(document_id=document.id, page_number=page_number))
                            step_id_in_progress = DocumentOperationStep.PERFORM_OCR
                            page:Page=await command_handler.handle_command(PerformOCR(document_operation_instance_id=document_operation_instance.id,
                                                                                    document_operation_definition_id=doc_operation_definition_id,
                                                                                    app_id=document.app_id, 
                                                                                    tenant_id=document.tenant_id,
                                                                                    patient_id=document.patient_id,
                                                                                    document_id=document.id, 
                                                                                    page_id=page.id))
                            
                            step_id_in_progress = DocumentOperationStep.TEXT_EXTRACTION
                            page:Page=await command_handler.handle_command(ExtractText(app_id=document.app_id, 
                                                                                    tenant_id=document.tenant_id,
                                                                                    patient_id=document.patient_id,
                                                                                    document_operation_instance_id=document_operation_instance.id,
                                                                                    document_operation_definition_id=doc_operation_definition_id,
                                                                                    document_id=document.id, 
                                                                                    page_id=page.id, 
                                                                                    page_number=page_number,
                                                                                    prompt=doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION.value).get("prompt"),
                                                                                    model = doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION.value).get("model")
                                                                                    ))
                            
                            page_texts.append(page_texts.append(PageText(text=page.text, pageNumber=page.number)))

                            step_id_in_progress = DocumentOperationStep.CLASSIFICATION
                            LOGGER.debug("Executing %s operation step %s for documentId %s:  Number of pages: %s", DocumentOperationType.MEDICATION_EXTRACTION.value, step_id_in_progress, document.id, document.page_count)
                            classified_page:ClassifiedPage = await command_handler.handle_command(ClassifyPage(app_id=document.app_id, 
                                                                                                                tenant_id=document.tenant_id,
                                                                                                                patient_id=document.patient_id,
                                                                                                                document_operation_instance_id=document_operation_instance.id,
                                                                                                                document_operation_definition_id=doc_operation_definition_id,
                                                                                                                document_id=document.id, 
                                                                                                                page_id=page.id,
                                                                                                                page_text=page.text,
                                                                                                                page_number=page.number,
                                                                                                                prompt=doc_operation_definition.step_config.get(DocumentOperationStep.CLASSIFICATION.value).get("prompt"),
                                                                                                                model = doc_operation_definition.step_config.get(DocumentOperationStep.CLASSIFICATION.value).get("model")
                                                                                                            ))
                            page_dict = await query.get_page(document_id=document.id, page_number=page_number)
                            if not page_dict:
                                LOGGER.warn("No page found for documentId %s and page number %s:  Continuing to next page", document.id, page_number)
                                continue
                            page:Page = Page(**page_dict)
                            LOGGER.debug("Getting classified page for documentId %s and page number %s", document.id, page_number)
                            classified_page = await query.get_classified_page(page_id=page.id)
                            label = "medications"
                            
                            if classified_page:
                                LOGGER.debug("Classified page found for documentId %s and page number %s", document.id, page_number)
                                labelled_content = [x.get(label) for x in classified_page.labels if x and label in x.keys()]
                                if labelled_content:
                                    LOGGER.debug("Labeled content found for documentId %s and page number %s", document.id, page_number)
                                    step_id_in_progress = DocumentOperationStep.MEDICATIONS_EXTRACTION
                                    extracted_medications:List[ExtractedMedication] = await command_handler.handle_command(ExtractMedication(app_id=document.app_id, 
                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                        patient_id=document.patient_id,
                                                                                                                        document_operation_instance_id=document_operation_instance.id,
                                                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                                                        document_id=document.id, 
                                                                                                                        page_id=page.id,
                                                                                                                        page_number=page.number, 
                                                                                                                        labelled_content=labelled_content,
                                                                                                                        prompt=doc_operation_definition.step_config.get(DocumentOperationStep.MEDICATIONS_EXTRACTION.value).get("prompt"),
                                                                                                                        model=doc_operation_definition.step_config.get(DocumentOperationStep.MEDICATIONS_EXTRACTION.value).get("model")
                                                                                                                        ))
                                    if extracted_medications:
                                        LOGGER.debug("Extracted medications found for documentId %s and page number %s", document.id, page_number)
                                        medications_to_search_for = []
                                        

                                        step_id_in_progress = DocumentOperationStep.MEDISPAN_MATCHING
                                        medispan_matched_medications = await command_handler.handle_command(MedispanMatching(
                                                        app_id=document.app_id,
                                                        tenant_id=document.tenant_id,
                                                        patient_id=document.patient_id,
                                                        document_operation_instance_id=document_operation_instance.id,
                                                        document_operation_definition_id=doc_operation_definition_id,
                                                        document_id=document.id, 
                                                        page_id=page.id,
                                                        page_number=page.number,
                                                        extracted_medications=extracted_medications,
                                                        prompt=doc_operation_definition.step_config.get(step_id_in_progress.value).get("prompt"),
                                                        model=doc_operation_definition.step_config.get(step_id_in_progress.value).get("model"),
                                                        step_id = step_id_in_progress                                                                                                
                                                    ))
                                        if medispan_matched_medications:                                            
                                            extracted_medications = medispan_matched_medications
                                        else:
                                            LOGGER.error("Medispan matching returned no results for documentId %s and page number %s with medications %s.  This is unexpected.  All medications will proceed forward as unlisted with no medispan match", document.id, page_number, extracted_medications)
                                  

                                        if ORCHESTRATION_MEDICALEXTRACTION_STEP_NORMALIZATION_ENABLED: 
                                            step_id_in_progress = DocumentOperationStep.NORMALIZE_MEDICATIONS
                                            normalized_extracted_medications = await command_handler.handle_command(NormalizeMedications(
                                                            app_id=document.app_id,
                                                            tenant_id=document.tenant_id,
                                                            patient_id=document.patient_id,
                                                            document_operation_instance_id=document_operation_instance.id,
                                                            document_operation_definition_id=doc_operation_definition_id,
                                                            document_id=document.id, 
                                                            extracted_medications=extracted_medications,
                                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.NORMALIZE_MEDICATIONS.value).get("prompt"),
                                                            model=doc_operation_definition.step_config.get(DocumentOperationStep.NORMALIZE_MEDICATIONS.value).get("model"),
                                                            step_id = DocumentOperationStep.NORMALIZE_MEDICATIONS,
                                                            page_number=page_number                                                 
                                                        ))
                                            if normalized_extracted_medications:
                                                extracted_medications = normalized_extracted_medications

                                        else:
                                            LOGGER.info("ORCHESTRATION_MEDICALEXTRACTION_STEP_NORMALIZATION_ENABLED is false.  Skipping normalization step.")


                                        #     medications_to_search_for.append(medication_string)
                                        step_id_in_progress = DocumentOperationStep.MEDICATION_PROFILE_CREATION                                                          
                                        medication_profile=await command_handler.handle_command(CreateorUpdateMedicationProfile(app_id=document.app_id,
                                                                                                                                    tenant_id=document.tenant_id,
                                                                                                                                    patient_id=document.patient_id,
                                                                                                                                    document_operation_instance_id=document_operation_instance.id,
                                                                                                                                    document_operation_definition_id=doc_operation_definition_id,
                                                                                                                                    document_id=document.id, 
                                                                                                                                    extracted_medications=extracted_medications if not config or config.extraction_persisted_to_medication_profile else [],
                                                                                                                                    step_id = DocumentOperationStep.MEDICATION_PROFILE_CREATION
                                                                                                                                    ))
                                        
                                    else:
                                        LOGGER.warn("No medications found for documentId %s and page number %s", document.id, page_number)

                            if config and config.extract_allergies and classified_page:
                                label_allergies = PageLabel.ALLERGIES.value
                                labelled_content_allergies = [x.get(label_allergies) for x in classified_page.labels if x and x.get(label_allergies) and label_allergies in x.keys()]
                                
                                if labelled_content_allergies:
                                    
                                    step_id_in_progress = DocumentOperationStep.ALLERGIES_EXTRACTION
                                    extracted_allergies:List[ExtractedClinicalData] = await command_handler.handle_command(ExtractClinicalData(app_id=document.app_id, 
                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                        patient_id=document.patient_id,
                                                                                                                        document_operation_instance_id=document_operation_instance.id,
                                                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                                                        document_id=document.id, 
                                                                                                                        page_id=page.id,
                                                                                                                        page_number=page.number, 
                                                                                                                        labelled_content=labelled_content_allergies,
                                                                                                                        prompt=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("prompt"),
                                                                                                                        model=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("model"),
                                                                                                                        clinical_data_type = PageLabel.ALLERGIES.value
                                                                                                                        ))
                                    
                            if config and config.extract_immunizations and classified_page:
                                label_immunizations = PageLabel.IMMUNIZATIONS.value
                                labelled_content_immunizations = [x.get(label_immunizations) for x in classified_page.labels if x and x.get(label_immunizations) and label_immunizations in x.keys()]
                                
                                if labelled_content_immunizations:
                                    
                                    step_id_in_progress = DocumentOperationStep.IMMUNIZATIONS_EXTRACTION
                                    extracted_immunizations:List[ExtractedClinicalData] = await command_handler.handle_command(ExtractClinicalData(app_id=document.app_id, 
                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                        patient_id=document.patient_id,
                                                                                                                        document_operation_instance_id=document_operation_instance.id,
                                                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                                                        document_id=document.id, 
                                                                                                                        page_id=page.id,
                                                                                                                        page_number=page.number, 
                                                                                                                        labelled_content=labelled_content_immunizations,
                                                                                                                        prompt=doc_operation_definition.step_config.get(DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value).get("prompt"),
                                                                                                                        model=doc_operation_definition.step_config.get(DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value).get("model"),
                                                                                                                        clinical_data_type = PageLabel.IMMUNIZATIONS.value
                                                                                                                        ))

                        except OrchestrationException as e:
                            # Certain exceptions already have an instance_log created by the command handler.  Thie allows for us to log the error but not create duplicate instance log entries
                            LOGGER.error("Error occured during TOC orchestration of documentId %s on page %s: %s", document.id, str(page_number), str(e))
                            LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))
                        except Exception as e:
                            LOGGER.error("Error occured in orchestration pipeline step '%s' for documentId: %s page %s: %s", step_id_in_progress, document.id, page_number, {str(e)})
                            if document:
                                operation_context['error'] = exceptionToMap(e)
                                if document_operation_instance and doc_operation_definition_id:
                                    doc_operation_instance_log = await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                                                                        step_id=step_id_in_progress,
                                                                                                                                        description="Error occured during orchestration",
                                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                                        patient_id=document.patient_id,
                                                                                                                                        document_id=document.id, 
                                                                                                                                        document_operation_instance_id=document_operation_instance.id,
                                                                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                                                                        status=DocumentOperationStatus.FAILED, 
                                                                                                                                        context=operation_context))
                                else:
                                    LOGGER.error("Error occured during orchestration: %s :::: %s ", str(e), traceback.format_exc())
                
                if config.extract_conditions:
                    step_id_in_progress = DocumentOperationStep.CONDITIONS_EXTRACTION
                    command = ExtractConditionsData(app_id=document.app_id,
                                                    tenant_id=document.tenant_id,
                                                    patient_id=document.patient_id,
                                                    document_id=document.id,
                                                    document_operation_instance_id=document_operation_instance.id,
                                                    document_operation_definition_id=doc_operation_definition_id,
                                                    page_texts=[x for x in page_texts if x and x.text and x.pageNumber],
                                                    step_id= DocumentOperationStep.CONDITIONS_EXTRACTION
                                                    )

                    results = await command_handler.handle_command(command)

                # create/update DocumentOperation with above instance as active instance for the doc so that frontend can switch to this instance results
                document_operation:DocumentOperation = await command_handler.handle_command(CreateOrUpdateDocumentOperation(app_id=document.app_id, 
                                                                                                                    tenant_id=document.tenant_id,
                                                                                                                    patient_id=document.patient_id,
                                                                                                                    document_id=document.id,
                                                                                                                    active_document_operation_definition_id=doc_operation_definition_id,
                                                                                                                    active_document_operation_instance_id=document_operation_instance.id,
                                                                                                                    status = DocumentOperationStatus.COMPLETED
                                                                                                                    ))
                
                LOGGER.info("Orchestration completed for document %s. Please refer document operation instance id: %s", document.id, document_operation_instance.id)

            except Exception as e:
                LOGGER.error("Error occured in orchestration pipeline step '%s' for documentId: %s: %s", step_id_in_progress, document.id, {str(e)})
                if document:
                    operation_context['error'] = exceptionToMap(e)
                    if document_operation_instance and doc_operation_definition_id:
                        doc_operation_instance_log = await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                                                            step_id=step_id_in_progress,
                                                                                                                            description="Error occured during orchestration",
                                                                                                                            tenant_id=document.tenant_id,
                                                                                                                            patient_id=document.patient_id,
                                                                                                                            document_id=document.id, 
                                                                                                                            document_operation_instance_id=document_operation_instance.id,
                                                                                                                            document_operation_definition_id=doc_operation_definition_id,
                                                                                                                            status=DocumentOperationStatus.FAILED, 
                                                                                                                            context=operation_context))
                    else:
                        LOGGER.error("Error occured during orchestration of document %s: %s :::: %s", document.id, str(e), traceback.format_exc())
    try:
        LOGGER.debug("Beginning orchestration of grader pipeline for document %s", document.id)
        await GraderOrchestrationAgent().orchestrate(document_id=document.id)
    except OrchestrationException as e:
        # Certain exceptions already have an instance_log created by the command handler.  Thie allows for us to log the error but not create duplicate instance log entries
        LOGGER.error("Error occured during Grader orchestration of documentId %s on page %s: %s", document.id, str(page_number), str(e))
        LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))
    except Exception as e:
        LOGGER.error("Error occured in grader orchestration pipeline for documentId: %s", document.id, str(e))
        LOGGER.error("Error occured during grader orchestration: %s :::: %s ", str(e), getTrimmedStacktraceAsString(e))

    # LOGGER.info("Beginning orchestration of TOC pipeline for document %s", document.id)
    # await orchestrate_for_custom_prompt(document)
    

# Run once or in a loop based on mode provided

async def run(mode,version,documentId):

    LOGGER.warn("Environment: %s", STAGE)

    if mode == 'pulse':
        # Code for mode1
        await check_for_new_document_and_trigger_orchestration(version)
    elif mode == 'loop':
        # Code for mode2
        while True:
            await check_for_new_document_and_trigger_orchestration(version)
            await asyncio.sleep(10)  # Adjust the sleep duration as per your requirements
    elif mode == "single":
        # Code for mode3
        document = await get_document(document_id=documentId)
        if version == '1':
            await orchestrate(document)
        else:
            await orchestrate_v2(document)
    else:
        print('Invalid mode specified')
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Orchestrator')
    parser.add_argument('--mode', type=str, choices=['pulse', 'loop','single'], default='pulse', help='Specify the mode')
    parser.add_argument('--version', type=str, choices=['1', '2'], default='2', help='Specify the version')
    parser.add_argument('--documentId', type=str, help='Specify the documentId')

    args = parser.parse_args()
    asyncio.run(run(args.mode,args.version,args.documentId))

if __name__ == "__main__":   
    main()