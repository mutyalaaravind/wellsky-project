import asyncio
import base64
from copy import deepcopy
import datetime
from datetime import time as dt_time
import time
from difflib import SequenceMatcher
from functools import singledispatch, wraps
from io import BytesIO
import json
import os
from re import match
import traceback
from typing import Dict, List, Tuple, Union
import uuid
import traceback
from uuid import uuid1

from pydantic import ValidationError

from kink import inject
from paperglass.domain.utils.change_tracker_utils import change_tracker_updates
from paperglass.domain.utils.auth_utils import  get_token
from paperglass.domain.utils.token_utils import mktoken2
from paperglass.domain.utils.uuid_utils import get_uuid, get_uuid4
from paperglass.domain.context import Context
from paperglass.domain.models_common import OrchestrationExceptionWithContext, UnsupportedFileTypeException, MessageContainer, WindowClosedException, NotFoundException
from paperglass.domain.utils.array_utils import chunk_array
from paperglass.domain.utils.file_utils import get_filetype_from_filename
from paperglass.usecases.configuration import get_config
from paperglass.usecases.medications import find_matching_medispan_medication_with_llm, find_matching_medispan_medication_with_logic, get_best_match_of_medispan_results
from paperglass.usecases.conditions import ConditionsService
from paperglass.usecases.step_medispan_matching import StepMedispanMatchingResolver
from paperglass.usecases.document_operation_instance_log import DocumentOperationInstanceLogService, does_success_operation_instance_exist
from paperglass.domain.time import now_utc, defer_until_after_time, get_ct_schedule_datetime
from paperglass.domain.service import RawJSONDecoder, extract_json
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.infrastructure.adapters.http_rest_client import HttpRestClient

#from paperglass.entrypoints.test_orchestration_cli import run as run_test_orchestration
from paperglass.usecases.rules_engine import RulesEngine

import pypdf

from paperglass.usecases.labeling import SingleLabeling
from paperglass.settings import (
    CLOUD_PROVIDER,
    GCP_LOCATION_2,
    MEDICATION_EXTRACTION_PRIORITY_QUARANTINE,
    SERVICE_ACCOUNT_EMAIL,
    CLOUD_TASK_QUEUE_NAME,
    APPLICATION_INTEGRATION_TRIGGER_ID,
    HHH_ATTACHMENTS_IMPORT_ENABLED,
    HHH_ATTACHMENTS_AUTH_SERVER,
    HHH_ATTACHMENTS_CLIENT_ID,
    HHH_ATTACHMENTS_CLIENT_SECRET,
    HHH_ATTACHMENTS_STORAGE_OBJECT_METADATA_ENABLE,
    INTEGRATION_PROJECT_NAME,
    SELF_API,
    SERVICE_ACCOUNT_EMAIL,
    CLOUD_TASK_QUEUE_NAME,
    CLOUD_TASK_COMMAND_QUEUE_NAME,
    CLOUD_TASK_COMMAND_SCHEDULE_QUEUE_NAME,
    HHH_CLASSIFICATION_CACHE_TTL,
    MEDISPAN_LLM_SCORING_ENABLED,
    get_module_root,
    MEDICATION_EXTRACTION_PRIORITY_DEFAULT,
    ORCHESTRATION_GRADER_STRATEGY,
    ORCHESTRATION_GRADER_SCHEDULE_OPERATION_TYPES,
    ORCHESTRATION_GRADER_SCHEDULE_WINDOW_ENABLED,
    ORCHESTRATION_GRADER_SCHEDULE_WINDOW_START,
    ORCHESTRATION_GRADER_SCHEDULE_WINDOW_END,
    PUBSUB_EVENT_ORCHESTRATIONCOMPLETE_TOPIC,
    PUBSUB_EVENT_MEDICATION_PUBLISH_TOPIC,
    E2E_TEST_MAX_DURATION_SECONDS,
    E2E_TEST_UPDATE_ENABLE,
    E2E_OWNER_GOLDEN_REPO_APP_ID,
    E2E_OWNER_GOLDEN_REPO_TENANT_ID,
    E2E_OWNER_GOLDEN_REPO_PATIENT_ID,
    E2E_OWNER_GOLDEN_RUN_PATIENT_ID,
    FEATUREFLAG_COMMAND_OUTOFBAND_CLOUDTASK_ENABLED,    
    MEDICATION_CATALOG_DEFAULT,
    START_TIME,
    END_TIME,
    ONBOARDING_PATIENT_LIST,
)

from paperglass.domain.models_common import OrchestrationException, ReferenceCodes
from paperglass.domain.model_metric import Metric
from paperglass.domain.utils.exception_utils import exceptionToMap, getTrimmedStacktraceAsString
from paperglass.domain.util_json import convertToJson
from paperglass.domain.utils.array_utils import chunk_array

from ..domain.models import (
    AppConfig,
    AppTenantConfig,
    ClassifiedPage,
    CustomPromptResult,
    Document,
    DocumentMedicationProfile2,
    DocumentOperation,
    DocumentOperationDefinition,
    DocumentOperationInstance,
    DocumentOperationInstanceLog,
    DocumentOperationStatusSnapshot,
    DocumentStatus,
    EntityRetryConfig,
    Evidences,
    ExtractedClinicalData,
    ExtractedMedication,
    ExtractedConditions,
    MedispanDrug,
    PageOperation,
    ReconcilledMedication,
    HostAttachmentAggregate,
    ImportedMedicationAggregate,
    ImportedGeneralMedicationAggregate,
    Medication,
    MedicationProfile,
    Note,
    Page,
    PageLabel,
    UserEnteredMedicationAggregate,
    PageLabel,
    ResolvedReconcilledMedication,
    ExtractedMedicationGrade,
    MedicalCodingRawData,
    OperationMeta,
)
from paperglass.domain.model_testing import (
    E2ETestCaseSummaryResults,
    E2ETestCaseSummaryResults,
    E2ETestCaseArchive,
    E2ETestCase,
    E2ETestDocumentExpections,
    E2ETestPageExpections,
)
from ..domain.model_toc import (
    DocumentTOC,
    DocumentFilterState
)
from ..domain.model_entity_toc import (
    DocumentEntityTOC
)
from ..domain.model_generic_step import (
    GenericPromptStep,
    OperationMetrics
)
from ..domain.model_testing import TestResults
from ..domain.values import (
    AnnotationToken,
    ChangeTracker,
    ChangedEntity,
    Configuration,
    DocumentOperationStatus,
    DocumentOperationType,
    DocumentOperationStep,
    DocumentSettings,
    HostAttachment,
    HostAttachmentMetadata,
    HostMedicationAddModel,
    HostFreeformMedicationAddModel,
    HostMedication,
    HostMedicationSyncStatus,
    HostMedicationUpdateModel,
    ImportedMedication,
    MedicationChangeSet,
    MedicationStatus,
    MedicationValue,
    ConditionValue,
    MedispanMedicationValue,
    MedispanStatus,
    OCRType,
    OrchestrationPriority,
    Page as PageModel,
    PageOperationStatus,
    ReconcilledMedication,
    Result,
    UserEnteredMedication,
    Origin,
    MedispanMatchMedicationLogEntry,
    StepConfigPrompt,
)
from paperglass.domain.values_http import (
    GenericExternalDocumentCreateEventRequestApi,
    GenericExternalDocumentCreateEventRequestUri,
    GenericExternalDocumentRepositoryApi,
    ExternalDocumentRepositoryType,
)
from ..domain.util_json import convertToJson
from ..usecases.commands import (
    AppBaseCommand,
    AddUserEnteredMedication,
    AssembleTOC,
    AddUserEnteredMedication,
    BaseCommand,
    CheckForAllPageOperationExtractionCompletion,
    CreateAppConfiguration,
    CreateClinicalData,
    CreateOrUpdateEntityRetryConfiguration,
    CreateTenantConfiguration,
    UpdateAppConfiguration,
    UpdateTenantConfiguration,
    CreateorUpdatePageOperation,
    DocumentBaseCommand,
    ExtractClinicalData,
    ExtractTextAndClassify,
    ImportHostAttachmentFromExternalStorageUri,
    ImportHostAttachmentFromExternalApi,
    ImportHostAttachmentFromExternalApiTask,
    ImportHostAttachments,
    UpdateDocumentStatusSnapshot,
    DocumentStateChange,
    UpdateHostMedications,
    ProcessOnboardingWizard
)
from ..usecases.commands import (
    GetStatus,
    AssembleTOC,
    ClassifyPage,
    CreateDefaultMedicationDocumentOperationDefinition,
    CreateOrUpdateDocumentOperation,
    CreateDocumentOperationInstance,
    UpdateDocumentOperationInstance,
    CreateDocumentOperationInstanceLog,
    CreateEvidence,
    CreateMedication,
    CreatePage,
    CreateorUpdateMedicationProfile,
    DeleteMedication,
    DeleteReconcilledMedication,
    ExecuteCustomPrompt,
    ExtractMedication,
    ExtractConditions,
    ExtractText,
    FindMedication,
    FindMedicationWithLLMFilter,
    GetDocument,
    GetDocumentLogs,
    ImportMedications,
    MedispanMatching,
    NormalizeMedications,
    Orchestrate,
    CreateTestDocument,
    PerformOCR,
    QueueCommand,
    QueueOrchestration,
    QueueDeferredOrchestration,
    StartOrchestration,
    PerformGrading,
    SplitPages,
    Command,
    ExternalCreateDocumentTask,
    CreateDocument,
    DocumentSpawnRevision,
    UpdateDocumentPriority,
    CreateNote,
    GetDocumentPDFURL,
    SendEmail,
    TriggerExtraction,
    UnDeleteReconcilledMedication,
    UndeleteMedication,
    UpdateMedication,
    UpdateNote,
    CreateDocumentMedicationProfileCommand,
    DeleteDocumentMedicationProfileCommand,
    UpdateUserEnteredMedication,
    LogPageProfileFilterState,
    ExecuteGenericPromptStep,
    GetHostMedicationClassifications,
    SaveTestResults,
    CreateGoldenDatasetTest,
    AutoCreateDocumentOperationDefinition,
    ExtractConditionsData,
    QueueE2ETest,
    RunE2ETest,
    CreateE2ETestCaseSummaryResults,
    AssessTestCaseResults,
    AssessTestCaseSummaryResults,
    ReassessTestCaseSummaryResults,
    CreateTestCaseFromDocument,
    ConfirmE2ETest,
    LoadTestPoke,
    CreateEntitySchema,
    DeleteEntitySchema,
    ImportEntities,
    CreateEntityTOC,
)

from paperglass.usecases.e2e_v4_tests import TestHarness
from paperglass.usecases.load_test import E2ELoadTestAgent, VertexAILoadTestAgent
from paperglass.usecases.evidence_linking import EvidenceLinking
from paperglass.usecases.v4.medications import list_medications
from paperglass.usecases.command_actions import create_command

from .medication_grader import (
    MedicationGraderLLM,
    MedicationGraderProcedural
)
from ..interface.ports import CommandError, ICommandHandlingPort
from ..infrastructure.ports import (
    IApplicationIntegration,
    IDocumentAIAdapter,
    IEmbeddings2Adapter,
    IEmbeddingsAdapter,
    IFhirStoreAdapter,
    IHHHAdapter,
    IMedispanPort,
    IPromptAdapter,
    IQueryPort,
    ISearchIndexer,
    ISettingsPort,
    IStoragePort,
    IUnitOfWork,
    IUnitOfWorkManagerPort,
    IRelevancyFilterPort,
    IMessagingPort,
    ICloudTaskPort,
)

from paperglass.usecases.orchestration_launcher import OrchestrationLauncher

from ..log import labels, CustomLogger

from ..usecases.toc import assemble, indexPageProfiles

LOGGER2 = CustomLogger(__name__)
LOGGER = LOGGER2

#OpenTelemetry instrumentation
SPAN_BASE: str = "APP:command_handling:"
from ..domain.utils.opentelemetry_utils import OpenTelemetryUtils
opentelemetry = OpenTelemetryUtils(SPAN_BASE)


@singledispatch
async def dispatcher(command: Command, uow: IUnitOfWork):
    raise ValueError(f'Don\'t know how to handle command {command}')


# Sample handlers


@dispatcher.register(CreateNote)
@inject()
async def create_note(command: CreateNote, uow: IUnitOfWork):
    note = Note.create(command.title, command.content)
    uow.register_new(note)
    return note


@dispatcher.register(UpdateNote)
@inject()
async def update_note(command: UpdateNote, uow: IUnitOfWork):
    note = await uow.get(Note, command.note_id)
    note.update_content(command.content)
    uow.register_dirty(note)
    return note


@dispatcher.register(SendEmail)
async def send_email(command: SendEmail, uow: IUnitOfWork):
    LOGGER.warning(
        'Sending email to %s with template %s and note_id %s', command.email, command.template, command.note_id
    )

@dispatcher.register(GetStatus)
async def get_status(command: GetStatus, uow: IUnitOfWork) -> dict:
    LOGGER.info('Getting status: %s', command)

    return {
        "status": "OK"
    }



@dispatcher.register(CreateAppConfiguration)
@inject()
async def create_app_configuration(command: CreateAppConfiguration, uow: IUnitOfWork):
    app_configuration = AppConfig.create(
        app_id=command.app_id, 
        config=command.config,
        name=command.name,
        description=command.description
    )
    uow.register_new(app_configuration)
    return app_configuration

@dispatcher.register(CreateTenantConfiguration)
@inject()
async def create_app_configuration(command: CreateTenantConfiguration, uow: IUnitOfWork):
    app_tenant_configuration = AppTenantConfig.create(app_id=command.app_id, tenant_id=command.tenant_id,config=command.config)
    uow.register_new(app_tenant_configuration)
    return app_tenant_configuration

@dispatcher.register(UpdateAppConfiguration)
@inject()
async def update_app_configuration(command: UpdateAppConfiguration, uow: IUnitOfWork, query: IQueryPort):
    # Get existing active config
    existing_config = await query.get_app_config(command.app_id)
    if not existing_config:
        # No existing config, create new one
        app_configuration = AppConfig.create(
            app_id=command.app_id, 
            config=command.config,
            name=command.name,
            description=command.description
        )
        app_configuration.created_by = command.created_by
        app_configuration.modified_by = command.modified_by
        uow.register_new(app_configuration)
        return app_configuration
    
    # Archive existing configuration if requested
    if command.archive_current:
        # Archive the existing configuration to subcollection under its current UUID
        existing_config.modified_by = command.modified_by
        uow.register_archived(existing_config)
    
    # Update the existing configuration in place (preserving UUID)
    existing_config.config = command.config
    existing_config.name = command.name
    existing_config.description = command.description
    existing_config.modified_by = command.modified_by
    existing_config.modified_at = now_utc()
    uow.register_dirty(existing_config)
    return existing_config

@dispatcher.register(UpdateTenantConfiguration)
@inject()
async def update_tenant_configuration(command: UpdateTenantConfiguration, uow: IUnitOfWork, query: IQueryPort):
    # Archive existing active configurations if requested
    if command.archive_current:
        # Get existing active config
        existing_config = await query.get_app_tenant_config(command.app_id, command.tenant_id)
        if existing_config:
            # Set it to inactive
            existing_config.active = False
            existing_config.modified_at = now_utc()
            existing_config.modified_by = command.modified_by
            uow.register_dirty(existing_config)
    
    # Create new configuration
    app_tenant_configuration = AppTenantConfig.create(app_id=command.app_id, tenant_id=command.tenant_id, config=command.config)
    app_tenant_configuration.created_by = command.created_by
    app_tenant_configuration.modified_by = command.modified_by
    uow.register_new(app_tenant_configuration)
    return app_tenant_configuration

"""
create default document operation definition
that will be created in case no operation definition is found
"""
@dispatcher.register(CreateDefaultMedicationDocumentOperationDefinition)
@inject()
async def create_default_document_operation_definition(command: CreateDefaultMedicationDocumentOperationDefinition, uow: IUnitOfWork, storage: IStoragePort):
    document_operation_definition = DocumentOperationDefinition.create(name=command.name,
                                       description=command.description,
                                       operation_type=command.operation_type,
                                       operation_name=command.operation_name,
                                       document_workflow_id=command.document_workflow_id,
                                       step_config=command.step_config)
    uow.register_new(document_operation_definition)
    return document_operation_definition

@dispatcher.register(AutoCreateDocumentOperationDefinition)
@inject()
async def autocreate_document_operation_definition(command: AutoCreateDocumentOperationDefinition, uow: IUnitOfWork, query: IQueryPort):
    doc_op_defs = await query.get_document_operation_definition_by_op_type(command.document_operation_type.value)
    doc_op_def = doc_op_defs[0] if doc_op_defs else None

    extra = command.toExtra()

    if doc_op_def is None:
        LOGGER.debug("Operation definition not found for operation type: %s  Creating...", command.document_operation_type.name, extra=extra)
        operation_type = command.document_operation_type.name
        LOGGER.debug("operation_type: %s", operation_type, extra=extra)

        root = get_module_root() + "/config/orchestration/" + operation_type

        files = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]

        step_config = {}

        has_step_config = False
        for file in files:
            step = file.replace(".json", "")
            LOGGER.debug("step: %s  file: %s", step, file, extra=extra)
            with open(root + "/" + file, 'r') as file:
                data = json.load(file)
                step_config[step] = data
                has_step_config = True

        if has_step_config:
            document_operation_definition = DocumentOperationDefinition.create(name=command.document_operation_type.value,
                                       description=command.document_operation_type.value,
                                       operation_type=command.document_operation_type.value,
                                       operation_name=command.document_operation_type.value,
                                       document_workflow_id=command.document_operation_type.value,
                                       step_config=step_config)
            uow.register_new(document_operation_definition)
            return document_operation_definition
        else:
            raise CommandError(f"Operation definition not found for operation type: {command.document_operation_type.name}")

    else:
        LOGGER.debug("Operation definition found for operation type: %s", command.document_operation_type.name, extra=extra)
        return doc_op_def

@dispatcher.register(UpdateDocumentStatusSnapshot)
@change_tracker_updates(name="UpdateDocumentStatusSnapshot")
@inject()
async def update_document_status_snapshot(command:UpdateDocumentStatusSnapshot, uow: IUnitOfWork | ChangeTracker,  query:IQueryPort):
    # Check if this is an onboarding/test case - these don't have real documents
    is_onboarding = command.patient_id in ONBOARDING_PATIENT_LIST

    if is_onboarding:
        LOGGER.info("Skipping document status update for onboarding/test case", extra={
            "patient_id": command.patient_id,
            "app_id": command.app_id,
            "document_id": command.document_id,
            "operation_type": command.doc_operation_status_snapshot.operation_type.value,
            "status": command.doc_operation_status_snapshot.status.value,
            "operation_instance_id": command.doc_operation_status_snapshot.operation_instance_id,
            "reason": "onboarding_test_extraction"
        })
        return None

    doc = await query.get_document(command.document_id)

    if doc:
        document:Document = Document(**doc)

        old_doc = await query.get_document(document.id)
        old_document = Document(**old_doc)
        LOGGER.debug("Old Document opstatus: %s", old_document.operation_status, extra=command.toExtra())

        old_status = old_document.operation_status[command.doc_operation_status_snapshot.operation_type.value] if command.doc_operation_status_snapshot.operation_type.value in document.operation_status else None

        document.update_operation_status(DocumentOperationStatusSnapshot(
            operation_type = command.doc_operation_status_snapshot.operation_type,
            status=command.doc_operation_status_snapshot.status,
            start_time=command.doc_operation_status_snapshot.start_time,
            end_time=command.doc_operation_status_snapshot.end_time,
            orchestration_engine_version=command.doc_operation_status_snapshot.orchestration_engine_version,
            operation_instance_id = command.doc_operation_status_snapshot.operation_instance_id
        ))
        uow.register_dirty(document)

        if old_status != document.operation_status[command.doc_operation_status_snapshot.operation_type.value]:
            LOGGER.debug("Document status changed for document %s: %s", command.document_id, document.operation_status[command.doc_operation_status_snapshot.operation_type.value].dict())
            status = document.operation_status[command.doc_operation_status_snapshot.operation_type.value]
            await document_state_change(DocumentStateChange(
                                app_id=command.app_id,
                                tenant_id=command.tenant_id,
                                patient_id=command.patient_id,
                                document=document,
                                operation_type=command.doc_operation_status_snapshot.operation_type,
                                status=status.status,
                            ),uow, query)
        else:
            LOGGER.debug("Document status not changed for document %s: %s", command.document_id, document.operation_status[command.doc_operation_status_snapshot.operation_type.value].dict())

        return document
    else:
        raise CommandError(f"Document with id {command.document_id} not found")

@dispatcher.register(DocumentStateChange)
@inject()
async def document_state_change(command: DocumentStateChange, uow: IUnitOfWork | ChangeTracker, query:IQueryPort):
    extra = command.toExtra()
    is_endstate = False
    if command.status == DocumentOperationStatus.COMPLETED:
        extra.update({
            "document": command.document.dict()
        })
        Metric.send("DOCUMENT_STATE_CHANGE", branch=command.status.value, tags=extra)
        is_endstate = True
    elif command.status == DocumentOperationStatus.FAILED:
        extra.update({
            "document": command.document.dict()
        })
        Metric.send("DOCUMENT_STATE_CHANGE", branch=command.status.value, tags=extra)
        is_endstate = True
    else:
        # Enhanced non-end state logging
        LOGGER.info("Document state change received but not an end state", extra={
            **extra,
            "document_state": {
                "status": command.status.value,
                "operation_type": command.operation_type.value if command.operation_type else None,
                "is_end_state": False,
                "document_id": command.document.id,
                "will_trigger_callback": False,
                "reason": "Not an end state (COMPLETED or FAILED)"
            }
        })


    if is_endstate and command.document.is_test:
        metadata = command.document.metadata
        mode = metadata.get("e2e_test", {}).get("mode", None)
        run_id = metadata.get("e2e_test", {}).get("testrun_id", None)
        testcase_id = metadata.get("e2e_test", {}).get("testcase_id", None)
        startdate = metadata.get("e2e_test", {}).get("test_startdate", None)
        document = command.document

        assess_command = AssessTestCaseResults(mode=mode,
                                               run_id=run_id,
                                               testcase_id=testcase_id,
                                               document=document,
                                               start_date=datetime.datetime.fromisoformat(startdate))

        extra.update({
            "parent_command_id": command.id,
            "command_id": assess_command.id
        })
        LOGGER.debug("Detected the orchestration completion for a test document.  Queuing command to assess the test case results: %s", assess_command.dict(), extra=extra)
        await create_command(assess_command, uow)

    # Send status callback for all status changes if configured
    await _send_status_callback_if_configured(command, query)

    # Log when document reaches an end state (COMPLETED or FAILED)
    if is_endstate:
        # Enhanced end state logging with structured data
        end_state_info = {
            "document_state": {
                "document_id": command.document.id,
                "status": command.status.value,
                "operation_type": command.operation_type.value if command.operation_type else None,
                "is_test_document": command.document.is_test,
                "has_metadata": bool(command.document.metadata),
                "operation_status_keys": list(command.document.operation_status.keys()) if command.document.operation_status else []
            },
            "callback_trigger": {
                "will_trigger_callback": True,
                "reason": "Document reached end state"
            }
        }

        # Add integration override detection
        if command.document.metadata and "integration" in command.document.metadata:
            integration_override = command.document.metadata["integration"]
            end_state_info["callback_trigger"]["has_integration_override"] = True
            end_state_info["callback_trigger"]["override_callback_enabled"] = integration_override.get("callback", {}).get("enabled", False)
            end_state_info["callback_trigger"]["override_base_url"] = integration_override.get("base_url", "not_specified")
        else:
            end_state_info["callback_trigger"]["has_integration_override"] = False

        LOGGER.info("Document reached end state: %s for document %s - triggering callback", command.status.value, command.document.id, extra={
            **extra,
            **end_state_info
        })

        from paperglass.usecases.documents import on_document_processing_complete
        await on_document_processing_complete(command.document, query)




@dispatcher.register(CreateOrUpdateDocumentOperation)
@inject()
async def create_document_operation(command: CreateOrUpdateDocumentOperation, uow: IUnitOfWork, query: IQueryPort, messaging: IMessagingPort, cloud_task: ICloudTaskPort):
    # in future, need to query by operation definition id

    extra = command.toExtra()
    document_operation_instance:DocumentOperationInstance = None

    document_operation: DocumentOperation = await query.get_document_operation_by_document_id(command.document_id,operation_type=command.operation_type)
    if not document_operation:
        document_operation: DocumentOperation = DocumentOperation.create(app_id=command.app_id,
                                    tenant_id=command.tenant_id,
                                    patient_id=command.patient_id,
                                    document_id=command.document_id,
                                    operation_type=command.operation_type,
                                    active_document_operation_definition_id=command.active_document_operation_definition_id,
                                    active_document_operation_instance_id=command.active_document_operation_instance_id
                                )
        uow.register_new(document_operation)
    else:
        document_operation.update_active_document_operation_instance_id(command.active_document_operation_instance_id,command.active_document_operation_definition_id)
        uow.register_dirty(document_operation)

    if command.active_document_operation_instance_id:
        document_operation_instance:DocumentOperationInstance = await query.get_document_operation_instance_by_id(command.active_document_operation_instance_id)
        if document_operation_instance:
            document_operation_instance.status = command.status or DocumentOperationStatus.COMPLETED
            document_operation_instance.end_date = now_utc().isoformat()
            uow.register_dirty(document_operation_instance)

        # Raise pubsub event for end of orchestration pipeline ------------------------------------------------------------------------------
        try:
            data = command.dict()
            msg = MessageContainer(
                message_type = "orchestration_complete",
                version = "1.0",
                metadata={},
                data=data,
            )
            LOGGER.debug("Publishing orchestration complete message to pubsub topic %s: %s", PUBSUB_EVENT_ORCHESTRATIONCOMPLETE_TOPIC, msg.dict(), extra=extra)
            messageId = await messaging.publish(PUBSUB_EVENT_ORCHESTRATIONCOMPLETE_TOPIC, msg.dict())
            LOGGER.debug("Submitted pubsub message to topic '%s' with messageId: %s", PUBSUB_EVENT_ORCHESTRATIONCOMPLETE_TOPIC, messageId, extra=extra)
        except Exception as e:
            extra2 = {
                "error": exceptionToMap(e)
            }
            extra2.update(extra)
            LOGGER.error("Error in publishing orchestration complete message to pubsub topic %s: %s", PUBSUB_EVENT_ORCHESTRATIONCOMPLETE_TOPIC, str(e), extra=extra2)

        # Directly schedule the grader to perform grading on the results (In future this should trigger from an eventarc from the orchestrationcomplete topic)
        try:
            if command.operation_type == DocumentOperationType.MEDICATION_EXTRACTION.value:
                operation_type = DocumentOperationType.MEDICATION_GRADER.value
                LOGGER.debug("Scheduling grader to perform grading window is enabled? %s", ORCHESTRATION_GRADER_SCHEDULE_WINDOW_ENABLED, extra=extra)
                if ORCHESTRATION_GRADER_SCHEDULE_WINDOW_ENABLED:
                    queue_orch_command = QueueOrchestration(document_operation_type=operation_type, document_id=command.document_id)
                    ret = await queue_orchestration(queue_orch_command, uow, cloud_task)
                    LOGGER.debug("Queued orchestration for medication grader to perform grading on document %s: %s", command.document_id, ret, extra=extra)
                else:
                    command_grader = StartOrchestration(
                        document_operation_type=operation_type,
                        document_id=command.document_id
                    )
                    LOGGER.debug("Starting orchestration for medication grader to perform grading on document %s immediately", command_grader.document_id, extra=extra)
                    ret = await start_orchestration(command_grader, uow)

            else:
                LOGGER.debug("No need to schedule medication grader for operation type: %s", command.operation_type, extra=extra)

        except Exception as e:
            extra2 = {
                "error": exceptionToMap(e)
            }
            extra2.update(extra)
            LOGGER.error("Error in scheduling grader to perform grading: %s", str(e), extra=extra2)

    await update_document_status_snapshot(UpdateDocumentStatusSnapshot(document_id=command.document_id,
                                                                    tenant_id=command.tenant_id,
                                                                    patient_id=command.patient_id,
                                                                    app_id=command.app_id,
                                                                    doc_operation_status_snapshot=DocumentOperationStatusSnapshot(
                                                                        operation_type=command.operation_type,
                                                                        status=command.status,
                                                                        start_time=document_operation_instance.start_date,
                                                                        end_time=document_operation_instance.end_date)
                                                                    ),
                                                                    uow, query)

    return document_operation

