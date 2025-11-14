import sys,os
import traceback
import uuid

import datetime
import time
from typing import Any, List, Dict
from kink import inject

from paperglass.domain.utils.auth_utils import get_token
from paperglass.domain.time import now_utc
from paperglass.usecases.queue_resolver import QueueResolver
from paperglass.domain.models import AppConfig, AppTenantConfig, ClassifiedPage, Document, DocumentOperation, DocumentOperationDefinition, DocumentOperationInstance, DocumentOperationInstanceLog, DocumentOperationStatusSnapshot, DocumentStatus, EntityRetryConfig, ExtractedClinicalData, ExtractedMedication,ExtractedConditions, Medication,Page, PageLabel, MedicalCodingRawData, PageOperation
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
    MedispanMatching,
    PerformOCR, 
    SplitPages, 
    AssembleTOC,
    ExtractConditionsData,
    UpdateDocumentOperationInstance,
    UpdateDocumentStatusSnapshot,
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
from paperglass.infrastructure.ports import ICloudTaskPort, IMessagingPort, IQueryPort, IStoragePort, IUnitOfWorkManagerPort

from paperglass.domain.models_common import OrchestrationException, OrchestrationExceptionWithContext
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
    thisSpanName = "orchestrate_v3"
    extra = {
        "document_id": document_id,
        "force_new_instance": force_new_instance,
        "priority": str(priority),
    }
    with await opentelemetry.getSpan(thisSpanName) as span:
        LOGGER.debug("Running orchestrate_v3", extra=extra)
        document_operation_instance:DocumentOperationInstance = None
        step_id_in_progress:DocumentOperationStep = DocumentOperationStep.DOCUMENT_OPERATION_INSTANCE_CREATED
        document:Document = None
        try:
            operation_context = {}
            document:Document = Document(**await query.get_document(document_id))
            # creating a default document operation definition if it doesnt' exist
            # this should be only for local dev, in cloud deployed version we will have this passed as argument to the orchestrator
            doc_operation_definition = None
            doc_operation_definition_id = None
            doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)

            extra["app_id"] = document.app_id
            extra["tenant_id"] = document.tenant_id
            extra["patient_id"] = document.patient_id

            if not doc_operation_definitions:
                LOGGER.debug("No existing DocumentOperationDefinition found.  Creating new DocumentOperationDefinition...", extra=extra)
                doc_operation_definition:DocumentOperationDefinition = await command_handler.handle_command(CreateDefaultMedicationDocumentOperationDefinition(app_id=document.app_id, tenant_id=document.tenant_id))
                doc_operation_definition_id = doc_operation_definition.id                
            else:
                doc_operation_definition = doc_operation_definitions[0] #Future: pick the right one based on some logic
                doc_operation_definition_id = doc_operation_definitions[0].id                
                extra["document_operation_definition_id"] = doc_operation_definition_id
                LOGGER.debug("Found existing definition: %s", doc_operation_definition_id, extra=extra)

            extra["document_operation_definition_id"] = doc_operation_definition_id

            # check if last operation instance is in progress
            if not force_new_instance:
                doc_operation_instances:List[DocumentOperationInstance] = await query.get_document_operation_instances_by_document_id(document_id=document.id, operation_definition_id=doc_operation_definition_id)
                if doc_operation_instances:
                    doc_operation_instances.sort(key=lambda x: x.created_at, reverse=True)
                    most_recent_doc_operation_instance = doc_operation_instances[0]
                    if most_recent_doc_operation_instance.status == DocumentOperationStatus.IN_PROGRESS:
                        LOGGER.debug("Document operation instance in progress found.  Skipping orchestration for documentId %s", document.id, extra=extra)
                        return
            # create new DocumentOperationInstance
            document_operation_instance:DocumentOperationInstance = await command_handler.handle_command_with_explicit_transaction(CreateDocumentOperationInstance(app_id=document.app_id, 
                                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                                        patient_id=document.patient_id,
                                                                                                                                        document_id=document.id,
                                                                                                                                        document_operation_definition_id=doc_operation_definition_id,
                                                                                                                                        status=DocumentOperationStatus.IN_PROGRESS,
                                                                                                                                        priority=priority
                                                                                                                                        ))
            
            await command_handler.handle_command_with_explicit_transaction(UpdateDocumentStatusSnapshot(
                                                                            app_id=document.app_id,
                                                                            tenant_id=document.tenant_id,
                                                                            patient_id=document.patient_id,
                                                                            document_id=document.id,
                                                                            doc_operation_status_snapshot = DocumentOperationStatusSnapshot(
                                                                                operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                                                                                status=DocumentOperationStatus.IN_PROGRESS,
                                                                                start_time=now_utc().isoformat(),
                                                                                end_time=None
                                                                            )
                                                                            
            ))
            
            await DocumentProcessorAgent().orchestrate(document, document_operation_instance.id, doc_operation_definition_id)
            span.set_attribute("step", step_id_in_progress)
            span.set_attribute("document_operation_instance_id", document_operation_instance.id)
            span.set_attribute("document_operation_definition_id", doc_operation_definition_id)
            LOGGER.info("Document orchestration started for documentId %s, document operation instance Id: %s", document.id,document_operation_instance.id, extra=extra)
        except (Exception,OrchestrationExceptionWithContext) as e:
            LOGGER.error("Error in orchestrate_v3: %s", traceback.format_exc(), extra=extra)
            if document:
                await command_handler.handle_command_with_explicit_transaction(CreateDocumentOperationInstanceLog(app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_id=document.id,
                                                                                        document_operation_definition_id=doc_operation_definition_id, 
                                                                                        document_operation_instance_id=document_operation_instance.id if document_operation_instance else "unknown", 
                                                                                        step_id=step_id_in_progress, 
                                                                                        page_number=-1,
                                                                                        context={"error":e.context if hasattr(e,"context") else traceback.format_exc()},
                                                                                        status=DocumentOperationStatus.FAILED,
                                                                                        description="Error in orchestrate_v3"
                                                                                        ))
                
            return


