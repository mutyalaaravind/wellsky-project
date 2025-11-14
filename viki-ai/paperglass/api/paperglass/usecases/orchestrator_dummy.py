import sys,os
import traceback
import uuid

import datetime
import time
from typing import Any, List, Dict
from kink import inject

from paperglass.domain.string_utils import to_int
from paperglass.domain.utils.auth_utils import get_token
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.time import now_utc
from paperglass.usecases.queue_resolver import QueueResolver
from paperglass.domain.models import AppConfig, AppTenantConfig, ClassifiedPage, Document, DocumentOperation, DocumentOperationDefinition, DocumentOperationInstance, DocumentOperationInstanceLog, DocumentStatus, EntityRetryConfig, ExtractedClinicalData, ExtractedMedication,ExtractedConditions, Medication, OperationMeta,Page, PageLabel, MedicalCodingRawData, PageOperation
from paperglass.domain.model_toc import PageTOC, DocumentTOC
from paperglass.usecases.configuration import get_config
from paperglass.usecases.commands import (
    CheckForAllPageOperationExtractionCompletion,
    ClassifyPage,
    CreateAppConfiguration, 
    CreateDefaultMedicationDocumentOperationDefinition, 
    CreateOrUpdateDocumentOperation, 
    CreateDocumentOperationInstance, 
    CreateDocumentOperationInstanceLog, 
    CreateEvidence,
    CreateOrUpdateEntityRetryConfiguration, 
    CreatePage, 
    CreateorUpdateMedicationProfile, 
    CreateorUpdateMedicationProfile,
    CreateorUpdatePageOperation, 
    ExecuteCustomPrompt,
    ExtractClinicalData, 
    ExtractMedication, 
    ExtractConditions,
    ExtractText,
    ExtractTextAndClassify, 
    GetDocument,
    GetDocumentLogs, 
    MedispanMatching,
    PerformOCR, 
    SplitPages, 
    AssembleTOC,
    ExtractConditionsData,
    UpdateDocumentOperationInstance,
)
from paperglass.interface.ports import ICommandHandlingPort, IMedispanMatchCommandHandlingPort
from paperglass.domain.values import Configuration, DocumentOperationStatus, DocumentOperationStep, DocumentStatusType, PageOperationStatus, PageText, Result
from paperglass.usecases.commands import ClassifyPage, CreateDefaultMedicationDocumentOperationDefinition, CreateOrUpdateDocumentOperation, CreateDocumentOperationInstance, CreateDocumentOperationInstanceLog, CreateEvidence, CreatePage, CreateorUpdateMedicationProfile, ExecuteCustomPrompt, ExtractMedication, ExtractText, GetDocument, PerformOCR, SplitPages, AssembleTOC, NormalizeMedications
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.values import (
    DocumentOperationStatus, 
    DocumentOperationStep, 
    DocumentStatusType, 
    DocumentOperationType,
    OrchestrationPriority
)
from paperglass.infrastructure.ports import ICloudTaskPort, IMessagingPort, IQueryPort, IPromptAdapter, IStoragePort, IUnitOfWorkManagerPort

from paperglass.domain.models_common import EntityFilter, OrchestrationException, OrchestrationExceptionWithContext
from paperglass.domain.utils.exception_utils import exceptionToMap, getTrimmedStacktraceAsString

import asyncio
import argparse
import json

from paperglass.settings import CLOUD_PROVIDER, CLOUD_TASK_QUEUE_NAME, GCP_LOCATION_2, SELF_API, SERVICE_ACCOUNT_EMAIL, STAGE,ORCHESTRATION_MEDICALEXTRACTION_STEP_NORMALIZATION_ENABLED

from paperglass.usecases.evidence_linking import EvidenceLinking

from paperglass.entrypoints.orchestrate_document_medication_grader import GraderOrchestrationAgent
from paperglass.settings import EXTRACTION_PUBSUB_TOPIC_NAME
from paperglass.log import getLogger, CustomLogger
LOGGER = CustomLogger(__name__)

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.domain.context import Context
context = Context()