@dispatcher.register(CreateDocumentOperationInstance)
@change_tracker_updates(name="CreateDocumentOperationInstance")
@inject()
async def create_document_operation_instance(command: CreateDocumentOperationInstance, uow: IUnitOfWork, storage: IStoragePort, query: IQueryPort):

    extra = command.toExtra()

    doc_operation_definition:DocumentOperationDefinition = await query.get_document_operation_definition_by_id(command.document_operation_definition_id)
    #doc_operation_definition:DocumentOperationDefinition = await uow.get(DocumentOperationDefinition, command.document_operation_definition_id)
    operation_type = doc_operation_definition.operation_type

    doc_operation_instance:DocumentOperationInstance = DocumentOperationInstance.create(app_id=command.app_id,
                                        tenant_id=command.tenant_id,
                                        patient_id=command.patient_id,
                                        document_id=command.document_id,
                                        document_operation_definition_id=command.document_operation_definition_id,
                                        start_date = now_utc().isoformat(),
                                        end_date = None,
                                        status=DocumentOperationStatus.IN_PROGRESS,
                                        priority=command.priority)
    uow.register_new(doc_operation_instance)

    extra["document_operation_instance_id"] = doc_operation_instance.id
    extra["operation_type"] = operation_type

    LOGGER2.info("Document operation instance created", extra=extra)
    return doc_operation_instance

@dispatcher.register(UpdateDocumentOperationInstance)
@change_tracker_updates(name="UpdateDocumentOperationInstance")
@inject()
async def update_document_operation_instance(command: UpdateDocumentOperationInstance, uow: IUnitOfWork, query:IQueryPort, storage: IStoragePort):
    document_operation_instance: DocumentOperationInstance = await query.get_document_operation_instance_by_id(command.id)
    if document_operation_instance:
        document_operation_instance.update_status(command.status)
        uow.register_dirty(document_operation_instance)
    else:
        raise CommandError(f"Document operation instance with id {command.id} not found")

    return document_operation_instance

@dispatcher.register(CreateDocumentOperationInstanceLog)
@change_tracker_updates(name="CreateDocumentOperationInstanceLog")
@inject()
async def create_document_operation_instance_log(command: CreateDocumentOperationInstanceLog, uow: IUnitOfWork, storage: IStoragePort):
    start_datetime = now_utc()
    doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                    tenant_id=command.tenant_id,
                                                                    patient_id=command.patient_id,
                                                                    document_operation_instance_id=command.document_operation_instance_id,
                                                                    document_operation_definition_id=command.document_operation_definition_id,
                                                                    document_id=command.document_id,
                                                                    step_id= command.step_id,
                                                                    start_datetime=start_datetime,
                                                                    context=command.context,
                                                                    page_number=command.page_number,
                                                                    status = command.status)
    doc_logger = DocumentOperationInstanceLogService()
    #uow.register_new(doc_operation_instance_log)
    await doc_logger.save(doc_operation_instance_log, uow)
    return doc_operation_instance_log


"""
create default document operation definition
that will be created in case no operation definition is found
"""
@dispatcher.register(CreateDefaultMedicationDocumentOperationDefinition)
@inject()
async def create_default_document_operation_definition(command: CreateDefaultMedicationDocumentOperationDefinition, uow: IUnitOfWork, storage: IStoragePort):
    document_operation_definition = DocumentOperationDefinition.create(name=command.name,
                                       description=command.description,
                                       operation_type=command.operation_type,
                                       operation_name=command.operation_name,
                                       document_workflow_id=command.document_workflow_id,
                                       step_config=command.step_config)
    uow.register_new(document_operation_definition)
    return document_operation_definition

# DUPLICATE functions
# @dispatcher.register(CreateDocumentOperationInstance)
# @inject()
# async def create_document_operation_instance(command: CreateDocumentOperationInstance, uow: IUnitOfWork, storage: IStoragePort):
#     doc_operation_instance:DocumentOperationInstance = DocumentOperationInstance.create(app_id=command.app_id,
#                                         tenant_id=command.tenant_id,
#                                         patient_id=command.patient_id,
#                                         document_id=command.document_id,
#                                         document_operation_definition_id=command.document_operation_definition_id,
#                                         start_date = now_utc().isoformat(),
#                                         end_date = None)
#     uow.register_new(doc_operation_instance)
#     return doc_operation_instance

# @dispatcher.register(CreateDocumentOperationInstanceLog)
# @inject()
# async def create_document_operation_instance_log(command: CreateDocumentOperationInstanceLog, uow: IUnitOfWork, storage: IStoragePort):
#     doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
#                                                                     tenant_id=command.tenant_id,
#                                                                     patient_id=command.patient_id,
#                                                                     document_operation_instance_id=command.document_operation_instance_id,
#                                                                     document_operation_definition_id=command.document_operation_definition_id,
#                                                                     document_id=command.document_id,
#                                                                     step_id= command.step_id,
#                                                                     context=command.context,
#                                                                     status = DocumentOperationStatus.COMPLETED)
#     uow.register_new(doc_operation_instance_log)


@dispatcher.register(TriggerExtraction)
@inject()
async def trigger_extraction(command: TriggerExtraction, uow: IUnitOfWork, storage: IStoragePort):
    thisSpanName = "trigger_extraction"
    with await opentelemetry.getSpan(thisSpanName) as span:
        extra = command.toExtra()

        LOGGER.warning('Triggering extraction for document %s', command.source_document_storage_uri, extra=extra)
        # temp_file = f'/tmp/{command.source_document_storage_uri.split("/")[-1]}'
        # file = open(temp_file, 'wb')
        # file.write(await storage.get_document_raw(command.source_document_storage_uri))
        return await create_document(CreateDocument(app_id=command.app_id,
                                        tenant_id=command.tenant_id,
                                        patient_id=command.patient_id,
                                        file_name=command.source_document_storage_uri.split('/')[-1],
                                        file=await storage.get_document_raw(command.source_document_storage_uri),
                                        source_storage_uri = command.source_document_storage_uri),
                                        uow,
                                        storage)

@dispatcher.register(Orchestrate)
@inject()
async def orchestrate_handler(command: Orchestrate, uow: IUnitOfWork, app_integration_adapter: IApplicationIntegration):
    extra = command.toExtra()

    LOGGER.warning('Orchestrating document %s', command.document_id, extra=extra)
    import requests
    try:
        if os.environ.get('CLOUD_PROVIDER') == 'local':
            LOGGER.warning("Running locally: %s", json.dumps(extra, indent=2))
            from paperglass.usecases.configuration import get_config
            from paperglass.usecases.orchestrator import orchestrate
            config:Configuration = await get_config(command.app_id, command.tenant_id)
            if not config:
                LOGGER.error(f'No configuration found for app_id {command.app_id} and tenant_id {command.tenant_id}')
                #config = await create_app_configuration(CreateAppConfiguration(app_id=command.app_id,config=Configuration()))
            if config and config.use_v3_orchestration_engine:
                LOGGER.debug("Orchestrating document %s using v3", command.document_id)
                await orchestrate(command.document_id, command.force_new_instance, priority=command.priority)
            return
        else:
            from paperglass.usecases.configuration import get_config
            from paperglass.usecases.orchestrator import orchestrate
            config:Configuration = await get_config(command.app_id, command.tenant_id)
            if not config:
                LOGGER.error(f'No configuration found for app_id {command.app_id} and tenant_id {command.tenant_id}', extra=extra)
                #config = await create_app_configuration(CreateAppConfiguration(app_id=command.app_id,config=Configuration()))
            if config and config.use_v3_orchestration_engine:
                LOGGER.debug("Orchestrating document %s using v3", command.document_id, extra=extra)
                await orchestrate(command.document_id, command.force_new_instance, priority=command.priority)
            else:
                url = f"{SELF_API}/orchestrate"
                queue = CLOUD_TASK_QUEUE_NAME
                payload = {"document_id": command.document_id}

                LOGGER.debug("Orchestrating document %s using v2", command.document_id, extra=extra)
                integration_project_name=INTEGRATION_PROJECT_NAME
                json_payload={
                    "START_CLOUD_TASK_API":f"{SELF_API}/start_cloud_task",
                    "CLOUD_TASK_ARGS":{
                        "location":"us-east4",
                        "url":url,
                        "queue":queue,
                        "service_account_email":SERVICE_ACCOUNT_EMAIL,
                        "payload":payload
                    },
                    "TOKEN":f"Bearer {command.token}"
                }

                extra2 = {
                    "cloudtask": json_payload
                }
                extra2.update(extra)
                LOGGER.debug("Application integration start payload", extra=extra2)
                trigger_id = APPLICATION_INTEGRATION_TRIGGER_ID
                result = await app_integration_adapter.start(integration_project_name, json_payload, trigger_id)
                LOGGER.info("application integration result: %s", result, extra=extra2)
                return result
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.error(f'Error in orchestrating document {command.document_id}, {str(e)}', extra=extra)

@dispatcher.register(GetDocument)
@inject()
async def get_document(command: GetDocument, uow: IUnitOfWork):
    return await uow.get(Document, command.document_id)


@dispatcher.register(CreateDocument)
@inject
async def create_document(command: CreateDocument, uow: IUnitOfWork, storage: IStoragePort, query:IQueryPort):
    extra = command.toExtra()
    try:
        LOGGER.warning('Uploading document %s', command.file_name, extra=extra)
        from paperglass.usecases.documents import create_document
        if command.source_storage_uri:
            doc_dict = await query.get_document_by_source_storage_uri(command.source_storage_uri,command.tenant_id, command.patient_id)
            if doc_dict:
                # doc_statuses = await query.get_document_statuses(doc_dict.get("id"), doc_dict.get("execution_id"))
                # doc_statuses = [DocumentStatus(**x) for x in doc_statuses]
                # if doc_statuses and any([x.status == DocumentStatusType.FAILED for x in doc_statuses]):
                #     LOGGER.warning('Skipping Uploading document %s since its already uploaded', command.file_name)
                LOGGER.warning('Skipping Uploading document %s since its already uploaded', command.file_name, extra=extra)
                return Document(**doc_dict)

            if command.source_storage_uri and command.source == 'host':
                doc_dict = await query.get_document_by_source_storage_uri(command.source_storage_uri,command.tenant_id, command.patient_id)
                if not doc_dict:
                    document:Document = await create_document(command.app_id,command.tenant_id,command.patient_id,
                                            command.file_name,
                                            await storage.get_external_document_raw(command.source_storage_uri),
                                            command.token,
                                            command.priority,
                                            storage)
                    document.source_storage_uri = command.source_storage_uri
                    document.source=command.source
                    document.metadata = command.metadata
                    document.priority = command.priority
                    document.source_id = command.source_id
                    extra.update({
                        "document_id": document.id,
                        "source_id": document.source_id
                    })
                    LOGGER.debug("[DEBUG_FLOW] Document persistence setting source_id", extra=extra)
                    uow.register_new(document)
                    return document
        elif command.source == "api" and command.source_api:
            #Retrieving document from an API endpoint
            from paperglass.domain.utils.sha256 import get_sha256_hash

            extra.update({
                "http_request": {
                    "method": command.source_api.method,
                    "url": command.source_api.url,
                    "headers": command.source_api.headers,
                    "body": command.source_api.body
                }
            })
            LOGGER.debug("Creating document from api reference", extra=extra)

            http_client = HttpRestClient()
                        
            connection_timeout = 5.0
            response_timeout = 10.0            
            
            doc_response = await http_client.resolve(method=command.source_api.method,
                                url=command.source_api.url,
                                headers=command.source_api.headers,
                                body=command.source_api.body,
                                connection_timeout=connection_timeout,
                                response_timeout=response_timeout
                                )

            extra.update({
                "http_response": {
                    "status": doc_response.get("status"),
                    "body": doc_response.get("data"),
                    "headers": doc_response.get("headers")
                }
            })

            if doc_response.get("status") != 200:
                LOGGER.error("Error in retrieving host document from API: %s", doc_response.get("data"), extra=extra)
                raise CommandError(f"Error in retrieving host document from API: {doc_response.get('data')}")

            LOGGER.debug("Host document retrieved from API", extra=extra)

            doc_data = doc_response.get("data")
            source_sha256 = get_sha256_hash(doc_data)

            LOGGER.debug("Document sha256: %s", source_sha256, extra=extra)

            doc_dict = await query.get_document_by_source_id(command.source_id, app_id=command.app_id, tenant_id=command.tenant_id, patient_id=command.patient_id)
            #doc_dict = await query.get_document_by_sha256(source_sha256, command.tenant_id, command.patient_id)
            if source_sha256 and doc_dict:
                LOGGER.debug("Document already exists in the system with sha256: %s", source_sha256, extra=extra)
                # doc_statuses = await query.get_document_statuses(doc_dict.get("id"), doc_dict.get("execution_id"))
                # doc_statuses = [DocumentStatus(**x) for x in doc_statuses]
                # if doc_statuses and any([x.status == DocumentStatusType.FAILED for x in doc_statuses]):
                #     LOGGER.warning('Skipping Uploading document %s since its already uploaded', command.file_name)
                LOGGER.warning('Skipping Uploading document %s since its already uploaded', command.file_name, extra=extra)
                return Document(**doc_dict)
            else:
                LOGGER.debug("Creating document", extra=extra)
                document:Document = await create_document(command.app_id,command.tenant_id,command.patient_id,
                                        command.file_name,
                                        doc_data,
                                        command.token,
                                        command.priority,
                                        storage,
                                        source_sha256=source_sha256
                                        )
                document.source=command.source
                document.source_id = command.source_id
                document.source_api = command.source_api
                document.metadata = command.metadata
                document.priority = command.priority
                extra["document_id"] = document.id
                extra["source_id"] = document.source_id
                LOGGER.info(f"[DEBUG_FLOW] Document persistence setting source_id", extra=extra)
                uow.register_new(document)
                return document


        document = await create_document(command.app_id,command.tenant_id,command.patient_id,
                                         command.file_name,
                                         command.file,command.token,command.priority,storage)
        document.execution_id = command.execution_id
        document.source_storage_uri = command.source_storage_uri
        document.source=command.source
        document.metadata = command.metadata
        document.priority = command.priority
        document.source_id = command.source_id
        extra.update({
            "document_id": document.id,
            "source_id": document.source_id
        })
        LOGGER.debug("[DEBUG_FLOW] Document persistence setting source_id", extra=extra)
        uow.register_new(document)
        return document
    except UnsupportedFileTypeException as e:
        raise e
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.exception('Error in creating document at uri "%s": %s', command.source_storage_uri, str(e), extra=extra)
        raise e

@dispatcher.register(DocumentSpawnRevision)
@inject
async def document_spawn_revision(command: DocumentSpawnRevision, uow: IUnitOfWork, storage: IStoragePort):
    extra = command.toExtra()
    try:

        #original_doc = Document(**command.document.dict())
        command.document.delete()

        LOGGER.debug("Deleting original document %s", command.document.id, extra=extra)
        #LOGGER.debug("Document: %s", json.dumps(command.document.dict(), indent=2, cls=DateTimeEncoder), extra=extra)
        uow.register_dirty(command.document)

        document = command.document.clone()

        extra.update({
            "new_document_id": document.id,
        })

        LOGGER.debug("Cloning document to new document %s", document.id, extra=extra)
        uow.register_new(document)        

        Metric.send("DOCUMENT:SPAWN_REVISION", tags=extra)

        return document
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.error(f'Error in spawning revision for document {command.document_id}, {str(e)}', extra=extra)
        raise e

@dispatcher.register(UpdateDocumentPriority)
@inject()
async def update_document_priority(command: UpdateDocumentPriority, uow: IUnitOfWork, query: IQueryPort) -> Document:

    #uow.get(Document, command.document_id)
    doc = await query.get_document(command.document_id)
    document:Document = Document(**doc)

    if not document:
        raise NotFoundException(f"Document with id {command.document_id} not found")

    if document.priority != command.priority:
        extra = command.toExtra()
        extra.update({
            "original_priority": document.priority,
        })
        LOGGER.info('Updating document priority from %s to %s', document.priority, command.priority, extra=extra)
        Metric.send("DOCUMENT:PRIORITY:UPDATE", tags=extra)
        document.priority = command.priority
        uow.register_dirty(document)
    else:
        LOGGER.debug("Document priority is already %s", command.priority)

    return document

@dispatcher.register(GetDocumentLogs)
@inject
async def get_document_logs(command: GetDocumentLogs, uow: IUnitOfWork):
    from paperglass.usecases.documents import get_document_logs

    ret = await get_document_logs(command.document_id, filter=command.filter)
    return ret