@inject()
async def recover(failed_instance_log_id:str, query:IQueryPort, command_handler:ICommandHandlingPort):
    
    failed_instance_log:DocumentOperationInstanceLog = None
    try:
        failed_instance_log = await query.get_document_operation_instance_log_by_id(failed_instance_log_id)
        extra = {
            "document_operation_instance_id": failed_instance_log_id,
        }
        
        if not failed_instance_log:
            LOGGER.info("Recovering failed instance log not found %s", failed_instance_log_id, extra=extra)
            return
        if failed_instance_log and failed_instance_log.status != DocumentOperationStatus.FAILED:
            LOGGER.info("Recovering failed instance log not in failed status hence skipping. %s", failed_instance_log_id, extra=extra)
            return
        
        config:Configuration = await get_config(failed_instance_log.app_id, failed_instance_log.tenant_id)

        document_operation_instance:DocumentOperationInstance = await query.get_document_operation_instance_by_id(failed_instance_log.document_operation_instance_id)

        extra.update({
            "app_id": failed_instance_log.app_id,
            "tenant_id": failed_instance_log.tenant_id,
            "patient_id": failed_instance_log.patient_id,
            "document_id": failed_instance_log.document_id,
            "document_operation_instance_id": failed_instance_log.document_operation_instance_id,
            "step_id": failed_instance_log.step_id,
            "page_number": failed_instance_log.page_number,
            "status": failed_instance_log.status,
            "priority": document_operation_instance.priority
        })

        if config.retry_config and config.retry_config.enabled:
            # get retry count and check if it is within limit
            entity_retry_config:EntityRetryConfig = await query.get_entity_retry_config(failed_instance_log.unique_identifier(), "DocumentOperationInstanceLog")
            
            extra["retry_count"] = entity_retry_config.retry_count if entity_retry_config else 0            

            if entity_retry_config and entity_retry_config.retry_count >= config.retry_config.max_retries:
                extra["max_retries"] = config.retry_config.max_retries
                extra["reason"] = "max retry achieved"
                LOGGER.info("max retry achieved for %s", failed_instance_log_id, extra=extra)                
                LOGGER.info("Orchestration failed", extra=extra) #Log metric
                return
            
            classification_step_group_steps = [DocumentOperationStep.SPLIT_PAGES, 
                                                DocumentOperationStep.CREATE_PAGE, 
                                                # DocumentOperationStep.PERFORM_OCR, #We moved this to medication step
                                                DocumentOperationStep.TEXT_EXTRACTION,
                                                DocumentOperationStep.CLASSIFICATION,
                                                DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION
                                            ]
            medication_step_group_steps = [DocumentOperationStep.MEDICATIONS_EXTRACTION,
                                            DocumentOperationStep.MEDICATION_PROFILE_CREATION,
                                            DocumentOperationStep.MEDISPAN_MATCHING,
                                            DocumentOperationStep.NORMALIZE_MEDICATIONS,
                                            DocumentOperationStep.PERFORM_OCR
                                        ]
            
            
            if failed_instance_log and failed_instance_log.step_id in classification_step_group_steps:
                page:Page = await query.get_page_by_document_operation_instance_id(failed_instance_log.document_id,
                                                                                failed_instance_log.document_operation_instance_id,
                                                                                failed_instance_log.page_number)
                extra["step_group"] = "classification"
                LOGGER.info("Recovering failed instance log for page classification %s", failed_instance_log_id, extra=extra)
                await PageClassificationAgent().orchestrate(document_id = failed_instance_log.document_id, 
                                                        document_operation_instance_id = failed_instance_log.document_operation_instance_id, 
                                                        document_operation_definition_id = failed_instance_log.document_operation_definition_id, 
                                                        page_number=failed_instance_log.page_number, 
                                                        page_storage_uri=page.storage_uri)
            if failed_instance_log and failed_instance_log.step_id in medication_step_group_steps:
                page:Page = await query.get_page_by_document_operation_instance_id(failed_instance_log.document_id,
                                                                                failed_instance_log.document_operation_instance_id,
                                                                                failed_instance_log.page_number)                
                extra["step_group"] = "medication_extraction"
                classified_page:ClassifiedPage = await query.get_classified_page(page.id)
                LOGGER.info("Recovering failed instance log for page medication extraction %s", failed_instance_log_id, extra=extra)
                await MedicationExtractionAgent().orchestrate(document_id = failed_instance_log.document_id, 
                                                        document_operation_instance_id = failed_instance_log.document_operation_instance_id, 
                                                        document_operation_definition_id = failed_instance_log.document_operation_definition_id, 
                                                        page_id=page.id,
                                                        labels=classified_page.labels,
                                                        )
            
            if failed_instance_log:
                try:
                    await command_handler.handle_command(CreateOrUpdateEntityRetryConfiguration(
                                                                            app_id = failed_instance_log.app_id,
                                                                            tenant_id = failed_instance_log.tenant_id,
                                                                            patient_id = failed_instance_log.patient_id,
                                                                            document_id = failed_instance_log.document_id,
                                                                            document_operation_instance_id = failed_instance_log.document_operation_instance_id,
                                                                            retry_entity_id=failed_instance_log.unique_identifier(), 
                                                                            retry_entity_type="DocumentOperationInstanceLog", 
                                                                            retry_count=entity_retry_config.retry_count if entity_retry_config else 0,
                                                                            cross_transaction_error_strict_mode=False)
                                                )
                except Exception as e:
                    extra["error"] = exceptionToMap(e)
                    LOGGER.error("Error in updating retry count", extra=extra)
                    return
        else:
            LOGGER.info("Recovery not enabled for %s and %s", failed_instance_log.app_id, failed_instance_log.tenant_id, extra=extra)
            extra["reason"] = "Recovery disabled"
            LOGGER.info("Orchestration failed", extra=extra) #Log metric
            return
            
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.error("Error during recovery", extra=extra)
        # update retry entity with retry count
        

@inject
async def send_recover_to_pubsub(failed_instance_log_id:str, pubsub_adapter:IMessagingPort):
    try:
        extra = {
            "failed_doc_operation_instance_log_id": failed_instance_log_id,
            "topic": EXTRACTION_PUBSUB_TOPIC_NAME
        }
        LOGGER.info("Sending recover message to pubsub for failed_instance_log_id: %s", failed_instance_log_id, extra=extra)
        await pubsub_adapter.publish(topic=EXTRACTION_PUBSUB_TOPIC_NAME, 
                                message=dict(
                                        failed_doc_operation_instance_log_id=failed_instance_log_id,
                                        event_type="recover"
                                    ),
                                ordering_key = DocumentOperationType.MEDICATION_EXTRACTION.value
                                )
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e),
        })
        LOGGER.error("Error in send_recover_to_pubsub", extra=extra)

"""
Initial document processing which splits pages
"""
class DocumentProcessorAgent:
    
    @inject()
    async def orchestrate(self, document: Document, document_operation_instance_id: str, document_operation_definition_id:str, query:IQueryPort, command_handler:ICommandHandlingPort,pubsub_adapter:IMessagingPort):
        thisSpanName = "orchestrate_v3"
        with await opentelemetry.getSpan(thisSpanName) as span: 
            
            extra = document.toExtra()
            extra.update({                                
                "document_operation_instance_id": document_operation_instance_id,
                "document_operation_definition_id": document_operation_definition_id,
            })
            step_id_in_progress = None
            try:
                operation_context = {}
                
                step_id_in_progress = DocumentOperationStep.SPLIT_PAGES
                extra["step_id"] = step_id_in_progress

                # look for app or tenant config
                config:Configuration = await get_config(document.app_id, document.tenant_id)

                if not config:
                    LOGGER.error("No configuration found for app %s and tenant %s", document.app_id, document.tenant_id, extra=extra)
                    #create default config
                    config:Configuration = await command_handler.handle_command(CreateAppConfiguration(app_id=document.app_id))
                
                document:Document = await command_handler.handle_command(SplitPages(document_operation_instance_id=document_operation_instance_id, 
                                                                                    document_operation_definition_id=document_operation_definition_id,
                                                                                    app_id=document.app_id, 
                                                                                    tenant_id=document.tenant_id,
                                                                                    patient_id=document.patient_id,
                                                                                    document_id=document.id))
                
                span.set_attribute("step", step_id_in_progress)
                span.set_attribute("document_id", document.id)
                span.set_attribute("document_operation_instance_id", document_operation_instance_id)
                span.set_attribute("document_operation_definition_id", document_operation_definition_id)
                LOGGER.info("Document orchestration splitpages completed for documentId %s", document.id, extra=extra)
                for page in document.pages:
                    await TriggerAgent().start_page_classification_pipeline(
                        app_id=document.app_id,
                        tenant_id=document.tenant_id,
                        patient_id=document.patient_id,
                        document_id=document.id,
                        document_operation_instance_id=document_operation_instance_id,
                        document_operation_definition_id=document_operation_definition_id,
                        page_number = page.number,
                        page_storage_uri = page.storage_uri,
                        config=config,
                        query=query
                    )
            except (Exception,OrchestrationExceptionWithContext) as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error("Error in orchestrate_v3: %s for document: %s", traceback.format_exc(),document.id if document else "unknown", extra=extra)
                if document and document_operation_definition_id:
                    document_operation_instance_log:DocumentOperationInstanceLog = await command_handler.handle_command(CreateDocumentOperationInstanceLog(document_operation_instance_id=document_operation_instance_id, 
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            step_id=step_id_in_progress, 
                                                                                            status=DocumentOperationStatus.FAILED, 
                                                                                            app_id=document.app_id, 
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_id=document.id,
                                                                                            page_number=-1,
                                                                                            context={"error":e.context if hasattr(e,"context") else exceptionToMap(e)},
                                                                                            description="Error in orchestrate_v3: %s" % traceback.format_exc()))
                    
                    document_operation_instance:DocumentOperationInstance = await command_handler.handle_command_with_explicit_transaction(UpdateDocumentOperationInstance(
                                                                                                                                        id=document_operation_instance_id,
                                                                                                                                        app_id=document.app_id, 
                                                                                                                                        tenant_id=document.tenant_id,
                                                                                                                                        patient_id=document.patient_id,
                                                                                                                                        document_id=document.id,
                                                                                                                                        status=DocumentOperationStatus.FAILED
                                                                                                                                        ))
                    if document_operation_instance_log:
                        await send_recover_to_pubsub(document_operation_instance_log.id)
                raise OrchestrationException("Error in orchestrate_v3: %s" % traceback.format_exc())