SPAN_BASE: str = "CONTROLLER:orchestrator:"
from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils
from opentelemetry.trace.status import Status, StatusCode
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

@inject()
async def orchestrate(document_id: str, force_new_instance:bool, priority:OrchestrationPriority, command_handler:ICommandHandlingPort, query:IQueryPort):
    thisSpanName = "orchestrate_v3_dummy"
    extra = {
        "document_id": document_id,
        "force_new_instance": force_new_instance,
        "priority": str(priority),
    }
    with await opentelemetry.getSpan(thisSpanName) as span:
        LOGGER.debug("Running orchestrate_v3_dummy", extra=extra)        
        try:

            document = await query.get_document(document_id=document_id)
            document = Document(**document)

            # Retrieve the log entry for SPLIT_PAGES
            filter_json = {
                "filterCriterion": [
                    {
                    "entity_name": "step_id",
                    "values": ["SPLIT_PAGES"]
                    }
                ]
            }

            filter = EntityFilter(**filter_json)            
            command_logs = GetDocumentLogs(app_id=document.app_id, 
                                           tenant_id=document.tenant_id, 
                                           patient_id=document.patient_id, 
                                           document_id=document_id, 
                                           filter=filter)                                    
            
            logs = await command_handler.handle_command(command_logs)            

            if logs:
                log_inner = logs["MEDICATION_EXTRACTION"]
                log = log_inner[0]

                # Get page_count from context["page_count"]
                page_count = to_int(log.context["page_count"])               
                
                

                # Submit a Cloud Task for each page in the document
                LOGGER.warning("Submitting Cloud Tasks for %s pages", page_count, extra=extra)
                for page in document.pages:
                    await TriggerAgent().start_page_classification_pipeline(
                        app_id=document.app_id,
                        tenant_id=document.tenant_id,
                        patient_id=document.patient_id,
                        document_id=document.id,
                        page_number = page.number,
                        page_storage_uri = page.storage_uri,
                        query=query
                    )

            else:
                LOGGER.error("No logs found for SPLIT_PAGES", extra=extra)            

        except (Exception,OrchestrationExceptionWithContext) as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Error in load test poke: %s", str(e), extra=extra)
            raise e