@dispatcher.register(SplitPages)
@change_tracker_updates(name="SplitPages")
@inject
async def split_pages(command: SplitPages, uow: IUnitOfWork, storage: IStoragePort):
    """
    Splits a PDF document into individual pages and uploads them to the storage.

    Args:
        command (SplitPages): The SplitPages command containing the document ID.
        uow (IUnitOfWork): The unit of work for accessing the database.
        storage (IStoragePort): The storage port for uploading the document pages.

    Returns:
        None
    """
    extra = command.toExtra()

    LOGGER.debug("Splitting pages for documentId %s", command.document_id, extra=extra)
    thisSpanName = "split_pages"
    start_datetime = now_utc()
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        try:
            operation_context = {}

            # Split PDF into page, each of size 1
            LOGGER.debug("SplitPages: Splitting pages for documentId %s", command.document_id, extra=extra)
            document = await uow.get(Document, command.document_id)
            success_log_exists, log = await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,-1,command.step_id)
            if success_log_exists:
                return document
            from paperglass.usecases.documents import split_pages
            document = await split_pages(command.app_id, command.tenant_id, command.patient_id, document, command.document_operation_instance_id, command.document_operation_definition_id, storage)
            LOGGER.debug("SplitPages: Pages split for documentId %s", command.document_id, extra=extra)

            document.execution_id = command.execution_id
            uow.register_dirty(document)
            operation_context['document_id'] = document.id
            operation_context['page_count'] = len(document.pages) if document.pages else 0
            LOGGER.debug("SplitPages: Writing document operation instance log for documentId %s", command.document_id, extra=extra)
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context=operation_context,
                                                                                page_number=-1,
                                                                                status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            # status = DocumentStatus.create(app_id=command.app_id, tenant_id=command.tenant_id,patient_id=command.patient_id, document_id=document.id, status=DocumentStatusType.PAGES_SPLITTING_COMPLETED, message="")
            # status.execution_id = command.execution_id
            # uow.register_new(status)

            page_count = len(document.pages) if document.pages else 0
            extra2 = {
                "page_count": page_count,
                "elapsed_time": doc_operation_instance_log.elapsed_time
            }
            extra2.update(extra)
            LOGGER2.info("Step::%s completed", command.step_id, extra=extra2) #Logging metric

            # Doing this because GCP dashboards can't aggregate by sum a distribution metric
            for i in range(page_count):
                extra2.update( {
                    "page_number": i
                })
                LOGGER2.info("Page::Created page %s", i, extra=extra2)

            return document
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            try:
                LOGGER.error('Error in splitting pages: %s', str(e), extra=extra)
                operation_context['error'] = exceptionToMap(e)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=-1,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id)

                doc_logger = DocumentOperationInstanceLogService()
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)
            except Exception as e1:
                extra["error_in_exception"] = exceptionToMap(e1)
                LOGGER.error('Exception in splitpages error block',str(e1), extra=extra)
            raise OrchestrationExceptionWithContext(f"Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e

@dispatcher.register(CreatePage)
@change_tracker_updates(name="CreatePage")
@inject
async def create_page(command: CreatePage, uow: IUnitOfWork, query:IQueryPort):
    thisSpanName = "create_page"
    start_datetime = now_utc()
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_number", command.page_number)

        extra = command.toExtra()

        try:
            operation_context={
                "page_number": str(command.page_number),
            }
            success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
            if success_log_exists:
                log:DocumentOperationInstanceLog = log
                return await query.get_page_by_document_operation_instance_id(log.document_id,log.document_operation_instance_id,log.page_number)
            page = Page.create(app_id=command.app_id,tenant_id=command.tenant_id,number=command.page_number, storage_uri=command.storage_uri, document_id=command.document_id, patient_id=command.patient_id)
            page.execution_id = command.execution_id
            page.document_operation_instance_id = command.document_operation_instance_id
            LOGGER.debug("CreatePage: Created page %s", command.page_number, extra=extra)
            uow.register_new(page)
            # status = DocumentStatus.create(app_id=command.app_id, tenant_id=command.tenant_id,patient_id=command.patient_id, document_id=command.document_id, status=DocumentStatusType.PAGE_CREATION_COMPLETED, message="")
            # status.execution_id = command.execution_id
            # status.page_id = page.id
            # uow.register_new(status)
            operation_context['page'] = page.dict()
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context=operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra.update({
                "elapsed_time": doc_operation_instance_log.elapsed_time
            })
            LOGGER.info("Step::%s completed", command.step_id, extra=extra)

            return page
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            try:
                LOGGER.error('CreatePage: Error in creating page for documentId %s: %s', command.document_id, str(e), extra=extra)

                operation_context["page_number"] = str(command.page_number)
                operation_context["storage_uri"] = command.storage_uri
                operation_context['error'] = exceptionToMap(e)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id)

                doc_logger = DocumentOperationInstanceLogService()
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

            except Exception as e1:
                extra["error_in_exception"] = exceptionToMap(e1)
                LOGGER.error('Exception in createPage error block',str(e1), extra=extra)
            raise OrchestrationExceptionWithContext(f"Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e

@dispatcher.register(PerformOCR)
@change_tracker_updates(name="PerformOCR")
@inject
async def perform_ocr(command: PerformOCR, uow: IUnitOfWork | ChangeTracker, query:IQueryPort, storage: IStoragePort,docai: IDocumentAIAdapter):
    thisSpanName = "perform_ocr"
    start_datetime = now_utc()
    page=None
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_id", command.page_id)

        extra = command.toExtra()

        doc_logger = DocumentOperationInstanceLogService()
        try:
            operation_context = {
                "page_id": command.page_id
            }

            #page = await uow.get(Page, command.page_id)
            page = Page(**await query.get_page_by_id(command.page_id))
            success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,page.number,command.step_id)
            if success_log_exists:
                return page

            extra["page_number"] = page.number
            LOGGER.warning('PerformOCR: Performing OCR on page %s of document %s', page.number, page.document_id, extra=extra)

            # Get app config for accounting information
            app_config = None
            try:
                app_config = await query.get_app_config(command.app_id)
            except Exception as e:
                LOGGER.warning(f"Could not retrieve app config for app_id {command.app_id}: {e}", extra=extra)

            # Build metadata for Document AI billing
            billing_metadata = {
                "app_id": command.app_id,
                "tenant_id": command.tenant_id,
                "patient_id": command.patient_id,
                "document_id": command.document_id,
                "domain_id": "paperglass",
                "step": "PERFORM_OCR",
                "page_id": command.page_id,
                "page_number": page.number
            }

            # Add config-dependent fields if config exists
            if app_config and app_config.config and app_config.config.get("accounting"):
                accounting = app_config.config.get("accounting")
                billing_metadata.update({
                    "business_unit": accounting.get("business_unit", "unknown"),
                    "solution_code": accounting.get("solution_code", "unknown")
                })
            else:
                # Default values if config not available
                billing_metadata.update({
                    "business_unit": "unknown",
                    "solution_code": "unknown"
                })

            LOGGER.debug(f"Document AI billing metadata: {billing_metadata}", extra=extra)

            # Perform OCR
            from paperglass.usecases.documents import perform_ocr
            doc_ai_output = await docai.process_document(page.storage_uri, metadata=billing_metadata)

            if doc_ai_output:
                # Identify page rotation
                LOGGER.debug('PerformOCR: Persisting OCR output for documentId %s', command.document_id, extra=extra)
                results = json.dumps(doc_ai_output[0]).encode('utf-8')
                page = await perform_ocr(page, results,storage)
                page.execution_id = command.execution_id
                page.document_operation_instance_id = command.document_operation_instance_id
                LOGGER.debug('PerformOCR: Identifying page rotation for documentId %s', command.document_id, extra=extra)
                rotation = docai.identify_rotation(doc_ai_output[0]['page'])

                extra["rotation"] = rotation
                LOGGER.info('PerformOCR: Identified page rotation for documentId %s page %s: %.4f', command.document_id, command.page_id, rotation, extra=extra)
                # page.rotation = rotation

                # uow.register_dirty(page)

                #ToDo: create new entity for ocr and store rotation value in it. refactor frontend code to use the same

                operation_context["page_id"] = page.id
                operation_context["page_number"] = page.number
                operation_context['page'] = page.dict()
                operation_context["rotation"] = rotation
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id,
                                                                                document_id=command.document_id,
                                                                                start_datetime=start_datetime,
                                                                                step_id= command.step_id,
                                                                                context=operation_context,
                                                                                page_number=page.number,
                                                                                status = DocumentOperationStatus.COMPLETED)
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

                extra.update({
                    "elapsed_time": doc_operation_instance_log.elapsed_time
                })
                LOGGER.info("Step::%s completed", command.step_id, extra=extra)

                return page
            else:
                LOGGER.error('PerformOCR: No output from OCR for documentId %s', command.document_id, extra=extra)

                operation_context['error'] = {'message': 'No output from OCR'}
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=page.number,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id)
                #uow.register_new(doc_operation_instance_log)
                doc_logger = DocumentOperationInstanceLogService()
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            try:
                LOGGER.error('PerformOCR: Error in performing OCR for documentId %s: %s', command.document_id, str(e), extra=extra)

                operation_context["page_id"] = str(command.page_id)
                operation_context["page_number"] = page.number if page else -1
                operation_context['error'] = exceptionToMap(e)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=page.number if page else -1,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id)

                #uow.register_new(doc_operation_instance_log)
                doc_logger = DocumentOperationInstanceLogService()
            except Exception as e1:
                extra["error_in_exception"] = exceptionToMap(e1)
                LOGGER.error('Exception in performocr error block',str(e1), extra=extra)
            raise OrchestrationExceptionWithContext(f"Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e


@dispatcher.register(ExtractTextAndClassify)
@change_tracker_updates(name="ExtractTextAndClassify")
@inject
async def extract_text(command: ExtractTextAndClassify,
                       uow: IUnitOfWork,
                       storage: IStoragePort,
                       settings: ISettingsPort,
                       query:IQueryPort,
                       prompt_adapter: IPromptAdapter):
    thisSpanName = "extract_text"
    start_datetime = now_utc()
    page = None
    medications = None
    conditions = None
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_id", command.page_id)
        span.set_attribute("page_number", command.page_number)

        extra = command.toExtra()

        try:

            operation_context = {
                "page_id": command.page_id,
                "page_number": command.page_number,
                "model": {
                    "name": command.model,
                },
            }

            page = Page(**await query.get_page_by_id(command.page_id))
            success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
            if success_log_exists:
                classified_page = ClassifiedPage(await query.get_classified_page(command.page_id))
                return classified_page

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = command.step_id,
                document_id = command.document_id,
                page_number = command.page_number,
                document_operation_def_id = command.document_operation_definition_id,
                document_operation_instance_id = command.document_operation_instance_id,
                priority = command.priority
            )

            LOGGER.warning('ExtractText: Extracting Text on page %s of document %s', command.page_id, command.document_id, extra=extra)
            # doc_content = await storage.get_document_page(app_id=command.app_id, tenant_id=command.tenant_id,patient_id=command.patient_id, document_id=command.document_id, page_number=command.page_number)
            LOGGER.debug('ExtractText: Calling multi modal predict for page %s of document %s', command.page_id, command.document_id, extra=extra)
            model = command.model
            operation_context["prompt"]=command.prompt
            #operation_context["doc_content_length"]=len(doc_content)
            prompts = [command.prompt, (page.storage_uri, "application/pdf")]
            result = await prompt_adapter.multi_modal_predict_2(prompts, model, metadata=opMeta.dict())
            import re

            if result:
                #extracted_text = re.search(r'<EXTRACT>(.*?)</EXTRACT>', result, re.DOTALL).group(1)
                medications_match = re.search(r'<MEDICATIONS>(.*?)</MEDICATIONS>', result, re.DOTALL)
                medications = medications_match.group(1) if medications_match else None
                conditions_match = re.search(r'<CONDITIONS>(.*?)</CONDITIONS>', result, re.DOTALL)
                conditions = conditions_match.group(1) if conditions_match else None
                #result = await prompt_adapter.multi_modal_predict([command.prompt, (doc_content, 'application/pdf')],model=model, metadata=opMeta.dict())

            # We dont need extracted_text anymore downstream
            # page.add_text(extracted_text)
            # page.execution_id = command.execution_id
            # page.document_operation_instance_id = command.document_operation_instance_id
            # uow.register_dirty(page)

            classified_page:ClassifiedPage=ClassifiedPage.create(command.app_id,
                                                                 command.tenant_id,
                                                                 command.patient_id,
                                                                 command.document_id,
                                                                 command.page_id,
                                                                 "",
                                                                 command.page_number)

            if medications:
                classified_page.add_label("medications",medications,
                                            command.document_operation_instance_id,
                                            command.document_operation_definition_id)

                operation_context["medications"] = medications

            if conditions:
                classified_page.add_label("conditions",conditions,
                                            command.document_operation_instance_id,
                                            command.document_operation_definition_id)
                operation_context["conditions"] = conditions


            uow.register_new(classified_page)

            LOGGER.debug("ExtractText: Writing document operation instance log for documentId %s", command.document_id, extra=extra)

            operation_context['page'] = page.dict()
            operation_context['model_response'] = result
            operation_context['llm_prompt'] = [command.prompt]
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra.update({
                "elapsed_time": doc_operation_instance_log.elapsed_time
            })
            LOGGER.info("Step::%s completed", command.step_id, extra=extra)

            return classified_page
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            try:
                LOGGER.error('ExtractText: Error in extracting text for page %s from documentId %s: %s', command.page_id, command.document_id, str(e), extra=extra)
                operation_context["page_id"] = command.page_id
                operation_context['page_number'] = page.number if page else -1
                operation_context['error'] = exceptionToMap(e)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id)

                doc_logger = DocumentOperationInstanceLogService()
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

            except Exception as e1:
                extra["error_in_exception"] = exceptionToMap(e1)
                LOGGER.error('Exception in extract text error block',str(e1), extra=extra)
            raise OrchestrationExceptionWithContext(f"Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e

@dispatcher.register(ExtractText)
@change_tracker_updates(name="ExtractText")
@inject
async def extract_text(command: ExtractText, uow: IUnitOfWork, storage: IStoragePort, settings: ISettingsPort, prompt_adapter: IPromptAdapter):
    thisSpanName = "extract_text"
    start_datetime = now_utc()
    page = None
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_id", command.page_id)
        span.set_attribute("page_number", command.page_number)

        extra = command.toExtra()

        try:

            operation_context = {}
            operation_context.update(extra)
            page = await uow.get(Page, command.page_id)
            success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
            if success_log_exists:
                return page

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = command.step_id,
                document_id = command.document_id,
                page_number = command.page_number,
                document_operation_def_id = command.document_operation_definition_id,
                document_operation_instance_id = command.document_operation_instance_id,
            )

            LOGGER.warning('ExtractText: Extracting Text on page %s of document %s', command.page_id, command.document_id, extra=extra)
            doc_content = await storage.get_document_page(app_id=command.app_id, tenant_id=command.tenant_id,patient_id=command.patient_id, document_id=command.document_id, page_number=command.page_number)
            LOGGER.debug('ExtractText: Calling multi modal predict for page %s of document %s', command.page_id, command.document_id, extra=extra)
            model = command.model
            operation_context["prompt"]=command.prompt
            operation_context["doc_content_length"]=len(doc_content)
            result = await prompt_adapter.multi_modal_predict([command.prompt, (doc_content, 'application/pdf')],model=model, metadata=opMeta.dict())

            page.add_text(result)
            page.execution_id = command.execution_id
            page.document_operation_instance_id = command.document_operation_instance_id
            uow.register_dirty(page)

            LOGGER.debug("ExtractText: Writing document operation instance log for documentId %s", command.document_id, extra=extra)

            operation_context['page'] = page.dict()
            operation_context['model_response'] = result
            operation_context['llm_prompt'] = [command.prompt]
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra.update({
                "elapsed_time": doc_operation_instance_log.elapsed_time
            })
            LOGGER2.info("Step::%s completed", command.step_id, extra=extra)

            return page
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            try:
                LOGGER.error('ExtractText: Error in extracting text for page %s from documentId %s: %s', command.page_id, command.document_id, str(e), extra=extra)
                operation_context["page_id"] = command.page_id
                operation_context['page_number'] = page.number if page else -1
                operation_context['error'] = exceptionToMap(e)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id)

                doc_logger = DocumentOperationInstanceLogService()
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)
            except Exception as e1:
                extra["error_in_exception"] = exceptionToMap(e1)
                LOGGER.error('Exception in extract text error block',str(e1), extra=extra)
            raise OrchestrationExceptionWithContext(f"Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e


@dispatcher.register(ClassifyPage)
@change_tracker_updates(name="ClassifyPage")
@inject
async def classify_page(command: ClassifyPage, uow: IUnitOfWork, prompt_adapter: IPromptAdapter, settings_adapter: ISettingsPort, query: IQueryPort):
    thisSpanName = "classify_page"
    start_datetime = now_utc()
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_id", command.page_id)

        extra = command.toExtra()

        try:
            LOGGER.info("ClassifyPage: Classifying page %s of document %s", command.page_id, command.document_id, extra=extra)

            operation_context={}
            operation_context.update(extra)

            success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
            if success_log_exists:
                classified_page: ClassifiedPage = query.get_classified_page(command.page_id)
                return classified_page

            labeler = SingleLabeling()
            labels = [x.value for x in PageLabel]

            operation_context["labels"] = labels

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = command.step_id,
                document_id = command.document_id,
                page_number = command.page_number,
                document_operation_def_id = command.document_operation_definition_id,
                document_operation_instance_id = command.document_operation_instance_id,
            )

            # Perform request
            prompt_prefix, prompt_suffix = labeler.render(labels)
            LOGGER.debug('ClassifyPage: Prompt prefix: %s', prompt_prefix, extra=extra)
            LOGGER.debug('ClassifyPage: Prompt suffix: %s', prompt_suffix, extra=extra)

            LOGGER.debug("ClassifyPage: Calling multi modal predict to classify page for page %s of document %s", command.page_id, command.document_id, extra=extra)

            text = await prompt_adapter.multi_modal_predict(
                [prompt_prefix , command.page_text, prompt_suffix], model=command.model, metadata=opMeta.dict())
            LOGGER.debug('ClassifyPage: Prompt result: %s', text, extra=extra)
            operation_context['model_response'] = text
            operation_context['llm_prompt'] = [prompt_prefix, command.page_text, prompt_suffix]

            response = labeler.parse_response(text)

            LOGGER.debug("ClassifyPage: Creating classified page for documentId %s", command.document_id, extra=extra)
            classified_page:ClassifiedPage=ClassifiedPage.create(command.app_id, command.tenant_id, command.patient_id, command.document_id, command.page_id,command.page_text, command.page_number)

            for label, content in response.items():
                LOGGER.info('ClassifyPage: Label: %s, Content: %s', label, content, extra=extra)
                classified_page.add_label(label,content,
                                          command.document_operation_instance_id,
                                          command.document_operation_definition_id)

                operation_context[label] = content

            if not response:
                classified_page.add_label("no_label","no_content",
                                          command.document_operation_instance_id,
                                          command.document_operation_definition_id)

            classified_page.execution_id = command.execution_id
            classified_page.document_operation_instance_id = command.document_operation_instance_id
            uow.register_new(classified_page)
            LOGGER.debug("ClassifyPage: Writing document operation instance log for documentId %s", command.document_id, extra=extra)
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra.update({
                "elapsed_time": doc_operation_instance_log.elapsed_time
            })
            LOGGER2.info("Step::%s completed", command.step_id, extra=extra)

            return classified_page
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            try:
                LOGGER.error('ClassifyPage: Error in classifying page for documentId %s: %s', command.document_id, str(e), extra=extra)
                operation_context["page_id"] = str(command.page_id)
                operation_context["page_number"] = command.page_number
                operation_context['error'] = exceptionToMap(e)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_instance_id=command.document_operation_instance_id,
                                                                                document_operation_definition_id=command.document_operation_definition_id)

                doc_logger = DocumentOperationInstanceLogService()
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)
            except Exception as e1:
                extra["error_in_exception"] = exceptionToMap(e1)
                LOGGER.error('Exception classify page error block',str(e1), extra=extra)
            raise OrchestrationExceptionWithContext(f"Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e

# below block goes in separate domain
@dispatcher.register(ExtractMedication)
@change_tracker_updates(name="ExtractMedication")
@inject()
async def extract_medication(command: ExtractMedication, uow:IUnitOfWork,
                             settings_adapter:ISettingsPort,
                             prompt_adapter:IPromptAdapter,
                             query_adapter:IQueryPort,
                             medispan_port:IMedispanPort,
                             relevancy_filter_adapter:IRelevancyFilterPort
                             ):
    thisSpanName = "extract_medication"
    start_datetime = now_utc()

    extra = command.toExtra()

    operation_context = {}
    operation_context.update(extra)

    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_id", command.page_id)
        span.set_attribute("page_number", command.page_number)

        doc_logger = DocumentOperationInstanceLogService()

        try:
            LOGGER.info('ExtractMedication: Extracting medication for documentId %s from %s', command.document_id, command.labelled_content, extra=extra)

            success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
            if success_log_exists:
                extracted_medications = await query_adapter.get_extracted_medications_by_operation_instance_id(command.document_id, command.document_operation_instance_id)

                return [x for x in extracted_medications if x.page_number == command.page_number]

            if not command.labelled_content:
                operation_context['error'] = {"message": 'No labelled content found'}
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
                #uow.register_new(doc_operation_instance_log)
                doc_logger.save(doc_operation_instance_log)

                extra.update({
                    "branch": "no_labelled_content",
                    "elapsed_time": doc_operation_instance_log.elapsed_time
                })
                LOGGER.info("Step::%s completed", command.step_id, extra=extra)

                return []

            all_contents = ""
            for content in command.labelled_content:
                all_contents += f'# Document: {command.document_id}, page: {command.page_number}\n'
                all_contents += content + '\n\n'


            if len(all_contents) <= 5:
                # for now treating as junk data and skipping
                operation_context['error'] = {"message": 'junk labelled content found'}
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

                extra.update({
                    "branch": "junk_labelled_content",
                    "elapsed_time": doc_operation_instance_log.elapsed_time
                })
                LOGGER.info("Step::%s completed", command.step_id, extra=extra)

                return []

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = command.step_id,
                document_id = command.document_id,
                page_number = command.page_number,
                document_operation_def_id = command.document_operation_definition_id,
                document_operation_instance_id = command.document_operation_instance_id,
                priority = command.priority
            )

            LOGGER.debug("ExtractMedication: Calling multi modal predict to extract medication for documentId %s", command.document_id, extra=extra)
            #llm_prompt = command.prompt.replace('<content></content>',all_contents)
            # llm_prompt = command.prompt.replace('<content></content>',"Refer to the attached pdf")
            llm_prompt =command.prompt
            operation_context['prompt'] = [llm_prompt]
            operation_context['model'] = {
                "name": command.model
            }

            page:Page = Page(**await query_adapter.get_page_by_id(command.page_id))

            prompts = [(page.storage_uri, "application/pdf"),llm_prompt]
            result = await prompt_adapter.multi_modal_predict_2(prompts,model=command.model, metadata=opMeta.dict())

            operation_context['model_response'] = result

            LOGGER.debug("ExtractMedication: Cleaning model response for extract medication for documentId %s", command.document_id, extra=extra)

            result = result.replace('**', '').replace('##', '').replace('```', '').replace('json', '')
            LOGGER.info("ExtractMedication: Prompt result: %s", result, extra=extra)
            result = Medication.toJSON(result)
            LOGGER.info('ExtractMedication: Prompt result: %s', result, extra=extra)
            if result and isinstance(result,dict) and "medications" in result.keys():
                result = result.get("medications")
                LOGGER.info('ExtractMedication: Prompt result 2: %s', result, extra=extra)

            medications = []
            idx = 0
            for medication in result:
                extra2 = {
                    "medication": medication,
                    "index": idx
                }
                extra2.update(extra)

                if not medication.get("name"):
                    LOGGER.debug("ExtractMedication: Medication does not have a name, skipping: %s", medication, extra=extra2)
                    continue

                extracted_medication_value = MedicationValue(
                                                                name=medication.get("name"),
                                                                strength=medication.get("strength"),
                                                                dosage=medication.get("dosage"),
                                                                route=medication.get("route"),
                                                                frequency=medication.get("frequency"),
                                                                instructions=medication.get("instructions") or medication.get("frequency"), # HHH maps frequency to instrutions
                                                                form = medication.get("form"),
                                                                start_date=medication.get("start_date"),
                                                                end_date=medication.get("end_date"),
                                                                discontinued_date=medication.get("discontinued_date"),
                                                            )


                medication_aggregate = ExtractedMedication.create(app_id=command.app_id, tenant_id=command.tenant_id,
                                                        patient_id=command.patient_id,
                                                        document_id=command.document_id,
                                                        page_id=command.page_id,
                                                        extracted_medication_value=extracted_medication_value,
                                                        explaination=medication.get("explanation") or medication.get("explaination"),
                                                        document_reference=command.document_id,
                                                        page_number=command.page_number,
                                                        medispan_medication=None,
                                                        medispan_id=None,
                                                        medispan_status=MedispanStatus.NONE,
                                                        score=None)

                medication_aggregate.execution_id = command.execution_id
                medication_aggregate.document_operation_instance_id = command.document_operation_instance_id
                #uow.register_new(medication_aggregate)
                medications.append(medication_aggregate)

                idx += 1

            operation_context['medications'] = [x.dict() for x in medications]
            operation_context["medication_count"] = len(medications) if medications else 0
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra.update({
                "branch": "medications_extracted",
                "medication_count": len(medications) if medications else 0,
                "elapsed_time": doc_operation_instance_log.elapsed_time
            })
            LOGGER.info("Step::%s completed", command.step_id, extra=extra)

            return medications
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            try:
                LOGGER.error('ExtractMedication: Error in extracting medications from documentId %s: %s', command.document_id, str(e), extra=extra)
                operation_context['error'] = extra["error"]
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                document_id=command.document_id,
                                                                                step_id= command.step_id,
                                                                                start_datetime=start_datetime,
                                                                                context = operation_context,
                                                                                page_number=command.page_number,
                                                                                status = DocumentOperationStatus.FAILED,
                                                                                document_operation_definition_id=command.document_operation_definition_id,
                                                                                document_operation_instance_id=command.document_operation_instance_id)

                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)
            except Exception as e1:
                extra["error_in_exception"] = exceptionToMap(e1)
                LOGGER.error('Exception in extract medication error block', extra=extra)
            raise OrchestrationExceptionWithContext(f"ExtractMedication: Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e


@dispatcher.register(ExtractConditions)
@inject()
async def extract_conditions(command: ExtractConditions, uow: IUnitOfWork,prompt_adapter:IPromptAdapter):
    thisSpanName = "extract_conditions"
    start_datetime = now_utc()

    extra = command.toExtra()

    operation_context = {}
    operation_context.update(extra)
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_id", command.page_id)
        span.set_attribute("page_number", command.page_number)
        try:
            LOGGER.info('ExtractCondition: Extracting condition for documentId %s from %s', command.document_id, command.labelled_content, extra=extra)
            if not command.labelled_content:
                operation_context['error'] = {"message": 'No labelled content found'}
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
                doc_logger = DocumentOperationInstanceLogService()
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)
                return []

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = command.step_id,
                document_id = command.document_id,
                page_number = command.page_number,
                document_operation_def_id = command.document_operation_definition_id,
                document_operation_instance_id = command.document_operation_instance_id,
            )

            all_contents = ""
            for content in command.labelled_content:
                all_contents += f'# Document: {command.document_id}, page: {command.page_number}\n'
                all_contents += content + '\n\n'
            LOGGER.debug("ExtractConditions: Calling multi modal predict to extract conditions for documentId %s", command.document_id, extra=extra)
            llm_prompt = command.prompt.replace('<content></content>',all_contents)
            operation_context['llm_prompt'] = [llm_prompt]
            result = await prompt_adapter.multi_modal_predict([llm_prompt],model=command.model, metadata=opMeta.dict())
            operation_context['model_response'] = result

            LOGGER.debug("ExtractCondtions: Cleaning model response for extract conditions for documentId %s", command.document_id, extra=extra)

            result = result.replace('**', '').replace('##', '').replace('```', '').replace('json', '').replace('\n\'', '')
            LOGGER.info("ExtractConditions: Prompt result: %s", result, extra=extra)
            extracted_json = json.loads(result)
            conditions = []
            for condition in extracted_json:
                extracted_condition_value = ConditionValue(
                                                                condition=condition["Condition"],
                                                                diagnosis_date=condition["Diagnosis Date"],
                                                                specific_details=condition["Specific Details"]
                                                            )


                condition_aggregate = ExtractedConditions.create(app_id=command.app_id, tenant_id=command.tenant_id,
                                                        patient_id=command.patient_id,
                                                        document_id=command.document_id,
                                                        page_id=command.page_id,
                                                        page_number=command.page_number,
                                                        extracted_condition_value=extracted_condition_value)

                condition_aggregate.execution_id = command.execution_id
                condition_aggregate.document_operation_instance_id = command.document_operation_instance_id
                uow.register_new(condition_aggregate)
                conditions.append(condition_aggregate)
            operation_context['conditions'] = conditions
            operation_context["conditions_count"] = len(conditions) if conditions else 0
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            start_datetime=now_utc(),
                                                                            status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra.update({

                "branch": "medications_extracted",
                "conditions_count": len(conditions) if conditions else 0,
                "elapsed_time": doc_operation_instance_log.elapsed_time
            })
            LOGGER.info("Step::%s completed", command.step_id, extra=extra)

            return conditions
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error('ExtractCondition: Error in extracting Conditions from documentId %s: %s', command.document_id, str(e), extra=extra)
            operation_context['error'] = exceptionToMap(e)
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            context = operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.FAILED,
                                                                            start_datetime=now_utc(),
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id)

            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)
            raise OrchestrationExceptionWithContext(f"ExtractCondition: Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=operation_context) from e

@dispatcher.register(MedispanMatching)
@change_tracker_updates(name="MedispanMatching")
@inject()
async def medispan_matching(command: MedispanMatching, uow: IUnitOfWork,
                             prompt_adapter:IPromptAdapter,
                             medispan_port:IMedispanPort,
                             relevancy_filter_adapter:IRelevancyFilterPort,
                             query:IQueryPort
                             ) -> List[ExtractedMedication]:
    extra = command.toExtra()

    operation_context = {
        "settings": {
            "MEDISPAN_LLM_SCORING_ENABLED": MEDISPAN_LLM_SCORING_ENABLED
        }
    }
    operation_context.update(extra)

    try:
        config:Configuration = await get_config(command.app_id,command.tenant_id,query)
        resolver = StepMedispanMatchingResolver()
        output_medications = await resolver.run(command, uow, config)

        return output_medications

    except Exception as e:
        operation_context['error'] = exceptionToMap(e)
        extra2 = {}
        extra2.update(operation_context)

        if isinstance(e, OrchestrationExceptionWithContext):
            operation_context.update(e.context)
            LOGGER2.error('MedispanMatching: OrchestrationExceptionError in extracting medications from documentId %s: %s', command.document_id, str(e), extra=extra2)
        else:
            LOGGER2.error('MedispanMatching: Error in extracting medications from documentId %s: %s', command.document_id, str(e), extra=extra2)

        doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                        tenant_id=command.tenant_id,
                                                                        patient_id=command.patient_id,
                                                                        document_id=command.document_id,
                                                                        step_id= command.step_id,
                                                                        context = operation_context,
                                                                        page_number=command.page_number,
                                                                        status = DocumentOperationStatus.FAILED,
                                                                        start_datetime=now_utc(),
                                                                        document_operation_definition_id=command.document_operation_definition_id,
                                                                        document_operation_instance_id=command.document_operation_instance_id)

        doc_logger = DocumentOperationInstanceLogService()
        await doc_logger.save(doc_operation_instance_log, uow)

        extra.update(operation_context)
        raise OrchestrationExceptionWithContext(f"MedispanMatching: Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",context=extra) from e

@dispatcher.register(NormalizeMedications)
@change_tracker_updates(name="NormalizeMedications")
@inject()
async def normalize_medications(command:NormalizeMedications, uow:IUnitOfWork, query:IQueryPort, prompt: IPromptAdapter) -> List[ExtractedMedication]:

        LOGGER.debug("Normalizing medication")

        start_datetime = now_utc()

        extra = command.toExtra()

        opMeta: OperationMeta = OperationMeta(
            type = DocumentOperationType.MEDICATION_EXTRACTION.value,
            step = command.step_id,
            document_id = command.document_id,
            page_number=command.page_number,
            document_operation_def_id=command.document_operation_definition_id,
            document_operation_instance_id=command.document_operation_instance_id,
        )

        with await opentelemetry.getSpan(command.step_id) as span:
            span.set_attribute("document_id", command.document_id)

            try:
                operation_context = {
                    "inputs": [],
                    "prompts": [],
                    "raw_results": [],
                    "model": {
                        "name": command.model,
                    },
                }

                doc_logger = DocumentOperationInstanceLogService()

                success_log_exists, log =  await does_success_operation_instance_exist(command.document_id, command.document_operation_instance_id,command.page_number,command.step_id)
                if success_log_exists:
                    return query.get_extracted_medications_by_operation_instance_id(command.document_id, command.document_operation_instance_id)

                prompt_text = command.prompt
                LOGGER.debug("Normalizing medication prompt for model %s: %s", command.model, prompt_text, extra=extra)

                operation_context["llm_prompt"] = prompt_text
                operation_context["model"] = command.model
                operation_context["page_number"] = command.page_number

                output: List[ExtractedMedication] = []

                search_fqns = []
                search_prompt_text = []
                search_raw_results = []

                idx = 0
                for extracted_medication in command.extracted_medications:

                    opMeta.iteration = idx

                    if extracted_medication.medispan_status == MedispanStatus.ERRORED:
                        LOGGER.debug("Medication errored to medispan.  Not performing Normalization.  Continuing. %s", extracted_medication.id, extra=extra)
                        output.append(extracted_medication)
                        continue

                    medication: MedicationValue = extracted_medication.medication

                    LOGGER.debug("Normalizing medication: %s", medication.to_string_with_instructions, extra=extra)
                    this_prompt_text = [prompt_text.replace("{search_term}", medication.to_string_with_instructions)]

                    search_prompt_text.append(this_prompt_text)
                    search_fqns.append(medication.to_string_with_instructions)

                    LOGGER.debug("Normalizing medication prompt: %s", this_prompt_text, extra=extra)

                    raw_results = await prompt.multi_modal_predict_2(
                        this_prompt_text,
                        response_mime_type = "application/json",
                        model=command.model,
                        metadata = opMeta.dict()
                    )
                    LOGGER.debug("Normalized medication '%s' raw response from LLM: %s", medication.to_string_with_instructions, raw_results, extra=extra)
                    search_raw_results.append(raw_results)

                    if raw_results:
                        try:
                            LOGGER.debug("Normalized medication raw response from LLM: %s", raw_results, extra=extra)
                            results = convertToJson(raw_results)
                            normalized_medication = MedicationValue(**results)
                            extracted_medication.medication = normalized_medication

                            if normalized_medication.dosage:
                                extracted_medication.set_dosage(normalized_medication.dosage)

                            if normalized_medication.instructions:
                                extracted_medication.set_instructions(normalized_medication.instructions)

                            output.append(extracted_medication)

                            operation_context["llm_raw_response"] = raw_results
                        except:
                            LOGGER.warning("Unable to parse normalized medication for medication %s with response from llm: %s", medication.to_string_with_instructions, raw_results, extra=extra)
                            output.append(extracted_medication)
                    else:
                        LOGGER.warning("No normalized medication found for medication %s", medication.to_string_with_instructions, extra=extra)
                        output.append(extracted_medication)

                    operation_context["inputs"].append(json.dumps(search_fqns))
                    operation_context["prompts"].append(json.dumps(search_prompt_text))
                    operation_context["raw_results"].append(json.dumps(search_raw_results))

                    idx += 1

                operation_context["iteration_count"] = idx

                for normalized_medication in output:
                    normalized_medication.modified_at = now_utc()
                    uow.register_dirty(normalized_medication)

                LOGGER.debug("NormalizeMedications: Writing document operation instance log for documentId %s", command.document_id, extra=extra)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                    tenant_id=command.tenant_id,
                                                                                    patient_id=command.patient_id,
                                                                                    document_operation_instance_id=command.document_operation_instance_id,
                                                                                    document_operation_definition_id=command.document_operation_definition_id,
                                                                                    document_id=command.document_id,
                                                                                    step_id= command.step_id,
                                                                                    start_datetime=start_datetime,
                                                                                    context=operation_context,
                                                                                    page_number=command.page_number,
                                                                                    status = DocumentOperationStatus.COMPLETED)
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

                extra.update({
                    "normalized_medication_count": len(output) if output else 0,
                    "elapsed_time": doc_operation_instance_log.elapsed_time
                })
                LOGGER.info("Step::%s completed", command.step_id, extra=extra)

            except Exception as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.warning("Unexpected exception occurred with performing normalization of medications: %s", command.extracted_medications, extra=extra)
                output = command.extracted_medications

            return output

@dispatcher.register(QueueCommand)
@inject
async def queue_command(command: QueueCommand, uow:IUnitOfWork, cloud_task: ICloudTaskPort):
    with await opentelemetry.getSpan("queue_orchestration") as span:

        extra = command.toExtra()
        cmd = command.command

        await create_command(cmd, uow)