"""
For each page, run ocr , extract text and classify

"""
class PageClassificationAgent:
    
    @inject()
    async def orchestrate(self, document_id: str, document_operation_instance_id: str, document_operation_definition_id:str, page_number: int, page_storage_uri: str, 
                          query:IQueryPort, command_handler:ICommandHandlingPort, pubsub_adapter:IMessagingPort):
        thisSpanName = "orchestrate_v3"
        document=None
        page=None
        extra = {
            "document_id": document_id,
            "document_operation_instance_id": document_operation_instance_id,
            "document_operation_definition_id": document_operation_definition_id,
            "page_number": page_number,
            "page_storage_uri": page_storage_uri
        }
        with await opentelemetry.getSpan(thisSpanName) as span: 
            start_time = now_utc()
            try:
                LOGGER.debug("Processing page %s", page_number, extra=extra)

                document:Document = Document(**await query.get_document(document_id=document_id))
                extra.update(document.toExtra())

                config:Configuration = await get_config(document.app_id, document.tenant_id)
                doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)                       
                doc_operation_definition = None
                if doc_operation_definitions:
                    doc_operation_definition = doc_operation_definitions[0] #Future: pick the right one based on some logic

                try:
                    document_operation_instance = await query.get_document_operation_instance_by_id(document_operation_instance_id)
                    overall_start_time = document_operation_instance.created_at
                    wait_elapsedtime = (start_time - overall_start_time).total_seconds()
                    extra2 = {
                        "wait_time": wait_elapsedtime
                    }
                    extra2.update(extra)
                    LOGGER.info("StepGroup:PageClassification wait time", extra=extra2)

                except Exception as e:
                    extra2 = {
                        "error": exceptionToMap(e)
                    }
                    extra2.update(extra)
                    LOGGER.error("Error in getting document operation instance: %s", str(e), extra=extra2)

                step_id_in_progress = DocumentOperationStep.CREATE_PAGE
                extra["step_id"] = step_id_in_progress

                page:Page=await command_handler.handle_command_with_explicit_transaction(CreatePage(document_operation_instance_id=document_operation_instance_id,
                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                            app_id=document.app_id, 
                                                                            tenant_id=document.tenant_id,
                                                                            patient_id=document.patient_id,
                                                                            document_id=document.id,
                                                                            page_number=page_number,
                                                                            priority=document.priority,
                                                                            storage_uri=page_storage_uri))
                
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                        app_id=document.app_id, 
                                                                                                        tenant_id=document.tenant_id,
                                                                                                        patient_id=document.patient_id,
                                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                                        document_id=document.id,
                                                                                                        page_id=page.id,
                                                                                                        page_number=page.number,
                                                                                                        priority=document.priority,
                                                                                                        step_id=step_id_in_progress,
                                                                                                        extraction_type=PageLabel.MEDICATIONS,
                                                                                                        extraction_status=PageOperationStatus.QUEUED,
                                                                                                        created_by="orchestrator",
                                                                                                        modified_by="orchestrator"
                                                                                                        ))
                
                if not config.use_extract_and_classify_strategy:
                
                    step_id_in_progress = DocumentOperationStep.TEXT_EXTRACTION
                    extra["step_id"] = step_id_in_progress

                    page:Page=await command_handler.handle_command(ExtractText(app_id=document.app_id, 
                                                                            tenant_id=document.tenant_id,
                                                                            patient_id=document.patient_id,
                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                            document_id=document.id, 
                                                                            page_id=page.id, 
                                                                            page_number=page_number,
                                                                            priority=document.priority,
                                                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION.value).get("prompt"),
                                                                            model = doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION.value).get("model")
                                                                            ))

                    
                    step_id_in_progress = DocumentOperationStep.CLASSIFICATION
                    extra["step_id"] = step_id_in_progress

                    LOGGER.debug("Executing %s operation step %s for documentId %s:  Number of pages: %s", DocumentOperationType.MEDICATION_EXTRACTION.value, step_id_in_progress, document.id, document.page_count, extra=extra)
                    classified_page:ClassifiedPage = await command_handler.handle_command(ClassifyPage(app_id=document.app_id, 
                                                                                                        tenant_id=document.tenant_id,
                                                                                                        patient_id=document.patient_id,
                                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                                        document_id=document.id, 
                                                                                                        page_id=page.id,
                                                                                                        page_text=page.text,
                                                                                                        page_number=page.number,
                                                                                                        priority=document.priority,
                                                                                                        prompt=doc_operation_definition.step_config.get(DocumentOperationStep.CLASSIFICATION.value).get("prompt"),
                                                                                                        model = doc_operation_definition.step_config.get(DocumentOperationStep.CLASSIFICATION.value).get("model")
                                                                                                    ))
                else:
                    step_id_in_progress = DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION
                    extra["step_id"] = step_id_in_progress

                    classified_page:ClassifiedPage=await command_handler.handle_command_with_explicit_transaction(ExtractTextAndClassify(app_id=document.app_id, 
                                                                            tenant_id=document.tenant_id,
                                                                            patient_id=document.patient_id,
                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                            document_id=document.id, 
                                                                            page_id=page.id, 
                                                                            page_number=page_number,
                                                                            priority=document.priority,
                                                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION.value).get("prompt"),
                                                                            model = doc_operation_definition.step_config.get(DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION.value).get("model")
                                                                            ))
                
                
                if config and config.extract_allergies:
                    page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                        app_id=document.app_id, 
                                                                                                        tenant_id=document.tenant_id,
                                                                                                        patient_id=document.patient_id,
                                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                                        document_id=document.id,
                                                                                                        page_id=page.id,
                                                                                                        page_number=page.number,
                                                                                                        priority=document.priority,
                                                                                                        step_id=step_id_in_progress,
                                                                                                        extraction_type=PageLabel.ALLERGIES,
                                                                                                        extraction_status=PageOperationStatus.QUEUED,
                                                                                                        created_by="orchestrator",
                                                                                                        modified_by="orchestrator"
                                                                                                        ))
                    if config and config.extract_immunizations:
                        page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                            app_id=document.app_id, 
                                                                                                            tenant_id=document.tenant_id,
                                                                                                            patient_id=document.patient_id,
                                                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                                            document_id=document.id,
                                                                                                            page_id=page.id,
                                                                                                            page_number=page.number,
                                                                                                            priority=document.priority,
                                                                                                            step_id=step_id_in_progress,
                                                                                                            extraction_type=PageLabel.IMMUNIZATIONS,
                                                                                                            extraction_status=PageOperationStatus.QUEUED,
                                                                                                            created_by="orchestrator",
                                                                                                            modified_by="orchestrator"
                                                                                                            ))
                
                
                span.set_attribute("step", step_id_in_progress)
                span.set_attribute("document_operation_instance_id", document_operation_instance_id)
                span.set_attribute("document_operation_definition_id", document_operation_definition_id)
                
                del extra["step_id"]
                LOGGER.info("Document page classification completed for documentId %s and page number: %s", document.id, page_number, extra=extra)
                await TriggerAgent().start_extraction_pipeline(
                    app_id=document.app_id,
                    tenant_id=document.tenant_id,
                    patient_id=document.patient_id,
                    document_id=document.id,
                    document_operation_instance_id=document_operation_instance_id,
                    document_operation_definition_id=document_operation_definition_id,
                    page_id=page.id,
                    page_number=page.number,
                    page_storage_uri=page.storage_uri,
                    labels = classified_page.labels,
                    config=config,
                    query=query
                )
                return Result(success=True, message="Page classification completed successfully")
                
            except (Exception,OrchestrationExceptionWithContext) as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error("Error in orchestrate_v3: %s for document: %s", traceback.format_exc(), document_id, extra=extra)
                if document and page and document_operation_instance_id:
                    page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                    app_id=document.app_id, 
                                                                                                    tenant_id=document.tenant_id,
                                                                                                    patient_id=document.patient_id,
                                                                                                    document_operation_instance_id=document_operation_instance_id,
                                                                                                    document_operation_definition_id=document_operation_definition_id,
                                                                                                    document_id=document.id,
                                                                                                    page_id=page.id if page else "",
                                                                                                    page_number=page.number if page else -1,
                                                                                                    priority=document.priority,
                                                                                                    step_id=step_id_in_progress,
                                                                                                    extraction_type=PageLabel.MEDICATIONS,
                                                                                                    extraction_status=PageOperationStatus.FAILED,
                                                                                                    created_by="orchestrator",
                                                                                                    modified_by="orchestrator"
                                                                                                    ))
                    
                    
                    document_operation_instance_log:DocumentOperationInstanceLog = await command_handler.handle_command_with_explicit_transaction(CreateDocumentOperationInstanceLog(app_id=document.app_id,
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_id=document.id,
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            document_operation_instance_id=document_operation_instance_id, 
                                                                                            step_id=step_id_in_progress, 
                                                                                            status=DocumentOperationStatus.FAILED, 
                                                                                            description="Error in orchestrate_v3",
                                                                                            page_number=page.number if page else -1,
                                                                                            priority=document.priority,
                                                                                            context={"error":e.context if hasattr(e,"context") else traceback.format_exc()}))
                    
                    if document_operation_instance_log:
                        await send_recover_to_pubsub(document_operation_instance_log.id)
                    # ensure that the document operation instance is marked as failed in situation where all pages failed to process
                    await command_handler.handle_command_with_explicit_transaction(CheckForAllPageOperationExtractionCompletion(
                                                                                            app_id=document.app_id, 
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            document_id=document.id,
                                                                                            step_id=step_id_in_progress,
                                                                                            priority=document.priority,
                                                                                            cross_transaction_error_strict_mode=False
                                                                                            ))
                return Result(success=False, error_message="Error in orchestrate_v3: %s" % traceback.format_exc())