"""
For each page, run ocr , extract text and classify

"""
class PageClassificationAgent:
    
    @inject()
    async def orchestrate(self, document_id: str, page_number: int, page_storage_uri: str, 
                          query:IQueryPort, command_handler:ICommandHandlingPort, pubsub_adapter:IMessagingPort, prompt: IPromptAdapter):
        thisSpanName = "orchestrate_v3"
        document=None
        
        extra = {
            "document_id": document_id,
            "page_number": page_number,
            "page_storage_uri": page_storage_uri,
            "labels": ["loadtest"]
        }
        with await opentelemetry.getSpan(thisSpanName) as span: 
            start_time = now_utc()
            step_id_in_progress = None
            try:
                
                LOGGER.debug("Processing page %s", page_number)

                document:Document = Document(**await query.get_document(document_id=document_id))

                # Retrieve the log entry
                command_logs = GetDocumentLogs(app_id=document.app_id, 
                                            tenant_id=document.tenant_id, 
                                            patient_id=document.patient_id, 
                                            document_id=document_id, 
                                            filter=None)
                
                logs_full = await command_handler.handle_command(command_logs)            
                logs = []

                if logs_full:
                    logs = logs_full["MEDICATION_EXTRACTION"]                                

                step_id_in_progress = DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION
                extra["step"] = step_id_in_progress
                extra["step_id"] = step_id_in_progress

                
                await self.step_text_extract_and_classify(document_id, page_number, page_storage_uri, logs)                                        
                
                LOGGER.info("StepGroup:PageClassification wait time", extra=extra)
                
                span.set_attribute("step", step_id_in_progress)
                LOGGER.info("Document orchestration page classification completed for documentId %s and page number: %s", document.id, page_number, extra=extra)

                LOGGER.info("StepGroup: Orchestration Page Classification", extra=extra)

                await TriggerAgent().start_extraction_pipeline(
                    app_id=document.app_id,
                    tenant_id=document.tenant_id,
                    patient_id=document.patient_id,
                    document_id=document.id,                    
                    page_number=page_number,
                    page_storage_uri=page_storage_uri,                    
                    query=query
                )
                
                return Result(success=True, message="Page classification completed successfully")

            except (Exception,OrchestrationExceptionWithContext) as e:
                elapsed_time = (now_utc() - start_time).total_seconds()
                extra.update({
                    "error": exceptionToMap(e),
                    "step_group": "PageClassification",
                    "step_id": step_id_in_progress,
                    "elapsed_time": elapsed_time
                })
                LOGGER.error("Error in orchestrate_v3: %s for document: %s", traceback.format_exc(), document_id, extra=extra)
                LOGGER.info("Orchestration failed", extra=extra)
                return Result(success=False, error_message="Error in orchestrate_v3: %s" % traceback.format_exc())
            

    @inject()
    async def step_text_extract_and_classify(self, document_id: str, page_number: int, page_storage_uri: str, 
                          logs: List[Dict], 
                          query:IQueryPort, prompt_adapter: IPromptAdapter):
        with await opentelemetry.getSpan("step_text_extract_and_classify") as span: 
            step_id_in_progress = DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION

            LOGGER.debug("Running step_text_extract_and_classify")

            start_time = now_utc()

            extra = {
                "document_id": document_id,
                "page_number": page_number,
                "step_id": step_id_in_progress                
            }

            try:

                filter_json = {
                    "filterCriterion": [
                        {
                        "entity_name": "step_id",
                        "values": ["TEXT_EXTRACTION_AND_CLASSIFICATION"]
                        },
                        {
                        "entity_name": "context.page_number",
                        "values": [str(page_number)]
                        }
                    ]
                }
                filter = EntityFilter(**filter_json) 
                
                logs_filtered = filter.filter(logs)

                if logs_filtered:
                    log = logs_filtered[0]

                    LOGGER.debug("Log: %s", json.dumps(log.dict(), indent=2, cls=DateTimeEncoder))

                    opMeta:OperationMeta = OperationMeta(
                        type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                        step = DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION,
                        document_id = document_id,
                        page_number = page_number,
                        document_operation_def_id = None,
                        document_operation_instance_id = None,
                    )

                    prompt = log.context["prompt"]
                    model = log.context["model"]["name"]
                    expected_response = log.context["model_response"]
                    
                    prompts = [prompt, (page_storage_uri, "application/pdf")]
                    result = await prompt_adapter.multi_modal_predict_2(prompts, model, metadata=opMeta.dict())
                    
                    elapsed_time = (now_utc() - start_time).total_seconds()
                    extra.update({
                        "elapsed_time": elapsed_time,
                        "result_as_expected": result == expected_response
                    })
                    extra.update(opMeta.dict())                    
                    
                    LOGGER.info("Step::%s completed", step_id_in_progress, extra=extra)

            except Exception as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error("Error in step %s: %s", step_id_in_progress, str(e), extra=extra)
                raise e
        