# Sends request to Cloud Task to schedule the orchestration run  The Cloud Task url will call /api/orchestrate/{document_operation_type} with the document_id
@dispatcher.register(QueueOrchestration)
@inject()
async def queue_orchestration(command: QueueOrchestration, uow:IUnitOfWork, cloud_task: ICloudTaskPort):
    with await opentelemetry.getSpan("queue_orchestration") as span:

        extra = command.toExtra()

        LOGGER.debug("QueueOrchestration: Scheduling orchestration for document operation type %s and documentId %s", command.document_operation_type, command.document_id, extra=extra)

        # Construct URL to start orchestration on the document
        url = f"{SELF_API}/orchestrate/{command.document_operation_type}"
        body = {
            "document_id": command.document_id
        }
        location = GCP_LOCATION_2
        queue = CLOUD_TASK_COMMAND_SCHEDULE_QUEUE_NAME
        service_account_email = SERVICE_ACCOUNT_EMAIL
        payload = body

        schedule_datetime = defer_until_after_time(ORCHESTRATION_GRADER_SCHEDULE_WINDOW_START)

        extra.update({
            "cloudtask": {
                "url": url,
                "queue": queue,
                "service_account_email": service_account_email,
                "payload": payload,
            }
        })

        LOGGER.debug("QueueOrchestration: Scheduling orchestration for documentId %s for deferred execution at %s", command.document_id, schedule_datetime, extra=extra)

        try:
            LOGGER.debug("Starting a cloud run task (v2), location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)
            response = await cloud_task.create_task_v2(location=location,
                                                            service_account_email=service_account_email,
                                                            queue=queue,
                                                            url=url,
                                                            payload=payload,
                                                            schedule_time=schedule_datetime)
            LOGGER.debug("Successfully started a cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s, response: %s", location, service_account_email, queue, url, payload, response, extra=extra)

            return response
        except ValidationError as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("ValidationException when starting a cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)
            raise e
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Exception when starting a cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)
            raise e


@dispatcher.register(QueueDeferredOrchestration)
@inject()
async def queue_deferred_orchestration(command: QueueDeferredOrchestration, uow: IUnitOfWork, cloud_task: ICloudTaskPort):
    with await opentelemetry.getSpan("queue_deferred_orchestration") as span:
        
        extra = command.toExtra()

        LOGGER.debug("QueueDeferredOrchestration: Scheduling deferred orchestration for document operation type %s and documentId %s",
                    command.document_operation_type, command.document_id, extra=extra)

        # Construct URL to start orchestration on the document
        url = f"{SELF_API}/orchestrate/{command.document_operation_type}"
        body = {
            "document_id": command.document_id
        }
        location = GCP_LOCATION_2
        queue = CLOUD_TASK_COMMAND_SCHEDULE_QUEUE_NAME
        service_account_email = SERVICE_ACCOUNT_EMAIL
        payload = body

        # Get schedule time based on CT timezone rules
        schedule_datetime = get_ct_schedule_datetime(START_TIME, END_TIME)

        extra.update({
            "cloudtask": {
                "url": url,
                "queue": queue,
                "service_account_email": service_account_email,
                "payload": payload,
                "schedule_time": schedule_datetime,
            }
        })

        LOGGER.debug("QueueDeferredOrchestration: Scheduling orchestration for documentId %s for deferred execution at %s",
                    command.document_id, schedule_datetime, extra=extra)

        try:
            LOGGER.debug("Starting a cloud run task (v2), location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)
            response = await cloud_task.create_task_v2(location=location,
                                                            service_account_email=service_account_email,
                                                            queue=queue,
                                                            url=url,
                                                            payload=payload,
                                                            schedule_time=schedule_datetime)
            LOGGER.debug("Successfully started a cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s, response: %s", location, service_account_email, queue, url, payload, response, extra=extra)

            Metric.send("EXTRACTION:RETRY:SCHEDULED", tags=extra)
            return response
        except ValidationError as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("ValidationException when starting a cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)            
            raise e
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Exception when starting a cloud run task: location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", location, service_account_email, queue, url, payload, extra=extra)            
            raise e


@dispatcher.register(StartOrchestration)
@inject()
async def start_orchestration(command: StartOrchestration, uow: IUnitOfWork, query: IQueryPort):
    extra = command.toExtra()

    #agent = ORCHESTRATION_RESOLVER.resolve(command.document_operation_type)
    LOGGER.debug("StartOrchestration: Starting orchestration for document operation type %s and documentId %s with priority %s", command.document_operation_type, command.document_id, command.priority, extra=extra)
    launcher = OrchestrationLauncher(document_id=command.document_id, priority=command.priority)

    await launcher.launch()

    # if agent:
    #     LOGGER.debug("Starting orchestration for document operation type %s and documentId %s with priority %s", command.document_operation_type, command.document_id, command.priority, extra=extra)
    #     await agent.orchestrate(command.document_id, priority=command.priority)
    #     LOGGER.debug("Initialization orchestration thread complete for document operation type %s", command.document_operation_type, extra=extra)
    # else:
    #     LOGGER.error("Could not find orchestration agent for document operation type %s", command.document_operation_type, extra=extra)
    #     raise Exception(f"Could not find orchestration agent for document operation type {command.document_operation_type}")

    return True


@dispatcher.register(PerformGrading)
@inject()
async def perform_grading(command: PerformGrading, uow: IUnitOfWork,
                             query: IQueryPort,
                             prompt: IPromptAdapter,
                             ) -> List[ExtractedMedication]:

    doc_op_defs = await query.get_document_operation_definition_by_op_type(DocumentOperationType.MEDICATION_GRADER)
    if not doc_op_defs:
        doc_op_defs = [await autocreate_document_operation_definition(DocumentOperationType.MEDICATION_GRADER, uow, query)]
    doc_op_def = doc_op_defs[0]

    agent = None
    if  ORCHESTRATION_GRADER_STRATEGY == "llm":
        agent = MedicationGraderLLM(doc_op_def=doc_op_def, uow=uow, query=query, prompt=prompt)
    else:
        agent = MedicationGraderProcedural(doc_op_def=doc_op_def, uow=uow, query=query, prompt=prompt)

    results = await agent.process(command=command)
    return results


"""
Usecases:
1. extracted medication will result in create/update medication profile
2. medication imported from other Apps or add/edit will result in create/update medication profile
depending upon the source, we need to take different actions
"""
@dispatcher.register(CreateorUpdateMedicationProfile)
@change_tracker_updates(name="CreateorUpdateMedicationProfile")
@inject()
async def create_or_update_medication_profile(command:CreateorUpdateMedicationProfile,uow:IUnitOfWork,query:IQueryPort):
    start_datetime = now_utc()
    with await opentelemetry.getSpan(command.step_id) as span:
        span.set_attribute("document_id", command.document_id)
        doc_logger = DocumentOperationInstanceLogService()

        extra = command.toExtra()

        try:
            operation_context = {}

            LOGGER.debug("UpsertMedProfile: Creating or updating medication profile for patient %s from documentId %s", command.patient_id, command.document_id, extra=extra)

            medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
            config:Configuration = await get_config(command.app_id,command.tenant_id,query)
            is_existing_medication_profile = False

            if not medication_profile:
                LOGGER.debug("Creating new medication profile for patient %s from documentId %s", command.patient_id, command.document_id, extra=extra)
                medication_profile:MedicationProfile = MedicationProfile.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id)
            else:
                LOGGER.debug("UpsertMedProfile: Medication profile exists", extra=extra)
                is_existing_medication_profile = True

            # legacy code: where we written medications to medication profile
            # if command.extracted_medications:
            #     LOGGER.debug("UpsertMedProfile: Reconciling extracted medications for patient %s from documentId %s", command.patient_id, command.document_id)
            #     medication_profile.reconcile_extracted_medications(command.extracted_medications, config)

            if is_existing_medication_profile:
                #uow.register_dirty(medication_profile)
                # we dont have to update if there are no changes
                pass
            else:
                uow.register_new(medication_profile)

                LOGGER.debug("UpsertMedProfile: Writing document operation instance log for documentId %s", command.document_id, extra=extra)
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                                    tenant_id=command.tenant_id,
                                                                                    patient_id=command.patient_id,
                                                                                    document_operation_instance_id=command.document_operation_instance_id,
                                                                                    document_operation_definition_id=command.document_operation_definition_id,
                                                                                    document_id=command.document_id,
                                                                                    step_id= command.step_id,
                                                                                    start_datetime=start_datetime,
                                                                                    context=operation_context,
                                                                                    page_number=-1,
                                                                                    status = DocumentOperationStatus.COMPLETED)
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)

            return medication_profile
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error('Error in creating or updating medication profile: %s', str(e), extra=extra)
            operation_context['error'] = exceptionToMap(e)
            raise OrchestrationExceptionWithContext(f"UpsertMedProfile: Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}",operation_context) from e

@dispatcher.register(CreateEvidence)
@inject
async def create_evidence(command: CreateEvidence, uow: IUnitOfWork, query_adapter: IQueryPort,
                          storage: IStoragePort, prompt_adapter: IPromptAdapter,
                          settings_adapter: ISettingsPort):
    start_datetime = now_utc()
    extra = command.toExtra()
    try:
        operation_context = {}
        LOGGER.debug("CreateEvidence: Retrieving page %s for document %s", command.page_id, command.document_id, extra=extra)
        page = await uow.get(Page, command.page_id)

        LOGGER.debug("CreateEvidence: Retrieving page OCR for document %s and page %s", command.document_id, command.page_id, extra=extra)
        raw_ocr = await storage.get_page_ocr(command.app_id,command.tenant_id,command.patient_id,command.document_id,command.page_id,OCRType.raw)

        line_annotation = page.get_ocr_page_line_annotations(json.loads(raw_ocr))
        doc_page_annotation_tokens = [x.token() for x in line_annotation]
        # for token in doc_page_annotations_list:
        table = ""
        for token in doc_page_annotation_tokens:
            token: AnnotationToken = token
            table = (
                table
                + "|".join(
                    [
                        token.text.strip().replace("\n", ""),
                        str(round(token.x1, 3)),
                        str(round(token.y1, 3)),
                        str(round(token.x2, 3)),
                        str(round(token.y2, 3))
                    ]
                )
                + "\n"
            )

        opMeta:OperationMeta = OperationMeta(
            type = DocumentOperationType.MEDICATION_EXTRACTION.value,
            step = command.step_id,
            document_id = command.document_id,
            page_number = command.page_number,
            document_operation_def_id = command.document_operation_definition_id,
            document_operation_instance_id = command.document_operation_instance_id,
        )

        LOGGER.debug("CreateEvidence: Calling multi modal predict to extract evidence for documentId %s", command.document_id, extra=extra)
        llm_prompt = command.prompt.replace('<table></table>',table).replace('<medications></medications>','\n'.join([f'- `{input}`' for input in command.medications]))
        operation_context["llm_prompt"] = [llm_prompt]
        response = await prompt_adapter.multi_modal_predict(llm_prompt, model=command.model, metadata=opMeta.dict())
        operation_context["model_response"] = response

        table_texts = response.split('---')
        index = 0
        evidences = []

        operation_context['evidence_parsing_result'] = {}
        idx = 0
        for table_text in table_texts:
            extra2 = {
                "index": idx,
            }
            table_text = table_text.strip()
            lines = [[part.strip() for part in line.split('|')] for line in table_text.split("\n")]
            lines = [x for x in lines if len(x) > 2]
            LOGGER.info('CreateEvidence: Parsing for evidneces: %s', str(lines), extra=extra2)
            operation_context['evidence_parsing_result'][index] = table_text
            try:
                text = ' '.join([part[1] for part in lines])
                x1 = min([float(part[2]) for part in lines if part[2] and part[2] != '' and part[2] != 'None'])
                y1 = min([float(part[3]) for part in lines if part[3] and part[3] != '' and part[3] != 'None'])
                x2 = max([float(part[4]) for part in lines if part[4] and part[4] != '' and part[4] != 'None'])
                y2 = max([float(part[5]) for part in lines if part[5] and part[5] != '' and part[5] != 'None'])

                    # command.evidence_requested_for,
                evidences.append(AnnotationToken(text=text, x1=x1, y1=y1, x2=x2, y2=y2, index=index))

                index = index + 1
            except Exception as e:
                extra2["error"] = exceptionToMap(e)
                LOGGER.error('Error in parsing table text in document %s page %s: %s', command.document_id, command.page_number, str(e), extra=extra2)

            idx += 1

        LOGGER.debug("CreateEvidence: Create Evidence: Creating evidence for documentId %s", command.document_id, extra=extra)
        evidences_model:Evidences = Evidences.create(app_id=command.app_id,tenant_id=command.tenant_id,patient_id=command.patient_id,
                                                     document_id=command.document_id,page_id=command.page_id,
                                                     page_number=command.page_number,evidences=evidences)
        evidences_model.execution_id = command.execution_id
        evidences_model.document_operation_instance_id = command.document_operation_instance_id
        uow.register_new(evidences_model)

        LOGGER.debug("CreateEvidence: Create Evidence: Writing document operation instance log for documentId %s", command.document_id, extra=extra)
        doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                        tenant_id=command.tenant_id,
                                                                        patient_id=command.patient_id,
                                                                        document_operation_instance_id=command.document_operation_instance_id,
                                                                        document_operation_definition_id=command.document_operation_definition_id,
                                                                        document_id=command.document_id,
                                                                        step_id= command.step_id,
                                                                        start_datetime=start_datetime,
                                                                        context=operation_context,
                                                                        page_number=command.page_number,
                                                                        status = DocumentOperationStatus.COMPLETED)
        doc_logger = DocumentOperationInstanceLogService()
        #uow.register_new(doc_operation_instance_log)
        await doc_logger.save(doc_operation_instance_log, uow)
        return Result(success=True,return_data=evidences_model)

    except Exception as e:
        extra["error"] = exceptionToMap(e)
        LOGGER.error('CreateEvidence: Error in evidence extraction of document %s page %s: %s', command.document_id, command.page_number, str(e), extra=extra)
        operation_context["page_number"] = str(command.page_id)
        operation_context['error'] = exceptionToMap(e)
        doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                        tenant_id=command.tenant_id,
                                                                        patient_id=command.patient_id,
                                                                        document_id=command.document_id,
                                                                        step_id= command.step_id,
                                                                        start_datetime=start_datetime,
                                                                        context = operation_context,
                                                                        page_number=command.page_number,
                                                                        status = DocumentOperationStatus.FAILED,
                                                                        document_operation_instance_id=command.document_operation_instance_id,
                                                                        document_operation_definition_id=command.document_operation_definition_id)

        doc_logger = DocumentOperationInstanceLogService()
        #uow.register_new(doc_operation_instance_log)
        await doc_logger.save(doc_operation_instance_log, uow)
        return Result(success=False,error_message=traceback.format_exc())

@dispatcher.register(ExecuteGenericPromptStep)
@inject
async def execute_generic_prompt_step(command: ExecuteGenericPromptStep, uow: IUnitOfWork, query_adapter: IQueryPort, prompt_adapter: IPromptAdapter, storage_adapter:IStoragePort):

    extra = command.toExtra()
    LOGGER.info("Executing Generic Prompt Step for operation %s and step %s for document %s", command.operation_type, command.operation_step, command.doc_storage_uri, extra=extra)

    thisSpanName = "execute_generic_prompt_step"
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("wsky-doc_uri", command.doc_storage_uri)
        span.set_attribute("wsky-op-type", command.operation_type)
        span.set_attribute("wsky-op-step", command.operation_step)

        start_time = time.time()
        start_date = now_utc()

        opMeta: OperationMeta = OperationMeta(
            type=command.operation_type,
            step = command.operation_step,
        )

        opLog: GenericPromptStep = GenericPromptStep(
            app_id=command.app_id,
            tenant_id=command.tenant_id,
            patient_id=command.patient_id,
            status = "SUCCESS",
            operation = opMeta,
            parameters = {
                "document_uri": command.doc_storage_uri,
                "prompt_document_execution_strategy": command.prompt_document_execution_strategy
            }
        )

        span.set_attribute("wsky-log-id", opLog.id)

        try:

            # Get the document operation definition
            LOGGER.debug("Getting OperationDefintion", extra=extra)
            with await opentelemetry.getSpan(thisSpanName + ":Getting Operation Definition by op_type") as span:
                operation_definition = await query_adapter.get_document_operation_definition_by_op_type(command.operation_type)
                op_def: DocumentOperationDefinition = operation_definition[0]
                opMeta.document_operation_def_id = op_def.id

            step_config = op_def.step_config[command.operation_step]
            model = step_config["model"]
            prompt = step_config["prompt"]

            if command.prompt_document_execution_strategy=="reference":
                with await opentelemetry.getSpan(thisSpanName + ":Processing through multi_modal_predict_2") as span:
                    LOGGER.debug("Processing through multi_modal_predict_2", extra=extra)
                    prompts = [prompt, (command.doc_storage_uri, "application/pdf")]
                    results = await prompt_adapter.multi_modal_predict_2(prompts, model, metadata=opMeta.dict())
            else:
                with await opentelemetry.getSpan(thisSpanName + ":Processing through multi_modal_predict") as span:
                    LOGGER.debug("Processing through multi_modal_predict", extra=extra)
                    prompts = [prompt]
                    file_bytes = await storage_adapter.get_document_raw(command.doc_storage_uri)
                    prompts.append((file_bytes, "application/pdf"))
                    results = await prompt_adapter.multi_modal_predict(prompts, model, metadata=opMeta.dict())

            end_time = time.time()
            end_date = now_utc()
            elapsed_time = end_time - start_time

            LOGGER.debug("elapsed time is: %s", str(elapsed_time), extra=extra)

            opMetrics: OperationMetrics = OperationMetrics(
                start_time = start_date,
                end_time = end_date,
                elapsed_time = elapsed_time
            )

            opLog.metrics = opMetrics

            uow.register_new(opLog)

            ret = convertToJson(results)
            opLog.response = ret

            return ret

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("An exception occurred during generic prompt step: %s", str(e), extra=extra)

            span.set_attribute("wsky-error-msg", str(e))

            end_time = time.time()
            end_date = now_utc()
            elapsed_time = end_time - start_time

            opMetrics: OperationMetrics = OperationMetrics(
                start_time = start_date,
                end_time = end_date,
                elapsed_time = elapsed_time
            )

            opLog.status = "FAILED"
            #opLog.metrics = opMetrics

            tb = traceback.extract_tb(e.__traceback__)
            stack = traceback.format_list(tb)

            error = {
                "type": type(e).__name__,
                "msg": str(e),
                "stack_trace": stack
            }
            opLog.errors = error

            LOGGER.info("Writing to operation log for step: %s", opLog, extra=extra)
            uow.register_new(opLog)

            return error



@dispatcher.register(ExecuteCustomPrompt)
@inject
async def execute_prompt(command: ExecuteCustomPrompt, uow: IUnitOfWork, prompt_adapter: IPromptAdapter, storage_adapter:IStoragePort):

    thisSpanName = "execute_prompt"
    start_datetime = now_utc()

    extra = command.toExtra()

    opMeta:OperationMeta = OperationMeta(
        type = DocumentOperationType.MEDICATION_EXTRACTION.value,
        step = command.step_id,
        document_id = command.document_id,
        page_number = command.page_number,
        document_operation_def_id=command.document_operation_definition_id,
        document_operation_instance_id=command.document_operation_instance_id
    )

    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        try:
            operation_context = deepcopy(command.context)
            operation_context["page_number"] = command.page_number

            uri = command.doc_storage_uri

            LOGGER.debug("CustomPrompt: Executing custom prompt for document %s page %s", uri, command.page_number, extra=extra)
            operation_context["llm_prompt"] = [command.prompt, {"uri": uri, "type": "application/pdf"}]
            response = await prompt_adapter.multi_modal_predict_2([command.prompt, (uri, 'application/pdf')], model=command.model, metadata=opMeta.dict())
            operation_context["model_response"] = response
            LOGGER.debug("CustomPrompt: Prompt response: %s", response, extra=extra)

            response_output = response
            response_parsed = None
            try:
                response_parsed = convertToJson(response)
                response_output = ""
                LOGGER.debug("CustomPrompt: Response parsed successfully for documentId %s and page %s", command.document_id, command.page_number, extra=extra)
            except Exception as e:
                LOGGER.error('CustomPrompt: Error in parsing prompt response into json for documentId %s and page %s.  Ignoring and saving raw response as prompt_output: %s', command.document_id, command.page_number, str(e), extra=extra)

            LOGGER.debug("CustomPrompt: Writing custom prompt result...", extra=extra)
            custom_prompt_result = CustomPromptResult.create(app_id=command.app_id,
                                    tenant_id=command.tenant_id,
                                    patient_id=command.patient_id,
                                    document_id=command.document_id,
                                    page_number = command.page_number,
                                    context=operation_context,
                                    prompt_input=command.prompt,
                                    prompt_output=response_output,
                                    prompt_output_data=response_parsed,
                                    document_operation_instance_id=command.document_operation_instance_id
                                    )
            uow.register_new(custom_prompt_result)

            LOGGER.debug("CustomPrompt: Writing to operation instance log...", extra=extra)
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context = operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            return custom_prompt_result

        except AttributeError as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error('CustomPrompt: AttributeError in executing prompt: %s, for uri %s Type: %s', str(e), uri, type(e).__name__, extra=extra)
            operation_context['error'] = extra["error"]
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context = operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.FAILED,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id)
            # Ignore AttributeError and continue.  This seems to be due to oddly formatted PDF
            o = {
                "doc": {
                    "name": "unknown",
                    "documentType": "unknown",
                    "internalPageNumber": "1",
                    "internalPageCount": "1",
                    "sections": []
                }
            }
            custom_prompt_result = CustomPromptResult.create(app_id=command.app_id,
                                    tenant_id=command.tenant_id,
                                    patient_id=command.patient_id,
                                    document_id=command.document_id,
                                    page_number = command.page_number,
                                    context=operation_context,
                                    prompt_input=command.prompt,
                                    prompt_output=json.dumps(o, indent=2),
                                    prompt_output_data=o,
                                    document_operation_instance_id=command.document_operation_instance_id
                                    )
            uow.register_new(custom_prompt_result)
            return custom_prompt_result

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error('CustomPrompt: Error in executing prompt: %s, Type: %s', str(e), type(e).__name__, extra=extra)
            operation_context['error'] = extra["error"]
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context = operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.FAILED,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id)
            raise OrchestrationException(f"Error in {str(command.step_id)} for documentId {command.document_id} on page {command.page_number} : {str(e)}") from e


@dispatcher.register(AssembleTOC)
@inject
async def assemble_toc(command: AssembleTOC, uow: IUnitOfWork, prompt_adapter: IPromptAdapter, storage_adapter:IStoragePort):
    thisSpanName = "assemble_toc"
    start_datetime = now_utc()

    extra = command.toExtra()

    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        try:
            LOGGER.info("AssembleTOC: Assembling TOC for document %s with operationInstanceId %s...", command.document_id, command.document_operation_instance_id, extra=extra)

            operation_context = {}
            operation_context = deepcopy(command.context)

            tocResults:DocumentTOC = await assemble(command.app_id, command.tenant_id, command.patient_id, command.document_id, command.pageTOCs)

            LOGGER.debug("AssembleTOC: Indexing page profiles for instanceid %s...", command.document_operation_instance_id, extra=extra)
            pageProfiles = await indexPageProfiles(tocResults)
            tocResults.pageProfiles = pageProfiles

            LOGGER.debug("AssembleTOC: UOW Registering TOC", extra=extra)
            tocResults.document_operation_instance_id = command.document_operation_instance_id
            uow.register_new(tocResults)

            LOGGER.debug("AssembleTOC: Preparing to write instance log", extra=extra)
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context = operation_context,
                                                                            page_number=-1,
                                                                            status = DocumentOperationStatus.COMPLETED,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)
            LOGGER.debug("AssembleTOC: Instance log written for completed", extra=extra)

            return tocResults

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error('AssembleTOC: Error in assembling toc for document %s: %s', command.document_id, str(e), extra=extra)
            operation_context['error'] = exceptionToMap(e)
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context = operation_context,
                                                                            page_number=-1,
                                                                            status = DocumentOperationStatus.FAILED,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            raise OrchestrationException(f"Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}") from e

@dispatcher.register(LogPageProfileFilterState)
@inject()
async def log_page_profile_filter_state(command: LogPageProfileFilterState, uow: IUnitOfWork, query: IQueryPort):

    filterState: DocumentFilterState = DocumentFilterState.create(app_id=command.app_id,
                           tenant_id=command.tenant_id,
                           patient_id=command.patient_id,
                           state=command.state,
                           created_by=command.user_id)

    uow.register_new(filterState)