"""
for each page classified, extract medication data
"""
class MedicationExtractionAgent:
    
    @inject()
    async def orchestrate(self, document_id: str, document_operation_instance_id: str, document_operation_definition_id:str, page_id:str, labels: List[Dict], query:IQueryPort, command_handler:ICommandHandlingPort):
        
        step_id_in_progress = DocumentOperationStep.MEDICATIONS_EXTRACTION
        thisSpanName = "orchestrate_v3"
        with await opentelemetry.getSpan(thisSpanName) as span:
            try: 
                label="medications"
                
                document = Document(**await query.get_document(document_id=document_id))                
                page:Page = Page(**await query.get_page_by_id(page_id=page_id))
                page_operation:PageOperation = await query.get_page_operation(page_id=page_id, document_operation_instance_id=document_operation_instance_id,extraction_type=PageLabel.MEDICATIONS)

                extra = document.toExtra()
                extra.update({
                    "document_operation_instance_id": document_operation_instance_id,
                    "document_operation_definition_id": document_operation_definition_id,
                    "page_id": page_id,
                    "page_number": page.number,
                })

                if not page_operation:
                    LOGGER.info("Medication extraction not queued yet. Skipping", extra=extra)
                    return Result(success=True, message="Medication extraction not queued yet. Skipping")
                
                if page_operation and page_operation.extraction_status not in [PageOperationStatus.QUEUED,PageOperationStatus.FAILED]:
                    # extraction is already iin progress or completed so lets skip
                    LOGGER.info("Medication extraction already in progress or completed", extra=extra)
                    return Result(success=True, message="Medication extraction already in progress or completed")
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id,
                                                                                                page_id=page.id,
                                                                                                page_number=page.number,
                                                                                                priority=document.priority,
                                                                                                step_id=step_id_in_progress,
                                                                                                extraction_type=PageLabel.MEDICATIONS,
                                                                                                extraction_status=PageOperationStatus.IN_PROGRESS,
                                                                                                created_by="orchestrator",
                                                                                                modified_by="orchestrator"
                                                                                                ))
                doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)                       
                doc_operation_definition = None
                if doc_operation_definitions:
                    doc_operation_definition = doc_operation_definitions[0] #Future: pick the right one based on some logic
                config:Configuration = await get_config(document.app_id, document.tenant_id)
                labelled_content = [x.get(label) for x in labels if x and label in x.keys()]
                
                if labelled_content:
                    
                    LOGGER.debug("Labeled content found for documentId %s and page id %s", document.id, page.number, extra=extra)
                    
                    extracted_medications:List[ExtractedMedication] = await command_handler.handle_command_with_explicit_transaction(ExtractMedication(app_id=document.app_id, 
                                                                                                        tenant_id=document.tenant_id,
                                                                                                        patient_id=document.patient_id,
                                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                                        document_id=document.id, 
                                                                                                        page_id=page.id,
                                                                                                        page_number=page.number, 
                                                                                                        priority=document.priority,
                                                                                                        labelled_content=labelled_content,
                                                                                                        prompt=doc_operation_definition.step_config.get(DocumentOperationStep.MEDICATIONS_EXTRACTION.value).get("prompt"),
                                                                                                        model=doc_operation_definition.step_config.get(DocumentOperationStep.MEDICATIONS_EXTRACTION.value).get("model")
                                                                                                        ))
                    if extracted_medications:
                        LOGGER.debug("Extracted medications found for documentId %s and page number %s", document.id, page.number, extra=extra)
                        medications_to_search_for = []
                        step_id_in_progress = DocumentOperationStep.MEDISPAN_MATCHING
                        medispan_matched_medications = await command_handler.handle_command_with_explicit_transaction(MedispanMatching(
                                        app_id=document.app_id,
                                        tenant_id=document.tenant_id,
                                        patient_id=document.patient_id,
                                        document_operation_instance_id=document_operation_instance_id,
                                        document_operation_definition_id=document_operation_definition_id,
                                        document_id=document.id, 
                                        page_id=page.id,
                                        page_number=page.number,
                                        priority=document.priority,
                                        extracted_medications=extracted_medications,
                                        prompt=doc_operation_definition.step_config.get(step_id_in_progress.value).get("prompt"),
                                        model=doc_operation_definition.step_config.get(step_id_in_progress.value).get("model"),
                                        step_id = step_id_in_progress                                                                                                
                                    ))
                        if medispan_matched_medications:                                            
                            extracted_medications = medispan_matched_medications
                        else:
                            LOGGER.error("Medispan matching returned no results for documentId %s and page number %s with medications %s.  This is unexpected.  All medications will proceed forward as unlisted with no medispan match", document.id, page.number, extracted_medications, extra=extra)

                        
                        if config.enable_ocr:
                            step_id_in_progress = DocumentOperationStep.PERFORM_OCR
                            page:Page=await command_handler.handle_command_with_explicit_transaction(PerformOCR(document_operation_instance_id=document_operation_instance_id,
                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                            app_id=document.app_id, 
                                                                            tenant_id=document.tenant_id,
                                                                            patient_id=document.patient_id,
                                                                            document_id=document.id, 
                                                                            page_id=page.id,
                                                                            priority=document.priority))
                            
                        
                        if config.orchestration_confirm_evidence_linking_enabled:
                            evidence_linking = EvidenceLinking(config)

                            if extracted_medications:                                
                                for extracted_medication in extracted_medications:
                                    try:
                                        evidences = await evidence_linking.get_evidence(app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        extracted_medication=extracted_medication)
                                        extra2 = {
                                            "medication_name": extracted_medication.medication.name,
                                            "evidence_count": len(evidences),
                                            "evidence": evidences
                                        }
                                        extra2.update(extra)
                                        if evidences and len(evidences) > 0:
                                            extra2["status"] = "found"
                                            LOGGER.info("MedicationExtraction::EvidenceLinking: Evidence found", extra=extra2) #Logging metric
                                        else:
                                            extra2["status"] = "notfound"
                                            LOGGER.info("MedicationExtraction::EvidenceLinking: Evidence not found", extra=extra2) #Logging metric
                                    except Exception as e:
                                        extra2["status"] = "error"
                                        extra2["error"] = exceptionToMap(e)                                        
                                        LOGGER.info("MedicationExtraction::EvidenceLinking: Evidence not found", extra=extra2) #Logging metric



                        if ORCHESTRATION_MEDICALEXTRACTION_STEP_NORMALIZATION_ENABLED: 
                            step_id_in_progress = DocumentOperationStep.NORMALIZE_MEDICATIONS
                            normalized_extracted_medications = await command_handler.handle_command(NormalizeMedications(
                                            app_id=document.app_id,
                                            tenant_id=document.tenant_id,
                                            patient_id=document.patient_id,
                                            document_operation_instance_id=document_operation_instance_id,
                                            document_operation_definition_id=document_operation_definition_id,
                                            document_id=document.id, 
                                            extracted_medications=extracted_medications,
                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.NORMALIZE_MEDICATIONS.value).get("prompt"),
                                            model=doc_operation_definition.step_config.get(DocumentOperationStep.NORMALIZE_MEDICATIONS.value).get("model"),
                                            step_id = DocumentOperationStep.NORMALIZE_MEDICATIONS,
                                            page_number=page.number,
                                            priority=document.priority,                     
                                        ))
                            if normalized_extracted_medications:
                                extracted_medications = normalized_extracted_medications

                        else:
                            LOGGER.info("ORCHESTRATION_MEDICALEXTRACTION_STEP_NORMALIZATION_ENABLED is false.  Skipping normalization step.", extra=extra)
                        
                        step_id_in_progress = DocumentOperationStep.MEDICATION_PROFILE_CREATION                                                          
                        medication_profile=await command_handler.handle_command_with_explicit_transaction(CreateorUpdateMedicationProfile(app_id=document.app_id,
                                                                                                                    tenant_id=document.tenant_id,
                                                                                                                    patient_id=document.patient_id,
                                                                                                                    document_operation_instance_id=document_operation_instance_id,
                                                                                                                    document_operation_definition_id=document_operation_definition_id,
                                                                                                                    document_id=document.id, 
                                                                                                                    extracted_medications=[],
                                                                                                                    priority=document.priority,
                                                                                                                    step_id = DocumentOperationStep.MEDICATION_PROFILE_CREATION
                                                                                                                    ))
                        
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id,
                                                                                                page_id=page.id,
                                                                                                page_number=page.number,
                                                                                                priority=document.priority,
                                                                                                step_id=step_id_in_progress,
                                                                                                extraction_type=PageLabel.MEDICATIONS,
                                                                                                extraction_status=PageOperationStatus.COMPLETED,
                                                                                                created_by="orchestrator",
                                                                                                modified_by="orchestrator"
                                                                                                ))
                
                await command_handler.handle_command_with_explicit_transaction(CheckForAllPageOperationExtractionCompletion(
                                                                                                app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id,
                                                                                                priority=document.priority,
                                                                                                step_id=step_id_in_progress,
                                                                                                cross_transaction_error_strict_mode=False
                                                                                                ))
                span.set_attribute("step", step_id_in_progress)
                span.set_attribute("document_operation_instance_id", document_operation_instance_id)
                span.set_attribute("document_operation_definition_id", document_operation_definition_id)
                LOGGER.info("Document orchestration page medication extraction completed for documentId %s and page number: %s", document.id, page.number if page else "unknown", extra=extra)
                return Result(success=True, message="Medication extraction completed successfully")
            except (Exception,OrchestrationExceptionWithContext) as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error("Error in orchestrate_v3: %s for document: %s", traceback.format_exc(), document_id, extra=extra)
                if document_operation_instance_id and document:
                    page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                            app_id=document.app_id, 
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            document_id=document.id,
                                                                                            page_id=page.id if page else "",
                                                                                            page_number=page.number if page else "",
                                                                                            priority=document.priority,
                                                                                            step_id=step_id_in_progress,
                                                                                            extraction_type=PageLabel.MEDICATIONS,
                                                                                            extraction_status=PageOperationStatus.FAILED,
                                                                                            created_by="orchestrator",
                                                                                            modified_by="orchestrator"
                                                                                            ))
                    await command_handler.handle_command_with_explicit_transaction(CheckForAllPageOperationExtractionCompletion(
                                                                                                app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id,
                                                                                                priority=document.priority,
                                                                                                step_id=step_id_in_progress,
                                                                                                cross_transaction_error_strict_mode=False
                                                                                                ))
                    document_operation_instance_log:DocumentOperationInstance = await command_handler.handle_command_with_explicit_transaction(CreateDocumentOperationInstanceLog(app_id=document.app_id,
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_id=document.id,
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            document_operation_instance_id=document_operation_instance_id, 
                                                                                            step_id=step_id_in_progress, 
                                                                                            status=DocumentOperationStatus.FAILED, 
                                                                                            description="Error in orchestrate_v3",
                                                                                            page_number=page.number if page else "",
                                                                                            priority=document.priority,
                                                                                            context={"error":e.context if hasattr(e,"context") else traceback.format_exc()}))
                                                                                            
                    if document_operation_instance_log:
                        await send_recover_to_pubsub(document_operation_instance_log.id)