"""
for each page classified, extract medication data
"""
class MedicationExtractionAgent:
    
    @inject
    async def orchestrate(self, document_id:str, page_number:int, page_storage_uri, query:IQueryPort, command_handler:ICommandHandlingPort, prompt_adapter:IPromptAdapter):
        
        step_id_in_progress = DocumentOperationStep.MEDICATIONS_EXTRACTION
        thisSpanName = "orchestrate_v3"
        step_id_in_progress = None
        start_time = now_utc()
        extra = {
            "document_id": document_id,
            "page_number": page_number,
            "page_storage_uri": page_storage_uri,
            "labels": ["loadtest"]
        }
        with await opentelemetry.getSpan(thisSpanName) as span:
            try: 
                
                document = Document(**await query.get_document(document_id=document_id))

                # Retrieve the log entry for step
                filter_json = {
                    "filterCriterion": [
                        {
                        "entity_name": "context.page_number",
                        "values": [str(page_number)]
                        }
                    ]
                }
                filter = EntityFilter(**filter_json)

                command_logs = GetDocumentLogs(app_id=document.app_id, 
                                            tenant_id=document.tenant_id, 
                                            patient_id=document.patient_id, 
                                            document_id=document_id, 
                                            filter=filter)
                
                logs_full = await command_handler.handle_command(command_logs)            
                logs = []

                if logs_full:
                    logs = logs_full["MEDICATION_EXTRACTION"]
                
                document = Document(**await query.get_document(document_id=document_id))                
                
                extra.update({
                    "app_id": document.app_id,
                    "tenant_id": document.tenant_id,
                    "patient_id": document.patient_id,                    
                    "step_id": step_id_in_progress
                })
                
                # Extract Medications -------------------------------------------------------------------------------------------------------------------------
                step_id_in_progress = DocumentOperationStep.MEDICATIONS_EXTRACTION
                extra["step_id"] = step_id_in_progress
                filter_json = {
                    "filterCriterion": [
                        {
                        "entity_name": "step_id",
                        "values": [step_id_in_progress.value]
                        },
                        {
                        "entity_name": "context.page_number",
                        "values": [str(page_number)]
                        }
                    ]
                }
                filter = EntityFilter(**filter_json)

                f_logs = filter.filter(logs)
                this_log = f_logs[0] if f_logs else None

                if this_log:
                    LOGGER.warning("Log found for step %s", step_id_in_progress, extra=extra)

                    await self.step_medication_extraction(document, page_number, page_storage_uri, this_log, query, command_handler, prompt_adapter)
                else:
                    LOGGER.warning("Log missing for step %s", step_id_in_progress, extra=extra)

                # Medispan Matching  -------------------------------------------------------------------------------------------------------------------------
                step_id_in_progress = DocumentOperationStep.MEDISPAN_MATCHING
                extra["step_id"] = step_id_in_progress
                filter_json = {
                    "filterCriterion": [
                        {
                        "entity_name": "step_id",
                        "values": [step_id_in_progress.value]
                        },
                        {
                        "entity_name": "context.page_number",
                        "values": [str(page_number)]
                        }
                    ]
                }
                filter = EntityFilter(**filter_json)

                f_logs = filter.filter(logs)
                this_log = f_logs[0] if f_logs else None

                if this_log:
                    LOGGER.warning("Log found for step %s", step_id_in_progress, extra=extra)

                    await self.step_medispan_matching(document, page_number, this_log, query, command_handler, prompt_adapter)
                                
                else:
                    LOGGER.warning("Log missing for step %s", step_id_in_progress, extra=extra)

                # -------------------------------------------------------------------------------------------------------------------------

                LOGGER.info("StepGroup: Orchestration Medication Extraction", extra=extra)

                elapsed_time = (now_utc() - start_time).total_seconds()

                extra["elapsed_time"] = elapsed_time
                LOGGER.info("Orchestration success", extra=extra)

                return Result(success=True, message="Medication extraction completed successfully")                

                                                                                            
            except (Exception,OrchestrationExceptionWithContext) as e:
                elapsed_time = (now_utc() - start_time).total_seconds()
                extra.update({
                    "error": exceptionToMap(e),
                    "step_group": "MedicationExtraction",
                    "step_id": step_id_in_progress,
                    "elapsed_time": elapsed_time
                })
                LOGGER.error("Error in orchestrate_v3: %s for document: %s", traceback.format_exc(), document_id, extra=extra)
                LOGGER.info("Orchestration failed", extra=extra)
                return Result(success=False, error_message="Error in orchestrate_v3: %s" % traceback.format_exc())

                    #if document_operation_instance_log:
                       # await send_recover_to_pubsub(document_operation_instance_log.id)



    async def step_medication_extraction(self, document, page_number, page_storage_uri, log, query, command_handler, prompt_adapter):
        step_id_in_progress = DocumentOperationStep.MEDICATIONS_EXTRACTION
        extra = {
            "app_id": document.app_id,
            "tenant_id": document.tenant_id,
            "patient_id": document.patient_id,
            "document_id": document.id,
            "page_number": page_number,
            "page_storage_uri": page_storage_uri,
            "step_id": step_id_in_progress,
            "labels": ["loadtest"]
        }

        start_time = now_utc()

        LOGGER.debug("Running step_medication_extraction", extra=extra)

        try:

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = step_id_in_progress,
                document_id = document.id,
                page_number = page_number,
                document_operation_def_id = None,
                document_operation_instance_id = None,
            )

            prompt = None
            if "prompt" in log.context:
                prompt = log.context["prompt"] 
            elif "llm_prompt" in log.context: # For backward compatibility
                prompt = log.context["llm_prompt"]
            
            model = log.context["model"]
            if isinstance(model, dict):  # For backward compatibility
                model = model["name"]            
            
            prompts = [(page_storage_uri, "application/pdf"), prompt[0]]

            result = await prompt_adapter.multi_modal_predict_2(prompts, model, metadata=opMeta.dict())
            LOGGER.debug("Result of medication_extraction: %s", result)

            elapsed_time = (now_utc() - start_time).total_seconds()
            extra.update({                
                "elapsed_time": elapsed_time,
            })
            LOGGER.info("Step::%s completed", step_id_in_progress, extra=extra)
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Error in step %s: %s", step_id_in_progress, str(e), extra=extra)
            raise e
  
    async def step_medispan_matching(self, document, page_number, log, query, command_handler, prompt_adapter):
        step_id_in_progress = DocumentOperationStep.MEDISPAN_MATCHING
        extra = {
            "app_id": document.app_id,
            "tenant_id": document.tenant_id,
            "patient_id": document.patient_id,
            "document_id": document.id,
            "page_number": page_number,
            "step_id": step_id_in_progress,
            "labels": ["loadtest"]
        }

        start_time = now_utc()

        LOGGER.debug("Running step_medispan_matching", extra=extra)

        try:

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = step_id_in_progress,
                document_id = document.id,
                page_number = page_number,
                document_operation_def_id = None,
                document_operation_instance_id = None,
            )

            model = log.context["model"]
            if isinstance(model, dict):  # For backward compatibility
                model = model["name"]   
            
            batch_contexts = log.context["batch_context"]

            if batch_contexts:
                for batch_context in batch_contexts:
                    prompt = batch_context["prompt"]

                    prompts = [prompt]

                    meta = opMeta.dict()
                    meta["batch_index"] = batch_context["batch_index"]
                    result = await prompt_adapter.multi_modal_predict_2(prompts, model, metadata=meta)

            elapsed_time = (now_utc() - start_time).total_seconds()
            extra.update({                
                "elapsed_time": elapsed_time,
            })
            LOGGER.info("Step::%s completed", step_id_in_progress, extra=extra)
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Error in step %s: %s", step_id_in_progress, str(e), extra=extra)
            raise e