@dispatcher.register(UpdateHostMedications)
@inject()
async def update_host_medications(command: UpdateHostMedications, uow: IUnitOfWork, query: IQueryPort, external_medication_adapter:IHHHAdapter, messaging: IMessagingPort):
    return_status = {
        "status": "UNKNOWN",
        "description": ""
    }

    extra = command.toExtra()

    config:Configuration = await get_config(command.app_id, command.tenant_id, query)

    if command.app_id == "hhh":

        IS_READONLY_AFTER_HOST_SYNC = True  # If we ever make this writeable again, this function needs correction.  The default fallthrough action is to Create in HHH even if a non-imported medication is deleted

        thisSpanName = "update_medication"
        with await opentelemetry.getSpan(thisSpanName) as span:
            LOGGER.debug("update_host_medications: getMedicationProfile_by_patient_id", extra=extra)
            medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
            LOGGER.debug("Medication profile: %s", medication_profile, extra=extra)

            medication = command.medication_dict
            LOGGER.debug("update_host_medications: get_reconciled_medication: %s", medication.get("name"), extra=extra)
            reconcilled_medication:ReconcilledMedication = medication_profile.get_reconcilled_medication(medication.get("id"))
            if not reconcilled_medication:
                if not config.extraction_persisted_to_medication_profile:
                    # this is mostly because of the fact that we are not persisting the extracted medications to medication profile
                    # get the medication from extracted medications and create a reconcilled medication and move forward
                    LOGGER.debug("update_host_medications: Reconciled medication not found.  Creating new reconcilled medication", extra=extra)
                    if medication.get("extractedMedications") and len(medication.get("extractedMedications"))>0:
                        extracted_medication:ExtractedMedication = await query.get_extracted_medication(medication.get("extractedMedications",{})[0].get("extractedMedicationId"))
                        if not extracted_medication:
                            from paperglass.usecases.v4.medications import get_medication
                            medication_id = medication.get("extractedMedications",{})[0].get("extractedMedicationId")
                            document_id = medication.get("extractedMedications",{})[0].get("documentId")
                            extracted_medication:ExtractedMedication = await get_medication(document_id,medication_id)
                        if extracted_medication:
                            reconcilled_medication = medication_profile.reconcile_extracted_medications([extracted_medication], config)
                        else:
                            LOGGER.error("update_host_medications: Extracted medication not found.  Skipping", extra=extra)
                            return_status["status"] = "NOT_FOUND"
                            return_status["description"] = "Extracted medication not found.  Skipping"
                            return return_status
                    else:
                            LOGGER.debug("update_host_medications: Extracted medication not found.  Skipping", extra=extra)
                            return_status["status"] = "NOT_FOUND"
                            return_status["description"] = "Extracted medication not found.  Skipping"
                            return return_status
            LOGGER.info("Reconciled medication: %s", reconcilled_medication, extra=extra)

            if reconcilled_medication.deleted==True:
                LOGGER.debug("Medication is deleted.  Skipping", extra=extra)
                return_status["status"] = "DELETED"
                return_status["description"] = "Deleted medication cannot be updated.  Skipping"
                return return_status

            elif not reconcilled_medication.imported_medication or not reconcilled_medication.imported_medication.host_medication_id:
                # Only create if we don't have a host_medication_sync_status
                LOGGER.debug("update_host_medications: Create HHH medication %s", medication.get("name"), extra=extra)
                LOGGER.debug("medication: %s", medication, extra=extra)
                LOGGER.debug("reconciled_medication: %s", reconcilled_medication, extra=extra)
                result:Result = None
                if not reconcilled_medication.unlisted:

                    # get medication to export
                    medication_value_object:MedicationValue = reconcilled_medication.resolved_medication
                    medication_fqn = f'{medication_value_object.name} {medication_value_object.route or ""} {medication_value_object.form or ""} {medication_value_object.strength or ""}'
                    LOGGER.debug("Creating medispan linked medication for patientId %s medispan_id: %s medication: %s", command.patient_id, reconcilled_medication.medispan_id, medication_fqn, extra=extra)
                    response = await external_medication_adapter.create_medication(command.patient_id,command.ehr_token,command.modified_by,
                                                            HostMedicationAddModel(modified_by=command.modified_by,
                                                                medispan_id=medication_value_object.medispan_id,
                                                                medicationInstructions=medication_value_object.instructions,
                                                                medicationName=medication_fqn,
                                                                dose=medication_value_object.dosage,
                                                                startDate=medication_value_object.start_date,
                                                                discontinueDate=medication_value_object.discontinued_date,
                                                                is_long_standing=medication_value_object.is_long_standing,
                                                                is_nonstandard_dose=medication_value_object.is_nonstandard_dose,
                                                            ))
                    # update importedMedication object
                    if response and not response.get("error") and not response.get("errors"):
                        imported_medication_agg = ImportedMedicationAggregate.create(
                                            app_id=command.app_id,
                                            tenant_id=command.tenant_id,
                                            patient_id=command.patient_id,
                                            medication=medication_value_object,
                                            host_medication_id=response.get("patientMedispanRegistryKey"),
                                            medispan_id=medication_value_object.medispan_id,
                                            original_payload=medication_value_object.dict(),
                                            created_by=command.modified_by,
                                            modified_by=command.modified_by)
                        reconcilled_medication.host_medication_sync_status = HostMedicationSyncStatus(
                            last_synced_at = now_utc(),
                            host_medication_unique_identifier=response.get("patientMedispanRegistryKey")
                        )

                        reconcilled_medication.update_imported_medication(ImportedMedication(
                                imported_medication_id=imported_medication_agg.id,
                                host_medication_id=response.get("patientMedispanRegistryKey"),
                                medispan_id=medication_value_object.medispan_id,
                                medication=medication_value_object,
                                modified_by=command.modified_by
                            ))
                elif reconcilled_medication.unlisted:
                    # freeform
                    medication_value_object:MedicationValue = reconcilled_medication.resolved_medication

                    medication_fqn = f'{medication_value_object.name} {medication_value_object.route or ""} {medication_value_object.strength or ""} {medication_value_object.dosage or ""} {medication_value_object.form or ""} {medication_value_object.frequency or medication_value_object.instructions or ""}'
                    LOGGER.debug("Creating unlisted medication for patientId %s medication: %s with classification %s", command.patient_id, medication_fqn, medication_value_object.classification, extra=extra)
                    model = HostFreeformMedicationAddModel(
                                                                modified_by=command.modified_by,
                                                                medispan_id=reconcilled_medication.medispan_id,
                                                                medicationInstructions=medication_value_object.instructions,
                                                                medicationName=medication_fqn,
                                                                dose=medication_value_object.dosage,
                                                                startDate=medication_value_object.start_date,
                                                                discontinueDate=medication_value_object.discontinued_date,
                                                                classification_id=medication_value_object.classification,
                                                                is_long_standing=medication_value_object.is_long_standing
                                                            )
                    LOGGER.debug("HostFreeformMedicationAddModel: %s", model, extra=extra)
                    response = await external_medication_adapter.create_freeform_medication(command.patient_id,command.ehr_token,command.modified_by,
                                                            model)
                    # update importMedication object
                    if response and not response.get("error") and not response.get("errors"):
                        imported_medication_agg = ImportedMedicationAggregate.create(
                                            app_id=command.app_id,
                                            tenant_id=command.tenant_id,
                                            patient_id=command.patient_id,
                                            medication=medication_value_object,
                                            host_medication_id=response.get("patientMedispanRegistryKey"),
                                            medispan_id=medication_value_object.medispan_id,
                                            original_payload=medication_value_object.dict(),
                                            created_by=command.modified_by,
                                            modified_by=command.modified_by)
                        reconcilled_medication.host_medication_sync_status = HostMedicationSyncStatus(
                            last_synced_at = now_utc(),
                            host_medication_unique_identifier=response.get("patientMedispanRegistryKey")
                        )

                        reconcilled_medication.update_imported_medication(ImportedMedication(
                                imported_medication_id=imported_medication_agg.id,
                                host_medication_id=response.get("patientMedispanRegistryKey"),
                                medispan_id=medication_value_object.medispan_id,
                                medication=medication_value_object,
                                modified_by=command.modified_by
                            ))


                if response and response.get("error") or response.get("errors"):
                    LOGGER.error("update_host_medications: Create errors in createMedication response: %s ::: %s", response.get("error"), response.get("errors"), extra=extra)
                    raise CommandError(response.get("error") or response.get("error") or response.get("errors"))

                return_status["status"] = "SUCCESS"
                return_status["description"] = "Create successful"
                return_status["payload"] = response
                return_status["result"] = result

                reconcilled_medication.host_medication_sync_status = HostMedicationSyncStatus(
                            last_synced_at = now_utc(),
                            host_medication_unique_identifier=response.get("patientMedispanRegistryKey")
                        )

            else:
                LOGGER.warn("Medication synced with host system and is read only.  Operation skipped.  patient_id: %s  reconciledMedId: %s", command.patient_id, reconcilled_medication.id, extra=extra)
                return_status["status"] = "SKIPPED"
                return_status["description"] = "Unexpected medication condition.  Operation skipped."
                return return_status

            uow.register_dirty(medication_profile)

            # Raise PubSub event for host medication update -------------------------------------------------------------------------------------
            msg = MessageContainer(
                message_type = "host_medication_update",
                version = "1.0",
                metadata={
                    "command": command.dict()
                },
                data=return_status,
            )
            LOGGER.debug("Publishing host medication update message to pubsub topic %s: %s", PUBSUB_EVENT_MEDICATION_PUBLISH_TOPIC, msg.dict(), extra=extra)
            messageId = await messaging.publish(PUBSUB_EVENT_ORCHESTRATIONCOMPLETE_TOPIC, msg.dict())
            LOGGER.debug("Submitted pubsub message to topic '%s' with messageId: %s", PUBSUB_EVENT_MEDICATION_PUBLISH_TOPIC, messageId, extra=extra)


            return return_status
    
    elif config.integration is not None:

        thisSpanName = "update_medication"
        with await opentelemetry.getSpan(thisSpanName) as span:
            
            host = config.integration.base_url
            path = config.integration.endpoints["create_medication"]
            path = path.format(tenantId=command.tenant_id, patientId=command.patient_id)
            host = f"{host}{path}"
            headers = {}
            if command.ehr_token:
                headers = {
                    "Authorization": f"Bearer {command.ehr_token}",
                }

            body = command.medication_dict

            #TODO: This is a temporary fix.  Need stronger pydantic typing/conversion here
            from paperglass.domain.utils.boolean_utils import is_truthy

            body = {
                "catalogType": config.meddb_catalog,
                "catalogId": body.get("medispanId"),
                "name": body.get("name"),
                "strength": body.get("strength"),
                "dosage": body.get("dosage"),
                "form": body.get("form"),
                "route": body.get("route"),
                "frequency": body.get("frequency"),
                "instructions": body.get("instructions"),
                "startDate": body.get("startDate"),
                "discontinueDate": body.get("discontinuedDate"),
                "isLongStanding": is_truthy(body.get("isLongStanding")),
                "isNonStandardDose": is_truthy(body.get("isNonStandardDose")),
            }

            extra.update({
                "http_request": {
                    "method": "POST",
                    "url": host,
                    "headers": headers,
                    "body": body
                }
            })
            LOGGER.debug("Updating medication to host: %s", host, extra=extra)

            http_client = HttpRestClient()

            try:
                doc_response = await http_client.resolve(
                    method="POST",
                    url=host,
                    headers=headers,
                    body=body,
                    connection_timeout=5.0,
                    response_timeout=10.0
                )
                extra.update({
                    "http_response": {
                        "status": doc_response.get("status"),
                        "body": doc_response.get("data"),
                        "headers": doc_response.get("headers")
                    }
                })
                if doc_response.get("status") == 200 or doc_response.get("status") == 201:
                    LOGGER.debug(f"REST call to host to update host medications returned a {doc_response.get('status')}", extra=extra)
                    created_medication = doc_response.get("data")
                else:
                    LOGGER.error("Unexpected status code %s when updating host medications", doc_response.get("status"), extra=extra)
                    raise CommandError(f"Unexpected status code {doc_response.get('status')} when updating host medications")
            except CommandError as e:
                raise e
            except Exception as e:
                extra.update({
                    "error": exceptionToMap(e),
                })
                LOGGER.error("Error calling update host medications API: %s", str(e), extra=extra)
                raise CommandError(f"Error updating host medications: {str(e)}")

            imported_medication_agg = ImportedGeneralMedicationAggregate.create(app_id=command.app_id,
                                                        tenant_id=command.tenant_id,
                                                        patient_id=command.patient_id,
                                                        medication=created_medication,
                                                        host_medication_id=created_medication.get("id", None),
                                                        catalog_type=config.meddb_catalog,
                                                        catalog_id=created_medication.get("catalogId", None),
                                                        medispan_id=created_medication.get("catalogId", None),
                                                        original_payload=created_medication,
                                                        modified_by=command.modified_by,
                                                        created_by=command.created_by
                                                    )

            LOGGER.debug("update_host_medications: getMedicationProfile_by_patient_id", extra=extra)
            medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
            LOGGER.debug("Medication profile: %s", medication_profile, extra=extra)

            if medication_profile:
                LOGGER.debug("Medical profile exists", extra=extra)
                result:Result = medication_profile.reconcile_imported_medications(imported_medication_agg)
                uow.register_dirty(medication_profile)
            else:
                LOGGER.debug("Medical profile does not exist.  Creating..", extra=extra)
                medication_profile:MedicationProfile = MedicationProfile.create(app_id=command.app_id, tenant_id=command.tenant_id, patient_id=command.patient_id)
                result:Result = medication_profile.reconcile_imported_medications(imported_medication_agg)
                uow.register_new(medication_profile)

            return_status["status"] = "SUCCESS"
            return_status["description"] = "Create successful"
            return_status["payload"] = created_medication
            return_status["result"] = result

            uow.register_dirty(medication_profile)
            return return_status
    else:
        LOGGER.info("Bypassing:  App %s is not supported for updating host medications", command.app_id, extra=extra)
        return []

@dispatcher.register(ImportHostAttachments)
@inject()
async def import_host_attachments(command: ImportHostAttachments, uow: IUnitOfWork, query: IQueryPort, external_attachment_adapter:IHHHAdapter, storage: IStoragePort, commands: ICommandHandlingPort):
    thisSpanName = "import_host_attachments"
    with await opentelemetry.getSpan(thisSpanName) as span:
        extra = command.toExtra()
        branch = "ImportHostAttachments"

        LOGGER.debug("Importing host attachments for app_id: %s tenant_id: %s patient_id: %s", command.app_id, command.tenant_id, command.patient_id, extra=extra)

        config:Configuration = await get_config(command.app_id, command.tenant_id, query)

        if command.app_id == "hhh":
            LOGGER.debug("Importing HHH Attachments", extra=extra)            

            ruleset = None
            if config and config.rulesets and "file_ingress" in config.rulesets:
                ruleset = config.rulesets["file_ingress"].dict()

            extra.update({
                "ruleengine": {
                    "ruleset": ruleset
                }
            })
            LOGGER.debug("Ruleset: %s", ruleset, extra=extra)

            if not config.on_demand_external_files_config or (config.on_demand_external_files_config and not config.on_demand_external_files_config.enabled):
                LOGGER.debug("Bypassing importing HHH Attachments:  HHH Attachments import is disabled", extra=extra)
                ret = ["Import disabled"]
                Metric.send("ATTACHMENT::BYPASS", branch=branch, tags=extra)
                return Result(success=True,return_data=ret)

            try:
                LOGGER.info("Getting external attachments for app_id: %s tenant_id: %s patient_id: %s", command.app_id, command.tenant_id, command.patient_id, extra=extra)
                host_attachments:List[HostAttachment] = await external_attachment_adapter.get_attachments(command.tenant_id,command.patient_id,command.ehr_token, uploaded_date_cut_off_window_in_days=config.on_demand_external_files_config.uploaded_date_cut_off_window_in_days)
                LOGGER.debug("Host attachments: %s", host_attachments, extra=extra)
                results = []
                for host_attachment in host_attachments:  #TODO:  This is duplicative code.  Have this call the ImportHostAttachmentFromExternalStorageUri instead
                    with await opentelemetry.getSpan(thisSpanName + ":attachment") as span:
                        host_attachment:HostAttachment = host_attachment
                        LOGGER.debug("Processing attachment: %s from GS uri %s", host_attachment.file_name, host_attachment.storage_uri, extra=extra)
                        span.set_attribute("source_attachment_id", host_attachment.host_attachment_id)
                        span.set_attribute("source_storage_uri", host_attachment.storage_uri)
                        span.set_attribute("source_file_name", host_attachment.file_name)
                        span.set_attribute("source_file_status", host_attachment.active)
                        # find if the attachment is already imported
                        document:dict = await query.get_document_by_source_storage_uri(host_attachment.storage_uri,command.tenant_id,command.patient_id)
                        if not document:
                            with await opentelemetry.getSpan(thisSpanName + ":creating_new_HostAttachmentAggregate") as span:
                                extra.update({
                                    "file_name": host_attachment.file_name,
                                    "file_type": get_filetype_from_filename(host_attachment.file_name)
                                })
                                try:
                                    storage_metadata = None
                                    if HHH_ATTACHMENTS_STORAGE_OBJECT_METADATA_ENABLE:
                                        try:
                                            storage_metadata = await storage.get_object_metadata(host_attachment.storage_uri)
                                            extra.update({
                                                "storage_metadata": storage_metadata
                                            })
                                            Metric.send("STORAGE_METADATA::RETRIEVED", branch="api", tags=extra)

                                        except NotFoundException as e:
                                            # So metadata wasn't found because the object isn't there.  Just keep metadata as null and let the process continue and decide what to do when it doesn't find the document
                                            LOGGER.warning("Storage metadata not found for attachment %s.  Skipping", host_attachment.file_name, extra=extra)
                                            Metric.send("STORAGE_METADATA::NOT_FOUND", branch=branch, tags=extra)
                                            pass

                                    LOGGER.info('Creating new pulled HostAttachmentAggregate for %s', host_attachment.file_name, extra=extra)
                                    host_aggregate = HostAttachmentAggregate.create(app_id=command.app_id,tenant_id=command.tenant_id,
                                                                patient_id=command.patient_id,
                                                                storage_uri=host_attachment.storage_uri,
                                                                file_name=host_attachment.file_name,token=command.api_token,
                                                                storage_metadata=storage_metadata )

                                    priority = MEDICATION_EXTRACTION_PRIORITY_DEFAULT
                                    metadata = {}

                                    if ruleset:
                                        rulesengine = RulesEngine(ruleset)
                                        actions = rulesengine.evaluate(host_aggregate.dict())
                                        extra.update({
                                            "ruleengine": {
                                                "ruleset": ruleset,
                                                "object": host_aggregate.dict(),
                                                "actions": actions
                                            }
                                        })
                                        LOGGER.debug("Actions: %s", actions, extra=extra)

                                        if "skip" in actions:
                                            LOGGER.info("Skipping attachment %s due to ruleset action", host_attachment.file_name, extra=extra)
                                            Metric.send("ATTACHMENT::RULES::SKIP", branch=branch, tags=extra)
                                            return Result(success=False,error_message="Attachment skipped due to ruleset action")

                                        if actions and "extract" in actions:
                                            priority = actions["extract"].get("params",{}).get("queue", MEDICATION_EXTRACTION_PRIORITY_DEFAULT)
                                            LOGGER.info("Setting extraction priority for %s to %s due to ruleset action", host_attachment.file_name, priority, extra=extra)
                                            metadata["file_ingress_actions"] = actions
                                        else:
                                            LOGGER.warning("Using default extration priority as no actions were output from the rules engine", extra=extra)
                                    else:
                                        LOGGER.warning("No ruleset found for file_ingress.  Using default extraction priority", extra=extra)

                                    #host_aggregate.upload()
                                    await create_document(CreateDocument(token=host_aggregate.token,
                                                            app_id=host_aggregate.app_id,
                                                            tenant_id=host_aggregate.tenant_id,
                                                            file_name=host_aggregate.file_name,
                                                            patient_id=host_aggregate.patient_id,
                                                            source="host",
                                                            source_id=command.source_id,
                                                            source_storage_uri=host_aggregate.storage_uri,
                                                            priority=priority,
                                                        ),uow)
                                    uow.register_new(host_aggregate)
                                    Metric.send("ATTACHMENT::ACCEPTED", branch=branch, tags=extra)
                                    results.append({"status":"CREATED","description":"New attachment created","host_attachment":host_attachment.dict()})
                                except UnsupportedFileTypeException as e:
                                    LOGGER.warning("Unsupported file type for pulled attachment %s.  Skipping", host_attachment.file_name, extra=extra)
                                    Metric.send("ATTACHMENT::UNSUPPORTED_TYPE", branch=branch, tags=extra)
                                    results.append({"status":"SKIPPED","description":"Unsupported file type","host_attachment":host_attachment.dict()})
                        else:
                            if not host_attachment.active:
                                document = Document(**document)
                                LOGGER.info("Host attachment is not active.  Deleting document %s", document.id, extra=extra)
                                Metric.send("ATTACHMENT::INACTIVE", branch=branch, tags=extra)
                                document.delete()
                                uow.register_dirty(document)
                                medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
                                medication_profile.delete_medications_from_deleted_document(document)
                                results.append({"status":"DELETED","description":"New attachment created","host_attachment":host_attachment.dict()})
                            else:
                                LOGGER.info("Host attachment already imported.  Skipping", extra=extra)
                                Metric.send("ATTACHMENT::EXISTS", branch=branch, tags=extra)
                                results.append({"status":"SKIPPED","description":"Host attachment already imported","host_attachment":host_attachment.dict()})
                return Result(success=True,return_data=results)
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error("Exception occurred during retrieval of external attachments for patient_id %s: %s", command.patient_id, str(e), extra=extra)
                Metric.send("ATTACHMENT::ERROR", branch=branch, tags=extra)
                raise CommandError(str(e))
        elif config.integration is not None:
            try:                
                host = config.integration.base_url
                path = config.integration.endpoints["list_attachments"]
                path = path.format(tenantId=command.tenant_id, patientId=command.patient_id)
                host = f"{host}{path}"
                headers = {}
                if command.ehr_token:
                    headers = {
                        "Authorization": f"Bearer {command.ehr_token}",
                    }

                extra.update({
                    "http_request": {
                        "method": "GET",
                        "url": host,
                        "headers": headers,
                        "body": None
                    }
                })
                LOGGER.debug("Importing external attachments from host: %s", host, extra=extra)

                # host_attachments:List[HostAttachment] = await external_attachment_adapter.get_attachments(command.tenant_id,command.patient_id,command.ehr_token, uploaded_date_cut_off_window_in_days=config.on_demand_external_files_config.uploaded_date_cut_off_window_in_days)

                http_client = HttpRestClient()
                try:
                    doc_response = await http_client.resolve(
                        method="GET",
                        url=host,
                        headers=headers,
                        body=None,
                        connection_timeout=5.0,
                        response_timeout=10.0
                    )
                    extra.update({
                        "http_response": {
                            "status": doc_response.get("status"),
                            "body": doc_response.get("data"),
                            "headers": doc_response.get("headers")
                        }
                    })
                    if doc_response.get("status") == 404:
                        LOGGER.info("REST call to host to retrieve host attachments returned a 404.  Setting imported attachments to empty list", extra=extra)
                        host_attachments = []
                    elif doc_response.get("status") == 200:
                        LOGGER.debug(f"REST call to host to retrieve host attachments returned a {doc_response.get('status')}", extra=extra)
                        host_attachments = doc_response.get("data", [])
                    else:
                        LOGGER.error("Unexpected status code %s when importing host attachments", doc_response.get("status"), extra=extra)
                        raise CommandError(f"Unexpected status code {doc_response.get('status')} when importing host attachments")
                except CommandError as e:
                    raise e
                except Exception as e:
                    extra.update({
                        "error": exceptionToMap(e),
                    })
                    LOGGER.error("Error calling host attachments API: %s", str(e), extra=extra)
                    raise CommandError(f"Error importing host attachments: {str(e)}")

                LOGGER.debug("Host attachments: %s", host_attachments, extra=extra)
                results = []
                for host_attachment in host_attachments:
                    with await opentelemetry.getSpan(thisSpanName + ":attachment") as span:
                        host_file_id = host_attachment.get("hostFileId", None)                        
                        if host_file_id is None:
                            LOGGER.warning("Host attachment does not have a hostFileId!  This may result in duplicate documents.  Defaulting to generated UUID", extra=extra)
                            host_file_id = uuid.uuid4().hex
                        metadata = host_attachment.get("metadata", {})

                        host_attachment:ImportHostAttachmentFromExternalApi = ImportHostAttachmentFromExternalApi(
                            app_id=command.app_id,
                            tenant_id=command.tenant_id,
                            patient_id=command.patient_id,
                            source_id=host_file_id,
                            file_name=host_attachment["fileName"],
                            file_type=host_attachment["fileType"],
                            created_on=host_attachment["createdOn"],
                            updated_on=host_attachment["updatedOn"],
                            sha256=host_attachment.get("sha256", None),
                            metadata=metadata,
                            active=host_attachment["active"],
                            repository_type=host_attachment["repositoryType"].upper(),
                            api=host_attachment["api"],
                            raw_event=GenericExternalDocumentCreateEventRequestApi(
                                appId=command.app_id,
                                tenantId=command.tenant_id,
                                patientId=command.patient_id,
                                hostFileId=host_file_id,
                                fileName=host_attachment["fileName"],
                                fileType=host_attachment["fileType"],
                                createdOn=host_attachment["createdOn"],
                                api=host_attachment["api"]
                                )
                        )

                        LOGGER.debug("Processing attachment: %s", host_attachment.file_name, extra=extra)
                        span.set_attribute("source_file_name", host_attachment.file_name)
                        span.set_attribute("source_file_status", host_attachment.active)
                        # find if the attachment is already imported
                        response = await commands.handle_command(host_attachment)
                        results.append(response.return_data[0])

                return Result(success=True,return_data=results)
            except Exception as e:
                extra["error"] = exceptionToMap(e)
                LOGGER.error("Exception occurred during retrieval of external attachments for patient_id %s: %s", command.patient_id, str(e), extra=extra)
                Metric.send("ATTACHMENT::ERROR", branch=branch, tags=extra)
                raise CommandError(str(e))
        else:
            LOGGER.info("Bypassing:  App %s is not supported for importing attachments", command.app_id, extra=extra)
            return []

@dispatcher.register(ImportHostAttachmentFromExternalStorageUri)
@inject()
async def import_host_attachment(command: ImportHostAttachmentFromExternalStorageUri, uow: IUnitOfWork, query: IQueryPort, external_attachment_adapter:IHHHAdapter, storage: IStoragePort):
    thisSpanName = "import_host_attachment"
    with await opentelemetry.getSpan(thisSpanName) as span:

        extra = command.toExtra()
        branch = "ImportHostAttachmentFromExternalStorageUri"

        try:
            LOGGER.info("Getting external attachment file", extra=extra)
            external_storage_file = command.external_storage_uri
            if external_storage_file:
                with await opentelemetry.getSpan(thisSpanName + ":attachment") as span:
                    tenant_id = external_storage_file.split("/")[-2]
                    file_name = external_storage_file.split("/")[-1]

                    extra.update({
                        "tenant_id": tenant_id,
                        "file_name": file_name,
                        "file_type": get_filetype_from_filename(external_storage_file)
                    })

                    host_attachment_metadata:HostAttachmentMetadata = None
                    priority_default = MEDICATION_EXTRACTION_PRIORITY_DEFAULT

                    skip_processing = False

                    id = uuid.uuid4().hex

                    config:Configuration = await get_config(command.app_id, tenant_id, query)

                    if config and config.tenant_allow_list and config.tenant_allow_list_check_enabled and tenant_id not in config.tenant_allow_list:
                        LOGGER.debug("Tenant %s not in allow list.  quarantine_enabled: %s", tenant_id, config.quarantine_enabled, extra=extra)
                        skip_processing = not config.quarantine_enabled

                    extra.update({
                        "quarantine_enabled": config.quarantine_enabled
                    })

                    if skip_processing:
                        LOGGER.info("Tenant %s not in allow list.  Skipping", tenant_id, extra=extra)
                        return Result(success=False,error_message="Tenant not in allow list")

                    ruleset = None
                    if config and config.rulesets and "file_ingress" in config.rulesets:
                        ruleset = config.rulesets["file_ingress"].dict()

                    extra.update({
                        "ruleengine": {
                            "ruleset": ruleset
                        }
                    })
                    LOGGER.debug("Ruleset: %s", ruleset, extra=extra)

                    try:
                        host_attachment_metadata = await external_attachment_adapter.get_attachment_metadata(tenant_id, file_name,external_storage_file)
                    except NotFoundException as e:
                        pass # This is expected if the clinic is not enabled for Extract

                    LOGGER.debug("Host attachment metadata: %s", host_attachment_metadata, extra=extra)
                    results = []


                    if not host_attachment_metadata and config.quarantine_enabled:
                        LOGGER.info("Quarantining attachment %s", file_name, extra=extra)
                        host_attachment_metadata = HostAttachmentMetadata(tenant_id=tenant_id, patient_id=f"quarantine-{id}",
                                                                            host_attachment=HostAttachment(host_attachment_id=id,file_name=file_name, storage_uri=external_storage_file)
                                                                        )
                        priority_default = MEDICATION_EXTRACTION_PRIORITY_QUARANTINE

                    if not host_attachment_metadata:
                        LOGGER.info("No attachment metadata found for %s.  Skipping", external_storage_file, extra=extra)
                        Metric.send("ATTACHMENT:METADATA_MISSING", branch=branch, tags=extra)
                    else:
                        host_attachment:HostAttachment = host_attachment_metadata.host_attachment
                        LOGGER.debug("Processing attachment: %s from GS uri %s", host_attachment.file_name, host_attachment.storage_uri, extra=extra)
                        span.set_attribute("source_attachment_id", host_attachment.host_attachment_id)
                        span.set_attribute("source_storage_uri", host_attachment.storage_uri)
                        span.set_attribute("source_file_name", host_attachment.file_name)
                        span.set_attribute("source_file_status", host_attachment.active)

                        extra["host_attachment"] = host_attachment.dict()

                        storage_metadata = None
                        if HHH_ATTACHMENTS_STORAGE_OBJECT_METADATA_ENABLE:
                            try:
                                storage_metadata = await storage.get_object_metadata(host_attachment.storage_uri)
                                extra.update({
                                    "storage_metadata": storage_metadata
                                })
                                Metric.send("STORAGE_METADATA::RETRIEVED", branch="storage_event", tags=extra)
                            except NotFoundException as e:
                                # So metadata wasn't found because the object isn't there.  Just keep metadata as null and let the process continue and decide what to do when it doesn't find the document
                                LOGGER.warning("Storage metadata not found for attachment %s.  Skipping", host_attachment.file_name, extra=extra)
                                Metric.send("STORAGE_METADATA::NOT_FOUND", branch=branch, tags=extra)
                                pass

                        # find if the attachment is already imported
                        document:dict = await query.get_document_by_source_storage_uri(host_attachment.storage_uri, host_attachment_metadata.tenant_id, host_attachment_metadata.patient_id)
                        if not document:
                            with await opentelemetry.getSpan(thisSpanName + ":creating_new_HostAttachmentAggregate") as span:
                                try:
                                    LOGGER.info('Creating new HostAttachmentAggregate for %s', host_attachment.file_name, extra=extra)
                                    host_aggregate = HostAttachmentAggregate.create(app_id=command.app_id,tenant_id=host_attachment_metadata.tenant_id,
                                                                    patient_id=host_attachment_metadata.patient_id,
                                                                    storage_uri=host_attachment.storage_uri,
                                                                    file_name=host_attachment.file_name,token=get_token(command.app_id,
                                                                                                                        host_attachment_metadata.tenant_id,
                                                                                                                        host_attachment_metadata.patient_id
                                                                                                                        ),
                                                                    raw_event=command.raw_event,
                                                                    storage_metadata=storage_metadata,
                                                                )
                                    extra.update({
                                        "priority_default": priority_default
                                    })

                                    priority = priority_default
                                    metadata = {}

                                    if ruleset and priority != "quarantine":
                                        rulesengine = RulesEngine(ruleset)
                                        actions = rulesengine.evaluate(host_aggregate.dict())
                                        extra.update({
                                            "ruleengine": {
                                                "ruleset": ruleset,
                                                "object": host_aggregate.dict(),
                                                "actions": actions
                                            }
                                        })
                                        LOGGER.debug("Actions: %s", actions, extra=extra)

                                        if "skip" in actions:
                                            LOGGER.info("Skipping attachment %s due to ruleset action", host_attachment.file_name, extra=extra)
                                            Metric.send("ATTACHMENT::RULES::SKIP", branch=branch, tags=extra)
                                            return Result(success=False,error_message="Attachment skipped due to ruleset action")

                                        if actions and "extract" in actions:
                                            priority = actions["extract"].get("params",{}).get("queue", priority_default)
                                            LOGGER.info("Setting extraction priority for %s to %s due to ruleset action", host_attachment.file_name, priority, extra=extra)
                                            metadata["file_ingress_actions"] = actions
                                        else:
                                            LOGGER.warning("Using default extration priority as no actions were output from the rules engine", extra=extra)
                                    else:
                                        LOGGER.warning("No ruleset found for file_ingress.  Using %s extraction priority", priority_default, extra=extra)

                                    await create_document(CreateDocument(token=host_aggregate.token,
                                                            app_id=host_aggregate.app_id,
                                                            tenant_id=host_aggregate.tenant_id,
                                                            file_name=host_aggregate.file_name,
                                                            patient_id=host_aggregate.patient_id,
                                                            source="host",
                                                            source_id=command.source_id,
                                                            source_storage_uri=host_aggregate.storage_uri,
                                                            priority=priority
                                                        ),uow)
                                    uow.register_new(host_aggregate)
                                    Metric.send("ATTACHMENT::ACCEPTED", branch=branch, tags=extra)
                                    results.append({"status":"CREATED","description":"New attachment created","host_attachment":host_attachment.dict()})
                                except UnsupportedFileTypeException as e:
                                    extra.update({
                                        "error": exceptionToMap(e)
                                    })
                                    LOGGER.warning("Unsupported file type for attachment %s.  Skipping", host_attachment.file_name, extra=extra)
                                    Metric.send("ATTACHMENT::UNSUPPORTED_TYPE", branch=branch, tags=extra)
                                    results.append({"status":"SKIPPED","description":"Unsupported file type","host_attachment":host_attachment.dict()})
                        else:
                            if not host_attachment.active:
                                document = Document(**document)

                                extra["document_id"] = document.id
                                LOGGER.info("Host attachment is not active.  Deleting document %s", document.id, extra=extra)
                                Metric.send("ATTACHMENT::INACTIVE", branch=branch, tags=extra)

                                document.delete()
                                uow.register_dirty(document)
                                medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(host_attachment_metadata.patient_id)
                                medication_profile.delete_medications_from_deleted_document(document)
                                results.append({"status":"DELETED","description":"New attachment created","host_attachment":host_attachment.dict()})
                            else:
                                LOGGER.info("Host attachment already imported.  Skipping", extra=extra)
                                Metric.send("ATTACHMENT::EXISTS", branch=branch, tags=extra)
                                results.append({"status":"SKIPPED","description":"Host attachment already imported","host_attachment":host_attachment.dict()})
            return Result(success=True,return_data=results)
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Exception occurred during retrieval of external attachment %s %s", command.external_storage_uri, str(e), extra=extra)
            Metric.send("ATTACHMENT::ERROR", branch=branch, tags=extra)
            return Result(success=False,error_message=str(e))