"""
for each page classified, extract condition data
"""
class ConditionPromptExtractionAgent:
    
    @inject()
    async def orchestrate(self, document_id: str, document_operation_instance_id: str, document_operation_definition_id:str, page_id:str, labels: List[Dict], query:IQueryPort, command_handler:ICommandHandlingPort):
        step_id_in_progress = DocumentOperationStep.CONDITIONS_EXTRACTION
        thisSpanName = "orchestrate_v3"
        with await opentelemetry.getSpan(thisSpanName) as span:
            try: 
                #label="conditions"
                label_list = ['conditions', 'diagnoses', 'medical_history']
                document = Document(**await query.get_document(document_id=document_id))
                page:Page = Page(**await query.get_page_by_id(page_id=page_id))
                page_operation:PageOperation = await query.get_page_operation(page_id=page_id, document_operation_instance_id=document_operation_instance_id,extraction_type=PageLabel.CONDITIONS)
                
                if page_operation and page_operation.extraction_status != PageOperationStatus.QUEUED:
                    # extraction is already iin progress or completed so lets skip
                    return Result(success=True, message="Conditions extraction already in progress or completed")
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id,
                                                                                                page_id=page.id,
                                                                                                page_number=page.number,
                                                                                                priority=document.priority,
                                                                                                step_id=step_id_in_progress,
                                                                                                extraction_type=PageLabel.CONDITIONS,
                                                                                                extraction_status=PageOperationStatus.IN_PROGRESS,
                                                                                                created_by="orchestrator",
                                                                                                modified_by="orchestrator"
                                                                                                ))
                doc_operation_definitions:List[DocumentOperationDefinition] = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.CONDITION_EXTRACTION)                       
                doc_operation_definition:DocumentOperationDefinition = None
                if doc_operation_definitions:
                    doc_operation_definition = doc_operation_definitions[0]
                config:Configuration = await get_config(document.app_id, document.tenant_id)
                #labelled_content = [x.get(label) for x in labels if x and label in x.keys()]
                labelled_content = [x.get(label) for x in labels if x for label in label_list if label in x.keys()]
                if doc_operation_definition and labelled_content:    
                    LOGGER.debug("Labeled content found for documentId %s and page id %s and Document Definition is %s", document.id, page.number, doc_operation_definition.id)
                    print(doc_operation_definition.dict())
                    await command_handler.handle_command(ExtractConditions(app_id=document.app_id, 
                                                                           tenant_id=document.tenant_id,
                                                                           patient_id=document.patient_id,
                                                                           document_operation_instance_id=document_operation_instance_id,
                                                                           document_operation_definition_id=doc_operation_definition.id,
                                                                           document_id=document.id, 
                                                                           page_id=page.id,
                                                                           page_number=page.number, 
                                                                           priority=document.priority,
                                                                           labelled_content=labelled_content,
                                                                           prompt=doc_operation_definition.step_config.get(DocumentOperationStep.CONDITIONS_EXTRACTION.value).get("prompt"),
                                                                           model=doc_operation_definition.step_config.get(DocumentOperationStep.CONDITIONS_EXTRACTION.value).get("model")
                                                                           ))
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                                app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id,
                                                                                                page_id=page.id,
                                                                                                page_number=page.number,
                                                                                                priority=document.priority,
                                                                                                step_id=step_id_in_progress,
                                                                                                extraction_type=PageLabel.CONDITIONS,
                                                                                                extraction_status=PageOperationStatus.COMPLETED,
                                                                                                created_by="orchestrator",
                                                                                                modified_by="orchestrator"
                                                                                                ))
                
                await command_handler.handle_command_with_explicit_transaction(CheckForAllPageOperationExtractionCompletion(
                                                                                                app_id=document.app_id, 
                                                                                                tenant_id=document.tenant_id,
                                                                                                patient_id=document.patient_id,
                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                document_operation_definition_id=document_operation_definition_id,
                                                                                                document_id=document.id,
                                                                                                priority=document.priority,
                                                                                                step_id=step_id_in_progress
                                                                                                ))
                span.set_attribute("step", step_id_in_progress)
                span.set_attribute("document_operation_instance_id", document_operation_instance_id)
                span.set_attribute("document_operation_definition_id", document_operation_definition_id)
                return Result(success=True, message="Condition extraction completed successfully")
            except(Exception,OrchestrationExceptionWithContext) as e:
                LOGGER.error("Error in orchestrate_v3: %s", traceback.format_exc())
                if document_operation_instance_id and document:
                    page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                            app_id=document.app_id, 
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            document_id=document.id,
                                                                                            page_id=page.id,
                                                                                            page_number=page.number,
                                                                                            priority=document.priority,
                                                                                            step_id=step_id_in_progress,
                                                                                            extraction_type=PageLabel.CONDITIONS,
                                                                                            extraction_status=PageOperationStatus.FAILED,
                                                                                            created_by="orchestrator",
                                                                                            modified_by="orchestrator"
                                                                                            ))
                    await command_handler.handle_command_with_explicit_transaction(CreateDocumentOperationInstanceLog(app_id=document.app_id,
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_id=document.id,
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            document_operation_instance_id=document_operation_instance_id,                                                                                             
                                                                                            step_id=step_id_in_progress, 
                                                                                            status=DocumentOperationStatus.FAILED, 
                                                                                            description="Error in orchestrate_v3",
                                                                                            page_number=page.number if page else "",
                                                                                            priority=document.priority,
                                                                                            context={"error":e.context if hasattr(e,"context") else traceback.format_exc()}))