class TriggerAgent:
    
    @inject()
    async def start_page_classification_pipeline(self, app_id:str, tenant_id:str, patient_id:str,
                                        document_id: str, 
                                        page_number:int,
                                        page_storage_uri:str,  
                                        query:IQueryPort,
                                        cloud_task_adapter:ICloudTaskPort,
                                        ):
        from paperglass.usecases.orchestrator_dummy import PageClassificationAgent, MedicationExtractionAgent
        
        from paperglass.settings import CLOUD_PROVIDER, GCP_LOCATION_2, SERVICE_ACCOUNT_EMAIL, SELF_API
        LOGGER.info(
            f'Got event that page no: {page_number}) is ready for further processing',
        )
    
        if CLOUD_PROVIDER == "local":
            await PageClassificationAgent().orchestrate(
                document_id=document_id,
                page_number=page_number,
                page_storage_uri=page_storage_uri
            )
        else:
            # call application integration which has cloud task to ensure it throttles
            start_time = now_utc()

            category="page_classification"
            priority = OrchestrationPriority.DEFAULT
            queue_name = QueueResolver().resolve_queue_name(category, priority)
            payload = {
                    "document_id": document_id,
                    "page_number": page_number,
                    "storage_uri": page_storage_uri,
                    "waittime_start": start_time.isoformat()
                }
            
            await cloud_task_adapter.create_task(
                token=get_token(app_id, tenant_id, patient_id),
                location=GCP_LOCATION_2,
                service_account_email=SERVICE_ACCOUNT_EMAIL,
                queue=queue_name,
                url=f"{SELF_API}/orchestrate_v3_page_classification_dummy",
                payload=payload
            )

            extra = {
                "app_id": app_id,
                "tenant_id": tenant_id,
                "patient_id": patient_id,
                "document_id": document_id,
                "page_number": page_number,
                "storage_uri": page_storage_uri,
                "category": category,
                "priority": priority,
                "queue_name": queue_name,
                "payload": payload
            }
            LOGGER.info("Submit CloudTask: %s", category, extra=extra)      

    @inject
    async def start_extraction_pipeline(self,app_id:str, tenant_id:str, patient_id:str,
                                        document_id: str,                                         
                                        page_number:int,
                                        page_storage_uri:str, 
                                        query:IQueryPort,
                                        cloud_task_adapter:ICloudTaskPort
                                        ):
        from paperglass.usecases.orchestrator_dummy import PageClassificationAgent, MedicationExtractionAgent
        LOGGER.info(
            f'Got event that page number: {page_number}) is ready for further processing',
        )
        
        
        if CLOUD_PROVIDER == "local":
            
            await MedicationExtractionAgent().orchestrate(
                document_id=document_id,                
                page_number=page_number,
                page_storage_uri=page_storage_uri   
            )

        else:
            # call application integration which has cloud task to ensure it throttles

            start_time = now_utc()
            
            priority = OrchestrationPriority.DEFAULT

            category="medication_extraction"
            url = f"{SELF_API}/orchestrate_v3_medication_extraction_dummy"
            queue_name = QueueResolver().resolve_queue_name(category, priority)           
            payload = {
                    "document_id": document_id,                                        
                    "page_number": page_number,
                    "storage_uri": page_storage_uri,
                    "waittime_start": start_time.isoformat()
                }
        
            extra = {
                "app_id": app_id,
                "tenant_id": tenant_id,
                "patient_id": patient_id,
                "document_id": document_id,                
                "page_number": page_number,
                "storage_uri": page_storage_uri,
                "category": category,
                "priority": priority,
                "queue_name": queue_name,
                "url": url,
                "payload": payload
            }
            
            await cloud_task_adapter.create_task(
                token=get_token(app_id, tenant_id, patient_id),
                location=GCP_LOCATION_2,
                service_account_email=SERVICE_ACCOUNT_EMAIL,
                queue=queue_name,
                url=url,
                payload=payload
            )
            
            LOGGER.info("Submit CloudTask: %s", category, extra=extra)


def get_args():
    parser = argparse.ArgumentParser(description='Orchestrate the extraction of medication data from a document')
    parser.add_argument('--document_id', type=str, help='The document id')
    parser.add_argument('--page_id', type=str, help='The page id')
    parser.add_argument('--page_number', type=int, help='The page number')
    parser.add_argument('--page_text', type=str, help='The page text')
    parser.add_argument('--tenant_id', type=str, help='The tenant id')
    parser.add_argument('--app_id', type=str, help='The app id')
    return parser.parse_args()