@dispatcher.register(ImportHostAttachmentFromExternalApiTask)
@inject
async def import_host_attachment_from_api_task(command: ImportHostAttachmentFromExternalApiTask, uow: IUnitOfWork, cloud_task_adapter:ICloudTaskPort):
    # Processes external documents retrieved from a host API.  Other repository types will be included in the future
    action_command = command.to_action_command()

    if CLOUD_PROVIDER == "local":
        LOGGER.debug("Running import_host_attachment_from_api_task in local mode", extra=command.toExtra())
        return await import_host_attachment_from_api(action_command, uow)
    else:
        LOGGER.debug("Running import_host_attachment_from_api_task in cloud mode", extra=command.toExtra())
        await cloud_task_adapter.create_task(
                token=mktoken2(command.app_id, command.raw_event.tenantId, command.raw_event.patientId),
                location=GCP_LOCATION_2,
                service_account_email=SERVICE_ACCOUNT_EMAIL,
                queue=CLOUD_TASK_COMMAND_QUEUE_NAME,
                url=f"{SELF_API}/document/external/create/task",
                payload = action_command.dict(),
            )


@dispatcher.register(ImportHostAttachmentFromExternalApi)
@inject
async def import_host_attachment_from_api(command: ImportHostAttachmentFromExternalApi, uow: IUnitOfWork, query: IQueryPort):
    thisSpanName = "import_host_attachment_from_api"
    with await opentelemetry.getSpan(thisSpanName) as span:
        request: Union[GenericExternalDocumentCreateEventRequestApi, GenericExternalDocumentCreateEventRequestUri] = command.raw_event

        extra = command.toExtra()
        branch = "ImportHostAttachmentFromExternalApi"

        app_id = command.app_id
        tenant_id = command.tenant_id
        patient_id = command.patient_id
        priority_default = MEDICATION_EXTRACTION_PRIORITY_DEFAULT
        skip_processing = False
        metadata = command.metadata or {}
        id = uuid.uuid4().hex
        results = []

        LOGGER.debug("Importing host attachment from external source: %s", request, extra=extra)

        try:
            if request:

                file_name = command.file_name

                # Get configuration
                config:Configuration = await get_config(command.app_id, tenant_id, query)

                # Check Tenant allow list and skip if not right conditions
                if config and config.tenant_allow_list and config.tenant_allow_list_check_enabled and tenant_id not in config.tenant_allow_list:
                    LOGGER.debug("Tenant %s not in allow list.  quarantine_enabled: %s", tenant_id, config.quarantine_enabled, extra=extra)
                    skip_processing = not config.quarantine_enabled

                extra.update({
                    "quarantine_enabled": config.quarantine_enabled
                })

                if skip_processing:
                    LOGGER.info("Tenant %s not in allow list.  Skipping", tenant_id, extra=extra)
                    Metric.send("ATTACHMENT::TENANTWHITELIST::SKIP", branch=branch, tags=extra)
                    return Result(success=False,error_message="Tenant not in allow list")

                # Prepare ruleset
                ruleset = None
                if config and config.rulesets and "file_ingress" in config.rulesets:
                    ruleset = config.rulesets["file_ingress"].dict()

                extra.update({
                    "ruleengine": {
                        "ruleset": ruleset
                    }
                })
                LOGGER.debug("Importing host attachment Ruleset: %s", ruleset, extra=extra)

                # Skip if metadata indicates tenant is not licensed for Extract
                #TODO:  Need to know which metadata field to check for this !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                license_enabled = True

                if not license_enabled and config.quarantine_enabled:
                    LOGGER.info("Quarantining attachment %s", file_name, extra=extra)
                    Metric.send("ATTACHMENT:NOT_LICENSED:QUARANTINE", branch=branch, tags=extra)
                    priority_default = MEDICATION_EXTRACTION_PRIORITY_QUARANTINE
                    skip_processing = False
                elif not license_enabled:
                    LOGGER.info("No license for tenantid %s.  Skipping", tenant_id, extra=extra)
                    Metric.send("ATTACHMENT:NOT_LICENSED:SKIPPED", branch=branch, tags=extra)
                    skip_processing = True

                if not skip_processing:

                    LOGGER.debug("Processing attachment: %s", file_name, extra=extra)

                    # Check if document already exists based on source_id
                    document:dict = await query.get_document_by_source_id(command.source_id, app_id=app_id, tenant_id=tenant_id, patient_id=patient_id)
                    if not document:
                        with await opentelemetry.getSpan(thisSpanName + ":creating_new_HostAttachmentAggregate") as span:
                            try:

                                LOGGER.debug("Document doesn't exist in system %s. Creating...", file_name, extra=extra)

                                # Save HostAggregateAttachment                                
                                if command.repository_type == ExternalDocumentRepositoryType.API:
                                    host_aggregate = HostAttachmentAggregate.create_api(app_id=command.app_id,tenant_id=tenant_id,
                                                                    patient_id=patient_id,
                                                                    api=request.api,
                                                                    file_name=file_name,token=get_token(command.app_id,
                                                                                                        tenant_id,
                                                                                                        patient_id
                                                                                                        ),
                                                                    raw_event=request.dict(),
                                                                    storage_metadata=request.metadata,
                                                                )
                                elif command.repository_type == ExternalDocumentRepositoryType.URI:
                                    # For URI type, create with URI instead of API
                                    host_aggregate = HostAttachmentAggregate.create(app_id=command.app_id,tenant_id=tenant_id,
                                                                    patient_id=patient_id,
                                                                    storage_uri=request.uri.uri,
                                                                    file_name=file_name,token=get_token(command.app_id,
                                                                                                        tenant_id,
                                                                                                        patient_id
                                                                                                        ),
                                                                    raw_event=request.dict(),
                                                                    storage_metadata=request.metadata,
                                                                )
                                extra.update({
                                    "priority_default": priority_default
                                })

                                # If ruleset exists, then evaluate for priority
                                priority = priority_default                                

                                if ruleset and priority != "quarantine":
                                    rulesengine = RulesEngine(ruleset)
                                    actions = rulesengine.evaluate(host_aggregate.dict())
                                    extra.update({
                                        "ruleengine": {
                                            "ruleset": ruleset,
                                            "object": host_aggregate.dict(),
                                            "actions": actions
                                        }
                                    })
                                    LOGGER.debug("Actions: %s", actions, extra=extra)

                                    if "skip" in actions:  #skip is a priority action and takes presidence over any other action
                                        LOGGER.info("Skipping attachment %s due to ruleset action", file_name, extra=extra)
                                        Metric.send("ATTACHMENT::RULES::SKIP", branch=branch, tags=extra)
                                        return Result(success=False,error_message="Attachment skipped due to ruleset action")

                                    if actions and "extract" in actions: # Priority will be either the name of a queue, or none.  If none, the document will by imported but not auto-extracted
                                        priority = actions["extract"].get("params",{}).get("queue", priority_default)
                                        LOGGER.info("Setting extraction priority for %s to %s due to ruleset action", file_name, priority, extra=extra)
                                        metadata["file_ingress_actions"] = actions
                                    else:
                                        LOGGER.warning("Using default extration priority as no actions were output from the rules engine", extra=extra)
                                elif priority == "quarantine":
                                    LOGGER.debug("Is assigned to quarantine queue.  Using %s extraction priority", priority, extra=extra)
                                else:
                                    LOGGER.warning("No ruleset found for file_ingress.  Using %s extraction priority", priority_default, extra=extra)

                                # Create document
                                if command.repository_type == ExternalDocumentRepositoryType.API:
                                    createdocument_command = CreateDocument(token=host_aggregate.token,
                                                            app_id=app_id,
                                                            tenant_id=tenant_id,
                                                            file_name=file_name,
                                                            patient_id=patient_id,
                                                            source="api",
                                                            source_id=command.source_id,
                                                            source_api=request.api,
                                                            priority=priority,
                                                            metadata=metadata
                                                        )
                                elif command.repository_type == ExternalDocumentRepositoryType.URI:
                                    createdocument_command = CreateDocument(token=host_aggregate.token,
                                                            app_id=app_id,
                                                            tenant_id=tenant_id,
                                                            file_name=file_name,
                                                            patient_id=patient_id,
                                                            source="host",
                                                            source_id=command.source_id,
                                                            source_storage_uri=request.uri.uri,
                                                            priority=priority,
                                                            metadata=metadata
                                                        )
                                extra["debug_source_id_set"] = command.source_id
                                LOGGER.info(f"[DEBUG_FLOW] CreateDocument command created with source_id: {command.source_id}", extra=extra)
                                await create_document(createdocument_command, uow)
                                uow.register_new(host_aggregate)

                                Metric.send("ATTACHMENT::ACCEPTED", branch=branch, tags=extra)
                                results.append({"status":"CREATED","description":"New attachment created","host_attachment":request.dict()})

                            except UnsupportedFileTypeException as e:
                                extra.update({
                                    "error": exceptionToMap(e)
                                })
                                LOGGER.warning("Unsupported file type for attachment %s.  Skipping", file_name, extra=extra)
                                Metric.send("ATTACHMENT::UNSUPPORTED_TYPE", branch=branch, tags=extra)
                                results.append({"status": "SKIPPED", "description": "Unsupported file type", "host_attachment": request.dict()})

                    else:
                        if not command.active:
                            document = Document(**document)

                            extra["document_id"] = document.id
                            LOGGER.info("Host attachment is not active.  Deleting document %s", document.id, extra=extra)
                            Metric.send("ATTACHMENT::INACTIVE", branch=branch, tags=extra)

                            document.delete()
                            uow.register_dirty(document)
                            medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id)
                            medication_profile.delete_medications_from_deleted_document(document)
                            results.append({"status":"DELETED","description": "Attachment deleted by host","host_attachment":request.dict()})
                        else:
                            LOGGER.info("Host attachment already imported.  Skipping", extra=extra)
                            Metric.send("ATTACHMENT::EXISTS", branch=branch, tags=extra)
                            results.append({"status":"SKIPPED","description":"Host attachment already imported","host_attachment":request.dict()})
                else:
                    LOGGER.info("Skipping processing of host attachment %s due to tenant allow list", file_name, extra=extra)
                    
                extra.update({
                    "results": results
                })   
                LOGGER.debug("Returning results: %s", results, extra=extra)
                return Result(success=True,return_data=results)

            else:
                LOGGER.error("API request is required for importing host attachment", extra=extra)
                raise ValueError("API request is required")

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error("Exception occurred during retrieval of external attachment from api %s %s", command.raw_event, str(e), extra=extra)
            Metric.send("ATTACHMENT::ERROR", branch=branch, tags=extra)
            return Result(success=False,error_message=str(e))


@dispatcher.register(GetHostMedicationClassifications)
@inject()
async def import_host_medication_classifications(command: GetHostMedicationClassifications, uow: IUnitOfWork, query: IQueryPort, external_attachment_adapter: IHHHAdapter):

    if command.app_id != "hhh":
        LOGGER.info("Bypassing:  App %s is not supported for importing host medication classifications", command.app_id, extra=command.toExtra())
        empty_list = ReferenceCodes.create(category="external", list="classification", codes=[])
        return empty_list

    extra = command.toExtra()
    LOGGER.debug("Getting host medication classifications for patient_id: %s", command.patient_id, extra=extra)

    existing_cache = False

    reference_id = "external:classification"

    ref_codes = await uow.get(ReferenceCodes, reference_id)
    if ref_codes:
        existing_cache = True

    #Use the cache if it the TTL is -1 (cache forever) or if the age on the cache is less than the cache ttl
    if ref_codes and (HHH_CLASSIFICATION_CACHE_TTL==-1 or (ref_codes.cached_on and (now_utc() - ref_codes.cached_on).total_seconds() < HHH_CLASSIFICATION_CACHE_TTL)):
        LOGGER.debug("Returning cached host medication classifications", extra=extra)
        return ref_codes

    try:
        LOGGER.debug("Fetching host medication classifications from external source", extra=extra)
        ref_codes: ReferenceCodes = await external_attachment_adapter.get_classifications(command.ehr_token)
        LOGGER.debug("Pushing external classification to cache", extra=extra)
        ref_codes.cached_on = now_utc()
        if existing_cache:
            uow.register_dirty(ref_codes)
        else:
            uow.register_new(ref_codes)
    except Exception as e:
        extra["error"] = exceptionToMap(e)
        if existing_cache and ref_codes:
            LOGGER.error("Exception fetching medication classifications from external source.  Returning cached reference codes", extra=extra)
            return ref_codes
        else:
            LOGGER.error("Exception fetching medication classifications from external source.  No cached reference codes available. Raising exception", extra=extra)
            raise e

    return ref_codes


@dispatcher.register(GetDocumentPDFURL)
@inject
async def get_document_pdf_url(command: GetDocumentPDFURL, uow: IUnitOfWork, storage: IStoragePort):
    LOGGER.debug("Getting document PDF URL for document_id: %s", command.document_id, extra=command.toExtra())
    return await storage.get_document_pdf_url(app_id=command.app_id,
                                              tenant_id=command.tenant_id,
                                              patient_id=command.patient_id,
                                              document_id=command.document_id)


@dispatcher.register(FindMedication)
@inject()
async def find_medication(command: FindMedication, uow: IUnitOfWork, medispan_port: IMedispanPort, relevancy_filter_adapter: IRelevancyFilterPort):
    from paperglass.infrastructure.adapters.medispan_api_search_filter import MedispanAPISearchFilterAdapter
    from paperglass.infrastructure.adapters.medispan import MedispanAdapter
    from paperglass.infrastructure.adapters.medispan_api import MedispanAPIAdapter
    from paperglass.settings import MEDISPAN_CLIENT_ID, MEDISPAN_CLIENT_SECRET
    try:
        config:Configuration = await get_config(command.app_id, command.tenant_id)
        catalog = config.meddb_catalog if config and config.meddb_catalog else MEDICATION_CATALOG_DEFAULT        

        # All catalogs other than medispan will automatically use the new API
        # Otherwise it is determined by configuration
        # TODO:  Once the new api has been proven in production, remove this feature flag
        if catalog != MEDICATION_CATALOG_DEFAULT or (config and config.medispan_match_config and \
            (command.tenant_id in config.medispan_match_config.v2_enabled_tenants or config.medispan_match_config.v2_enabled_globally)):
                LOGGER.debug(f"Medication catalog {catalog} V2 enabled for tenant {command.tenant_id}", extra=command.toExtra())

                medispan_port_result =  await MedispanAPIAdapter(catalog=catalog).search_medications(command.term)
        else:
            LOGGER.debug(f"Medication catalog {catalog} V1 enabled for tenant {command.tenant_id}", extra=command.toExtra())
            medispan_port_result =  await MedispanAdapter(MEDISPAN_CLIENT_ID,MEDISPAN_CLIENT_SECRET).search_medications(command.term)

        medispan_port_result = await MedispanAPISearchFilterAdapter().aggregate(command.term, medispan_port_result,False,None)
        return medispan_port_result
    except IMedispanPort.Error as exc:
        raise CommandError(str(exc)) from exc

# Used for quick testing a medication string against the Medispan Search and LLM filter
@dispatcher.register(FindMedicationWithLLMFilter)
@inject()
async def medispan_vector_matching_with_llm(command: FindMedicationWithLLMFilter, uow: IUnitOfWork,
                             query:IQueryPort,
                             medispan_port:IMedispanPort,
                             relevancy_filter_adapter:IRelevancyFilterPort
                             ) -> List[MedispanDrug]:

    extra = command.toExtra()

    opMeta:OperationMeta = OperationMeta(
        type = DocumentOperationType.MEDICATION_EXTRACTION.value,
        step = "FindMedicationWithLLMFilter",
    )

    with await opentelemetry.getSpan("medispan_matching") as span:
        search_term: str = command.term
        medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)

        # If initial search does not return any results, try searching with just the first word of the medication name
        if not medispan_port_result:
            search_term = f"{search_term.name.split(' ')[0]}"
            LOGGER.debug("MedispanVectorMatchingWithLLM: Initial search for medication '%s' did not yield any results.  Trying search with just the first word of the medication name: '%s'", command.term, search_term, extra=extra)
            medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)
        else:
            LOGGER.debug("MedispanVectorMatchingWithLLM: Initial search for medication '%s' yielded results:", command.term, extra=extra)

        if not command.enable_llm:
            return medispan_port_result if medispan_port_result else []

        # Get doc op def for the prompt and model
        doc_op_definitions:DocumentOperationDefinition = await query.get_document_operation_definition_by_op_type(DocumentOperationType.MEDICATION_EXTRACTION)
        if not doc_op_definitions:
            LOGGER.error(f"MedispanVectorMatchingWithLLM: DocumentOperationDefinition not found for {DocumentOperationType.MEDICATION_EXTRACTION}", extra=extra)
            raise Exception(f"DocumentOperationDefinition not found for {DocumentOperationType.MEDICATION_EXTRACTION}")
        doc_op_definition = doc_op_definitions[0]
        opMeta.document_operation_def_id = doc_op_definition.get("id")
        model = doc_op_definition.step_config.get(DocumentOperationStep.MEDISPAN_MATCHING).get("model")
        prompt = doc_op_definition.step_config.get(DocumentOperationStep.MEDISPAN_MATCHING).get("prompt")

        medispan_results_tuple = await relevancy_filter_adapter.re_rank(search_term, medispan_port_result, model=model, prompt=prompt, enable_llm=True, metadata=opMeta.dict())
        medispan_port_result, context = medispan_results_tuple
        medispan_drug:MedispanDrug = medispan_port_result

        return [medispan_drug] if medispan_drug else []



@dispatcher.register(CreateMedication)
@inject()
async def create_medication(command: CreateMedication, uow: IUnitOfWork, query:IQueryPort):
    # TODO: Check if user is allowed to create medication in the given document/page
    # page = await uow.get(Page, command.page_id)

    extra = command.toExtra()

    LOGGER.debug("Medication values: %s", command.values, extra=extra)

    medication:Medication = Medication.create(
        app_id=command.app_id,
        tenant_id=command.tenant_id,
        patient_id=command.patient_id,
        document_id=command.document_id,

        page_id='',  # TODO
        page_number=1,  # TODO
        # page_id=command.page_id,
        # page_number=page.number,

        document_reference=command.document_id,  # Deprecated?

        name=command.values['name'],
        medispan_id=command.values.get("medispan_id"),
        dosage=command.values.get('dosage'),
        route=command.values.get('route'),
        frequency=command.values.get('frequency'),
        start_date=command.values.get('start_date'),
        end_date=command.values.get('end_date'),
        explaination=command.values.get('explaination')
    )
    medication.created_by = command.created_by
    medication.modified_by = command.modified_by
    LOGGER.debug("Persisting Medication %s", medication, extra=extra)
    uow.register_new(medication)

    existing_medication_profile: DocumentMedicationProfile2 = await query.get_document_medication_profile_by_key(medication.generate_key())
    if not existing_medication_profile:
        new_document_medication_profile = DocumentMedicationProfile2.create(app_id=medication.app_id,
                                                                            tenant_id=medication.tenant_id,
                                                                            patient_id=medication.patient_id,
                                                                            document_id=medication.document_id,
                                                                            page_id=medication.page_id,
                                                                            page_number=medication.page_number,
                                                                            document_reference=medication.document_reference,
                                                                            name=command.values['name'],
                                                                            dosage=command.values.get('dosage'),
                                                                            route=command.values.get('route'),
                                                                            frequency=command.values.get('frequency'),
                                                                            start_date=command.values.get('start_date'),
                                                                            end_date=command.values.get('end_date'),
                                                                            explaination=command.values.get('explaination'),
                                                                            medication_status=command.values.get('medication_status'),
                                                                            medication_status_reason=command.values.get('medication_status_reason'),
                                                                            medication_status_reason_explaination=command.values.get('medication_status_reason_explaination'))

        new_document_medication_profile.modified_by = command.modified_by
        new_document_medication_profile.key = medication.generate_key()
        uow.register_new(new_document_medication_profile)
    else:
        existing_medication_profile.update(**command.values)
        existing_medication_profile.key = medication.generate_key()
        uow.register_dirty(existing_medication_profile)

    return medication


@dispatcher.register(UpdateMedication)
@inject()
async def update_medication(command: UpdateMedication, uow: IUnitOfWork,query:IQueryPort):
    extra = command.toExtra()

    fields_to_exclude_in_medication = ['medication_status','medication_status_reason','medication_status_reason_explaination']
    medication_update_values = deepcopy(command.values)
    for field in fields_to_exclude_in_medication:
        if field in medication_update_values.keys():
            medication_update_values.pop(field)
    medication = await uow.get(Medication, command.medication_id)
    medication.update(**medication_update_values)
    medication.modified_by = command.modified_by
    LOGGER.debug("Updating medication to: %s", medication, extra=extra)
    uow.register_dirty(medication)

    existing_medication_profile: DocumentMedicationProfile2 = await query.get_document_medication_profile_by_key(medication.generate_key())
    if not existing_medication_profile:
        new_document_medication_profile = DocumentMedicationProfile2.create(app_id=medication.app_id,
                                                                            tenant_id=medication.tenant_id,
                                                                            patient_id=medication.patient_id,
                                                                            document_id=medication.document_id,
                                                                            page_id=medication.page_id,
                                                                            page_number=medication.page_number,
                                                                            document_reference=medication.document_reference,
                                                                            **command.values)
        new_document_medication_profile.modified_by = command.modified_by
        new_document_medication_profile.key = medication.generate_key()
        LOGGER.debug("Creating medication profile: %s", new_document_medication_profile, extra=extra)
        uow.register_new(new_document_medication_profile)
    else:
        existing_medication_profile.update(**command.values)
        existing_medication_profile.key = medication.generate_key()
        LOGGER.debug("Updating medication profile: %s", existing_medication_profile, extra=extra)
        uow.register_dirty(existing_medication_profile)

    return medication


@dispatcher.register(DeleteMedication)
@inject()
async def delete_medication(command: DeleteMedication, uow: IUnitOfWork):
    medication = await uow.get(Medication, command.medication_id)
    medication.modified_by = command.modified_by
    medication.delete()
    uow.register_dirty(medication)
    return medication


@dispatcher.register(UndeleteMedication)
@inject()
async def undelete_medication(command: UndeleteMedication, uow: IUnitOfWork):
    medication = await uow.get(Medication, command.medication_id)
    medication.undelete()
    medication.modified_by = command.modified_by
    uow.register_dirty(medication)
    return medication

@dispatcher.register(AddUserEnteredMedication)
@inject()
async def add_user_entered_medication(command: UpdateUserEnteredMedication, uow: IUnitOfWork, query:IQueryPort)->UserEnteredMedicationAggregate:
    # create user entered medication record
    extra = command.toExtra()

    user_entered_medication_aggregate:UserEnteredMedicationAggregate = UserEnteredMedicationAggregate.create(app_id=command.app_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                medication=command.medication,
                                                                                medication_status=command.medication_status,
                                                                                created_by=command.created_by,
                                                                                modified_by=command.modified_by,
                                                                                document_id=command.document_id,
                                                                                extracted_medication_references=command.extracted_medication_references
                                                                            )

    LOGGER.debug("Manual Medication to add:  %s", user_entered_medication_aggregate, extra=extra)

    # create or update medication profile with user entered medication
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
    if medication_profile:
        reconcilled_medication = medication_profile.add_user_entered_medication(user_entered_medication_aggregate,edit_type="added")
        uow.register_dirty(medication_profile)
        user_entered_medication_aggregate.medication_profile_reconcilled_medication_id = reconcilled_medication.id
        uow.register_new(user_entered_medication_aggregate)
    else:
        medication_profile:MedicationProfile = MedicationProfile.create(app_id=command.app_id, tenant_id=command.tenant_id, patient_id=command.patient_id)
        reconcilled_medication =  medication_profile.add_user_entered_medication(user_entered_medication_aggregate,edit_type="added")
        uow.register_new(medication_profile)
        user_entered_medication_aggregate.medication_profile_reconcilled_medication_id = reconcilled_medication.id
        uow.register_new(user_entered_medication_aggregate)

    return user_entered_medication_aggregate