class AllergyExtractionAgent:
    
    @inject()
    async def orchestrate(self, document_id: str, document_operation_instance_id: str, document_operation_definition_id:str, page_id:str, labels: List[Dict], query:IQueryPort, command_handler:ICommandHandlingPort):
        step_id_in_progress = DocumentOperationStep.ALLERGIES_EXTRACTION
        try:
            document:Document = Document(**await query.get_document(document_id=document_id))
            page:Page = Page(**await query.get_page_by_id(page_id=page_id))
            page_operation:PageOperation = await query.get_page_operation(page_id=page_id, document_operation_instance_id=document_operation_instance_id,extraction_type=PageLabel.ALLERGIES)
            
            if page_operation and page_operation.extraction_status != PageOperationStatus.QUEUED:
                # extraction is already iin progress or completed so lets skip
                return Result(success=True, message="Allergies extraction already in progress or completed")
            page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_id=document.id,
                                                                                        page_id=page.id,
                                                                                        page_number=page.number,
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress,
                                                                                        extraction_type=PageLabel.ALLERGIES,
                                                                                        extraction_status=PageOperationStatus.IN_PROGRESS,
                                                                                        created_by="orchestrator",
                                                                                        modified_by="orchestrator"
                                                                                        ))
            doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)                       
            doc_operation_definition = None
            if doc_operation_definitions:
                doc_operation_definition = doc_operation_definitions[0] #Future: pick the right one based on some logic
            config: Configuration = await get_config(document.app_id, document.tenant_id)
            if config and config.extract_allergies and labels:
                label_allergies = PageLabel.ALLERGIES.value
                labelled_content_allergies = [x.get(label_allergies) for x in labels if x and x.get(label_allergies) and label_allergies in x.keys()]
                
                if labelled_content_allergies:
                    
                    step_id_in_progress = DocumentOperationStep.ALLERGIES_EXTRACTION
                    extracted_allergies:List[ExtractedClinicalData] = await command_handler.handle_command(ExtractClinicalData(app_id=document.app_id, 
                                                                                                            tenant_id=document.tenant_id,
                                                                                                            patient_id=document.patient_id,
                                                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                                            document_id=document.id, 
                                                                                                            page_id=page.id,
                                                                                                            page_number=page.number, 
                                                                                                            priority=document.priority,
                                                                                                            labelled_content=labelled_content_allergies,
                                                                                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("prompt"),
                                                                                                            model=doc_operation_definition.step_config.get(DocumentOperationStep.ALLERGIES_EXTRACTION.value).get("model"),
                                                                                                            clinical_data_type = PageLabel.ALLERGIES.value
                                                                                                        ))
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_id=document.id,
                                                                                        page_id=page.id,
                                                                                        page_number=page.number,
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress,
                                                                                        extraction_type=PageLabel.ALLERGIES,
                                                                                        extraction_status=PageOperationStatus.COMPLETED,
                                                                                        created_by="orchestrator",
                                                                                        modified_by="orchestrator"
                                                                                        ))
            await command_handler.handle_command_with_explicit_transaction(CheckForAllPageOperationExtractionCompletion(
                                                                                        idempotent_key = document_operation_instance_id,
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_id=document.id,
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress,
                                                                                        cross_transaction_error_strict_mode=False
                                                                                        ))
        except:
            LOGGER.error("Error in orchestrate_v3: %s", traceback.format_exc())
            if document_operation_instance_id and document:
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_id=document.id,
                                                                                        page_id=page.id,
                                                                                        page_number=page.number,
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress,
                                                                                        extraction_type=PageLabel.ALLERGIES,
                                                                                        extraction_status=PageOperationStatus.FAILED,
                                                                                        created_by="orchestrator",
                                                                                        modified_by="orchestrator"
                                                                                        ))
                await command_handler.handle_command_with_explicit_transaction(CreateDocumentOperationInstanceLog(app_id=document.app_id,
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_id=document.id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_operation_instance_id=document_operation_instance_id, 
                                                                                        step_id=step_id_in_progress, 
                                                                                        status=DocumentOperationStatus.FAILED, 
                                                                                        description="Error in orchestrate_v3",
                                                                                        page_number=page.number if page else "",
                                                                                        priority=document.priority,
                                                                                        context={"error":traceback.format_exc()}))
            return Result(success=False, error_message="Error in orchestrate_v3: %s" % traceback.format_exc())

class ImmunizationExtractionAgent:
    
    @inject()
    async def orchestrate(self, document_id: str, document_operation_instance_id: str, document_operation_definition_id:str, page_id:str, labels: List[Dict], query:IQueryPort, command_handler:ICommandHandlingPort):
        step_id_in_progress = DocumentOperationStep.IMMUNIZATIONS_EXTRACTION
        try:
            document:Document = Document(**await query.get_document(document_id=document_id))
            page:Page = Page(**await query.get_page_by_id(page_id=page_id))
            doc_operation_definitions = await query.get_document_operation_definition_by_op_type(operation_type = DocumentOperationType.MEDICATION_EXTRACTION.value)                       
            doc_operation_definition = None
            if doc_operation_definitions:
                doc_operation_definition = doc_operation_definitions[0] #Future: pick the right one based on some logic
                
            page_operation:PageOperation = await query.get_page_operation(page_id=page_id, document_operation_instance_id=document_operation_instance_id,extraction_type=PageLabel.IMMUNIZATIONS)
            if page_operation and page_operation.extraction_status != PageOperationStatus.QUEUED:
                # extraction is already iin progress or completed so lets skip
                return Result(success=True, message="Immunizations extraction already in progress or completed")
            page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_id=document.id,
                                                                                        page_id=page.id,
                                                                                        page_number=page.number,
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress,
                                                                                        extraction_type=PageLabel.IMMUNIZATIONS,
                                                                                        extraction_status=PageOperationStatus.IN_PROGRESS,
                                                                                        created_by="orchestrator",
                                                                                        modified_by="orchestrator"
                                                                                        ))
            config: Configuration = await get_config(document.app_id, document.tenant_id)
            if config and config.extract_immunizations and labels:
                label_immunizations = PageLabel.IMMUNIZATIONS.value
                labelled_content_allergies = [x.get(label_immunizations) for x in labels if x and x.get(label_immunizations) and label_immunizations in x.keys()]
                
                if labelled_content_allergies:
                    
                    step_id_in_progress = DocumentOperationStep.IMMUNIZATIONS_EXTRACTION
                    extracted_allergies:List[ExtractedClinicalData] = await command_handler.handle_command(ExtractClinicalData(app_id=document.app_id, 
                                                                                                            tenant_id=document.tenant_id,
                                                                                                            patient_id=document.patient_id,
                                                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                                            document_id=document.id, 
                                                                                                            page_id=page.id,
                                                                                                            page_number=page.number, 
                                                                                                            priority=document.priority,
                                                                                                            labelled_content=labelled_content_allergies,
                                                                                                            prompt=doc_operation_definition.step_config.get(DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value).get("prompt"),
                                                                                                            model=doc_operation_definition.step_config.get(DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value).get("model"),
                                                                                                            clinical_data_type = PageLabel.IMMUNIZATIONS.value
                                                                                                        ))
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_id=document.id,
                                                                                        page_id=page.id,
                                                                                        page_number=page.number,
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress,
                                                                                        extraction_type=PageLabel.IMMUNIZATIONS,
                                                                                        extraction_status=PageOperationStatus.COMPLETED,
                                                                                        created_by="orchestrator",
                                                                                        modified_by="orchestrator"
                                                                                        ))
            await command_handler.handle_command_with_explicit_transaction(CheckForAllPageOperationExtractionCompletion(
                                                                                            app_id=document.app_id, 
                                                                                            tenant_id=document.tenant_id,
                                                                                            patient_id=document.patient_id,
                                                                                            document_operation_instance_id=document_operation_instance_id,
                                                                                            document_operation_definition_id=document_operation_definition_id,
                                                                                            document_id=document.id,
                                                                                            priority=document.priority,
                                                                                            step_id=step_id_in_progress,
                                                                                            cross_transaction_error_strict_mode=False
                                                                                            ))
        except:
            LOGGER.error("Error in orchestrate_v3: %s", traceback.format_exc())
            if document_operation_instance_id and document:
                page_operation:PageOperation = await command_handler.handle_command_with_explicit_transaction(CreateorUpdatePageOperation(
                                                                                        app_id=document.app_id, 
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_id=document.id,
                                                                                        page_id=page.id,
                                                                                        page_number=page.number,
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress,
                                                                                        extraction_type=PageLabel.IMMUNIZATIONS,
                                                                                        extraction_status=PageOperationStatus.FAILED,
                                                                                        created_by="orchestrator",
                                                                                        modified_by="orchestrator"
                                                                                        ))
                await command_handler.handle_command_with_explicit_transaction(CreateDocumentOperationInstanceLog(app_id=document.app_id,
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_id=document.id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_operation_instance_id=document_operation_instance_id, 
                                                                                        step_id=step_id_in_progress, 
                                                                                        status=DocumentOperationStatus.FAILED,
                                                                                        page_number=page.number if page else "", 
                                                                                        priority=document.priority,
                                                                                        description="Error in orchestrate_v3",
                                                                                        context={"error":traceback.format_exc()}))
            return Result(success=False, error_message="Error in orchestrate_v3: %s" % traceback.format_exc())

class ConditionExtractionAgent:
    
    @inject()
    async def orchestrate(self, document_id: str, document_operation_instance_id: str, document_operation_definition_id:str, query:IQueryPort, command_handler:ICommandHandlingPort):
        
        try:
            step_id_in_progress = DocumentOperationStep.CONDITIONS_EXTRACTION
            document:Document = Document(**await query.get_document(document_id=document_id))
            page_texts:List[PageText] = await query.get_page_texts(document_id=document_id, 
                                                                   document_operation_instance_id=document_operation_instance_id)
            command = ExtractConditionsData(app_id=document.app_id,
                                            tenant_id=document.tenant_id,
                                            patient_id=document.patient_id,
                                            document_id=document.id,
                                            document_operation_instance_id=document_operation_instance_id,
                                            document_operation_definition_id=document_operation_definition_id,
                                            page_texts=[x for x in page_texts if x and x.text and x.pageNumber],
                                            priority=document.priority,
                                            step_id= DocumentOperationStep.CONDITIONS_EXTRACTION
                                            )

            results = await command_handler.handle_command(command)
        except:
            LOGGER.error("Error in orchestrate_v3: %s", traceback.format_exc())
            if document_operation_instance_id and document:
                await command_handler.handle_command(CreateDocumentOperationInstanceLog(app_id=document.app_id,
                                                                                        tenant_id=document.tenant_id,
                                                                                        patient_id=document.patient_id,
                                                                                        document_id=document.id,
                                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                                        document_operation_instance_id=document_operation_instance_id, 
                                                                                        priority=document.priority,
                                                                                        step_id=step_id_in_progress, 
                                                                                        status=DocumentOperationStatus.FAILED, 
                                                                                        description="Error in orchestrate_v3",
                                                                                        context={"error":traceback.format_exc()}))
            return Result(success=False, error_message="Error in orchestrate_v3: %s" % traceback.format_exc())
  