@dispatcher.register(UpdateUserEnteredMedication)
@inject()
async def update_user_entered_medication(command: UpdateUserEnteredMedication, uow: IUnitOfWork, query:IQueryPort):
    extra = command.toExtra()

    user_entered_medication_aggregate:UserEnteredMedicationAggregate = UserEnteredMedicationAggregate.create(app_id=command.app_id,
                                                                                medication_profile_reconcilled_medication_id=command.medication_profile_reconcilled_medication_id,
                                                                                tenant_id=command.tenant_id,
                                                                                patient_id=command.patient_id,
                                                                                medication=command.medication,
                                                                                medication_status=command.medication_status,
                                                                                created_by=command.created_by,
                                                                                modified_by=command.modified_by,
                                                                                document_id=command.document_id,
                                                                                extracted_medication_references=command.extracted_medication_references
                                                                            )
    #user_entered_medication_aggregate.update(old_values=None,new_values=command.changed_values)

    LOGGER.debug("Persisting user_entered_medication_aggregate: %s", json.dumps(json.loads(command.json()), indent=2), extra=extra)

    uow.register_new(user_entered_medication_aggregate)

    # create or update medication profile with user entered medication
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)

    reconcilled_medication_record:ReconcilledMedication = medication_profile.get_reconcilled_medication(command.medication_profile_reconcilled_medication_id)
    if reconcilled_medication_record:
        medication:MedicationValue = reconcilled_medication_record.medication
        if reconcilled_medication_record.user_entered_medication:
            medication = reconcilled_medication_record.user_entered_medication.medication
        user_entered_medication_aggregate.change_sets = medication.diff(command.medication)
        #medication_profile.reconcile_user_entered_medication(user_entered_medication_aggregate)
        # update the reconcilled medication record with the new user entered medication
        reconcilled_medication_record.update_user_entered_medication(UserEnteredMedication(
            medication=command.medication,
            medispan_id=command.medication.medispan_id,
            edit_type= "updated",
            change_sets=reconcilled_medication_record.user_entered_medication.change_sets if reconcilled_medication_record.user_entered_medication else [] + [user_entered_medication_aggregate.change_sets],
            medication_status=command.medication_status,
            modified_by=command.modified_by,
            start_date=command.medication.start_date,
            end_date=command.medication.end_date,
            document_id=command.document_id))
        uow.register_dirty(medication_profile)
    else:
        LOGGER.warning("Reconcilled medication record not found for medication_profile_reconcilled_medication_id: %s", command.medication_profile_reconcilled_medication_id, extra=extra)
        medication_profile.add_user_entered_medication(user_entered_medication_aggregate,edit_type="updated")
        uow.register_dirty(medication_profile)

    return user_entered_medication_aggregate

@dispatcher.register(DeleteReconcilledMedication)
@inject()
async def delete_medication(command: DeleteReconcilledMedication, uow: IUnitOfWork, query:IQueryPort):
    user_entered_medication_aggregate:UserEnteredMedicationAggregate = await query.get_user_entered_medication_by_reconcilled_medication_id(command.medication_profile_reconcilled_medication_id)
    if user_entered_medication_aggregate:
        user_entered_medication_aggregate.delete()
        uow.register_dirty(user_entered_medication_aggregate)

    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
    medication_profile.delete_reconcilled_medication(command.medication_profile_reconcilled_medication_id)
    uow.register_dirty(medication_profile)


@dispatcher.register(UnDeleteReconcilledMedication)
@inject()
async def undelete_medication(command: UnDeleteReconcilledMedication, uow: IUnitOfWork, query:IQueryPort):
    user_entered_medication_aggregate:UserEnteredMedicationAggregate = await query.get_user_entered_medication_by_reconcilled_medication_id(command.medication_profile_reconcilled_medication_id)
    if user_entered_medication_aggregate:
        user_entered_medication_aggregate.un_delete()
        uow.register_dirty(user_entered_medication_aggregate)
    medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
    medication_profile.un_delete_reconcilled_medication(command.medication_profile_reconcilled_medication_id)
    uow.register_dirty(medication_profile)

@dispatcher.register(ImportMedications)
@inject()
async def import_medications(command: ImportMedications, uow: IUnitOfWork, query:IQueryPort, external_medication_adapter:IHHHAdapter):

    thisSpanName = "import_medications"
    with await opentelemetry.getSpan(thisSpanName) as span:

        extra = command.toExtra()

        if command.app_id == "hhh":
            LOGGER.debug("Importing medications for hhh patient with command %s", command, extra=extra)
            # import medications
            imported_medications = []
            imported_medications:List[HostMedication] = await external_medication_adapter.get_medications(command.patient_id, command.ehr_token)

            LOGGER.debug("imported medications: %s", imported_medications, extra=extra)

            medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
            LOGGER.debug("medication profile: %s", medication_profile, extra=extra)

            # TODO:  Fix this.  We shouldn't need to create a MedicationProfile synchronously...  The issue was that this function was blowing up the first time the user went
            # to a patient due to an attempt to update a MedProfile which hadn't been created in Firestore yet. Second time to the client, it would work fine.
            if not medication_profile:
                LOGGER.warn("Medication profile does not exist.  Creating synchronously...", extra=extra)
                medication_profile = MedicationProfile.create(app_id=command.app_id, tenant_id=command.tenant_id, patient_id=command.patient_id)
                LOGGER.debug("Creating (sync) medication_profile: %s", medication_profile, extra=extra)
                await uow.create_sync(medication_profile)

            imported_host_medication_ids = []
            results:List[Result] = []
            # create or update medication profile with imported medications
            idx = 0
            for imported_medication in imported_medications:
                imported_medication_agg = ImportedMedicationAggregate.create(app_id=command.app_id,
                                                        tenant_id=command.tenant_id,
                                                        patient_id=command.patient_id,
                                                        medication=imported_medication.medication,
                                                        host_medication_id=imported_medication.host_medication_id,
                                                        medispan_id=imported_medication.medispan_id,
                                                        original_payload=imported_medication.original_payload,
                                                        modified_by=command.modified_by,
                                                        created_by=command.created_by
                                                    )
                imported_host_medication_ids.append(imported_medication_agg.host_medication_id)

                uow.register_new(imported_medication_agg)

                extra2 = {
                    "index": idx,
                }
                extra2.update(extra)
                if medication_profile:
                    LOGGER.debug("Medical profile exists", extra=extra2)
                    result:Result = medication_profile.reconcile_imported_medications(imported_medication_agg)
                    uow.register_dirty(medication_profile)
                else:
                    LOGGER.debug("Medical profile does not exist.  Creating..", extra=extra2)
                    medication_profile:MedicationProfile = MedicationProfile.create(app_id=command.app_id, tenant_id=command.tenant_id, patient_id=command.patient_id)
                    result:Result = medication_profile.reconcile_imported_medications(imported_medication_agg)
                    uow.register_new(medication_profile)
                results.append(result)
                idx += 1
            LOGGER.debug("Pruning removed host medications from medication profile: %s", imported_host_medication_ids, extra=extra)
            medication_profile = await prune_removed_host_medications(medication_profile, imported_host_medication_ids)
            LOGGER.debug("Pruning complete", extra=extra)
            uow.register_dirty(medication_profile)
            return Result(success=True,return_data=results)
        elif command.app_id == "ltc" or command.app_id == "007":
            LOGGER.debug(f"Importing medications for {command.app_id} patient with command %s", command, extra=extra)
            app_config = await query.get_app_config(command.app_id)

            host = app_config.config.integration.base_url
            path = app_config.config.integration.endpoints["list_medications"]
            path = path.format(tenantId=command.tenant_id, patientId=command.patient_id)
            host = f"{host}{path}"
            headers = {}
            if command.ehr_token:
                headers = {
                    "Authorization": f"Bearer {command.ehr_token}",
                }

            extra.update({
                "http_request": {
                    "method": "GET",
                    "url": host,
                    "headers": headers,
                    "body": None
                }
            })
            LOGGER.debug("Importing medications from host: %s", host, extra=extra)

            http_client = HttpRestClient()
            try:
                doc_response = await http_client.resolve(
                    method="GET",
                    url=host,
                    headers=headers,
                    body=None,
                    connection_timeout=5.0,
                    response_timeout=10.0
                )
                extra.update({
                    "http_response": {
                        "status": doc_response.get("status"),
                        "body": doc_response.get("data"),
                        "headers": doc_response.get("headers")
                    }
                })
                if doc_response.get("status") == 404:
                    LOGGER.info("REST call to host to retrieve medications returned a 404.  Setting imported medications to empty list", extra=extra)
                    imported_medications = []
                elif doc_response.get("status") == 200:
                    LOGGER.debug("REST call to host to retrieve medications returned a 200", extra=extra)
                    imported_medications = doc_response.get("data", [])
                else:
                    LOGGER.error("Unexpected status code %s when importing medications", doc_response.get("status"), extra=extra)
                    raise CommandError(f"Unexpected status code {doc_response.get('status')} when importing medications")
            except CommandError as e:
                    raise e
            except Exception as e:
                extra.update({
                    "error": exceptionToMap(e),
                })
                LOGGER.error("Error calling medications API: %s", str(e), extra=extra)
                raise CommandError(f"Error importing medications: {str(e)}")

            medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(command.patient_id)
            LOGGER.debug("medication profile: %s", medication_profile, extra=extra)

            # TODO:  Fix this.  We shouldn't need to create a MedicationProfile synchronously...  The issue was that this function was blowing up the first time the user went
            # to a patient due to an attempt to update a MedProfile which hadn't been created in Firestore yet. Second time to the client, it would work fine.
            if not medication_profile:
                LOGGER.warn("Medication profile does not exist.  Creating synchronously...", extra=extra)
                medication_profile = MedicationProfile.create(app_id=command.app_id, tenant_id=command.tenant_id, patient_id=command.patient_id)
                LOGGER.debug("Creating (sync) medication_profile: %s", medication_profile, extra=extra)
                await uow.create_sync(medication_profile)

            imported_host_medication_ids = []
            results:List[Result] = []
            idx = 0
            for imported_medication in imported_medications:
                imported_medication_agg = ImportedGeneralMedicationAggregate.create(app_id=command.app_id,
                                                        tenant_id=command.tenant_id,
                                                        patient_id=command.patient_id,
                                                        medication=imported_medication,
                                                        host_medication_id=imported_medication.get("id", None),
                                                        catalog_type=app_config.config.meddb_catalog,
                                                        catalog_id=imported_medication.get("catalogId", None),
                                                        medispan_id=imported_medication.get("catalogId", None),
                                                        original_payload=imported_medication,
                                                        modified_by=command.modified_by,
                                                        created_by=command.created_by
                                                    )
                imported_host_medication_ids.append(imported_medication_agg.host_medication_id)

                uow.register_new(imported_medication_agg)

                extra2 = {
                    "index": idx,
                }
                extra2.update(extra)
                if medication_profile:
                    LOGGER.debug("Medical profile exists", extra=extra2)
                    result:Result = medication_profile.reconcile_imported_medications(imported_medication_agg)
                    uow.register_dirty(medication_profile)
                else:
                    LOGGER.debug("Medical profile does not exist.  Creating..", extra=extra2)
                    medication_profile:MedicationProfile = MedicationProfile.create(app_id=command.app_id, tenant_id=command.tenant_id, patient_id=command.patient_id)
                    result:Result = medication_profile.reconcile_imported_medications(imported_medication_agg)
                    uow.register_new(medication_profile)
                results.append(result)
                idx += 1

            LOGGER.debug("Pruning removed host medications from medication profile: %s", imported_host_medication_ids, extra=extra)
            medication_profile = await prune_removed_host_medications(medication_profile, imported_host_medication_ids)
            LOGGER.debug("Pruning complete", extra=extra)
            uow.register_dirty(medication_profile)
            return Result(success=True,return_data=results)

        else:
            LOGGER.info("Bypassing:  App %s is not supported for importing medications", command.app_id, extra=extra)
            return Result(success=True,return_data=[],error_message="App not supported for importing medications")


# Helper function to prune removed host medications from medication profile
async def prune_removed_host_medications(medication_profile: MedicationProfile, imported_host_medication_ids: List[str]):
    if medication_profile and medication_profile.medications:
        filtered_medications = []
        for med in medication_profile.medications:
            if med.imported_medication and med.imported_medication.host_medication_id not in imported_host_medication_ids:
                LOGGER.debug("Med: %s  document_references: %s  len(doc_references): %s", med, med.document_references, len(med.document_references) > 0)
                if med.document_references and len(med.document_references) > 0:
                    # This handles medications that were originally sourced from the host system but linked to at least one document
                    LOGGER.debug("Delinking imported medication %s %s as it is also extracted and linked to documents: %s", med.id, med.medication.name, med.document_references)
                    LOGGER.debug("Medication: %s", med)
                    med.host_medication_sync_status = None
                    med.origin = Origin.EXTRACTED
                    med.imported_medication = None
                    med.deleted = True

                    filtered_medications.append(med)
                else:
                    # This handles medications that were originally sourced from the host system
                    LOGGER.info("Removing medicationId %s '%s' which was originally sourced from the host system", med.imported_medication.host_medication_id, med.medication.name)
                    pass
            elif med.host_medication_sync_status and med.host_medication_sync_status.host_medication_unique_identifier and med.host_medication_sync_status.host_medication_unique_identifier not in imported_host_medication_ids:
                # This handles medications that were originally sourced from the viki either as extracted or user_entered
                LOGGER.debug("Delinking imported medication %s %s as it is also extracted and linked to documents: %s", med.id, med.medication.name, med.document_references)
                LOGGER.debug("Medication: %s", med)
                med.host_medication_sync_status = None
                med.origin = Origin.EXTRACTED
                med.imported_medication = None
                med.deleted = True

                filtered_medications.append(med)
            else:
                filtered_medications.append(med)
        medication_profile.medications = filtered_medications
    return medication_profile

@dispatcher.register(CreateDocumentMedicationProfileCommand)
@inject()
async def create_document_medication_profile(command: CreateDocumentMedicationProfileCommand,  uow: IUnitOfWork):
    extra = command.toExtra()
    key = command.key
    o = command.document_medication_profile
    LOGGER.info("Creating document medication profile for key %s", key, extra=extra)
    ret = await svc.add_document_medication_profile(key, o)
    LOGGER.debug("Document medication profile for key %s created", key, extra=extra)
    return ret


@dispatcher.register(DeleteDocumentMedicationProfileCommand)
@inject()
async def delete_document_medication_profile(command: DeleteDocumentMedicationProfileCommand,  uow: IUnitOfWork):
    extra = command.getExtra()
    key = command.key
    LOGGER.debug("Deleting document medication profile for key %s", key, extra=extra)
    ret =  await svc.delete_document_medication_profile(key)
    LOGGER.debug("Document medication profile for key %s deleted", key, extra=extra)
    return ret

@dispatcher.register(SaveTestResults)
@inject()
async def save_test_results(command: SaveTestResults, uow: IUnitOfWork, query:IQueryPort):
    test_results = command.test_results
    uow.register_new(test_results)

@dispatcher.register(CreateGoldenDatasetTest)
@inject()
async def create_golden_test_data(command: CreateGoldenDatasetTest, uow: IUnitOfWork, query:IQueryPort):
    test_data = command.test_data
    uow.register_new(test_data)

@dispatcher.register(CreateClinicalData)
@inject()
async def create_clinical_data(command: CreateClinicalData, uow: IUnitOfWork, query:IQueryPort):
    extracted_clinical_data:ExtractedClinicalData = ExtractedClinicalData.create(app_id=command.app_id,
                                                                                 tenant_id=command.tenant_id,
                                                                                 patient_id=command.patient_id,
                                                                                 document_id=command.document_id,
                                                                                 document_operation_instance_id=command.document_operation_instance_id,
                                                                                 clinical_data_type=command.clinical_data_type,
                                                                                 clinical_data=command.clinical_data,
                                                                                 page_id=command.page_id,
                                                                                page_number=command.page_number
                                                                                )
    uow.register_new(extracted_clinical_data)

@dispatcher.register(ExtractClinicalData)
@inject()
async def extract_clinical_data(command: ExtractClinicalData, uow: IUnitOfWork, query:IQueryPort, prompt_adapter: IPromptAdapter):
    thisSpanName = "extract_medication"
    start_datetime = now_utc()
    with await opentelemetry.getSpan(thisSpanName) as span:
        span.set_attribute("document_id", command.document_id)
        span.set_attribute("page_number", command.page_number)
        span.set_attribute("page_id", command.page_id)

        extra = command.toExtra()

        try:
            operation_context = {
                "page_id": command.page_id,
                "page_number": command.page_number,
            }
            extracted_clinical_data:ExtractedClinicalData = None
            LOGGER.info('ExtractClinicalData: Extracting %s for documentId %s from %s', command.clinical_data_type, command.document_id, command.labelled_content, extra=extra)

            if not command.labelled_content:

                operation_context['error'] = {"message": 'No labelled content found'}
                doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            start_datetime=start_datetime,
                                                                            step_id= command.step_id,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
                doc_logger = DocumentOperationInstanceLogService()
                #uow.register_new(doc_operation_instance_log)
                await doc_logger.save(doc_operation_instance_log, uow)
                return []

            all_contents = ""
            for content in command.labelled_content:
                all_contents += f'# Document: {command.document_id}, page: {command.page_number}\n'
                all_contents += content + '\n\n'

            opMeta:OperationMeta = OperationMeta(
                type = DocumentOperationType.MEDICATION_EXTRACTION.value,
                step = command.step_id,
                document_id = command.document_id,
                page_number = command.page_number,
                document_operation_def_id = command.document_operation_definition_id,
                document_operation_instance_id = command.document_operation_instance_id,
            )

            LOGGER.debug("ExtractClinicalData: Calling multi modal predict to extract %s for documentId %s", command.clinical_data_type, command.document_id, extra=extra)
            llm_prompt = command.prompt.replace('<content></content>',all_contents)
            operation_context['llm_prompt'] = [llm_prompt]
            result = await prompt_adapter.multi_modal_predict([llm_prompt],model=command.model, metadata=opMeta.dict())
            operation_context['model_response'] = result

            LOGGER.debug("ExtractClinicalData: Cleaning model response for extract %s for documentId %s", command.clinical_data_type, command.document_id, extra=extra)

            result = result.replace('**', '').replace('##', '').replace('```', '').replace('json', '')
            LOGGER.info("ExtractClinicalData: Prompt result: %s", result, extra=extra)

            result = json.loads(result)

            if result and isinstance(result,list):
                LOGGER.info('ExtractClinicalData: Prompt result 2: %s', result, extra=extra)

                extracted_clinical_data:ExtractedClinicalData = ExtractedClinicalData.create(
                                                                        app_id=command.app_id,
                                                                        tenant_id=command.tenant_id,
                                                                        patient_id=command.patient_id,
                                                                        document_id=command.document_id,
                                                                        page_id=command.page_id,
                                                                        page_number=command.page_number,
                                                                        clinical_data_type=command.clinical_data_type,
                                                                        clinical_data=result,
                                                                        document_operation_instance_id=command.document_operation_instance_id
                                                                    )


                extracted_clinical_data.document_operation_instance_id = command.document_operation_instance_id
                uow.register_new(extracted_clinical_data)

            operation_context['extracted_clinical_data'] = result
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra["elapsed_time"] = doc_operation_instance_log.elapsed_time
            LOGGER2.info("Step::%s completed", command.step_id, extra=extra)

            return extracted_clinical_data
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error('ExtractMedication: Error in extracting medications from documentId %s: %s', command.document_id, str(e), extra=extra)
            operation_context["page_number"] = str(command.page_id)
            operation_context['error'] = exceptionToMap(e)
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context = operation_context,
                                                                            page_number=command.page_number,
                                                                            status = DocumentOperationStatus.FAILED,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id)


            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            raise OrchestrationException(f"ExtractMedication: Error in {str(command.step_id)} for documentId {command.document_id}: {str(e)}") from e

@dispatcher.register(ExtractConditionsData)
@inject()
async def extract_conditions_data(command: ExtractConditionsData, uow: IUnitOfWork, query:IQueryPort, prompt_adapter: IPromptAdapter):
    clinical_data_type = PageLabel.CONDITIONS.value
    operation_context = {}
    start_datetime = now_utc()

    with await opentelemetry.getSpan("extract_conditions_data") as span:

        extra= command.toExtra()

        ret = None

        try:
            LOGGER.debug("ExtractConditions: Extracting %s for documentId %s from %s", clinical_data_type, command.document_id,command.page_texts, extra=extra)
            input_fhir, ret = await ConditionsService().extract_conditions(command)

            # try:
            #     data = json.loads(ret)
            #     ret["fhirBundle"] = data
            # except Exception as e:
            #     LOGGER.warning("ExtractConditions: Error in deserializing conditions from documentId %s: %s", command.document_id, str(e))
            #     operation_context["error"] = exceptionToMap(e)
            #     ret["rawFhirBundle"] = ret["fhirBundle"]
            #     del ret["fhirBundle"]

            raw_data = MedicalCodingRawData.create(
                                app_id=command.app_id,
                                tenant_id=command.tenant_id,
                                patient_id=command.patient_id,
                                document_id=command.document_id,
                                document_operation_instance_id=command.document_operation_instance_id,
                                medical_coding_data=ret,
                                input_fhir_data=input_fhir
            )

            uow.register_new(raw_data)

            operation_context['raw_data'] = raw_data
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context=operation_context,
                                                                            page_number=-1,
                                                                            status = DocumentOperationStatus.COMPLETED)
            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)

            extra["elapsed_time"] = doc_operation_instance_log.elapsed_time
            LOGGER2.info("Step::%s completed", command.step_id, extra=extra)

            pass

        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER.error('ExtractMedication: Error in extracting conditions from documentId %s: %s', command.document_id, str(e), extra=extra)
            operation_context['error'] = extra["error"]
            doc_operation_instance_log = DocumentOperationInstanceLog.create(app_id=command.app_id,
                                                                            tenant_id=command.tenant_id,
                                                                            patient_id=command.patient_id,
                                                                            document_id=command.document_id,
                                                                            step_id= command.step_id,
                                                                            start_datetime=start_datetime,
                                                                            context = operation_context,
                                                                            page_number=-1,
                                                                            status = DocumentOperationStatus.FAILED,
                                                                            document_operation_definition_id=command.document_operation_definition_id,
                                                                            document_operation_instance_id=command.document_operation_instance_id)

            doc_logger = DocumentOperationInstanceLogService()
            #uow.register_new(doc_operation_instance_log)
            await doc_logger.save(doc_operation_instance_log, uow)
            #raise OrchestrationException(f"ExtractMedication: Error in {str(command.step_id)} for documentId {command.document_id}: {str(traceback.format_exc())}") from e

        return ret



@dispatcher.register(CreateorUpdatePageOperation)
@change_tracker_updates(name="create_or_update_page_operation")
@inject()
async def create_or_update_page_operation(command: CreateorUpdatePageOperation, uow: IUnitOfWork, query:IQueryPort):

    page_operation:PageOperation = PageOperation.create(app_id=command.app_id,
                            tenant_id=command.tenant_id,
                            patient_id=command.patient_id,
                            document_id=command.document_id,
                            extraction_type=command.extraction_type,
                            extraction_status=command.extraction_status,
                            page_id=command.page_id,
                            page_number=command.page_number,
                            document_operation_instance_id=command.document_operation_instance_id,
                            created_by=command.created_by,
                            modified_by=command.modified_by)
    uow.register_new(page_operation)


@dispatcher.register(CheckForAllPageOperationExtractionCompletion)
@change_tracker_updates(name="page_operation_completed")
@inject()
async def page_operation_completed(command: CheckForAllPageOperationExtractionCompletion, uow: IUnitOfWork, query:IQueryPort):
    operation_context = {}

    extra = command.toExtra()

    try:
        async def calculate_elapsed_time(doc_operation_instance_id, doc_operation_instance):
            if not doc_operation_instance:
                doc_operation_instance = await query.get_document_operation_instance_by_id(doc_operation_instance_id)
            if doc_operation_instance:
                return (now_utc() - doc_operation_instance.created_at).total_seconds()
            else:
                return -1

        page_operations_medications:List[PageOperation] = []
        completed_extraction_page_operations:List[PageOperation] = []
        failed_extraction_page_operations:List[PageOperation]= []
        in_progress_extraction_page_operations:List[PageOperation] = []

        document:Document = Document(**await query.get_document(command.document_id))
        config:Configuration = await get_config(command.app_id,command.tenant_id)
        page_operations_medications = await query.get_all_page_operations(command.document_id,command.document_operation_instance_id,PageLabel.MEDICATIONS)

        completed_extraction_page_operations = [x for x in page_operations_medications
                                                if x.extraction_status == PageOperationStatus.COMPLETED]

        failed_extraction_page_operations = [x for x in page_operations_medications
                                                if x.extraction_status == PageOperationStatus.FAILED]

        in_progress_extraction_page_operations = [x for x in page_operations_medications
                                                    if x.extraction_status == PageOperationStatus.IN_PROGRESS
                                                ]

        queued_extraction_page_operations = [x for x in page_operations_medications
                                                if x.extraction_status == PageOperationStatus.QUEUED
                                            ]

        if failed_extraction_page_operations and len(completed_extraction_page_operations+failed_extraction_page_operations) == len(document.pages):

            extra2 = {
                "failed_page_operations": [x.dict() for x in failed_extraction_page_operations],
                "completed_extraction_page_operations": [x.dict() for x in completed_extraction_page_operations],
                "in_progress_extraction_page_operations": [x.dict() for x in in_progress_extraction_page_operations],
                "queued_extraction_page_operations": [x.dict() for x in queued_extraction_page_operations]
            }
            extra2.update(extra)

            LOGGER2.error("Some page operations failed for document %s", command.document_id, extra=extra2)
            document_operation_instance:DocumentOperationInstance = await update_document_operation_instance(
                UpdateDocumentOperationInstance(
                                                app_id=command.app_id,
                                                tenant_id=command.tenant_id,
                                                patient_id=command.patient_id,
                                                document_id=command.document_id,
                                                id=command.document_operation_instance_id,
                                                status=DocumentOperationStatus.FAILED),uow)
            await create_document_operation(CreateOrUpdateDocumentOperation(
                app_id=command.app_id,
                tenant_id=command.tenant_id,
                patient_id=command.patient_id,
                document_id=command.document_id,
                active_document_operation_instance_id=command.document_operation_instance_id,
                active_document_operation_definition_id=command.document_operation_definition_id,
                created_by=command.created_by,
                modified_by=command.modified_by,
                status=DocumentOperationStatus.FAILED
            ),uow, query)
            elasped_time = await calculate_elapsed_time(command.document_operation_instance_id,document_operation_instance)
            extra.update({
                "elapsed_time": elasped_time,
                "priority": document_operation_instance.priority
            })

            #LOGGER2.info("Orchestration failed", extra=extra)  # Turning off here as this is handled by recover() in orchestrator now
            return

        if page_operations_medications and len(completed_extraction_page_operations) == len(page_operations_medications) and len(completed_extraction_page_operations) == len(document.pages):
            # all page completed operations
            if config and config.extract_conditions:
                from paperglass.usecases.orchestrator import ConditionExtractionAgent
                await ConditionExtractionAgent().orchestrate(
                    document_id=document.id,
                    document_operation_definition_id=command.document_operation_definition_id,
                    document_operation_instance_id=command.document_operation_instance_id
                )
            LOGGER.info("All page operations completed for document %s", command.document_id, extra=extra)
            document_operation_instance:DocumentOperationInstance = await update_document_operation_instance(
                UpdateDocumentOperationInstance(
                                                app_id=command.app_id,
                                                tenant_id=command.tenant_id,
                                                patient_id=command.patient_id,
                                                document_id=command.document_id,
                                                id=command.document_operation_instance_id,
                                                status=DocumentOperationStatus.COMPLETED),uow)
            await create_document_operation(CreateOrUpdateDocumentOperation(
                app_id=command.app_id,
                tenant_id=command.tenant_id,
                patient_id=command.patient_id,
                document_id=command.document_id,
                active_document_operation_instance_id=command.document_operation_instance_id,
                active_document_operation_definition_id=command.document_operation_definition_id,
                created_by=command.created_by,
                modified_by=command.modified_by,
                status = DocumentOperationStatus.COMPLETED
            ),uow, query)
            elasped_time = await calculate_elapsed_time(command.document_operation_instance_id,document_operation_instance)
            extra.update({
                "elapsed_time": elasped_time,
                "priority": document_operation_instance.priority
            })
            LOGGER2.info("Orchestration success", extra=extra)

        if len(failed_extraction_page_operations) > 0:
            # some page operations failed
            extra2 = {
                "failed": [x.dict() for x in failed_extraction_page_operations]
            }
            extra2.update(extra)
            LOGGER.error("Some page operations failed for document %s", command.document_id, extra=extra2)

        if len(in_progress_extraction_page_operations) > 0:
            # some page operations are still in progress
            LOGGER.info("Some page operations are still in progress for document %s", command.document_id, extra=extra)
    except Exception as e:
        operation_context["error"] = exceptionToMap(e)
        raise OrchestrationExceptionWithContext(f"Error in checking for all page operation extraction completion: {str(e)}", operation_context)

@dispatcher.register(QueueE2ETest)
@inject
async def queue_e2e_test(command: QueueE2ETest, uow: IUnitOfWork):
    extra = command.toExtra()
    try:
        LOGGER.debug("Deferred command to run e2e test asynchronously", extra=extra)
        app_id = E2E_OWNER_GOLDEN_REPO_APP_ID
        tenant_id = E2E_OWNER_GOLDEN_REPO_TENANT_ID
        patient_id = E2E_OWNER_GOLDEN_REPO_PATIENT_ID
        run_id = get_uuid4()
        command = RunE2ETest(
                app_id=app_id,
                tenant_id=tenant_id,
                patient_id=patient_id,
                mode=command.mode,
                sample_size=command.sample_size,
                filename=command.filename,
                run_id=run_id
            )

        await queue_command(command, uow)

        return {
            "run_id": run_id
        }

    except Exception as e:
        LOGGER.error("Error queueing e2e test: %s", str(e), extra=extra)
        raise e

@dispatcher.register(RunE2ETest)
@inject()
async def run_e2e_test(command: RunE2ETest, uow: IUnitOfWork):
    extra = command.toExtra()
    try:
        LOGGER.debug("Running e2e test command: %s", command)
        LOGGER.debug("CommandHandler: Running e2e test", extra=extra)
        harness = TestHarness()
        ret = await harness.run(mode=command.mode, sample_size=command.sample_size, filename=command.filename, run_id=command.run_id)

        return {
            "run_id": command.run_id
        }
    except Exception as e:
        LOGGER.error("CommandHandler: Error running e2e test: %s", str(e), extra=extra)
        raise e


@dispatcher.register(CreateE2ETestCaseSummaryResults)
@inject
async def create_e2e_testcase_summary_results(command: CreateE2ETestCaseSummaryResults, uow: IUnitOfWork):
    LOGGER.debug("CommandHandler: Creating e2e test case summary results: %s", command)
    uow.register_new(command.summary_testcase_results)


@dispatcher.register(AssessTestCaseResults)
@inject
async def assess_test_case_results(command: AssessTestCaseResults, uow: IUnitOfWork, query:IQueryPort):
    LOGGER.debug("CommandHandler: Assessing test case results: %s", command)

    harness = TestHarness()

    testcase = await query.get_testcase_by_id(command.testcase_id)

    assessment = await query.get_testcase_results_details_by_testcase_and_runid(run_id=command.run_id, testcase_id=command.testcase_id)
    existing_assessment_id = assessment.id if assessment else None

    assessment = await harness.assess_testcase(mode=command.mode,
                                            run_id=command.run_id,
                                            testcase=testcase,
                                            document=command.document,
                                            test_startdate=command.start_date)


    if not existing_assessment_id:
        LOGGER.debug("Assessment for runid %s and testcase %s not found.  Creating new assessment", command.run_id, command.testcase_id)
        uow.register_new(assessment)
    else:
        LOGGER.debug("Assessment for runid %s and testcase %s found.  Updating existing assessment", command.run_id, command.testcase_id)
        assessment.id = existing_assessment_id
        uow.register_dirty(assessment)

    if command.is_assess_summary:
        LOGGER.debug("Assessing summary results for runid %s", command.run_id)
        assess_summary_command = AssessTestCaseSummaryResults(run_id=command.run_id)
        await create_command(assess_summary_command, uow)
    else:
        LOGGER.debug("Not assessing summary results for runid %s", command.run_id)

    #LOGGER.debug("CommandHandler: Test case results assessed: %s", assessment)


@dispatcher.register(ReassessTestCaseSummaryResults)
@inject
async def reassess_test_case_summary_results(command: ReassessTestCaseSummaryResults, uow: IUnitOfWork, query:IQueryPort):
    summary_results = await query.get_testcase_results_summary_by_runid(command.run_id)
    summary:E2ETestCaseSummaryResults = summary_results[0] if summary_results else None

    documents = await query.list_documents_in_test_run(command.run_id)

    for document in documents:
        testcase_assess_command = AssessTestCaseResults(mode=document.metadata.get("e2e_test", {}).get("mode"),
                              run_id=command.run_id,
                              testcase_id=document.metadata.get("e2e_test", {}).get("testcase_id"),
                              document=document,
                              start_date=document.metadata.get("e2e_test", {}).get("test_startdate"),
                              is_assess_summary=False
                              )

        await assess_test_case_results(testcase_assess_command, uow, query)

    summary_command = AssessTestCaseSummaryResults(run_id=command.run_id)

    results = await assess_test_case_summary_results(summary_command, uow, query)

    return results



# @dispatcher.register(ReassessTestCaseSummaryResults)
# @inject
# async def reassess_test_case_summary_results(command: ReassessTestCaseSummaryResults, uow: IUnitOfWork, query:IQueryPort):
#     results = await query.get_testcase_results_summary_by_runid(command.run_id)
#     summary:E2ETestCaseSummaryResults = results[0] if results else None

#     documents = await query.get_documents_by_runid(command.run_id)

#     for document in documents:
#         AssessTestCaseResults(mode=document.metadata.get("mode"),
#                               run_id=command.run_id,
#                               testcase_id=document.metadata.get("testcase_id"),
#                               document=document,
#                               start_date=document.metadata.get("test_startdate")
#                               )
#     if summary:
#         for testcase in summary.test_cases:
#             assessment = await query.get_testcase_results_details_by_testcase_and_runid(run_id=command.run_id, testcase_id=testcase.id)
#             existing_assessment_id = assessment.id if assessment else None







@dispatcher.register(AssessTestCaseSummaryResults)
@inject
async def assess_test_case_summary_results(command: AssessTestCaseSummaryResults, uow: IUnitOfWork, query:IQueryPort):
    LOGGER.debug("CommandHandler: Assessing test case summary results: %s", command)
    harness = TestHarness()
    try:
        summary_results:E2ETestCaseSummaryResults = await harness.assess_summary(run_id=command.run_id, uow=uow, query=query)

        await harness.persist_summary(summary_results) # Persists to GCS

        # Remove all results as it will likely exceed Firestore size limit and they are stored separately
        if summary_results.status == DocumentOperationStatus.COMPLETED:
            summary_results.results = None
            uow.register_dirty(summary_results)

            extra ={
                "mode": summary_results.mode,
                "run_id": summary_results.run_id,
                "test_startdate": summary_results.test_startdate,
                "summary": summary_results.summary,
            }
            Metric.send("E2E::TestHarness::complete", tags=extra)
        else:
            LOGGER.debug("CommandHandler: Test case summary results assessed but test run is not yet complete: %s", command.run_id, extra={"summary_results": summary_results.dict()})

        return summary_results

    except NotFoundException as e:
        extra = command.toExtra()
        extra.update({
            "error": exceptionToMap(e)
        })
        # End of the line. If there is no summary for this runid, running this again won't help
        LOGGER.error("CommandHandler: Test case summary results not found: %s", command.run_id, extra=extra)


@dispatcher.register(CreateTestCaseFromDocument)
@inject
async def create_test_case_from_document(command: CreateTestCaseFromDocument, uow: IUnitOfWork, query: IQueryPort):
    GOLDEN_DATASET_CATEGORY = "golden dataset"
    doc = await query.get_document(command.document_id)
    document: Document = Document(**doc)

    orig_doc_metadata = document.metadata or {}
    orig_doc_metadata["golden_data"] = True
    document.metadata = orig_doc_metadata

    LOGGER.debug("Creating test case from document: %s", document)

    documentExpectations = E2ETestDocumentExpections(
        elapsed_time = E2E_TEST_MAX_DURATION_SECONDS
    )

    existing_testcase = None
    try:
        LOGGER.debug("Checking if test case already exists for document: %s", document.file_name)
        existing_testcase = await query.get_testcase_by_document_id(document.id)
        LOGGER.debug("Existing test case: %s", existing_testcase)
        if existing_testcase:
            if E2E_TEST_UPDATE_ENABLE:
                LOGGER.debug("Test case already exists for document: %s.  Updating existing test case", document.file_name)
            else:
                raise Exception("Test case already exists for this document")
    except NotFoundException as e:
        # This is an expected condition that the target document doesn't have a test case already
        LOGGER.debug("Test case does not exist for document: %s  Ok to create a test case", document.file_name)

    page_expectations = {}
    for i in range(document.page_count):
        page_number = i + 1

        #Retrieve medications for this page
        medications = await list_medications(command.document_id, page_number)

        LOGGER.debug("Medications for page %s: %s", page_number, len(medications))

        medispan_ids = []
        medispan_matched_count = 0
        unlisted_count = 0
        for medication in medications:
            medispan_id = medication.medispan_id
            if medispan_id:
                medispan_ids.append(medispan_id)
                medispan_matched_count += 1
            else:
                unlisted_count += 1

            page_expectations[page_number] = E2ETestPageExpections(
                total_count = len(medications),
                list_of_medispan_ids = medispan_ids,
                medispan_matched_count = medispan_matched_count,
                unlisted_count = unlisted_count,
                medication = medications
            )

    testcase: E2ETestCase = E2ETestCase(
        id=get_uuid4(),
        category=GOLDEN_DATASET_CATEGORY,
        test_document_id=document.id,
        test_document_name=document.file_name,
        document_expectations=documentExpectations,
        page_expections=page_expectations
    )

    LOGGER.debug("Test case: %s", testcase)

    # Update document metadata that this is golden data
    uow.register_dirty(document)

    if existing_testcase and E2E_TEST_UPDATE_ENABLE:
        LOGGER.debug("Deleting existing test case: %s", existing_testcase)
        existing_testcase.active = False
        uow.register_removed(existing_testcase)

        archived_testcase = E2ETestCaseArchive(**existing_testcase.dict())
        uow.register_new(archived_testcase)


    uow.register_new(testcase)

    return testcase

@dispatcher.register(ConfirmE2ETest)
@inject
async def confirm_e2e_test(command: ConfirmE2ETest, uow: IUnitOfWork):
    from paperglass.entrypoints.test_orchestration_cli import confirm_test_results
    extra = command.toExtra()
    extra.update({
        "document_id": command.document_id
    })
    try:
        ret = await confirm_test_results(document_id=command.document_id)
        return ret
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e)
        })
        LOGGER.error("Error confirming e2e test for document_id %s: %s", command.document_id, str(e), extra=extra)
        raise e

@dispatcher.register(LoadTestPoke)
@inject()
async def load_test_poke(command: LoadTestPoke, uow: IUnitOfWork):

    loadTestAgent = None
    if command.loadtest_type == "vertex-ai":
        loadTestAgent = VertexAILoadTestAgent(get_document_logs)
    elif command.loadtest_type == "default":
        loadTestAgent = E2ELoadTestAgent(create_document)
    else:
        LOGGER.error("Load test type not supported: %s", command.loadtest_type, extra=command.toExtra())
        raise Exception(f"Load test type not supported: {command.loadtest_type}")

    await loadTestAgent.run(command, uow)


@dispatcher.register(CreateOrUpdateEntityRetryConfiguration)
@change_tracker_updates(name="update_document_entity_retry_config")
@inject()
async def update_document_entity_retry_config(command: CreateOrUpdateEntityRetryConfiguration, uow: IUnitOfWork, query:IQueryPort):
    entity_retry_config:EntityRetryConfig = None
    entity_retry_config = await query.get_entity_retry_config(command.retry_entity_id,command.retry_entity_type)

    if entity_retry_config:
        entity_retry_config.retry_count = command.retry_count+1
        uow.register_dirty(entity_retry_config)
    else:
        entity_retry_config = EntityRetryConfig.create(
            app_id=command.app_id,
            tenant_id=command.tenant_id,
            patient_id=command.patient_id,
            retry_entity_id=command.retry_entity_id,
            retry_entity_type=command.retry_entity_type,
            retry_count=command.retry_count+1,
            document_id=command.document_id,
            document_operation_instance_id=command.document_operation_instance_id,
        )
        uow.register_new(entity_retry_config)
    return entity_retry_config

class CommandHandlingUseCase(ICommandHandlingPort):
    @inject()
    async def handle_command(self, command: Command, uowm: IUnitOfWorkManagerPort):
        extra = command.toExtra()
        try:
            Context().extractCommand(command)
            async with uowm.start() as uow:
                extra.update(labels(command_type=command.type))
                LOGGER.debug('Received command %s', type(command), extra=extra) # Changed this to only output the type of command as some commands have binary data being injected into the logs
                if not await uow.start_command_processing(command):
                    LOGGER.error('Command already processed, command=%s', command, extra=extra)
                    return
                result = await dispatcher(command, uow)
                uow.finish_command_processing(command)
                return result
        except Exception as e:  #ToDo: fid the actual ExceptionType for cross transaction error
            extra.update({
                "error": exceptionToMap(e),
                "command_type": type(command).__name__,
                "command": str(command)
            })
            LOGGER.error('Error processing command %s: %s', type(command), str(e), extra=extra)
            if command.cross_transaction_error_strict_mode:
                raise e
            else:
                LOGGER.error('Ignore error %s: %s', type(command), str(e), extra=extra)
                return


    async def commit(self, command, changes:ChangeTracker, uowm: IUnitOfWorkManagerPort):
        with await opentelemetry.getSpan(f"firestore_commit:{changes.name}") as span:
            span.set_attribute("operation_name", changes.name)
            extra = command.toExtra()
            async with uowm.start() as uow:
                uow.set_context({"command": command.__class__.__name__})
                if not await uow.start_command_processing(command):
                    LOGGER.error('Command already processed, command=%s', command, extra=extra)
                    return False
                span.set_attribute("entity_count", len(changes.entities) if changes.entities else 0)
                for change in changes.entities:
                    change:ChangedEntity = change
                    if change.value:
                        span.set_attribute("entity_type", change.value.__class__.__name__)
                        span.set_attribute("entity_id", change.value.id)
                        if change.is_new:
                            uow.register_new(change.value)
                        if change.is_dirty:
                            uow.register_dirty(change.value)
                        if change.is_removed:
                            uow.register_removed(change.value)
                    else:
                        LOGGER.error("Entity not found for change %s", change, extra=extra)
                for sub_command in changes.commands:
                    await create_command(sub_command, uow)

                uow.finish_command_processing(command)
                return True

    @inject()
    async def handle_command_with_explicit_transaction(self, command: Command, uowm: IUnitOfWorkManagerPort):
        try:
            Context().extractCommand(command)

            changes:ChangeTracker = ChangeTracker()
            result = await dispatcher(command,changes)

            success= await self.commit(command, changes, uowm)
            if success:
                return result
            return
        except Exception as e:  #ToDo: fid the actual ExceptionType for cross transaction error
            command_name = command.__class__.__name__
            extra = command.toExtra()

            if isinstance(e, OrchestrationExceptionWithContext) and e.context:
                extra.update(e.context)

            extra["error"] = exceptionToMap(e)

            LOGGER2.error('Error processing command %s: %s', command_name, str(e), extra=extra)

            if command.cross_transaction_error_strict_mode:
                raise e
            else:
                LOGGER2.error('ignore error %s: %s', command_name, str(e), extra=extra)
                return


@dispatcher.register(CreateTestDocument)
@inject()
async def create_doc_handler(command: CreateTestDocument, uow: IUnitOfWork, storage: IStoragePort, query:IQueryPort):
    from paperglass.usecases.documents import create_document

    filename = command.name
    if filename is None:
        LOGGER.debug("No filename provided.  Generating one...", extra=command.toExtra())
        filename = f"e2e-test-{now_utc().strftime('%Y%m%d-%H%M%S')}.pdf"
    else:
        LOGGER.debug("Filename provided: %s", filename, extra=command.toExtra())

    document = await create_document(app_id=command.app_id,tenant_id=command.tenant_id,patient_id=command.patient_id,
                                        file_name=filename,
                                        uploaded_bytes= await storage.get_external_document_raw(command.storage_uri),token=command.token,
                                        priority=OrchestrationPriority.DEFAULT,
                                        storage=storage,
                                        metadata=command.metadata)
    document.source_storage_uri=command.storage_uri
    document.source="app"
    LOGGER.debug("Test Document created: %s", document, extra=command.toExtra())
    uow.register_new(document)
    return document


@dispatcher.register(CreateEntitySchema)
@inject()
async def create_entity_schema(command: CreateEntitySchema, uow: IUnitOfWork, query: IQueryPort):
    """Handler for CreateEntitySchema command that persists EntitySchema to Firestore."""
    from paperglass.domain.model_entities import EntitySchemaAggregate
    
    extra = command.toExtra()
    
    try:
        # Create EntitySchemaAggregate object from the dictionary
        entity_schema = EntitySchemaAggregate.create_from_dict(command.entity_schema_dict)
        
        LOGGER.info("Creating entity schema with ID: %s", entity_schema.schema_id, extra=extra)
        
        # TODO: Add check for existing schema once get_entity_schema_by_id is implemented
        # For now, we'll allow creation without checking for duplicates
        
        # Persist the entity schema to Firestore via the "entity_schema" collection
        uow.register_new(entity_schema)
        
        LOGGER.info("Successfully registered entity schema for persistence: %s", entity_schema.schema_id, extra=extra)
        
        # Return a simple dict instead of the domain object
        return {
            "id": entity_schema.id,
            "schema_id": entity_schema.schema_id,
            "title": entity_schema.title,
            "app_id": entity_schema.app_id,
            "success": True
        }
        
    except Exception as e:
        error_message = str(e) if str(e) else f"Unknown error of type {type(e).__name__}"
        extra["error"] = exceptionToMap(e)
        LOGGER.error("Error creating entity schema: %s", error_message, extra=extra)
        raise CommandError(f"Failed to create entity schema: {error_message}") from e


@dispatcher.register(DeleteEntitySchema)
@inject()
async def delete_entity_schema(command: DeleteEntitySchema, uow: IUnitOfWork, query: IQueryPort):
    """Handler for DeleteEntitySchema command that soft-deletes EntitySchema in Firestore."""
    from paperglass.domain.model_entities import EntitySchemaAggregate
    from paperglass.domain.utils.exception_utils import exceptionToMap
    
    extra = command.toExtra()
    
    try:
        # Find the entity schema by schema_id
        entity_schema = await query.get_entity_schema_by_id(command.schema_id)
        
        if not entity_schema:
            raise ValueError(f"Entity schema with schema_id '{command.schema_id}' not found")
        
        LOGGER.info("Deleting entity schema with ID: %s", entity_schema.schema_id, extra=extra)
        
        # Soft delete by setting active to False
        entity_schema.active = False
        entity_schema.modified_at = now_utc()
        
        # Register for update
        uow.register_dirty(entity_schema)
        
        LOGGER.info("Successfully marked entity schema for deletion: %s", entity_schema.schema_id, extra=extra)
        
        # Return a simple dict instead of the domain object
        return {
            "id": entity_schema.id,
            "schema_id": entity_schema.schema_id,
            "title": entity_schema.title,
            "app_id": entity_schema.app_id,
            "success": True,
            "deleted": True
        }
        
    except Exception as e:
        error_message = str(e) if str(e) else f"Unknown error of type {type(e).__name__}"
        extra["error"] = exceptionToMap(e)
        LOGGER.error("Error deleting entity schema: %s", error_message, extra=extra)
        raise CommandError(f"Failed to delete entity schema: {error_message}") from e


@dispatcher.register(ImportEntities)
@inject()
async def import_entities_handler(command: ImportEntities, uow: IUnitOfWork):
    """Handler for ImportEntities command that processes EntityWrapper and saves entities to Firestore."""
    from paperglass.usecases.entities import import_entities
    
    extra = command.toExtra()
    
    try:
        LOGGER.info("Processing ImportEntities command", extra=extra)
        
        # Call the business logic function
        result = await import_entities(command.entity_wrapper, uow)
        
        LOGGER.info("ImportEntities command completed successfully", extra=extra)
        
        return result
        
    except Exception as e:
        error_message = str(e) if str(e) else f"Unknown error of type {type(e).__name__}"
        extra["error"] = exceptionToMap(e)
        LOGGER.error("Error importing entities: %s", error_message, extra=extra)
        raise CommandError(f"Failed to import entities: {error_message}") from e


@dispatcher.register(CreateEntityTOC)
@inject()
async def create_entity_toc_handler(command: CreateEntityTOC, uow: IUnitOfWork):
    """Handler for CreateEntityTOC command that creates a DocumentEntityTOC from entity counts."""
    
    extra = command.toExtra()
    
    try:
        LOGGER.info("Creating entity TOC for document %s with run_id %s", command.document_id, command.run_id, extra=extra)
        
        # Determine which factory method to use based on the command data
        if command.page_entity_counts:
            # Create with page-level entity counts
            entity_toc = DocumentEntityTOC.create_with_page_counts(
                app_id=command.app_id,
                tenant_id=command.tenant_id,
                patient_id=command.patient_id,
                document_id=command.document_id,
                run_id=command.run_id,
                page_entity_counts=command.page_entity_counts,
                schema_uri_map=command.schema_uri_map
            )
            LOGGER.info("Created entity TOC with page-level counts for %d pages", 
                       len(command.page_entity_counts), extra=extra)
        elif command.entity_counts:
            # Create with document-level entity counts
            entity_toc = DocumentEntityTOC.create(
                app_id=command.app_id,
                tenant_id=command.tenant_id,
                patient_id=command.patient_id,
                document_id=command.document_id,
                run_id=command.run_id,
                entity_counts=command.entity_counts,
                schema_uri_map=command.schema_uri_map
            )
            LOGGER.info("Created entity TOC with document-level counts", extra=extra)
        else:
            # Create empty TOC if no counts provided
            entity_toc = DocumentEntityTOC(
                id=uuid1().hex,
                app_id=command.app_id,
                tenant_id=command.tenant_id,
                patient_id=command.patient_id,
                document_id=command.document_id,
                run_id=command.run_id,
                entries=[]
            )
            LOGGER.info("Created empty entity TOC (no counts provided)", extra=extra)
        
        # Register for persistence
        uow.register_new(entity_toc)
        
        LOGGER.info("Successfully created entity TOC with %d entries for document %s", 
                   len(entity_toc.entries), command.document_id, extra=extra)
        
        return entity_toc
        
    except Exception as e:
        error_message = str(e) if str(e) else f"Unknown error of type {type(e).__name__}"
        extra["error"] = exceptionToMap(e)
        LOGGER.error("Error creating entity TOC: %s", error_message, extra=extra)
        raise CommandError(f"Failed to create entity TOC: {error_message}") from e


@dispatcher.register(ProcessOnboardingWizard)
@inject()
async def process_onboarding_wizard(command: ProcessOnboardingWizard, uow: IUnitOfWork, storage: IStoragePort, cloud_task: ICloudTaskPort):
    """Handler for ProcessOnboardingWizard command that processes onboarding wizard requests."""
    from paperglass.usecases.onboarding_wizard import OnboardingWizardService
    service = OnboardingWizardService(storage, cloud_task)
    return await service.process_onboarding_wizard(command, uow)


async def _send_status_callback_if_configured(command: DocumentStateChange, query: IQueryPort):
    """Send status callback if configured in integration settings."""
    from datetime import datetime, timezone
    from paperglass.domain.utils.exception_utils import exceptionToMap

    extra = command.toExtra()

    try:
        # Get app configuration
        config: Configuration = await get_config(command.app_id, command.tenant_id, query)

        # Check for integration override in document metadata
        integration_config = config.integration
        if command.document.metadata and "integration" in command.document.metadata:
            LOGGER.debug("Found integration override in document metadata", extra=extra)
            integration_config = _apply_integration_override(
                config.integration,
                command.document.metadata["integration"]
            )

        # Check if status callback is configured
        callback_config = integration_config.callback
        if not callback_config.enabled or not callback_config.status_callback:
            LOGGER.debug("Status callback not configured or disabled", extra=extra)
            return

        # Prepare callback payload
        callback_payload = {
            "document_id": command.document.source_id,
            "status": command.status.value,
            "operation_type": command.operation_type.value if command.operation_type else None,
            "app_id": command.app_id,
            "tenant_id": command.tenant_id,
            "patient_id": command.patient_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        LOGGER.info("Sending status callback", extra={
            **extra,
            "callback_url": callback_config.status_callback,
            "callback_payload": callback_payload
        })

        # Send callback using existing callback infrastructure
        from paperglass.usecases.callback_invoker import CallbackInvoker
        callback_invoker = CallbackInvoker()

        success = await callback_invoker._send_direct_request(
            callback_url=callback_config.status_callback,
            payload=callback_payload,
            callback_config=integration_config.callback,
            extra=extra
        )

        if success:
            LOGGER.info("Status callback sent successfully", extra=extra)
        else:
            LOGGER.warning("Status callback failed", extra=extra)

    except Exception as e:
        LOGGER.error("Error sending status callback", extra={
            **extra,
            "error": exceptionToMap(e)
        })


def _apply_integration_override(base_config, override_data):
    """Apply integration configuration overrides from document metadata"""
    # Handle case where base_config is None
    if base_config is None:
        # If base_config is None, we need at least base_url from override_data
        if "base_url" not in override_data:
            return None
        config_dict = {"base_url": override_data["base_url"]}
    else:
        # Create a copy of base config
        config_dict = base_config.dict() if hasattr(base_config, 'dict') else base_config
        if config_dict is None:
            config_dict = {}

    # Apply overrides
    if "callback" in override_data:
        if "callback" not in config_dict:
            config_dict["callback"] = {}
        config_dict["callback"].update(override_data["callback"])

    # Apply other overrides
    for key, value in override_data.items():
        if key != "callback":  # callback is handled specially above
            config_dict[key] = value

    # Return updated configuration object
    from paperglass.domain.values import IntegrationConfiguration
    return IntegrationConfiguration(**config_dict)