class TriggerAgent:
    
    @inject()
    async def start_page_classification_pipeline(self, app_id:str, tenant_id:str, patient_id:str,
                                        document_id: str, 
                                        document_operation_instance_id: str, 
                                        document_operation_definition_id:str,
                                        page_number:int,
                                        page_storage_uri:str,  
                                        config:Configuration,
                                        query:IQueryPort,
                                        cloud_task_adapter:ICloudTaskPort,
                                        ):
        from paperglass.usecases.orchestrator import PageClassificationAgent, AllergyExtractionAgent, ImmunizationExtractionAgent, MedicationExtractionAgent, ConditionPromptExtractionAgent
        from paperglass.usecases.orchestrator import get_config
        from settings import CLOUD_PROVIDER, GCP_LOCATION_2, SERVICE_ACCOUNT_EMAIL, SELF_API
        
        extra = {
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id,
            "document_id": document_id,
            "document_operation_instance_id": document_operation_instance_id,
            "document_operation_definition_id": document_operation_definition_id,
            "page_number": page_number,
            "storage_uri": page_storage_uri,
        }
        
        LOGGER.info(f'Got event that page no: {page_number}) is ready for further processing', extra=extra)
        
        if config and config.use_v3_orchestration_engine:
            if CLOUD_PROVIDER == "local":
                await PageClassificationAgent().orchestrate(
                    document_id=document_id,
                    document_operation_instance_id=document_operation_instance_id,
                    document_operation_definition_id=document_operation_definition_id,
                    page_number=page_number,
                    page_storage_uri=page_storage_uri
                )
            else:
                # call application integration which has cloud task to ensure it throttles

                doc_op_inst = await query.get_document_operation_instance_by_id(document_operation_instance_id)
                category="page_classification"
                priority = doc_op_inst.priority if doc_op_inst else OrchestrationPriority.DEFAULT
                queue_name = QueueResolver().resolve_queue_name(category, priority)
                url = f"{SELF_API}/orchestrate_v3_page_classification"
                payload = {
                    "document_id": document_id,
                    "document_operation_instance_id": document_operation_instance_id,
                    "document_operation_definition_id": document_operation_definition_id,
                    "page_number": page_number,
                    "storage_uri": page_storage_uri,
                    "priority": priority
                }

                extra.update({
                    "category": category,
                    "priority": priority,
                    "cloud_task": {
                        "url": url,
                        "location": GCP_LOCATION_2,
                        "queue": queue_name,
                        "payload": payload
                    }
                })
                
                await cloud_task_adapter.create_task(
                    token=get_token(app_id, tenant_id, patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue_name,
                    url=url,
                    payload=payload
                )
                
                LOGGER.info("Submit CloudTask: %s", category, extra=extra)      

    @inject
    async def start_extraction_pipeline(self,app_id:str, tenant_id:str, patient_id:str,
                                        document_id: str, 
                                        document_operation_instance_id: str, 
                                        document_operation_definition_id:str,
                                        page_number:int,
                                        page_storage_uri:str,
                                        page_id:str,  
                                        labels:List[Dict],
                                        config:Configuration,
                                        query:IQueryPort,
                                        cloud_task_adapter:ICloudTaskPort
                                        ):
        from paperglass.usecases.orchestrator import PageClassificationAgent, AllergyExtractionAgent, ImmunizationExtractionAgent, MedicationExtractionAgent, ConditionPromptExtractionAgent
        
        extra = {
            "app_id": app_id,
            "tenant_id": tenant_id,
            "patient_id": patient_id,
            "document_id": document_id,
            "document_operation_instance_id": document_operation_instance_id,
            "document_operation_definition_id": document_operation_definition_id,
            "page_number": page_number,
            "storage_uri": page_storage_uri,
        }

        LOGGER.info(f'Got event that page id: {page_id}) is ready for further processing', extra=extra)
        
        if config and config.use_v3_orchestration_engine:
            if CLOUD_PROVIDER == "local":
                
                await MedicationExtractionAgent().orchestrate(
                    document_id=document_id,
                    document_operation_instance_id=document_operation_instance_id,
                    document_operation_definition_id=document_operation_definition_id,
                    page_id=page_id,
                    labels=labels
                )

                if config.extract_conditions:
                    await ConditionPromptExtractionAgent().orchestrate(
                        document_id=document_id,
                        document_operation_instance_id=document_operation_instance_id,
                        document_operation_definition_id=document_operation_definition_id,
                        page_id=page_id,
                        labels=labels
                    )
                
                if config.extract_allergies:
                    await AllergyExtractionAgent().orchestrate(
                        document_id=document_id,
                        document_operation_instance_id=document_operation_instance_id,
                        document_operation_definition_id=document_operation_definition_id,
                        page_id=page_id,
                        labels=labels
                    )
                    
                if config.extract_immunizations:
                    await ImmunizationExtractionAgent().orchestrate(
                        document_id=document_id,
                        document_operation_instance_id=document_operation_instance_id,
                        document_operation_definition_id=document_operation_definition_id,
                        page_id=page_id,
                        labels=labels
                    )
            else:
                # call application integration which has cloud task to ensure it throttles
                start_time = now_utc()

                doc_op_inst = await query.get_document_operation_instance_by_id(document_operation_instance_id)
                priority = doc_op_inst.priority if doc_op_inst else OrchestrationPriority.DEFAULT

                category="medication_extraction"
                url = f"{SELF_API}/orchestrate_v3_medication_extraction"
                queue_name = QueueResolver().resolve_queue_name(category, priority)
                payload={
                    "document_id": document_id,
                    "document_operation_instance_id": document_operation_instance_id,
                    "document_operation_definition_id": document_operation_definition_id,
                    "page_id": page_id,
                    "priority": priority,
                    "labels": labels,
                    "page_number": page_number,
                    "waittime_start": start_time.isoformat()
                }
                
                await cloud_task_adapter.create_task(
                    token=get_token(app_id, tenant_id, patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue_name,
                    url=url,
                    payload=payload
                )

                this_extra = extra.copy()
                this_extra.update({
                    "category": category,
                    "priority": priority,                    
                    "cloud_task": {
                        "url": url,
                        "location": GCP_LOCATION_2,
                        "queue": queue_name,
                        "payload": payload
                    }
                })
                LOGGER.info("Submit CloudTask: %s", category, extra=this_extra)

                if config and config.extract_conditions:
                    category="conditions_extraction"
                    queue_name = QueueResolver().resolve_queue_name(category, priority)
                    url = f"{SELF_API}/orchestrate_v3_conditions_extraction"
                    payload = {
                        "document_id": document_id,
                        "document_operation_instance_id": document_operation_instance_id,
                        "document_operation_definition_id": document_operation_definition_id,
                        "page_id": page_id,
                        "priority": priority,
                        "labels": labels
                    }

                    await cloud_task_adapter.create_task(
                        token=get_token(app_id, tenant_id, patient_id),
                        location=GCP_LOCATION_2,
                        service_account_email=SERVICE_ACCOUNT_EMAIL,
                        queue=queue_name,
                        url=url,
                        payload=payload
                    )
                    this_extra = extra.copy()
                    this_extra.update({
                        "category": category,
                        "priority": priority,
                        "queue_name": queue_name,
                        "cloud_task": {
                            "url": url,
                            "location": GCP_LOCATION_2,
                            "queue": queue_name,
                            "payload": payload
                        }
                    })             
                    LOGGER.info("Submit CloudTask: %s", category, extra=this_extra)
                
                if config and config.extract_allergies:
                    category="allergies_extraction"
                    queue_name = QueueResolver().resolve_queue_name(category, priority)
                    url = f"{SELF_API}/orchestrate_v3_allergies_extraction"
                    payload = {
                        "document_id": document_id,
                        "document_operation_instance_id": document_operation_instance_id,
                        "document_operation_definition_id": document_operation_definition_id,
                        "page_id": page_id,
                        "priority": priority,
                        "labels": labels
                    }

                    await cloud_task_adapter.create_task(
                        token=get_token(app_id, tenant_id, patient_id),
                        location=GCP_LOCATION_2,
                        service_account_email=SERVICE_ACCOUNT_EMAIL,
                        queue=CLOUD_TASK_QUEUE_NAME,
                        url=url,
                        payload=payload
                    )
                    this_extra = extra.copy()
                    this_extra.update({
                        "category": category,
                        "priority": priority,
                        "cloud_task": {
                            "url": url,
                            "location": GCP_LOCATION_2,
                            "queue": queue_name,
                            "payload": payload
                        }
                    })                    
                    LOGGER.info("Submit CloudTask: %s", category, extra=this_extra)
                
                if config and config.extract_immunizations:
                    category="immunizations_extraction"
                    queue_name = QueueResolver().resolve_queue_name(category, priority)
                    url = f"{SELF_API}/orchestrate_v3_immunizations_extraction"
                    payload = {
                        "document_id": document_id,
                        "document_operation_instance_id": document_operation_instance_id,
                        "document_operation_definition_id": document_operation_definition_id,
                        "page_id": page_id,
                        "priority": priority,
                        "labels": labels
                    }
                    
                    await cloud_task_adapter.create_task(
                        token=get_token(app_id, tenant_id, patient_id),
                        location=GCP_LOCATION_2,
                        service_account_email=SERVICE_ACCOUNT_EMAIL,
                        queue=CLOUD_TASK_QUEUE_NAME,
                        url=url,
                        payload=payload
                    )

                    this_extra = extra.copy()
                    this_extra.update({
                        "category": category,
                        "priority": priority,
                        "cloud_task": {
                            "url": url,
                            "location": GCP_LOCATION_2,
                            "queue": queue_name,
                            "payload": payload
                        }
                    })               
                    LOGGER.info("Submit CloudTask: %s", category, extra=this_extra)

def get_args():
    parser = argparse.ArgumentParser(description='Orchestrate the extraction of medication data from a document')
    parser.add_argument('--document_id', type=str, help='The document id')
    parser.add_argument('--page_id', type=str, help='The page id')
    parser.add_argument('--page_number', type=int, help='The page number')
    parser.add_argument('--page_text', type=str, help='The page text')
    parser.add_argument('--tenant_id', type=str, help='The tenant id')
    parser.add_argument('--app_id', type=str, help='The app id')
    return parser.parse_args()