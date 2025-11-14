from difflib import SequenceMatcher
import json
import os
from typing import List
from json import loads
from datetime import datetime, timedelta, timezone
import asyncio

from paperglass.domain.time import now_utc
from paperglass.domain.util_json import JsonUtil
from paperglass.domain.string_utils import to_int, to_float
from paperglass.domain.utils.token_utils import mktoken2
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.usecases.conditions import ConditionsService
from paperglass.usecases.clinical_data import get_extracted_clinical_data
from paperglass.usecases.configuration import get_config
from paperglass.settings import (
    STAGE,
    GCP_PROJECT_ID,
    SETTINGS_MAP,
    APPLICATION_INTEGRATION_TRIGGER_ID,
    CLOUD_TASK_QUEUE_NAME,
    INTEGRATION_PROJECT_NAME,
    SELF_API,
    SERVICE_ACCOUNT_EMAIL,
    MEDICATION_EVIDENCE_MATCH_TOKEN_SIZE_THRESHOLD,
    E2E_TEST_ENABLE,
    E2E_TEST_ASSERTION_F1_GOOD_LOWER,
    E2E_TEST_TLDR_RESULTS_WINDOW_MINUTES,
)
from paperglass.usecases.documents import get_documents
from paperglass.interface.utils import decode_token, verify_okta, verify_service_okta, verify_gcp_service_account
from paperglass.interface.security import require_any_auth, require_service_auth, require_user_auth
from pydantic import BaseModel, ValidationError
from pydantic import parse_obj_as
import pydantic
from kink import inject
from logging import getLogger
import traceback
from aiohttp import ClientConnectorError
import time

from ...log import CustomLogger

LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from ...settings import EXTRACTION_PUBSUB_TOPIC_NAME, STAGE

from ...domain.util_json import DateTimeEncoder, JsonUtil
from paperglass.domain.utils.uuid_utils import get_uuid4

from ...domain.values import (
    AnnotationToken,
    Configuration,
    DocumentOperationStatus,
    DocumentSettings,
    ExtractedMedicationReference,
    HostAttachment,
    LLMModel,
    MedicationPageProfile,
    MedicationStatus,
    MedicationValue,
    OCRType,
    ReconcilledMedication,
    ResolvedReconcilledMedication,
    Result,
    UserEnteredMedication,
    DocumentOperationType,
    OrchestrationPriority,
)

from paperglass.domain.values_http import (
    GenericExternalDocumentCreateEventRequestBase,
    GenericExternalDocumentCreateEventRequestApi,
    GenericExternalDocumentCreateEventRequestUri,
    ExternalDocumentRepositoryType,
    ExternalDocumentCreateResponse,
)

from ...domain.models import (
    AppConfig,
    AppTenantConfig,
    Document,
    DocumentOperation,
    DocumentOperationStatusSnapshot,
    ExtractedClinicalData,
    ExtractedCondition,
    ExtractedMedication,
    MedicationProfile,
    MedispanDrug,
    Page,
    OCRType,
    UserEnteredMedicationAggregate,
    Status as StatusModel,
    StatusCode,
    DocumentAssessment
)

from ...domain.model_toc import (
    ProfileType,
)

from ...domain.models import Document, Page
from ...domain.models_common import (
    EntityFilter,
    GenericMessage,
    NotFoundException,
    WindowClosedException
)

from ...interface.ports import CommandError, ICommandHandlingPort
from ...usecases.commands import (
    Command,
    AddUserEnteredMedication,    
    CreateDocument,
    CreateMedication,
    CreateNote,
    DeleteReconcilledMedication,
    FindMedication,
    FindMedicationWithLLMFilter,
    DeleteMedication,
    GetDocumentLogs,
    GetDocumentPDFURL,
    ImportHostAttachments,
    ImportHostAttachmentFromExternalApi,
    ImportHostAttachmentFromExternalApiTask,
    ImportMedications,
    Orchestrate,
    SplitPages,
    TriggerExtraction,
    UnDeleteReconcilledMedication,
    UndeleteMedication,
    UpdateDocumentStatusSnapshot,
    UpdateHostMedications,
    UpdateMedication,
    UpdateUserEnteredMedication,
    UpdateNote,
    CreateDocumentMedicationProfileCommand,
    DeleteDocumentMedicationProfileCommand,
    LogPageProfileFilterState,
    ExecuteGenericPromptStep,
    GetHostMedicationClassifications,
    StartOrchestration,
    QueueE2ETest,
    RunE2ETest,
    ReassessTestCaseSummaryResults,
    CreateTestCaseFromDocument,
    ConfirmE2ETest,
    LoadTestPoke,
    CreateEntitySchema,
    DeleteEntitySchema,
    ImportEntities,
    QueueDeferredOrchestration,
)
from paperglass.usecases.configuration import get_config
from paperglass.usecases.evidence_linking import EvidenceLinking
from paperglass.usecases.e2e_v4_tests import TestHarness
from paperglass.entrypoints.workbench.golden_dataset_sync import GoldenDatasetSync
from paperglass.interface.adapters.admin import AdminAdapter
from ...infrastructure.ports import IMessagingPort, IUnitOfWorkManagerPort, IApplicationIntegration, ICloudTaskPort, IQueryPort, IStoragePort

#OpenTelemetry instrumentation
SPAN_BASE: str = "CONTROLLER:rest_controller:"
from ...domain.utils.opentelemetry_utils import OpenTelemetryUtils
from opentelemetry.trace.status import Status, StatusCode
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

REPOSITORY_TYPE_MAP = {
    "API": GenericExternalDocumentCreateEventRequestApi,
    "URI": GenericExternalDocumentCreateEventRequestUri
}

class CreateNoteRequest(BaseModel):
    title: str
    content: str


class UpdateNoteRequest(BaseModel):
    content: str


class CreateMedicationRequest(BaseModel):
    document_id: str
    # page_id: str
    values: dict


class UpdateMedicationRequest(BaseModel):
    values: dict


class CreateDocumentMedicationProfileRequest(BaseModel):
    document_id: str
    page_id: str
    values: dict

class UpdateDocumentMedicationProfileRequest(BaseModel):
    values: dict


class RestAdapter(Starlette):
    def __init__(self):
        super().__init__(
            debug=True,
            routes=[

                # Here comes the real API
                Route("/status", self.status, methods=["GET"]),
                Route("/status/token", self.status_token, methods=["GET"]),
                Route("/status/oktatoken", self.status_oktatoken, methods=["GET"]),
                Route("/status/oktaservicetoken", self.status_oktaservicetoken, methods=["GET"]),

                Route("/config/{app_id}", self.get_app_config, methods=["GET"]),
                Route("/v1/keys", self.get_jwks_keys, methods=["GET"]),  # Endpoint for testing jwks key retrieval.  Won't be used in real world
                Route("/v1/configs/{app_id}", self.get_app_config_v1, methods=["GET"]),
                Route("/v1/configs", self.list_app_configs_v1, methods=["GET"]),

                Route("/command", self.command, methods=["POST"]),
                Route('/documents/assessment', self.assess_documents, methods=['GET']),
                Route('/orchestrate/golden-dataset/sync', self.sync_golden_dataset, methods=['GET']),
                Route("/platform/annotation", self.add_platform_annotation, methods=["GET"]),


                Route('/trigger_extraction', self.trigger_extraction, methods=['POST']),
                Route('/start_cloud_task', self.start_cloud_task, methods=['POST']),
                Route('/orchestrate', self.orchestrate, methods=['POST']),
                Route('/orchestrate/{operation_type}', self.run_orchestration, methods=['POST']),
                Route('/orchestrate/{operation_type}/test', self.queue_e2e_test, methods=['POST']),
                Route('/orchestrate/{operation_type}/test/reassess/{run_id}', self.e2e_test_reassess, methods=['POST']),
                Route('/orchestrate/{operation_type}/test/report/{mode}/tldr/latest', self.get_e2e_test_tldr_results, methods=['GET']),
                Route('/orchestrate/{operation_type}/test/report/{mode}/summary/latest', self.get_e2e_test_summary_results, methods=['GET']),
                Route('/orchestrate/{operation_type}/test/confirm', self.confirm_e2e_test, methods=['POST']),             
                Route('/orchestrate/{operation_type}/loadtest/poke', self.queue_loadtest_poke, methods=['POST']),
                Route('/orchestrate/{operation_type}/{operation_step}', self.run_generic_prompt_step, methods=['POST']),


                #V3 orchestrate related
                Route('/orchestrate_v3_medication_extraction', self.orchestrate_v3_medication_extraction, methods=['POST']),
                Route('/orchestrate_v3_conditions_extraction', self.orchestrate_v3_conditions_extraction, methods=['POST']),
                Route('/orchestrate_v3_page_classification', self.orchestrate_v3_page_classification, methods=['POST']),
                Route('/orchestrate_v3_allergies_extraction', self.orchestrate_v3_allergies_extraction, methods=['POST']),
                Route('/orchestrate_v3_immunizations_extraction', self.orchestrate_v3_immunizations_extraction, methods=['POST']),
                Route('/orchestrate_v3_recover', self.orchestrate_v3_recover, methods=['POST']),

                #VertexAI Load Test
                Route('/orchestrate_v3_page_classification_dummy', self.orchestrate_v3_page_classification_dummy, methods=['POST']),
                Route('/orchestrate_v3_medication_extraction_dummy', self.orchestrate_v3_medication_extraction_dummy, methods=['POST']),

                # documents
                Route('/documents', self.list_documents, methods=['GET']),
                Route('/documents_with_pagination', self.list_documents_with_pagination, methods=['GET']),
                Route('/documents/{document_id}/status', self.get_document_status, methods=['GET']),
                Route('/v1/documents/status', self.get_document_status_by_host_attachment_id, methods=['GET']),
                Route('/documents', self.upload_document, methods=['POST']),
                Route('/documents/{document_id}', self.get_document, methods=['GET','DELETE']),
                Route('/documents/{document_id}/pdf-url', self.get_document_pdf_url, methods=['GET']),
                Route('/documents/{document_id}/events', self.list_document_events, methods=['GET']),
                Route('/documents/{document_id}/pages/{page_number}', self.get_page, methods=['GET']),
                Route(
                    '/documents/{document_id}/pagenumber/{page_number}/labels',
                    self.get_page_labels,
                    methods=['GET'],
                ),
                Route('/document/update_status', self.update_document_status, methods=['POST']),
                Route('/documents/{document_id}/extract', self.extract, methods=['POST']),
                Route('/documents/{document_id}/toc', self.get_document_toc, methods=['GET']),
                Route('/v2/documents/{document_id}/toc', self.get_document_entity_toc, methods=['GET']),
                Route('/documents/{document_id}/toc/pageprofiles/{profile_type}', self.get_document_page_profiles, methods=['GET']),
                Route('/documents/{document_id}/logs', self.get_document_logs, methods=['GET', "POST"]),
                Route('/documents/{document_id}/page-logs', self.get_document_page_logs, methods=['GET']),
                Route('/documents/{document_id}/create-testcase', self.create_testcase, methods=['POST']),
                Route('/documents/filter/state', self.create_page_filter_state, methods=['POST']),
                Route('/document/external/create', self.on_document_external_create, methods=['POST']), 
                Route('/document/external/create/task', self.on_document_external_create_task, methods=['POST']),
                Route('/document/internal/create', self.on_document_internal_create, methods=['POST']),

                # command API for splitting pages
                Route('/split_pages', self.split_pages, methods=['GET','POST']),

                #get medications
                Route('/medications', self.get_medications, methods=['GET']),
                Route('/medications_by_documents', self.get_medications_by_documents, methods=['GET']),
                Route('/v2/medications_by_documents', self.get_medication_profile_by_documents, methods=['GET']),
                Route('/get_medications_grouped', self.get_medications_grouped, methods=['GET']),
                Route('/v2/get_extracted_medications/{extracted_medication_id}', self.get_extracted_medication, methods=['GET']),

                # Medispan
                Route('/medispan/search', self.medispan_search, methods=['GET']),
                Route('/medispan/search_vector_with_llm_filter', self.medispan_vector_search, methods=['GET']), # Exposed for testing with notebook using precice same logic as application

                # medications CRUD
                Route('/medications', self.create_medication, methods=['POST']),
                Route('/medications/{medication_id}', self.update_medication, methods=['PATCH']),
                Route('/medications/{medication_id}', self.delete_medication, methods=['DELETE']),
                Route('/medications/{medication_id}/undelete', self.undelete_medication, methods=['POST']),
                Route('/v2/medications', self.create_medication_v2, methods=['POST']),
                Route('/v2/medications/{medication_id}', self.update_medication_v2, methods=['PATCH']),
                Route('/v2/medications/{medication_id}', self.delete_medication_v2, methods=['DELETE']),
                Route('/v2/medications/{medication_id}/undelete', self.undelete_medication_v2, methods=['POST']),
                Route('/v2/medications/import', self.import_medications, methods=['POST']),
                Route('/v2/medications/update_host_medications', self.update_host_medications, methods=['POST']),

                # generic extracted clinical data
                Route('/v2/extracted_clinical_data/{clinical_data_type}', self.get_extracted_clinical_data, methods=['GET']),

                # Reference data endpoint
                Route('/v2/reference/{category}/{list}', self.get_reference_list, methods=['GET']),

                # host attachments
                Route('/v2/attachments/import', self.import_host_attachments, methods=['POST']),

                # document medication profile
                Route('/documents/{document_id}/medication-profile', self.list_document_medication_profile_by_document, methods=['GET']),
                Route('/documents/{document_id}/medication-profile/map', self.map_document_medication_profile, methods=['GET']),
                Route('/documents/{document_id}/medication-profile/{key}', self.add_document_medication_profile, methods=['POST']),
                Route('/documents/{document_id}/medication-profile/{key}', self.delete_document_medication_profile, methods=['DELETE']),
                Route('/documents/{document_id}/medication-profile/grades', self.list_extracted_medication_grades, methods=['GET']),

                # evidences
                Route('/search_evidences', self.get_brute_force_search_based_evidence, methods=['GET']),
                Route('/v2/search_evidences', self.get_brute_force_search_based_evidence_v2, methods=['GET']),
                Route('/v2/search_evidences_for_clinical_data', self.get_brute_force_search_based_evidence_for_clinical_data, methods=['GET']),
                Route('/v2/search_evidences_for_conditions', self.get_brute_force_search_based_evidence_for_conditions, methods=['GET']),
                Route('/settings/{key}', self.get_setting, methods=['GET']),
                Route('/v2/configuration', self.get_config, methods=['GET']),
                Route('/v2/configuration/document-operation-definition/{operation_type}', self.get_document_operation_definition_config, methods=['GET']),
                
                #v4
                Route('/v4/medications_by_documents', self.get_medication_profile_by_documents_v4, methods=['GET']),
                Route('/v4/documents/{document_id}/toc/pageprofiles/{profile_type}', self.get_document_page_profiles_v4, methods=['GET']),
                Route('/v4/search_evidences', self.get_brute_force_search_based_evidence_v4, methods=['GET']),
                Route('/v4/status_update', self.update_document_status_v4, methods=['POST']),
                Route('/v4/create_medications', self.create_medications_v4, methods=['POST']),
                Route('/v4/trigger_page_ocr/{document_id}/{page_number}', self.trigger_page_ocr_v4, methods=['POST']),
                Route('/v4/ocr/{document_id}/{page_number}/process', self.process_page_ocr_v4, methods=['POST']),
                Route('/v4/ocr/{document_id}/{page_number}/status', self.get_ocr_v4_status, methods=['GET']),

                #v5 Entity Extraction                
                Route('/v5/status_update/{operation_type}', self.update_document_status_v5, methods=['POST']),
                Route('/v5/entities', self.create_entities_v5, methods=['POST']),
                
                # Admin endpoints
                Route('/admin/entity_schema', self.create_entity_schema, methods=['POST']),
                Route('/admin/entity_schema/search', self.get_entity_schema_by_fqn, methods=['GET']),
                Route('/admin/schemas', self.list_entity_schemas, methods=['GET']),
                Route('/admin/schemas/{schema_id}', self.get_entity_schema_by_id, methods=['GET']),
                Route('/admin/schemas/{schema_id}', self.delete_entity_schema_by_id, methods=['DELETE']),
                Route('/admin/config', self.create_or_update_app_config, methods=['POST']),
                Route('/admin/onboarding-wizard', self.process_onboarding_wizard, methods=['POST']),
                Route('/admin/schemas/{app_id}/{schema_id}.json', self.create_or_update_entity_schema, methods=['POST']),
                Route('/schemas/{app_id}/{schema_id}.json', self.get_entity_schema, methods=['GET']),
            ],
        )

    async def get_jwks_keys(self, request: Request):
        jwks = {
            "keys": [
                {
                "kty": "RSA",
                "use": "sig",
                "kid": "3e4977fc3e1d4f5b8123c4a7200be321",
                "alg": "RS256",
                "n": "splNNkuhPlBBfumvwhOQmlse-69RfXc78SvwSWLgtuTy_ox-tzIoBShHfjCwgsAk-yYNIv4kmYtZ4rqHEciiqlYSncG_hV_2-NEdpqYFCsSyZgv5dfcye8IaD5OKA0uvrWM5FRCGxD16R-BQGk79RYbXPKMtTpDfkS81N1Qa4HcspKoWxk6kKPyrQc_YLGYX1YN7BHslUDcfeUQ_wJhIkMCuusiDDbr2-BLckniK6dppP0JXndF5JX7gdKXLez8E4b7X-bzyqkDUx5SYna4Gcyz4vZUs7ORS2PIiQqSqfk1XjGxhnLsNJLzt7Hh9z-9S-JaQIXM2x9YTM8kKTojmFw",
                "e": "AQAB"
                }
            ]
        }
        return JSONResponse(jwks)

    @inject
    async def list_notes(self, request: Request, query: IQueryPort):
        # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
        return JSONResponse(await query.list_notes())

    @inject
    async def create_note(self, request: Request, commands: ICommandHandlingPort):
        payload = await request.json()
        try:
            payload = CreateNoteRequest(**payload)
        except ValidationError as e:
            return JSONResponse({'success': False, 'errors': e.errors()})
        note = await commands.handle_command(CreateNote(title=payload.title, content=payload.content))
        return JSONResponse({'id': note.id})

    @inject
    async def get_note(self, request: Request, query: IQueryPort):
        # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
        note_id = request.path_params['note_id']
        return JSONResponse(await query.get_note(note_id))

    @inject
    async def update_note(self, request: Request, commands: ICommandHandlingPort):
        note_id = request.path_params['note_id']
        payload = await request.json()
        try:
            payload = UpdateNoteRequest(**payload)
        except ValidationError as e:
            return JSONResponse({'success': False, 'errors': e.errors()})
        note = await commands.handle_command(UpdateNote(note_id=note_id, content=payload.content))
        return JSONResponse({'id': note.id})

    @decode_token
    @inject
    async def get_app_config(self, request: Request, query: IQueryPort):
        app_id = request.path_params['app_id']
        tenant_id = request['tenant_id']

        LOGGER2.debug(f"app_id in token: {request.get('app_id')}  app_id in path: {app_id}")

        if app_id != request['app_id']:
            return JSONResponse({"message": "Forbidden"}, status_code=403)

        config: Configuration = await get_config(app_id, tenant_id, query)
        return JSONResponse(config.dict())


    @require_service_auth
    @inject
    async def get_app_config_v1(self, request: Request, query: IQueryPort):
        """
        Get application configuration for the specified app_id (v1 endpoint).
        
        This endpoint retrieves the application configuration from the database.
        If generate_if_missing is True and no config is found, it returns a default
        configuration with the specified app_id without saving it to the database.
        
        Requires Google service account authentication.
        """
        from paperglass.domain.utils.exception_utils import exceptionToMap
        from uuid import uuid1
        
        app_id = request.path_params['app_id']
        generate_if_missing = request.query_params.get('generate_if_missing', 'false').lower() == 'true'
        
        extra = {
            "operation": "get_app_config_v1",
            "app_id": app_id,
            "generate_if_missing": generate_if_missing
        }
        
        try:
            LOGGER2.debug(f"Getting app config v1 for app_id: {app_id}, generate_if_missing: {generate_if_missing}", extra=extra)
            
            # Try to get existing app config
            app_config: AppConfig = await query.get_app_config(app_id)
            
            if app_config and app_config.active:
                extra["config_found"] = True
                LOGGER2.debug(f"Found existing app config for app_id: {app_id}", extra=extra)
                return JSONResponse(JsonUtil.clean(app_config.dict()))
            
            # If not found and generate_if_missing is True, create default config
            if generate_if_missing:
                extra["config_found"] = False
                extra["generated_default"] = True
                LOGGER2.debug(f"Generating default config for app_id: {app_id}", extra=extra)
                
                # Create default configuration
                default_config = Configuration(
                    extract_allergies=False,
                    extract_conditions=True,
                    extract_immunizations=False,
                    extraction_persisted_to_medication_profile=False,
                    use_extract_and_classify_strategy=True,
                    use_ordered_events=False,
                    use_v3_orchestration_engine=True
                )
                
                # Create AppConfig with default values (not saved to DB)
                default_app_config = AppConfig(
                    id=uuid1().hex,
                    app_id=app_id,
                    name=f"App {app_id}",
                    description=f"Default configuration for application {app_id}",
                    config=default_config,
                    active=True
                )
                
                return JSONResponse(JsonUtil.clean(default_app_config.dict()))
            
            # Config not found and not generating default
            extra["config_found"] = False
            extra["generated_default"] = False
            LOGGER2.warning(f"App config not found for app_id: {app_id}", extra=extra)
            return JSONResponse(
                {"message": f"App configuration not found for app_id: {app_id}"}, 
                status_code=404
            )
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER2.error(f"Error getting app config v1 for app_id {app_id}: {e}", extra=extra, exc_info=True)
            return JSONResponse(
                {"message": "Internal server error"}, 
                status_code=500
            )


    @require_service_auth
    @inject
    async def list_app_configs_v1(self, request: Request, query: IQueryPort):
        """
        List all application configurations (v1 endpoint).
        
        This endpoint retrieves all application configurations from the database.
        Supports pagination via limit and offset query parameters.
        
        Requires Google service account authentication.
        """
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        # Validate limit (max 100)
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0
        
        extra = {
            "operation": "list_app_configs_v1",
            "limit": limit,
            "offset": offset
        }
        
        try:
            LOGGER2.debug(f"Listing app configs with limit: {limit}, offset: {offset}", extra=extra)
            
            # Get all app configs from the database
            app_configs = await query.list_app_configs(limit=limit, offset=offset)
            
            extra["configs_found"] = len(app_configs)
            LOGGER2.debug(f"Found {len(app_configs)} app configs", extra=extra)
            
            # Convert to list of dicts and serialize with JsonUtil.clean
            configs_data = [JsonUtil.clean(config.dict()) for config in app_configs if config.active]
            
            response_data = {
                "configs": configs_data,
                "total": len(configs_data),
                "limit": limit,
                "offset": offset
            }
            
            return JSONResponse(response_data)
            
        except Exception as e:
            extra["error"] = exceptionToMap(e)
            LOGGER2.error(f"Error listing app configs: {e}", extra=extra, exc_info=True)
            return JSONResponse(
                {"message": "Internal server error"}, 
                status_code=500
            )


    @decode_token
    @inject
    async def command(self, request: Request, commands: ICommandHandlingPort):
        payload = await request.json()
        type = payload.get("type")
        command_dict = payload.get("command")
        extra={
            "type": type,
            "command": command_dict
        }
        LOGGER.info("Received REST command: %s", command_dict.get("type"), extra=extra)
        try:
            command = parse_obj_as(Command, command_dict)
            await commands.handle_command_with_explicit_transaction(command)
            return JSONResponse({'success': True})
        except CommandError as e:
            LOGGER.error("REST command error: %s", e, extra=extra)
            return JSONResponse({'success': False, 'errors': e.errors})
        

    @verify_okta
    @decode_token
    @inject
    async def list_documents(self, request: Request, query: IQueryPort):
        thisSpanName = "list_documents"
        with await opentelemetry.getSpan(thisSpanName) as span:
            # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
            #patient_id = request.query_params['patientId']
            patient_id = request['patient_id']
            app_id = request['app_id']
            tenant_id = request['tenant_id']
            return JSONResponse(await get_documents(app_id, tenant_id, patient_id, None,None, query))

    @verify_okta
    @decode_token
    @inject
    async def list_documents_with_pagination(self, request: Request, query: IQueryPort):
        thisSpanName = "list_documents_with_pagination"
        with await opentelemetry.getSpan(thisSpanName) as span:
            # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
            patient_id = request['patient_id']
            app_id = request['app_id']
            tenant_id = request['tenant_id']
            start_at = request.query_params['startAt']
            if start_at == "null":
                start_at = None
            end_at = request.query_params['endAt']
            if end_at == "null":
                end_at = None
            limit = request.query_params['limit']
            if limit:
                limit = int(limit)
                
            # page = request.query_params['page']
            # page_size = request.query_params['pageSize']
            documents = await get_documents(app_id, tenant_id, patient_id, start_at,end_at,limit, query)
            return JSONResponse(documents)

    @verify_okta
    @decode_token
    @inject
    async def get_document_status(self, request: Request, query: IQueryPort):
        from ...usecases.documents import get_document_status_v3
        thisSpanName = "get_document_status"
        with await opentelemetry.getSpan(thisSpanName) as span:
            document_id = request.path_params['document_id']
            app_id = request['app_id']
            tenant_id = request['tenant_id']
            patient_id = request['patient_id']
            return JSONResponse(await get_document_status_v3(app_id, tenant_id, patient_id, document_id, query))

    @verify_gcp_service_account
    @inject
    async def get_document_status_by_host_attachment_id(self, request: Request, query: IQueryPort):
        from ...usecases.documents import get_document_status_by_host_attachment_id
        LOGGER.info(f"[DEBUG] get_document_status_by_host_attachment_id method called with URL: {request.url}")
        thisSpanName = "get_document_status_by_host_attachment_id"
        with await opentelemetry.getSpan(thisSpanName) as span:
            # Extract query parameters
            host_attachment_id = request.query_params.get('host_attachment_id')
            app_id = request.query_params.get('app_id')
            tenant_id = request.query_params.get('tenant_id')
            patient_id = request.query_params.get('patient_id')

            # Validate required parameters
            if not all([host_attachment_id, app_id, tenant_id, patient_id]):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing required parameters: host_attachment_id, app_id, tenant_id, patient_id"}
                )

            try:
                result = await get_document_status_by_host_attachment_id(
                    app_id, tenant_id, patient_id, host_attachment_id, query
                )
                return JSONResponse(result.dict())
            except ValueError as e:
                LOGGER.info(f"[DEBUG] ValueError in get_document_status_by_host_attachment_id: {str(e)}")
                return JSONResponse(status_code=404, content={"error": str(e)})
            except Exception as e:
                return JSONResponse(status_code=500, content={"error": "Internal server error"})

    @decode_token
    @inject
    async def update_document_status(self, request: Request, commands: ICommandHandlingPort):
        payload = await request.json()
        try:
            patient_id = request["patient_id"]
            app_id = request["app_id"]
            tenant_id = request["tenant_id"]
            
            await commands.handle_command(UpdateDocumentStatusSnapshot(
                document_id=payload.get("document_id"),
                patient_id=patient_id,
                app_id=app_id,
                tenant_id=tenant_id,
                doc_operation_status_snapshot=DocumentOperationStatusSnapshot(
                    operation_type=DocumentOperationType.MEDICATION_EXTRACTION,
                    status=payload.get("status"),
                    end_time=datetime.now(timezone.utc).isoformat(),
                    orchestration_engine_version=payload.get("orchestration_engine_version")
                )
            ))
            return JSONResponse({'success': True})
        except ValidationError as e:
            return JSONResponse({'success': False, 'errors': e.errors()})

    @decode_token
    @inject
    async def upload_document(self, request: Request, commands: ICommandHandlingPort):
        # Get uploaded file
        form = await request.form()
        file = form['file']
        #patient_id = form['patientId']
        file_name = file.filename

        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']
        token = request['token']
        result = await commands.handle_command(CreateDocument(token=token,app_id=app_id,
                                                              tenant_id=tenant_id,
                                                              file_name=file_name,
                                                              file=await file.read(),
                                                              patient_id=patient_id,
                                                              priority=OrchestrationPriority.HIGH))

        return JSONResponse({'id': result.id})

    @decode_token
    @inject
    async def get_document(self, request: Request,query: IQueryPort):
        # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
        document_id = request.path_params['document_id']
        if request.method == 'DELETE':
            return JSONResponse(await query.delete_document(document_id))
        return JSONResponse(await query.get_document(document_id))

    @decode_token
    @inject
    async def get_document_pdf_url(self, request: Request,commands: ICommandHandlingPort):
        document_id = request.path_params['document_id']
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']
        command = GetDocumentPDFURL(app_id=app_id, tenant_id=tenant_id,patient_id=patient_id,document_id=document_id)

        return JSONResponse(await commands.handle_command(command))
        # return JSONResponse(await query.get_document_pdf_url(document_id))

    @decode_token
    @inject
    async def get_document_logs(self, request: Request, commands: ICommandHandlingPort):
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']
        document_id = request.path_params['document_id']

        filter = None
        if request.method == 'POST':
            body = await request.json()
            filter = EntityFilter(**body)

        command = GetDocumentLogs(app_id=app_id, tenant_id=tenant_id, patient_id=patient_id, document_id=document_id, filter=filter)

        response = await commands.handle_command(command)

        if response is None:
            return JSONResponse({}, status_code=404)

        output = {}
        for key in response.keys():
            output[key] = [x.dict() for x in response[key]]

        serialized = json.loads(json.dumps(output, cls=DateTimeEncoder))

        return JSONResponse(serialized)

    @decode_token
    @inject
    async def get_document_page_logs(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']
        document_id = request.path_params['document_id']

        LOGGER.debug("get_document_page_logs: %s", document_id)

        extraction_type = "medications"
        if "extraction_type" in request.query_params:
            extraction_type = request.query_params['extraction_type']

        #For now this will only work for the main extraction pipeline
        document_operation_type = DocumentOperationType.MEDICATION_EXTRACTION

        document_operation: DocumentOperation = await query.get_document_operation_by_document_id(document_id, document_operation_type)
        if not document_operation:
            msg = GenericMessage("Document operation not found")
            return JSONResponse(msg.to_dict(), status_code=404)

        document_operation_instance_id = document_operation.active_document_operation_instance_id
        LOGGER.debug("get_document_page_logs DocumentId: %s DocumentOperationInstanceId: %s extraction_type: %s", document_id, document_operation_instance_id, extraction_type)

        response = await query.get_all_page_operations(document_id, document_operation_instance_id, extraction_type)

        if response is None:
            return JSONResponse({}, status_code=404)

        output = [x.dict() for x in response]
        serialized = json.loads(json.dumps(output, cls=DateTimeEncoder))

        return JSONResponse(serialized)

    @inject
    async def create_testcase(self, request: Request, commands: ICommandHandlingPort):

        document_id = request.path_params['document_id']
        command = CreateTestCaseFromDocument(document_id=document_id)

        testcase = await commands.handle_command(command)
        
        cleaned_obj = JsonUtil.clean(testcase.dict())
        return JSONResponse(cleaned_obj)


    #-------------------------------------------------------------------------------------------------------------------------
    # @decode_token  # Disabled for testing
    @inject
    async def get_document_toc(self, request: Request,query: IQueryPort):
        document_id = request.path_params['document_id']
        run_id = request.query_params.get('run_id')
        
        try:
            # Check if this is a request for entity TOC
            if run_id:
                # Get specific entity TOC by document_id and run_id
                ret = await query.get_document_entity_toc_by_document_id_and_run_id(document_id, run_id)
                if not ret:
                    var: GenericMessage = GenericMessage("Entity TOC not found")
                    return JSONResponse(var.to_dict(), status_code=404)
                return JSONResponse(ret)
            else:
                # Check if we should return entity TOC or traditional TOC
                entity_toc_list = await query.get_document_entity_toc_by_document_id(document_id)
                if entity_toc_list:
                    # Return entity TOC list
                    return JSONResponse(entity_toc_list)
                else:
                    # Fall back to traditional TOC
                    ret = await query.get_document_toc(document_id)
                    return JSONResponse(ret)
        except NotFoundException as e:
            var: GenericMessage = GenericMessage("Resource not found")
            var.details = e.message
            return JSONResponse(var.to_dict(), status_code=404)

    # @decode_token  # Disabled for testing
    @inject
    async def get_document_entity_toc(self, request: Request, query: IQueryPort):
        """
        New v2 endpoint specifically for entity extraction TOC.
        Returns a summary of entity_toc categories and total counts of entities extracted for the document.
        Implements retry logic to handle race conditions where TOC is requested before entity processing completes.
        """
        document_id = request.path_params['document_id']
        run_id = request.query_params.get('run_id')
        
        # Check if retry is requested (for handling race conditions)
        retry_param = request.query_params.get('retry', 'true').lower()
        enable_retry = retry_param in ['true', '1', 'yes']
        
        try:
            if run_id:
                # Get specific entity TOC by document_id and run_id
                entity_toc_data = await query.get_document_entity_toc_by_document_id_and_run_id(document_id, run_id)
                if not entity_toc_data:
                    var: GenericMessage = GenericMessage("Entity TOC not found")
                    return JSONResponse(var.to_dict(), status_code=404)
                
                # Create summary from specific run data
                summary = await self._create_entity_toc_summary([entity_toc_data], query)
                return JSONResponse(summary)
            else:
                # Implement retry logic for race condition handling
                max_retries = 3
                retry_delay = 1.0  # seconds
                
                for attempt in range(max_retries + 1):  # 0, 1, 2, 3 (4 total attempts)
                    LOGGER.debug(f"Entity TOC retrieval attempt {attempt + 1}/{max_retries + 1} for document {document_id}")
                    
                    # Try to get the active document operation instance for entity extraction
                    from ...domain.values import DocumentOperationType
                    document_operation = await query.get_document_operation_by_document_id(document_id, DocumentOperationType.ENTITY_EXTRACTION.value)
                    
                    active_run_id = None
                    if document_operation and document_operation.active_document_operation_instance_id:
                        active_run_id = document_operation.active_document_operation_instance_id
                    
                    if active_run_id:
                        # Get entity TOC for the active run only
                        entity_toc_data = await query.get_document_entity_toc_by_document_id_and_run_id(document_id, active_run_id)
                        
                        if entity_toc_data:
                            # Create summary from active run data only
                            summary = await self._create_entity_toc_summary([entity_toc_data], query)
                            if summary.get("total_entities", 0) > 0:
                                LOGGER.debug(f"Entity TOC found with {summary['total_entities']} entities on attempt {attempt + 1}")
                                return JSONResponse(summary)
                    
                    # Fallback: Get all entity TOC entries for the document and use the most recent one
                    entity_toc_list = await query.get_document_entity_toc_by_document_id(document_id)
                    
                    if entity_toc_list:
                        # Sort by created_at descending and take the most recent one to avoid count multiplication
                        entity_toc_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                        most_recent_toc = entity_toc_list[0]
                        
                        # Create summary from most recent run data only
                        summary = await self._create_entity_toc_summary([most_recent_toc], query)
                        if summary.get("total_entities", 0) > 0:
                            LOGGER.debug(f"Entity TOC found with {summary['total_entities']} entities on attempt {attempt + 1}")
                            return JSONResponse(summary)
                    
                    # If no entities found and we have retries left, wait and try again
                    if enable_retry and attempt < max_retries:
                        LOGGER.debug(f"No entities found on attempt {attempt + 1}, retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 1.5  # Exponential backoff: 1.0, 1.5, 2.25 seconds
                    else:
                        # Last attempt or retry disabled, return empty result
                        LOGGER.debug(f"No entities found after {attempt + 1} attempts, returning empty TOC")
                        break
                
                # Return empty summary if no entity TOC data found after all retries
                return JSONResponse({
                    "document_id": document_id,
                    "total_entities": 0,
                    "categories": [],
                    "runs": []
                })
                
        except NotFoundException as e:
            var: GenericMessage = GenericMessage("Resource not found")
            var.details = e.message
            return JSONResponse(var.to_dict(), status_code=404)
        except Exception as e:
            var: GenericMessage = GenericMessage("Internal server error")
            var.details = str(e)
            return JSONResponse(var.to_dict(), status_code=500)

    async def _create_entity_toc_summary(self, entity_toc_list: List[dict], query: IQueryPort) -> dict:
        """
        Create a summary of entity TOC data showing categories and total counts.
        
        Args:
            entity_toc_list: List of entity TOC documents
            query: Query port for database operations
            
        Returns:
            Dictionary with summary of categories and counts
        """
        if not entity_toc_list:
            return {
                "total_entities": 0,
                "categories": [],
                "runs": []
            }
        
        # Get document_id from first entry
        document_id = entity_toc_list[0].get("document_id", "")
        
        # Aggregate counts by category across all runs
        category_totals = {}
        runs_summary = []
        total_entities = 0
        
        for toc_doc in entity_toc_list:
            run_id = toc_doc.get("run_id", "")
            entries = toc_doc.get("entries", [])
            
            run_categories = []
            run_total = 0
            
            for entry in entries:
                category = entry.get("category", "")
                count = entry.get("count", 0)
                
                # Add to category totals
                if category in category_totals:
                    category_totals[category] += count
                else:
                    category_totals[category] = count
                
                # Add to run summary (convert to list format)
                existing_run_category = next((c for c in run_categories if c["category"] == category), None)
                if existing_run_category:
                    existing_run_category["count"] += count
                else:
                    schema_uri = entry.get("schema_uri")
                    run_categories.append({
                        "category": category,
                        "label": await self._create_human_friendly_label(category, query, schema_uri),
                        "count": count
                    })
                
                run_total += count
                total_entities += count
            
            # Add run summary
            runs_summary.append({
                "run_id": run_id,
                "total_entities": run_total,
                "categories": run_categories,
                "created_at": toc_doc.get("created_at"),
                "updated_at": toc_doc.get("updated_at")
            })
        
        # Convert category_totals dict to list format
        # We need to get the schema_uri for each category from the most recent run
        categories_list = []
        category_to_schema_uri = {}
        
        # Build a mapping of category to schema_uri from the most recent run data
        if entity_toc_list:
            most_recent_toc = entity_toc_list[0]  # Already sorted by created_at descending
            entries = most_recent_toc.get("entries", [])
            for entry in entries:
                category = entry.get("category", "")
                schema_uri = entry.get("schema_uri")
                if category and schema_uri:
                    category_to_schema_uri[category] = schema_uri
        
        for category, count in category_totals.items():
            schema_uri = category_to_schema_uri.get(category)
            categories_list.append({
                "category": category,
                "label": await self._create_human_friendly_label(category, query, schema_uri),
                "count": count
            })
        
        return {
            "document_id": document_id,
            "total_entities": total_entities,
            "categories": categories_list,
            "runs": runs_summary
        }

    async def _create_human_friendly_label(self, category: str, query: IQueryPort, schema_uri: str = None) -> str:
        """
        Create a human-friendly label from a category string.
        First tries to get the label from entity schema using schema_uri (FQN), falls back to capitalizing words.
        
        Args:
            category: The category string to convert
            query: Query port for database operations
            schema_uri: Optional schema URI (FQN) to look up the entity schema
            
        Returns:
            Human-friendly label string
        """
        if not category:
            return ""
        
        LOGGER.debug(f"_create_human_friendly_label called with category='{category}', schema_uri='{schema_uri}'")
        
        try:
            # Try to get label from entity schema using schema_uri (FQN) if provided
            if schema_uri:
                LOGGER.debug(f"Looking up entity schema by FQN: {schema_uri}")
                entity_schema = await query.get_entity_schema_by_fqn(schema_uri)
                LOGGER.debug(f"Entity schema found: {entity_schema is not None}")
                if entity_schema:
                    LOGGER.debug(f"Entity schema label: '{entity_schema.label}', title: '{entity_schema.title}'")
                    if entity_schema.label:
                        LOGGER.debug(f"Returning label from entity schema: '{entity_schema.label}'")
                        return entity_schema.label
                    elif entity_schema.title:
                        LOGGER.debug(f"Returning title from entity schema: '{entity_schema.title}'")
                        return entity_schema.title
                else:
                    LOGGER.debug(f"No entity schema found for FQN: {schema_uri}")
            else:
                LOGGER.debug("No schema_uri provided, skipping FQN lookup")
            
            # Fallback: Try to get label from entity schema using app_id and schema_id
            # For now, we'll use a default app_id since we don't have it in this context
            # This could be improved by passing app_id through the call chain
            LOGGER.debug(f"Trying fallback lookup with app_id='GLOBAL', schema_id='{category}'")
            entity_schema = await query.get_entity_schema_by_app_id_and_schema_id("GLOBAL", category)
            
            if entity_schema and entity_schema.label:
                LOGGER.debug(f"Returning label from fallback lookup: '{entity_schema.label}'")
                return entity_schema.label
            elif entity_schema and entity_schema.title:
                LOGGER.debug(f"Returning title from fallback lookup: '{entity_schema.title}'")
                return entity_schema.title
                
        except Exception as e:
            # Log the error but continue with fallback
            LOGGER.error(f"Error retrieving entity schema for category '{category}' with schema_uri '{schema_uri}': {str(e)}")
        
        # Fallback: Replace underscores and hyphens with spaces and capitalize
        label = category.replace("_", " ").replace("-", " ")
        label = " ".join(word.capitalize() for word in label.split())
        
        LOGGER.debug(f"Using synthesized fallback label: '{label}'")
        return label


    @decode_token  # Disabled for testing
    @inject
    async def get_document_page_profiles(self, request: Request,query: IQueryPort):
        document_id = request.path_params['document_id']
        patient_id = request['patient_id']
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        config:Configuration = Configuration()
        try:
            from ...usecases.medications import get_document_filter_profile_v3, get_document_filter_profile
            
            config = await get_config(app_id, tenant_id, query)

            if not config or config.extraction_persisted_to_medication_profile:
                page_profiles: List[MedicationPageProfile] = await get_document_filter_profile(document_id,patient_id,query)
            else:
                page_profiles: List[MedicationPageProfile] = await get_document_filter_profile_v3(document_id, patient_id, app_id, tenant_id,query)

            ret = {}

            for page_profile in page_profiles:
                page_profile: MedicationPageProfile = page_profile
                ret[page_profile.page_profile_number] = {
                    "hasItems": page_profile.has_items,
                    "items": page_profile.items,
                    "numberOfItems": page_profile.number_of_items,
                    "type": "medication"
                }

            return JSONResponse(ret)
        except NotFoundException as e:
            var: GenericMessage = GenericMessage("Resource not found")
            var.details = e.message
            return JSONResponse(var.to_dict(), status_code=404)
        
    @decode_token  # Disabled for testing
    @inject
    async def get_document_page_profiles_v4(self, request: Request,query: IQueryPort, commands: ICommandHandlingPort):
        document_id = request.path_params['document_id']
        patient_id = request['patient_id']
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        config:Configuration = Configuration()
        try:
            from ...usecases.v4.medications import get_document_filter_profile_v4
            
            config = await get_config(app_id, tenant_id, query)            

            LOGGER.debug(f"Command Handler type: {type(commands)}")

            page_profiles: List[MedicationPageProfile] = await get_document_filter_profile_v4(document_id, patient_id, app_id, tenant_id, query, commands)

            ret = {}

            for page_profile in page_profiles:
                page_profile: MedicationPageProfile = page_profile
                ret[page_profile.page_profile_number] = {
                    "hasItems": page_profile.has_items,
                    "items": page_profile.items,
                    "numberOfItems": page_profile.number_of_items,
                    "type": "medication"
                }

            return JSONResponse(ret)
        except NotFoundException as e:
            var: GenericMessage = GenericMessage("Resource not found")
            var.details = e.message
            return JSONResponse(var.to_dict(), status_code=404)

    @decode_token
    @inject
    async def create_page_filter_state(self, request: Request, commands: ICommandHandlingPort):
        LOGGER.debug("create_page_filter_state")

        # These values are not necessary for logging purposes
        app_id = request["app_id"]
        tenant_id = request["tenant_id"]
        patient_id = request["patient_id"]
        user_id = request["user_id"]
        LOGGER.debug("User ID: %s", user_id)

        payload = await request.json()
        try:
            LOGGER.info("Payload: %s", payload)
            logentry = LogPageProfileFilterState(app_id=app_id, tenant_id=tenant_id, patient_id=patient_id, state=payload, user_id=user_id)
            await commands.handle_command(logentry)
        except ValidationError as e:
            LOGGER.error("Validation error: %s", e.errors())
            return JSONResponse({'success': False, 'errors': e.errors()})

        msg:GenericMessage = GenericMessage("Log entry captured")
        return JSONResponse(content=msg.to_dict())


    #-------------------------------------------------------------------------------------------------------------------------

    @inject
    async def list_document_events(self, request: Request, query: IQueryPort):
        # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
        document_id = request.path_params['document_id']
        return JSONResponse(await query.list_document_events(document_id))

    @inject
    async def get_page(self, request: Request, query: IQueryPort):
        # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
        document_id = request.path_params['document_id']
        page_number = request.path_params['page_number']
        return JSONResponse(await query.get_page(document_id, int(page_number)))

    @decode_token
    @inject
    async def get_page_labels(self, request: Request, query: IQueryPort):
        # For queries, we can bypass domain/usecase layers and work directly with the infrastructure.
        document_id = request.path_params['document_id']
        page_number = request.path_params['page_number']
        page_dict = await query.get_page(document_id, int(page_number))
        if page_dict:
            page = Page(**page_dict)
            return JSONResponse(await query.get_page_labels( page.id))
        return JSONResponse([])

    @decode_token
    @inject
    async def split_pages(self, request: Request, commands: ICommandHandlingPort):
        document_id = request.query_params.get('documentId')
        await commands.handle_command(SplitPages(document_id=document_id))
        return JSONResponse({"status": True})

    @decode_token
    @inject
    async def get_medications(self, request: Request, query: IQueryPort):
        document_id = request.query_params.get('documentId')
        page_number = request.query_params.get('pageNumber')
        # if page_number:
        #     page_number = int(page_number)
        page_id = request.query_params.get('pageId')
        # # ideally we should get medications based on page_id
        # if page_id:
        #     return JSONResponse(await query.get_medications(document_id,page_id))

        # # if page_id is not provided based on page_number we can get the active page_id
        # if page_number:
        #     page = await query.get_page(document_id,page_number)
        #     if page:
        #         return JSONResponse(await query.get_medications(document_id,page.get("id")))
        # return JSONResponse([])
        from ...usecases.medications import get_medications
        return JSONResponse(await get_medications(document_id, page_number,page_id, query))

    @decode_token
    @inject
    async def get_medications_grouped(self, request: Request, query: IQueryPort):
        from ...usecases.medications import get_medications_grouped_by_patient
        document_ids = request.query_params.get('documentIds')
        patient_id = request['patient_id']

        return JSONResponse(await get_medications_grouped_by_patient(patient_id, document_ids))

    @decode_token
    @inject
    async def get_medications_by_documents(self, request: Request, query: IQueryPort):
        document_ids = request.query_params.get('documentIds')
        from ...usecases.medications import get_medications_by_document
        return JSONResponse(await get_medications_by_document(document_ids, query))

    @verify_okta
    @decode_token
    @inject
    async def get_medication_profile_by_documents(self, request: Request, query: IQueryPort):
        from ...usecases.medications import get_resolved_reconcilled_medications,get_resolved_reconcilled_medications_v3
        document_ids = request.query_params.get('documentIds')
        patient_id = request['patient_id']
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        config:Configuration = Configuration() #default config

        LOGGER.debug("get_medication_profile_by_documents: %s", document_ids)

        config = await get_config(app_id, tenant_id, query)

        if not config or config.extraction_persisted_to_medication_profile:
            ret = [x.dict() for x in await get_resolved_reconcilled_medications(document_ids, patient_id,query)]
        else:
            ret = [x.dict() for x in await get_resolved_reconcilled_medications_v3(document_ids, patient_id,app_id, tenant_id,query)]

        LOGGER.debug("get_medication_profile_by_documents results: %s", ret)

        return JSONResponse(json.loads(json.dumps(ret, indent=4, sort_keys=True, default=str)))

    @verify_okta
    @decode_token
    @inject
    async def get_medication_profile_by_documents_v4(self, request: Request, query: IQueryPort):
        from ...usecases.v4.medications import get_resolved_reconcilled_medications
        document_ids_with_orchestration_engine_version = request.query_params.get('documentVersions')
        if document_ids_with_orchestration_engine_version:
            document_ids_with_orchestration_engine_version = json.loads(document_ids_with_orchestration_engine_version)
        patient_id = request['patient_id']
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        config:Configuration = Configuration()
        
        LOGGER.debug("get_medication_profile_by_documents_v4: %s", document_ids_with_orchestration_engine_version)

        config = await get_config(app_id, tenant_id, query)

        ret = [x.dict() for x in await get_resolved_reconcilled_medications(document_ids_with_orchestration_engine_version, patient_id,app_id, tenant_id,config,query) if x]
        
        LOGGER.debug("get_medication_profile_by_documents results: %s", ret)

        return JSONResponse(json.loads(json.dumps(ret, indent=4, sort_keys=True, default=str)))

    @decode_token
    @inject
    async def get_extracted_medication(self, request: Request, query: IQueryPort):
        from ...usecases.medications import get_resolved_reconcilled_medications_v3
        extracted_medication_id = request.path_params['extracted_medication_id']

        extracted_medication:ExtractedMedication = await query.get_extracted_medication(extracted_medication_id)
        resolved_reconcilled_medications:List[ResolvedReconcilledMedication] = await get_resolved_reconcilled_medications_v3(extracted_medication.document_id, extracted_medication.patient_id, extracted_medication.app_id, extracted_medication.tenant_id, query)
        for reconcilled_medication in resolved_reconcilled_medications:
            extracted_medication_reference = [x for x in reconcilled_medication.extracted_medication_reference if x.extracted_medication_id == extracted_medication_id]
            if extracted_medication_reference:
                extracted_medication.medication=reconcilled_medication.medication

        if extracted_medication:
            return JSONResponse(json.loads(json.dumps(extracted_medication.dict(), indent=4, sort_keys=True, default=str)))
        return JSONResponse({})

    @decode_token
    @inject
    async def get_brute_force_search_based_evidence(self, request: Request, storage:IStoragePort,query: IQueryPort):
        document_id = request.query_params.get('documentId')
        page_id = request.query_params.get('pageId')
        page_number = request.query_params.get('pageNumber')
        evidence_requested_for = request.query_params.get('evidenceRequestedFor')
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']
        page_raw_ocr = await storage.get_page_ocr(app_id,tenant_id,patient_id,document_id,page_id,ocr_type=OCRType.raw)
        # page = await query.get_page(document_id,int(page_number))
        # page = Page(**page)
        page = await query.get_page_by_id(page_id)
        page = Page(**page)
        page_annotations = page.get_ocr_page_line_annotations(json.loads(page_raw_ocr))

        evidences = [x.token().dict() for x in page_annotations if evidence_requested_for.lower() in x.token().text.lower()]

        return JSONResponse(evidences)

    @decode_token
    @inject
    async def get_brute_force_search_based_evidence_v2(self, request: Request, storage:IStoragePort,query: IQueryPort):
        extracted_medication_id = request.query_params.get('extractedMedicationId')
        extracted_medication:ExtractedMedication = await query.get_extracted_medication(extracted_medication_id)
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']

        config:Configuration = Configuration()
        try:
            config = await get_config(app_id, tenant_id, query)
        except Exception as e:
            LOGGER.error("Exception in get_config: %s", str(e))

        evidence_linking = EvidenceLinking(config)
        evidences = await evidence_linking.get_evidence(app_id, tenant_id, patient_id, extracted_medication)

        return JSONResponse(evidences)

    @decode_token
    @inject
    async def get_brute_force_search_based_evidence_v4(self, request: Request, storage:IStoragePort,query: IQueryPort):
        from usecases.v4.medications import get_medication
        extracted_medication_id = request.query_params.get('extractedMedicationId')
        document_id = request.query_params.get('documentId')
        doc:Document = Document(**await query.get_document(document_id))
        if doc.operation_status.get(DocumentOperationType.MEDICATION_EXTRACTION) and doc.operation_status.get(DocumentOperationType.MEDICATION_EXTRACTION).orchestration_engine_version =="v4":
            extracted_medication:ExtractedMedication = await get_medication(document_id,extracted_medication_id)
        else:
            extracted_medication:ExtractedMedication = await query.get_extracted_medication(extracted_medication_id)
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']

        config:Configuration = Configuration()
        try:
            config = await get_config(app_id, tenant_id, query)
        except Exception as e:
            LOGGER.error("Exception in get_config: %s", str(e))

        evidence_linking = EvidenceLinking(config)
        evidences = await evidence_linking.get_evidence(app_id, tenant_id, patient_id, extracted_medication)

        return JSONResponse(evidences)


    @decode_token
    @inject
    async def list_extracted_medication_grades(self, request: Request, query: IQueryPort):
        document_id = request.path_params['document_id']
        response = [x.dict() for x in await query.get_extracted_medication_grades(document_id)]
        return JSONResponse(json.loads(json.dumps(response, cls=DateTimeEncoder)))

    @decode_token
    @inject
    async def start_cloud_task(self, request: Request, cloud_task_adapter: ICloudTaskPort):
        thisSpanName = "start_cloud_task"
        with await opentelemetry.getSpan(thisSpanName) as span:
            request_payload = await request.json()
            queue = request_payload.get('queue')
            url = request_payload.get('url')
            location = request_payload.get('location')
            service_account_email = request_payload.get('service_account_email')
            payload = request_payload.get('payload')
            token = request['token']
            try:
                #response = await cloud_task_adapter.create_task("paperglass-extraction-queue","https://ai-paperglass-widget-zqftmopgsq-uk.a.run.app/api/trigger_extraction")
                LOGGER.debug("Starting a cloud run task: token: %s, location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", token, location, service_account_email, queue, url, payload)
                response = await cloud_task_adapter.create_task(token=token,
                                                                location=location,
                                                                service_account_email=service_account_email,
                                                                queue=queue,
                                                                url=url,
                                                                payload=payload)
                return JSONResponse({'response': response})
            except ValidationError as e:
                LOGGER.error("ValidationException when starting a cloud run task: token: %s, location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", token, location, service_account_email, queue, url, payload)
                LOGGER.error("ValidationException when starting a cloud run task: %s", e.errors())
                return JSONResponse({'success': False, 'errors': e.errors(), 'trace': traceback.format_exc()}, status_code=500)
            except Exception as e:
                LOGGER.error("Exception when starting a cloud run task: token: %s, location: %s, service_account_email: %s, queue: %s, url: %s, payload: %s", token, location, service_account_email, queue, url, payload)
                LOGGER.error("ValidationException when starting a cloud run task: %s", e.errors())
                return JSONResponse({'success': False, 'errors': str(e), 'trace': traceback.format_exc()}, status_code=500)

    @decode_token
    @inject
    async def trigger_extraction(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        payload = await request.json()
        source_document_storage_uri = payload.get('source_document_storage_uri')
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']

        thisSpanName = "trigger_extraction"
        with await opentelemetry.getSpan(thisSpanName) as span:

            LOGGER.info("Triggering extraction for document: %s", source_document_storage_uri)
            span.set_attribute("app_id", app_id)
            span.set_attribute("tenant_id", tenant_id)
            span.set_attribute("patient_id", patient_id)
            span.set_attribute("source_document_storage_uri", source_document_storage_uri)

            document = await commands.handle_command(TriggerExtraction(source_document_storage_uri=source_document_storage_uri,
                                                                    app_id=app_id,
                                                                    tenant_id=tenant_id,
                                                                    patient_id=patient_id)
                                                                    )
            from ...entrypoints.orchestrator import orchestrate_v2
            execution_id = await orchestrate_v2(document,commands,query)
            return JSONResponse({'execution_id': execution_id})

    @decode_token
    @inject
    async def orchestrate(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        thisSpanName = "orchestrate"
        with await opentelemetry.getSpan(thisSpanName) as span:
            payload = await request.json()
            patient_id = request["patient_id"]
            tenant_id = request["tenant_id"]
            app_id = request["app_id"]
            document_id = payload.get('document_id')
            token = request["token"]

            priority = payload.get('priority', "default")

            LOGGER.info("Orchestrating document: %s", payload.get('document_id'))
            span.set_attribute("app_id", app_id)
            span.set_attribute("tenant_id", tenant_id)
            span.set_attribute("patient_id", patient_id)
            span.set_attribute("document_id", payload.get('document_id'))

            document = await query.get_document(payload.get('document_id'))
            if document:
                command = Orchestrate( app_id=app_id,
                                      tenant_id=tenant_id,
                                      patient_id=patient_id,
                                      document_id=document_id,
                                      token=token,
                                      priority = OrchestrationPriority(priority)
                                    )
                results = await commands.handle_command(command)
                return JSONResponse(results)

                # document = Document(**document)
                # assert document.patient_id == patient_id
                # assert document.tenant_id == tenant_id
                # assert document.app_id == app_id
                # print(f"Document found: {document.id}")
                # from ...entrypoints.orchestrator import orchestrate_v2
                # execution_id = await orchestrate_v2(document,commands)
                # return JSONResponse({'execution_id': execution_id})

    @inject
    async def run_orchestration(self, request: Request, commands: ICommandHandlingPort):
        with await opentelemetry.getSpan("run_orchestration") as span:

            operation_type: str = request.path_params["operation_type"]
            payload = await request.json()
            document_id = payload.get('document_id')
            priority = payload.get('priority', None)

            LOGGER.debug("Request to run orchestration %s: %s", operation_type, json.dumps(payload, indent=2))

            if priority:
                LOGGER.debug("Priority: %s", priority)
                priority = OrchestrationPriority(priority)
                LOGGER.debug("Priority: %s", priority)

            command = StartOrchestration(
                document_operation_type=operation_type,
                document_id=document_id,
                priority=priority
            )

            try:
                ret = await commands.handle_command(command)
                msg = GenericMessage("Orchestration started")
                return JSONResponse(msg.to_dict(), status_code=200)
            except WindowClosedException as e:
                msg = GenericMessage("Orchestration unavailable")
                msg.details = e.message
                return JSONResponse(msg.to_dict(), status_code=409)

    @inject
    async def queue_e2e_test(self, request: Request, commands: ICommandHandlingPort):
        with await opentelemetry.getSpan("queue_e2e_test") as span:

            if not E2E_TEST_ENABLE:
                LOGGER.warning("E2E test support is not enabled")
                msg = GenericMessage("E2E test disabled")
                return JSONResponse(msg.to_dict(), status_code=200)
            
            operation_type: str = request.path_params["operation_type"]
            runnow: str = request.query_params.get("runnow", "false")  # Default to "false" if not provided
            mode = request.query_params.get("mode", "sample")
            sample_size = None
            if mode == "sample":
                sample_size = request.query_params.get("sample_size", None)

            filename = request.query_params.get("filename", None)

            LOGGER.debug("Request to execute E2E test (runnow: %s)", runnow)

            if runnow.lower() == "true":

                from paperglass.settings import (
                    E2E_OWNER_GOLDEN_REPO_APP_ID,
                    E2E_OWNER_GOLDEN_REPO_TENANT_ID,
                    E2E_OWNER_GOLDEN_RUN_PATIENT_ID
                )

                run_id = get_uuid4()
                command = RunE2ETest(app_id=E2E_OWNER_GOLDEN_REPO_APP_ID,
                                     tenant_id=E2E_OWNER_GOLDEN_REPO_TENANT_ID,
                                     patient_id=E2E_OWNER_GOLDEN_RUN_PATIENT_ID,
                                     mode=mode, sample_size=sample_size, filename=filename,
                                     run_id=run_id)

                try:
                    LOGGER.debug("Running E2E test now")
                    #ret = await commands.handle_command(command)
                    ret = await commands.handle_command_with_explicit_transaction(command)
                    msg = GenericMessage(f"Orchestration E2E Test running now.  runid: {ret.get('run_id')}")                    
                    return JSONResponse(msg.to_dict(), status_code=200)
                except Exception as e:
                    LOGGER.error("Exception when running E2E test: %s", str(e))
                    msg = GenericMessage("Orchestration E2E Test failed to run")
                    msg.details = e.message
                    return JSONResponse(msg.to_dict(), status_code=409)

            else:
                command = QueueE2ETest(mode=mode, sample_size=sample_size, filename=filename)

                try:
                    LOGGER.debug("Queuing E2E test")
                    #ret = await commands.handle_command(command)
                    ret = await commands.handle_command_with_explicit_transaction(command)
                    msg = GenericMessage(f"Orchestration E2E Test queued. runid: {ret.get('run_id')}")
                    return JSONResponse(msg.to_dict(), status_code=200)
                except Exception as e:
                    LOGGER.error("Exception when queuing E2E test: %s", str(e))
                    msg = GenericMessage("Orchestration E2E Test failed to queue")
                    msg.details = e.message
                    return JSONResponse(msg.to_dict(), status_code=409)

    @inject
    async def e2e_test_reassess(self, request: Request, commands: ICommandHandlingPort):
        with await opentelemetry.getSpan("e2e_test_reassess") as span:
            operation_type: str = request.path_params["operation_type"]
            run_id = request.path_params.get("run_id")

            command = ReassessTestCaseSummaryResults(run_id=run_id)
            response = await commands.handle_command_with_explicit_transaction(command)
            return JSONResponse(JsonUtil.clean(response.dict()))
    
    @inject
    async def get_e2e_test_tldr_results(self, request: Request):
        with await opentelemetry.getSpan("get_e2e_test_results") as span:

            try:
                operation_type: str = request.path_params["operation_type"]
                mode = request.path_params.get("mode", "sample")
                f1_threshold = request.query_params.get("f1_threshold", E2E_TEST_ASSERTION_F1_GOOD_LOWER)
                f1_threshold = to_float(f1_threshold, E2E_TEST_ASSERTION_F1_GOOD_LOWER)            
                age_window = request.query_params.get("age_window", E2E_TEST_TLDR_RESULTS_WINDOW_MINUTES)
                age_window = to_int(age_window, E2E_TEST_TLDR_RESULTS_WINDOW_MINUTES)
                
                test_harness = TestHarness()
                results = await test_harness.get_testcase_latest_tldr(mode=mode, age_window=age_window, f1_threshold=f1_threshold)

                return JSONResponse(JsonUtil.clean(results))
            except Exception as e:
                return JSONResponse({"error": str(e)}, status_code=400)


    @inject
    async def get_e2e_test_summary_results(self, request: Request):
        with await opentelemetry.getSpan("get_e2e_test_results") as span:

            operation_type: str = request.path_params["operation_type"]
            mode = request.path_params.get("mode", "sample")

            test_harness = TestHarness()
            results = await test_harness.get_testcase_latest_results(mode=mode)
            

            return JSONResponse(JsonUtil.clean(results.dict()))
    
    @inject
    async def confirm_e2e_test(self, request: Request, commands: ICommandHandlingPort):
        with await opentelemetry.getSpan("confirm_e2e_test") as span:

            payload = await request.json()

            document_id = request.query_params["document_id"]

            command = ConfirmE2ETest(document_id=document_id)

            results = await commands.handle_command(command)

            return JSONResponse(JsonUtil.clean(results))

    @decode_token
    @inject
    async def queue_loadtest_poke(self, request: Request, commands: ICommandHandlingPort):
        with await opentelemetry.getSpan("loadtest_poke") as span:

            if STAGE in ["prod"]:
                LOGGER.warning("Loadtest support is not enabled in %s", STAGE)
                msg = GenericMessage("Not found")
                return JSONResponse(msg.to_dict(), status_code=404)

            loadtest_type: str = request.query_params.get("loadtest_type", "default")
            document_id: str = request.query_params.get("document_id", None)

            payload = await request.json()

            LOGGER.debug("Request to queue loadtest poke: %s", json.dumps(payload, indent=2))

            command = LoadTestPoke(
                app_id=request.get('app_id'),
                tenant_id=request.get('tenant_id'),
                patient_id=request.get('patient_id'),
                loadtest_type=loadtest_type,
                document_id=document_id,
                metadata = payload
            )

            await commands.handle_command(command)

            msg = GenericMessage("Loadtest poke queued")
            return JSONResponse(msg.to_dict(), status_code=200)

    @decode_token
    @inject
    async def run_generic_prompt_step(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):

        thisSpanName = "run_generic_prompt_step"
        with await opentelemetry.getSpan(thisSpanName) as span:

            app_id = request["app_id"]
            tenant_id = request["tenant_id"]
            patient_id = request["patient_id"]
            document_id = ""

            document_operation_definition_id = ""
            document_operation_instance_id = ""

            operation_type: str = request.path_params["operation_type"]
            operation_step: str = request.path_params["operation_step"]
            document_uri: str = request.query_params["document_uri"]
            if "prompt_document_execution_strategy" in request.query_params:
                prompt_document_execution_strategy: str = request.query_params["prompt_document_execution_strategy"]
            else:
                prompt_document_execution_strategy: str = "reference"
            instance_context = {}

            command: ExecuteGenericPromptStep = ExecuteGenericPromptStep(app_id=app_id,
                                                                        tenant_id = tenant_id,
                                                                        patient_id = patient_id,
                                                                        document_id = document_id,
                                                                        step_id = operation_step,
                                                                        document_operation_definition_id=document_operation_definition_id,
                                                                        document_operation_instance_id=document_operation_instance_id,
                                                                        operation_type=operation_type,
                                                                        operation_step=operation_step,
                                                                        doc_storage_uri = document_uri,
                                                                        prompt_document_execution_strategy=prompt_document_execution_strategy,
                                                                        context=instance_context)
            LOGGER.info("FOO")
            ret = await commands.handle_command(command)

            # Ugly, but replace once intial testing is completed
            if "stack_trace" in ret:
                return JSONResponse(ret, status_code=500)
            else:
                return JSONResponse(ret)

    @decode_token
    @inject
    async def orchestrate_v3_page_classification(self, request:Request):
        start_time = time.time()
        payload = await request.json()
        document_id = payload.get('document_id')
        document_operation_instance_id = payload.get('document_operation_instance_id')
        document_operation_definition_id = payload.get('document_operation_definition_id')
        page_number = payload.get('page_number')
        priority = payload.get("priority", "default")
        storage_uri = payload.get('storage_uri')
        from paperglass.usecases.orchestrator import PageClassificationAgent
        await PageClassificationAgent().orchestrate(
            document_id=document_id,
            document_operation_instance_id=document_operation_instance_id,
            document_operation_definition_id=document_operation_definition_id,
            page_number=page_number,
            page_storage_uri=storage_uri
        )
        elapsed_time = time.time() - start_time
        extra = {
            "document_id": document_id,
            "document_operation_instance_id": document_operation_instance_id,
            "page_number": page_number,
            "priority": priority,
            "storage_uri": storage_uri,
            "elapsed_time": elapsed_time
        }
        LOGGER2.info("Orchestration Page Classification", extra=extra)
        return JSONResponse({'status': True})

    @decode_token
    @inject
    async def orchestrate_v3_medication_extraction(self, request:Request):
        starttime = time.time()
        payload = await request.json()
        document_id = payload.get('document_id')
        document_operation_instance_id = payload.get('document_operation_instance_id')
        document_operation_definition_id = payload.get('document_operation_definition_id')
        page_id = payload.get('page_id')
        priority = payload.get("priority", "default")
        labels = payload.get('labels')

        page_number = payload.get('page_number', -1)  # Default to now to avoid error for events created before this field was added
        waittime_start_str = payload.get("waittime_start", now_utc().isoformat()) # Default to now to avoid error for events created before this field was added
        waittime_start = datetime.fromisoformat(waittime_start_str)
        wait_elapsedtime = (now_utc() - waittime_start).total_seconds()

        from paperglass.usecases.orchestrator import MedicationExtractionAgent
        await MedicationExtractionAgent().orchestrate(
            document_id=document_id,
            document_operation_instance_id=document_operation_instance_id,
            document_operation_definition_id=document_operation_definition_id,
            page_id=page_id,
            labels=labels
        )
        elapsed_time = time.time() - starttime
        extra = {
            "document_id": document_id,
            "document_operation_instance_id": document_operation_instance_id,
            "page_id": page_id,
            "page_number": page_number,
            "priority": priority,
            "elapsed_time": elapsed_time,
            "wait_time": wait_elapsedtime,
        }
        LOGGER2.info("Orchestration Medication Extraction", extra=extra)

        return JSONResponse({'status': True})

    @decode_token
    @inject
    async def orchestrate_v3_conditions_extraction(self, request:Request):
        payload = await request.json()
        document_id = payload.get('document_id')
        document_operation_instance_id = payload.get('document_operation_instance_id')
        document_operation_definition_id = payload.get('document_operation_definition_id')
        page_id = payload.get('page_id')
        labels = payload.get('labels')
        from paperglass.usecases.orchestrator import ConditionPromptExtractionAgent
        await ConditionPromptExtractionAgent().orchestrate(
            document_id=document_id,
            document_operation_instance_id=document_operation_instance_id,
            document_operation_definition_id=document_operation_definition_id,
            page_id=page_id,
            labels=labels
        )
        return JSONResponse({'status': True})

    @decode_token
    @inject
    async def orchestrate_v3_allergies_extraction(self, request:Request):
        payload = await request.json()
        document_id = payload.get('document_id')
        document_operation_instance_id = payload.get('document_operation_instance_id')
        document_operation_definition_id = payload.get('document_operation_definition_id')
        page_id = payload.get('page_id')
        labels = payload.get('labels')
        from paperglass.usecases.orchestrator import AllergyExtractionAgent
        await AllergyExtractionAgent().orchestrate(
            document_id=document_id,
            document_operation_instance_id=document_operation_instance_id,
            document_operation_definition_id=document_operation_definition_id,
            page_id=page_id,
            labels=labels
        )
        return JSONResponse({'status': True})

    @decode_token
    @inject
    async def orchestrate_v3_immunizations_extraction(self, request:Request):
        payload = await request.json()
        document_id = payload.get('document_id')
        document_operation_instance_id = payload.get('document_operation_instance_id')
        document_operation_definition_id = payload.get('document_operation_definition_id')
        page_id = payload.get('page_id')
        labels = payload.get('labels')
        from paperglass.usecases.orchestrator import ImmunizationExtractionAgent
        await ImmunizationExtractionAgent().orchestrate(
            document_id=document_id,
            document_operation_instance_id=document_operation_instance_id,
            document_operation_definition_id=document_operation_definition_id,
            page_id=page_id,
            labels=labels
        )
        return JSONResponse({'status': True})

    @decode_token
    @inject
    async def orchestrate_v3_recover(self, request:Request):
        payload = await request.json()
        from ...usecases.orchestrator import recover
        failed_doc_operation_instance_log_id = payload.get('failed_doc_operation_instance_log_id')
        await recover(failed_doc_operation_instance_log_id)
        return JSONResponse({'status': True})


    @decode_token
    @inject
    async def orchestrate_v3_page_classification_dummy(self, request:Request):
        start_time = time.time()
        payload = await request.json()
        document_id = payload.get('document_id')
        page_number = payload.get('page_number')
        storage_uri = payload.get('storage_uri')
        wait_elapsedtime = None
        if "waittime_start" in payload:
            waittime_start_str = payload.get("waittime_start")
            waittime_start = datetime.fromisoformat(waittime_start_str)
            wait_elapsedtime = (now_utc() - waittime_start).total_seconds()

        extra = {
            "document_id": document_id,
            "page_number": page_number,
            "page_storage_uri": storage_uri,
            "payload": payload,
            "wait_time": wait_elapsedtime
        }
        LOGGER2.debug("REST: Orchestration Page Classification", extra=extra)

        from paperglass.usecases.orchestrator_dummy import PageClassificationAgent
        await PageClassificationAgent().orchestrate(
            document_id=document_id,
            page_number=page_number,
            page_storage_uri=storage_uri
        )
        elapsed_time = time.time() - start_time
        extra.update({
            "elapsed_time": elapsed_time
        })
        LOGGER2.info("Orchestration Page Classification", extra=extra)
        return JSONResponse({'status': True})


    @decode_token
    @inject
    async def orchestrate_v3_medication_extraction_dummy(self, request:Request):
        starttime = time.time()
        payload = await request.json()
        document_id = payload.get('document_id')
        page_number = payload.get('page_number', -1)  # Default to now to avoid error for events created before this field was added
        storage_uri = payload.get('storage_uri')
        waittime_start_str = payload.get("waittime_start", now_utc().isoformat()) # Default to now to avoid error for events created before this field was added
        waittime_start = datetime.fromisoformat(waittime_start_str)
        wait_elapsedtime = (now_utc() - waittime_start).total_seconds()

        extra = {
            "document_id": document_id,
            "page_number": page_number,
            "page_storage_uri": storage_uri,
            "payload": payload,
            "wait_time": wait_elapsedtime,
        }
        LOGGER2.debug("REST: Orchestration Page Medication Extraction", extra=extra)

        from paperglass.usecases.orchestrator_dummy import MedicationExtractionAgent
        await MedicationExtractionAgent().orchestrate(
            document_id=document_id,
            page_number=page_number,
            page_storage_uri=storage_uri
        )
        elapsed_time = time.time() - starttime
        extra.update({
            "elapsed_time": elapsed_time
        })
        LOGGER2.info("Orchestration Medication Extraction", extra=extra)

        return JSONResponse({'status': True})


    @inject
    async def status(self, request: Request):

        s_delay = request.query_params.get("delay", "0")
        delay = int(s_delay)

        if delay > 0:
            await asyncio.sleep(delay)

        status = StatusModel.create(
            status = "OK",
            message = "Things are working"
        )
        return JSONResponse(status.dict())
    
    @decode_token
    @inject
    async def status_token(self, request: Request):

        s_delay = request.query_params.get("delay", "0")
        delay = int(s_delay)

        if delay > 0:
            await asyncio.sleep(delay)

        status = StatusModel.create(
            status = "OK",
            message = "Things are working"
        )
        return JSONResponse(status.dict())

    @verify_okta    
    @inject
    async def status_oktatoken(self, request: Request):

        s_delay = request.query_params.get("delay", "0")
        delay = int(s_delay)

        if delay > 0:
            await asyncio.sleep(delay)

        status = StatusModel.create(
            status = "OK",
            message = "Things are working"
        )
        return JSONResponse(status.dict())
    
    @verify_service_okta
    @inject
    async def status_oktaservicetoken(self, request: Request):

        s_delay = request.query_params.get("delay", "0")
        delay = int(s_delay)

        if delay > 0:
            await asyncio.sleep(delay)

        status = StatusModel.create(
            status = "OK",
            message = "Things are working"
        )
        return JSONResponse(status.dict())



    @decode_token
    @inject
    async def medispan_search(self, request: Request, commands: ICommandHandlingPort):
        DEFAULT_MAX_RESULTS = 100
        search_term = request.query_params.get('term')
        enable_llm = request.query_params.get('enable_llm')
        max_results = request.query_params.get('max_results')
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        if enable_llm:
            enable_llm = True
        else:
            enable_llm = False

        if max_results:
            try:
                max_results = int(max_results)
            except Exception as e:
                LOGGER.warning("Invalid max_results value: %s: %s", max_results, str(e))
                max_results = DEFAULT_MAX_RESULTS
        else:
            max_results = DEFAULT_MAX_RESULTS

        try:
            command = FindMedication(app_id=app_id, tenant_id=tenant_id,term=search_term, enable_llm=enable_llm, max_results=max_results)
        except ValidationError as e:
            LOGGER.error("Medispan_search validation error: %s", e.errors())
            return JSONResponse({'success': False, 'errors': e.errors()})
        try:
            drugs:List[MedispanDrug] = await commands.handle_command(command)
        except CommandError as exc:
            LOGGER.error("Medispan_search command error: %s", exc.errors)
            return JSONResponse({'success': False, 'error': str(exc)}, status_code=400)
        return JSONResponse([drug.dict() for drug in drugs] if drugs else [])

    @decode_token
    @inject
    async def medispan_vector_search(self, request: Request, commands: ICommandHandlingPort):
        search_term = request.query_params.get('term')
        enable_llm = request.query_params.get('enable_llm')

        command: FindMedicationWithLLMFilter = FindMedicationWithLLMFilter(term=search_term, enable_llm=enable_llm)

        results: MedispanDrug = await commands.handle_command(command)

        return JSONResponse([x.dict() for x in results])

    @decode_token
    @inject
    async def create_medication(self, request: Request, commands: ICommandHandlingPort):
        with await opentelemetry.getSpan("create_medication") as span:
            payload = await request.json()
            try:
                payload = CreateMedicationRequest(**payload)
            except ValidationError as e:
                return JSONResponse({'success': False, 'errors': e.errors()}, status_code=400)
            medication = await commands.handle_command(CreateMedication(
                app_id=request['app_id'], tenant_id=request['tenant_id'], patient_id=request['patient_id'],
                document_id=payload.document_id,  # page_id=payload.page_id,
                values=payload.values,
                created_by=request['user_id']
            ))
            return JSONResponse(loads(medication.json()))

    @decode_token
    @inject
    async def update_medication(self, request: Request, commands: ICommandHandlingPort):
        medication_id = request.path_params['medication_id']
        payload = await request.json()
        print(request['user_id'])
        try:
            payload = UpdateMedicationRequest(**payload)
        except ValidationError as e:
            return JSONResponse({'success': False, 'errors': e.errors()}, status_code=400)
        medication = await commands.handle_command(UpdateMedication(medication_id=medication_id, values=payload.values,created_by = request["user_id"]))
        return JSONResponse(loads(medication.json()))

    @decode_token
    @inject
    async def delete_medication(self, request: Request, commands: ICommandHandlingPort):
        medication_id = request.path_params['medication_id']
        medication = await commands.handle_command(DeleteMedication(medication_id=medication_id,created_by=request['user_id']))
        return JSONResponse(loads(medication.json()))

    @decode_token
    @inject
    async def undelete_medication(self, request: Request, commands: ICommandHandlingPort):
        medication_id = request.path_params['medication_id']
        medication = await commands.handle_command(UndeleteMedication(medication_id=medication_id,created_by=request['user_id']))
        return JSONResponse(loads(medication.json()))

    @decode_token
    @inject
    async def create_medication_v2(self, request: Request, commands: ICommandHandlingPort):
        payload = await request.json()
        LOGGER.debug("Create Medication V2 payload: %s", payload)
        try:

            medication = payload["medication"]
            # TODO:  Shim for when we start consistently using medispan_id as the key
            medispan_id = None
            classification = None
            if "medispan_id" in medication:
                medispan_id = medication["medispan_id"]
            elif "medispanId" in medication:
                medispan_id = medication["medispanId"]
            if "classification" in medication:
                classification = medication["classification"]

            medication_value = MedicationValue(name=payload.get("medication").get("name"),
                                                medispan_id=medispan_id,
                                                classification=classification,
                                                strength = payload.get("medication").get("strength"),
                                                dosage=payload.get("medication").get("dosage"),
                                                route=payload.get("medication").get("route"),
                                                frequency=payload.get("medication").get("frequency"),
                                                instructions=payload.get("medication").get("instructions"),
                                                form=payload.get("medication").get("form"),
                                                start_date=payload.get("medication").get("startDate"),
                                                end_date=payload.get("medication").get("endDate"),
                                                discontinued_date=payload.get("medication").get("discontinuedDate"),
                                                is_long_standing=payload.get("medication").get("isLongStanding"),
                                                is_nonstandard_dose=payload.get("medication").get("isNonStandardDose")
                                            )
            medication_status = MedicationStatus(status=payload.get("medication").get("medicationStatus",{}).get("status"),
                                                status_reason=payload.get("medication").get("medicationStatus",{}).get("statusReason"),
                                                status_reason_explaination=payload.get("medication").get("medicationStatus",{}).get("statusReasonExplaination")
                                            )
                        
        except ValidationError as e:
            return JSONResponse({'success': False, 'errors': e.errors()}, status_code=400)
        
        command = AddUserEnteredMedication(
            app_id=request['app_id'],
            tenant_id=request['tenant_id'],
            patient_id=request['patient_id'],
            document_id=payload.get("documentId"),  # page_id=payload.page_id,
            created_by=request['user_id'],
            modified_by=request['user_id'],
            medication=medication_value,
            medication_status=medication_status
        )
        
        extra = {
            "payload": payload,
            "medication_value":  medication_value.dict(),
            "command": command.dict()
        }
        LOGGER2.debug("Preparing for AddUserEnteredMedication command", extra=extra)

        user_entered_medication:UserEnteredMedication = await commands.handle_command(command)
        return JSONResponse(json.loads(json.dumps(user_entered_medication.dict(), indent=4, sort_keys=True, default=str)))

    @decode_token
    @inject
    async def update_medication_v2(self, request: Request, commands: ICommandHandlingPort):
        payload = await request.json()

        LOGGER.debug("Updating medication payload: %s", json.dumps(payload, indent=2))

        medication = payload["medication"]
        # TODO:  Shim for when we start consistently using medispan_id as the key
        medispan_id = None
        classification = None
        medication_status = MedicationStatus(status=None,status_reason=None,status_reason_explaination=None)
        if "medispan_id" in medication:
            medispan_id = medication["medispan_id"]
        elif "medispanId" in medication:
            medispan_id = medication["medispanId"]
        if "classification" in medication:
            classification = medication["classification"]

        try:
            medication_profile_reconcilled_medication_id = payload.get("medication").get('id')
            medication_value = MedicationValue(name=payload.get("medication").get("name"),
                                                medispan_id=medispan_id,
                                                classification=classification,
                                                dosage=payload.get("medication").get("dosage"),
                                                strength=payload.get("medication").get("strength"),
                                                form=payload.get("medication").get("form"),
                                                route=payload.get("medication").get("route"),
                                                frequency=payload.get("medication").get("frequency"),
                                                instructions=payload.get("medication").get("instructions"),
                                                start_date=payload.get("medication").get("startDate"),
                                                end_date=payload.get("medication").get("endDate"),
                                                discontinued_date=payload.get("medication").get("discontinuedDate"),
                                                is_long_standing=payload.get("medication").get("isLongStanding"),
                                                is_nonstandard_dose=payload.get("medication").get("isNonStandardDose"),
                                                name_original=payload.get("medication").get("name_original"),
                                            )

            if payload.get("medication").get("medicationStatus"):
                medication_status = MedicationStatus(status=payload.get("medication").get("medicationStatus",{}).get("status"),
                                                    status_reason=payload.get("medication").get("medicationStatus",{}).get("statusReason"),
                                                    status_reason_explaination=payload.get("medication").get("medicationStatus",{}).get("statusReasonExplaination")
                                                )

        except ValidationError as e:
            return JSONResponse({'success': False, 'errors': e.errors()}, status_code=400)

        user_entered_medication:UserEnteredMedication = await commands.handle_command(UpdateUserEnteredMedication(
            app_id=request['app_id'], tenant_id=request['tenant_id'], patient_id=request['patient_id'],
            modified_by=request['user_id'],
            medication_profile_reconcilled_medication_id=medication_profile_reconcilled_medication_id,
            medication=medication_value,
            medication_status=medication_status,
            extracted_medication_references = [ExtractedMedicationReference(
                    document_id = x.get("documentId"),
                    extracted_medication_id= x.get("extractedMedicationId"),
                    document_operation_instance_id= x.get("documentOperationInstanceId"),
                    page_number= x.get("pageNumber")
                ) for x in payload.get("medication",{}).get("extractedMedications")],
            document_id=payload.get("documentId")
        ))
        return JSONResponse(json.loads(json.dumps(user_entered_medication.dict(), indent=4, sort_keys=True, default=str)))

    @decode_token
    @inject
    async def delete_medication_v2(self, request: Request, commands: ICommandHandlingPort, query:IQueryPort):
        medication_id = request.path_params['medication_id']
        patient_id = request["patient_id"]
        tenant_id = request["tenant_id"]
        app_id = request["app_id"]
        user_id = request["user_id"]
        payload = await request.json()

        config:Configuration = await get_config(app_id, tenant_id, query)
        if config and not config.extraction_persisted_to_medication_profile:
            # check if reconcilled medication exists to be deleted (since we do a in memory merge of extracted and reconcilled medications)
            medication_profile:MedicationProfile = await query.get_medication_profile_by_patient_id(patient_id)
            reconcilled_medication = medication_profile.get_reconcilled_medication(medication_id)
            if not reconcilled_medication:
                LOGGER.error("Reconcilled medication not found for deletion: %s. Lets build one", medication_id)
                medication_value = MedicationValue(name=payload.get("medication").get("name"),
                                                    medispan_id=payload.get("medication").get("medispanId"),
                                                    classification=payload.get("medication").get("classification"),
                                                    dosage=payload.get("medication").get("dosage"),
                                                    strength=payload.get("medication").get("strength"),
                                                    form=payload.get("medication").get("form"),
                                                    route=payload.get("medication").get("route"),
                                                    frequency=payload.get("medication").get("frequency"),
                                                    instructions=payload.get("medication").get("instructions"),
                                                    start_date=payload.get("medication").get("startDate"),
                                                    end_date=payload.get("medication").get("endDate"),
                                                    discontinued_date=payload.get("medication").get("discontinuedDate"),
                                                    is_long_standing=payload.get("medication").get("isLongStanding"),
                                                    is_nonstandard_dose=payload.get("medication").get("isNonStandardDose")
                                                )
                medication_status = MedicationStatus(status=None,
                                                    status_reason=None,
                                                    status_reason_explaination=None
                                                )
                user_entered_medication:UserEnteredMedicationAggregate = await commands.handle_command(AddUserEnteredMedication(
                app_id=app_id, tenant_id=tenant_id, patient_id=patient_id,
                modified_by=user_id,

                medication=medication_value,
                medication_status=medication_status,
                extracted_medication_references = [ExtractedMedicationReference(
                        document_id = x.get("documentId"),
                        extracted_medication_id= x.get("extractedMedicationId"),
                        document_operation_instance_id= x.get("documentOperationInstanceId"),
                        page_number= x.get("pageNumber")
                    ) for x in payload.get("medication",{}).get("extractedMedications")],
                document_id=payload.get("documentId")
                ))

                medication_id = user_entered_medication.medication_profile_reconcilled_medication_id

        medication = await commands.handle_command(DeleteReconcilledMedication(
            app_id=app_id, tenant_id=tenant_id, patient_id=patient_id,
            medication_profile_reconcilled_medication_id=medication_id,
            modified_by=request['user_id']))
        return JSONResponse([])

    @decode_token
    @inject
    async def undelete_medication_v2(self, request: Request, commands: ICommandHandlingPort):
        medication_id = request.path_params['medication_id']
        patient_id = request["patient_id"]
        tenant_id = request["tenant_id"]
        app_id = request["app_id"]
        medication = await commands.handle_command(UnDeleteReconcilledMedication(
                app_id=app_id, tenant_id=tenant_id, patient_id=patient_id,
                medication_profile_reconcilled_medication_id=medication_id,
                modified_by=request['user_id']))
        return JSONResponse([])

    @decode_token
    @inject
    async def import_medications(self, request: Request, commands: ICommandHandlingPort,pubsub_adapter:IMessagingPort):
        thisSpanName = "import_host_medications"
        with await opentelemetry.getSpan(thisSpanName) as span:
            patient_id = request["patient_id"]
            tenant_id = request["tenant_id"]
            app_id = request["app_id"]
            ehr_token = request["ehr_token"]
            user_id = request["user_id"]

            span.set_attribute("app_id", app_id)
            span.set_attribute("tenant_id", tenant_id)
            span.set_attribute("patient_id", patient_id)

            try:
                result:Result = await commands.handle_command(ImportMedications(patient_id=patient_id,
                                                            tenant_id=tenant_id,
                                                            app_id=app_id,
                                                            ehr_token=ehr_token,
                                                            created_by=user_id,
                                                            modified_by=user_id)
                                                        )
                result = result.dict()
                # await pubsub_adapter.publish(topic=EXTRACTION_PUBSUB_TOPIC_NAME, 
                # message=dict(
                #             app_id=app_id, 
                #             tenant_id=tenant_id, 
                #             patient_id=patient_id,
                #             ehr_token=ehr_token,
                #             api_token=request["token"],
                #             event_type="import_medications"
                #         ),
                #     ordering_key = DocumentOperationType.MEDICATION_EXTRACTION.value
                # )
                # result = {"success": True}
                return JSONResponse(json.loads(json.dumps(result,indent=4, sort_keys=True, default=str)))
            except Exception as e:
                LOGGER.error("Error importing medications: %s", str(e))
                LOGGER.error(traceback.print_exc())
                return JSONResponse({'success': False, 'error': str(e)}, status_code=500)


    @decode_token
    @inject
    async def update_host_medications(self, request: Request, query:IQueryPort, commands: ICommandHandlingPort):

        try:
            patient_id = request["patient_id"]
            tenant_id = request["tenant_id"]
            app_id = request["app_id"]
            ehr_token = request["ehr_token"]
            user_id = request["user_id"]
            payload = await request.json()
            medications_dict = payload.get("medications")
            profileFilter = payload.get("profileFilter")

            extra = {
                "app_id": app_id,
                "tenant_id": tenant_id,
                "patient_id": patient_id,
                "ehr_token": ehr_token,
                "user_id": user_id,
                "medications_dict": medications_dict,
                "profileFilter": profileFilter
            }

            errored_medications = []
            success_medications = []
            skipped_medications = []

            LOGGER.debug("REST:  Medications payload: %s", medications_dict, extra=extra)

            for medication_dict in medications_dict:
                try:

                    LOGGER.debug("Medication payload: %s", medication_dict, extra=extra)

                    status = await commands.handle_command(UpdateHostMedications(patient_id=patient_id,
                                                                    tenant_id=tenant_id,
                                                                    app_id=app_id,
                                                                    ehr_token=ehr_token,
                                                                    created_by=user_id,
                                                                    modified_by=user_id,
                                                                    medication_dict=medication_dict,
                                                                    profileFilter=None)
                                                                )
                    if status["status"] == "SUCCESS":
                        success_medications.append(medication_dict)
                    elif status["status"] == "SKIPPED":
                        skipped_medications.append(medication_dict)
                    elif status["status"] == "DELETED":
                        pass
                    else:
                        err: str = status["description"]
                        try:
                            err_json = json.loads(err)
                        except Exception:
                            err_json = [err]

                        errored_medications.append({"error": err_json, "medication": medication_dict})

                except Exception as e:
                    extra.update({
                        "error": exceptionToMap(e)
                    })
                    LOGGER.error("Exception while updating host medications: %s  medication_dict: %s", str(e), medication_dict, extra=extra)                    
                    errored_medications.append({"error": [str(e)], "medication":medication_dict})

            ret = {
                "success_medications": success_medications,
                "skipped_medications": skipped_medications,
                "errored_medications": errored_medications
                }

            LOGGER.debug("Host sync operation returned: %s", ret, extra=extra)

            return JSONResponse(ret)
        except Exception as e:
            extra.update({
                "error": exceptionToMap(e)
            })
            LOGGER.error("Error updating host medications: %s", str(e), extra=extra)
            
            msg = GenericMessage(message="Error: " + str(e), details=traceback.format_exc())
            return JSONResponse(msg.to_dict(), response_code=500)

    @decode_token
    @inject
    async def list_document_medication_profile_by_document(self, request: Request, query: IQueryPort):
        document_id = request.path_params['document_id']

        results = await query.list_document_medication_profile_by_document(document_id=document_id)

        if not results:
            LOGGER.info("No document medication profile map found for document %s", document_id)
            results = []
        else:
            LOGGER.debug("Found %d document medication profiles for document %s", len(results), document_id)

        LOGGER.debug("Results: %s", str(results))

        return JSONResponse(results)

    @decode_token
    @inject
    async def map_document_medication_profile(self, request: Request,  query: IQueryPort):
        document_id = request.path_params['document_id']

        results = await query.list_document_medication_profile_by_document(document_id=document_id)

        m = {}
        if not results:
            LOGGER.info("No document medication profile map found for document %s", document_id)
        else:
            LOGGER.debug("Found %d document medication profiles for document %s", len(results), document_id)

            for record in results:
                m[record.key] = record

        return JSONResponse(m)


    @decode_token
    @inject
    async def add_document_medication_profile(self, request: Request, commands: ICommandHandlingPort):
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id'],
        document_id = request.path_params['document_id']
        key = request.path_params['key']
        payload = await request.json()
        user_id = request['user_id']

        try:
            payload = CreateDocumentMedicationProfileRequest(**payload)
        except ValidationError as e:
            LOGGER.error("Validation error: %s", e.errors())
            return JSONResponse({'success': False, 'errors': e.errors()}, status_code=400)

        command = CreateDocumentMedicationProfileCommand(
            app_id=request['app_id'], tenant_id=request['tenant_id'], patient_id=request['patient_id'],
            document_id=payload.document_id,
            page_id = payload.page_id,
            key=key,
            values=payload.values,
            user_id=user_id
        )
        profile_item = await commands.handle_command(command)

        return JSONResponse(profile_item)

        #return JSONResponse(loads(profile_item.json()))


    @decode_token
    @inject
    async def delete_document_medication_profile(self, request: Request, commands: ICommandHandlingPort):
        key = request.path_params['key']

        command = DeleteDocumentMedicationProfileCommand(key=key)

        results = await commands.handle_command(command)

        if not results:
            LOGGER.info("Unable to delete profile: No document medication profile found for key %s", key)
        else:
            LOGGER.debug("Document medication profile for key %s deleted", key)

        return JSONResponse(loads(results.json()))

    @decode_token
    @inject
    async def import_host_attachments(self, request: Request, commands: ICommandHandlingPort,pubsub_adapter:IMessagingPort):
        thisSpanName = "import_host_attachments"
        with await opentelemetry.getSpan(thisSpanName) as span:
            app_id = request['app_id']
            tenant_id = request['tenant_id']
            patient_id = request['patient_id']
            ehr_token = request['ehr_token']

            span.set_attribute("app_id", app_id)
            span.set_attribute("tenant_id", tenant_id)
            span.set_attribute("patient_id", patient_id)
            if STAGE in ["local", "dev", "qa"]:
                span.set_attribute("ehr_token", ehr_token)
                LOGGER2.debug("Importing host attachments for app_id: %s, tenant_id: %s, patient_id: %s, ehr_token: %s", app_id, tenant_id, patient_id, ehr_token)
            else:
                LOGGER2.debug("Importing host attachments for app_id %s, tenant_id %s, patient_id %s", app_id, tenant_id, patient_id)

            try:
                ret = await commands.handle_command(ImportHostAttachments(app_id=app_id, tenant_id=tenant_id, patient_id=patient_id,ehr_token=ehr_token,api_token=request["token"]))
                # await pubsub_adapter.publish(topic=EXTRACTION_PUBSUB_TOPIC_NAME, 
                # message=dict(
                #             app_id=app_id, 
                #             tenant_id=tenant_id, 
                #             patient_id=patient_id,
                #             ehr_token=ehr_token,
                #             api_token=request["token"],
                #             event_type="import_attachments"
                #         ),
                #     ordering_key = DocumentOperationType.MEDICATION_EXTRACTION.value
                # )
                # ret = {"success": True}
                return JSONResponse(json.loads(json.dumps(ret, indent=4, sort_keys=True, default=str)))
            except CommandError as e:
                LOGGER.error("Error importing host attachments: CommandError: %s", str(e))
                span.set_status(StatusCode.ERROR, str(e))
                msg = GenericMessage("Unable to retrieve attachments from EHR", details=str(e))
                LOGGER.error("Returning message: %s", msg.to_dict())
                return JSONResponse(msg.to_dict(), status_code=500)
            except  ClientConnectorError as e:
                LOGGER.error("Error importing host attachments: ClientConnectorError: %s", str(e))
                span.set_status(StatusCode.ERROR, str(e))
                msg = GenericMessage("Unable to retrieve attachments from EHR", details=str(e))
                return JSONResponse(msg.to_dict(), status_code=500)
            except  Exception as e:
                LOGGER.error("Error importing host attachments: Exception: %s", str(e))
                span.set_status(StatusCode.ERROR, str(e))
                msg = GenericMessage("Unable to retrieve attachments from EHR", details=str(e))
                return JSONResponse(msg.to_dict(), status_code=500)

    @decode_token
    @inject
    async def extract(self, request: Request, commands: ICommandHandlingPort,app_integration_adapter: IApplicationIntegration):
        document_id = request.path_params['document_id']
        if os.environ.get('CLOUD_PROVIDER') == 'local':
            from ...entrypoints.orchestrator import orchestrate_for_new_transaction
            await orchestrate_for_new_transaction(request["app_id"],request["app_id"],request["app_id"],document_id)
            return JSONResponse({'success': False, 'message': 'Extraction is not supported in local environment'})

        token = request["token"]
        integration_project_name=INTEGRATION_PROJECT_NAME
        json_payload={
            "START_CLOUD_TASK_API":f"{SELF_API}/start_cloud_task",
            "CLOUD_TASK_ARGS":{
                "location":"us-east4",
                "url":f"{SELF_API}/orchestrate",
                "queue":CLOUD_TASK_QUEUE_NAME,
                "service_account_email":SERVICE_ACCOUNT_EMAIL,
                "payload":{"document_id": document_id}
            },
            "TOKEN":f"Bearer {token}"
        }
        trigger_id = APPLICATION_INTEGRATION_TRIGGER_ID
        result = await app_integration_adapter.start(integration_project_name, json_payload, trigger_id)
        return JSONResponse(result)


    @decode_token
    @inject
    async def get_reference_list(self, request: Request, query: IQueryPort, commands: ICommandHandlingPort):
        patient_id = request["patient_id"]
        tenant_id = request["tenant_id"]
        app_id = request["app_id"]
        ehr_token = request['ehr_token']

        category = request.path_params["category"]
        list = request.path_params["list"]

        try:

            if category == "external" and list == "classification":

                command = GetHostMedicationClassifications(app_id=app_id, tenant_id=tenant_id, patient_id=patient_id, ehr_token=ehr_token)
                result = await commands.handle_command(command)
            else:
                msg = GenericMessage(f"Category {category} and list {list} not supported")
                return JSONResponse(msg.to_dict(), status_code=404)

            return JSONResponse(json.loads(result.json()))
        except Exception as e:
            msg = GenericMessage(f"Exception retrieving reference data for category {category} and list {list}: " + str(e), details=traceback.format_exc())
            LOGGER.error("Exception retrieving reference data for category %s and list %s: %s  %s", category, list, str(e), traceback.format_exc())
            return JSONResponse(msg.to_dict(), status_code=500)

    @decode_token
    @inject
    async def get_setting(self, request: Request):
        setting_key = request.path_params["key"]

        # Only settings in the map can be retrieved. Prevents exposure of senstive settings.
        if setting_key not in SETTINGS_MAP:
            msg = GenericMessage(f"Forbidden", details=f"Not permitted to view setting key {setting_key}")
            return JSONResponse(msg.to_dict(), status_code=403)

        ret = {
            "settings": SETTINGS_MAP.get(setting_key),
            "env": os.environ.get(setting_key)
        }

        return JSONResponse(ret)


    @decode_token
    @inject
    async def get_extracted_clinical_data(self, request: Request, query: IQueryPort):
        clinical_data_type = request.path_params["clinical_data_type"]
        patient_id = request["patient_id"]
        app_id = request["app_id"]
        tenant_id = request["tenant_id"]
        document_ids = request.query_params.get('documentIds')
        document_ids:List[str] = document_ids.split(",") if document_ids else []

        if clinical_data_type == "conditions":
            extracted_conditions:List[ExtractedCondition] = await ConditionsService().get_extracted_conditins(document_ids, query)
            return JSONResponse(json.loads(json.dumps([x.dict() for x in extracted_conditions], indent=4, sort_keys=True, default=str)))
        else:
            extracted_clinical_data:List[ExtractedClinicalData] = await get_extracted_clinical_data(clinical_data_type, document_ids,query)
            return JSONResponse(json.loads(json.dumps([x.dict() for x in extracted_clinical_data], indent=4, sort_keys=True, default=str)))

    @decode_token
    @inject
    async def get_config(self, request: Request, query: IQueryPort):
        app_id = request["app_id"]
        tenant_id = request["tenant_id"]
        config:Configuration = await get_config(app_id, tenant_id, query)

        config_dict = config.get_ui_settings()
        
        #return JSONResponse(json.loads(json.dumps(config.dict(), indent=4, sort_keys=True, default=str)))
        return JSONResponse(json.loads(json.dumps(config_dict, indent=4, sort_keys=True, default=str)))

    @decode_token
    @inject
    async def get_document_operation_definition_config(self, request: Request, query: IQueryPort):
        operation_type = request.path_params["operation_type"]

        LOGGER.debug("Retrieving Document Operation Definition for %s", operation_type)
        doc_op_defs = await query.get_document_operation_definition_by_op_type(operation_type)

        doc_op_def = doc_op_defs[0] if doc_op_defs else None

        if doc_op_def is not None:
            return JSONResponse(json.loads(json.dumps(doc_op_def.dict(), cls=DateTimeEncoder)))
        else:
            return JSONResponse({}, status_code=404)

    @decode_token
    @inject
    async def get_brute_force_search_based_evidence_for_clinical_data(self, request: Request, storage:IStoragePort,query: IQueryPort):
        extracted_clinical_data_id = request.query_params.get('extractedClinicalDataId')
        extracted_clinical_string = request.query_params.get('extractedClinicalString')
        extracted_clinical_string = extracted_clinical_string.lower()
        clinical_data:ExtractedClinicalData = await query.get_extracted_clinical_data_by_id(extracted_clinical_data_id)
        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']

        if clinical_data:
            page_raw_ocr = await storage.get_page_ocr(app_id,tenant_id,patient_id,clinical_data.document_id,clinical_data.page_id,ocr_type=OCRType.raw)
            page = await query.get_page(clinical_data.document_id,int(clinical_data.page_number))
            page = Page(**page)
            page_annotations = page.get_ocr_page_line_annotations(json.loads(page_raw_ocr))

            #LOGGER.debug("Page annotations: %s", json.dumps([x.dict() for x in page_annotations], indent=4))

            config:Configuration = Configuration()
            try:
                config = await get_config(app_id, tenant_id, query)
            except Exception as e:
                LOGGER.error("Exception in get_config: %s", str(e))

            evidence_linking = EvidenceLinking(config)

            evidences = [x.token().dict() for x in page_annotations if extracted_clinical_string in x.token().text.lower().replace('\n', '').rstrip()]

            try:
                #Fallback in case where the medication does not match a token specifically in the list of tokens
                if len(evidences) == 0:
                    LOGGER.warn("Pass 1:  No evidence found for extracted clinical data: %s  Running pass 2...", extracted_clinical_string)
                    evidences = await evidence_linking.evidence_matching_loose(extracted_clinical_string, page_annotations)

                tokens = []
                if len(evidences) == 0:
                    tokens = extracted_clinical_string.split("-")
                    LOGGER.warn("Pass 2:  No evidence found for extracted clinical data: %s  Tokenizing name and running pass 3...", extracted_clinical_string)
                    evidences = await evidence_linking.evidence_multiterm_matching_loose(tokens, page_annotations)

                if len(evidences) == 0:
                    LOGGER.warn("Pass 3:  No evidence found for tokenized extracted clinical data: %s  No more passes", tokens)

                LOGGER.debug("Evidences: %s", json.dumps(evidences, indent=2))
            except Exception as e:
                LOGGER.error("Exception in additional evidence search for clinical data '%s': %s", extracted_clinical_string, str(e))

            return JSONResponse(evidences)
        return JSONResponse([])

    @decode_token
    @inject
    async def get_brute_force_search_based_evidence_for_conditions(self, request: Request, storage:IStoragePort,query: IQueryPort):
        evidence_snippet = request.query_params.get('evidenceSnippet')
        document_id = request.query_params.get('documentId')
        page_number = request.query_params.get('pageNumber')
        evidence_snippet = evidence_snippet.lower()
        start_position = request.query_params.get('startPosition')
        end_position = request.query_params.get('endPosition')

        app_id = request['app_id']
        tenant_id = request['tenant_id']
        patient_id = request['patient_id']

        if evidence_snippet:

            config:Configuration = Configuration()
            try:
                config = await get_config(app_id, tenant_id, query)
            except Exception as e:
                LOGGER.error("Exception in get_config: %s", str(e))

            evidence_linking = EvidenceLinking(config)

            page = await query.get_page(document_id,int(page_number))
            page = Page(**page)
            page_raw_ocr = await storage.get_page_ocr(app_id,tenant_id,patient_id,document_id,page.id,ocr_type=OCRType.raw)
            #print(json.loads(page_raw_ocr).get("page").get("lines"))
            page_annotations = page.get_ocr_page_line_annotations(json.loads(page_raw_ocr), start_position, end_position)

            min_x1 = None
            max_x2 = None
            min_y1 = None
            max_y2 = None
            text = ""
            for page_annotation in page_annotations:
                min_x1 = min(page_annotation.token().x1, min_x1) if min_x1 else page_annotation.token().x1
                max_x2 = max(page_annotation.token().x2, max_x2) if max_x2 else page_annotation.token().x2
                min_y1 = min(page_annotation.token().y1, min_y1) if min_y1 else page_annotation.token().y1
                max_y2 = max(page_annotation.token().y2, max_y2) if max_y2 else page_annotation.token().y2

            return JSONResponse([AnnotationToken(x1 = min_x1, x2 = max_x2, y1 = min_y1, y2 = max_y2, text = text, orientation=page_annotation.token().orientation).dict()])

            return JSONResponse([x.token().dict() for x in page_annotations])
            evidences = [x.token().dict() for x in page_annotations if evidence_snippet in x.token().text.lower().replace('\n', '').rstrip()]

            try:
                #Fallback in case where the medication does not match a token specifically in the list of tokens
                if len(evidences) == 0:
                    LOGGER.warn("Pass 1:  No evidence found for extracted clinical data: %s  Running pass 2...", evidence_snippet)
                    evidences = await evidence_linking.evidence_matching_loose(evidence_snippet, page_annotations)

                tokens = []
                if len(evidences) == 0:
                    tokens = evidence_snippet.split("-")
                    LOGGER.warn("Pass 2:  No evidence found for extracted clinical data: %s  Tokenizing name and running pass 3...", evidence_snippet)
                    evidences = await evidence_linking.evidence_multiterm_matching_loose(tokens, page_annotations)

                if len(evidences) == 0:
                    LOGGER.warn("Pass 3:  No evidence found for tokenized extracted clinical data: %s  No more passes", tokens)

                LOGGER.debug("Evidences: %s", json.dumps(evidences, indent=2))
            except Exception as e:
                LOGGER.error("Exception in additional evidence search for clinical data '%s': %s", evidence_snippet, str(e))

            return JSONResponse(evidences)
        return JSONResponse([])

    @verify_okta
    @inject
    async def assess_documents(self, request: Request, query: IQueryPort):
        """Assess documents from the last 24 hours that haven't completed within the accepted window."""
        thisSpanName = "assess_documents"
        with await opentelemetry.getSpan(thisSpanName) as span:
                try:
                    # Get the accepted processing window in minutes from query params, default to 30 minutes
                    accepted_window = float(request.query_params.get('accepted_window_minutes', 30))
                    search_time = float(request.query_params.get('search_time_hours',24))
                    # Calculate the time threshold for the last x hours
                    time_threshold = now_utc() - timedelta(hours=search_time)

                    # Get all documents from the last 24 hours
                    documents = await query.get_documents_by_time_range(time_threshold)
                    assessments = []
                    for doc in documents:
                        # Calculate processing time
                        if doc.created_at:
                            processing_time_seconds = (now_utc() - doc.created_at).total_seconds()
                            processing_time_minutes = processing_time_seconds / 60

                            # If over 60 minutes, convert to hours
                            if processing_time_minutes > 60:
                                processing_time = processing_time_minutes / 60  # Convert to hours
                                time_unit = "hours"
                            else:
                                processing_time = processing_time_minutes
                                time_unit = "minutes"
                            is_delayed = processing_time_seconds > (accepted_window * 60)

                            assessment = DocumentAssessment(
                            document_id=doc.id,
                            created_at=doc.created_at.isoformat(),
                            processing_time=processing_time,
                            processing_time_unit = time_unit,
                            is_delayed=is_delayed
                        )
                        assessments.append(assessment)

                    return JSONResponse([assessment.dict() for assessment in assessments])

                except Exception as e:
                    LOGGER.error(f"Error in assess_documents: {str(e)}")
                    return JSONResponse(
                        {"error": "Failed to assess documents", "details": str(e)},
                        status_code=500
                    )
                
    @inject
    async def sync_golden_dataset(self, request: Request):
        with await opentelemetry.getSpan("sync_golden_dataset") as span:
            try:
                syncer = GoldenDatasetSync()
                updated, created, total_tc = await syncer.sync_golden_dataset()
                msg = GenericMessage("Golden Dataset sync completed successfully", details= f"{updated} updated Testcases, {created} created TestCases out of {total_tc} TestCases")
                return JSONResponse(msg.to_dict(), status_code=200)
            except Exception as e:
                LOGGER.error(f"Error in Golden Dataset sync: {str(e)}")
                LOGGER.error(traceback.format_exc())
                msg = GenericMessage(
                    "Error running Golden Dataset sync", 
                    details=str(e)
                )
                return JSONResponse(msg.to_dict(), status_code=500)         


    @inject
    async def update_document_status_v5(self, request:Request, commands: ICommandHandlingPort, query:IQueryPort):
        operation_type_str = request.path_params['operation_type']
        operation_type = DocumentOperationType(operation_type_str)

        payload = await request.json()
        document_id = payload.get("document_id")
        patient_id = payload.get("patient_id")
        app_id = payload.get("app_id")
        tenant_id = payload.get("tenant_id")
        status = payload.get("status")
        operation_instance_id = payload.get("run_id")     
        elapsed_time = payload.get("elapsed_time", None)
        pipelines = payload.get("pipelines", None)   

        if operation_type == DocumentOperationType.MEDICATION_EXTRACTION:
            return await self.update_document_status_v4(request, commands, query)

        config:Configuration = await get_config(app_id, tenant_id, query)
        
        if not config.enable_v4_orchestration_engine_parallel_processing or config.orchestration_engine_version == "v4":
            await commands.handle_command(UpdateDocumentStatusSnapshot(
                        document_id=document_id,
                        patient_id=patient_id,
                        app_id=app_id,
                        tenant_id=tenant_id,
                        doc_operation_status_snapshot=DocumentOperationStatusSnapshot(
                            operation_type=DocumentOperationType.ENTITY_EXTRACTION,
                            status=status,
                            end_time=datetime.now(timezone.utc).isoformat(),
                            operation_instance_id=operation_instance_id,
                            elapsed_time=elapsed_time,
                            pipelines=pipelines
                        )
                    ))
        else:
            LOGGER2.debug("Skipping updating document status since pipeline is in parallel processing mode")
        
        return JSONResponse({"success": True})


    @inject
    async def update_document_status_v4(self, request:Request, commands: ICommandHandlingPort, query:IQueryPort):
        payload = await request.json()
        document_id = payload.get("document_id")
        patient_id = payload.get("patient_id")
        app_id = payload.get("app_id")
        tenant_id = payload.get("tenant_id")
        status = payload.get("status")
        operation_instance_id = payload.get("run_id")

        config:Configuration = await get_config(app_id, tenant_id, query)

        if config.extraction.retry.offhours_retry_enabled:
            if status in [DocumentOperationStatus.FAILED]:
                await commands.handle_command(QueueDeferredOrchestration(document_operation_type=DocumentOperationType.MEDICATION_EXTRACTION, document_id=document_id))

        
        
        if not config.enable_v4_orchestration_engine_parallel_processing or config.orchestration_engine_version == "v4":
            await commands.handle_command(UpdateDocumentStatusSnapshot(
                        document_id=document_id,
                        patient_id=patient_id,
                        app_id=app_id,
                        tenant_id=tenant_id,
                        doc_operation_status_snapshot=DocumentOperationStatusSnapshot(
                            operation_type=DocumentOperationType.MEDICATION_EXTRACTION,
                            status=status,
                            end_time=datetime.now(timezone.utc).isoformat(),
                            operation_instance_id=operation_instance_id
                        )
                    ))
        else:
            LOGGER2.debug(f"Skipping updating document status since pipeline is in parallel processing mode")
        
        return JSONResponse({"success": True})
    
    @inject
    async def create_medications_v4(self, request:Request, commands: ICommandHandlingPort):
        from paperglass.usecases.v4.medications import create_medications
        payload = await request.json()
        document_id = payload.get("document_id")
        medications_storage_uri = payload.get("medications_storage_uri")
        run_id = payload.get("run_id")
        patient_id = payload.get("patient_id")
        app_id = payload.get("app_id")
        tenant_id = payload.get("tenant_id")
        page_number = payload.get("page_number")
        
        try:
            await create_medications(document_id,page_number,run_id, medications_storage_uri)
        except Exception as e:
            LOGGER2.error(f"Error processing medications from {medications_storage_uri}: {traceback.format_exc()}",extra={})
            await commands.handle_command(UpdateDocumentStatusSnapshot(
                    document_id=document_id,
                    patient_id=patient_id,
                    app_id=app_id,
                    tenant_id=tenant_id,
                    doc_operation_status_snapshot=DocumentOperationStatusSnapshot(
                        operation_instance_id=run_id,
                        operation_type=DocumentOperationType.MEDICATION_EXTRACTION,
                        status=DocumentOperationStatus.FAILED,
                        end_time=datetime.now(timezone.utc).isoformat()
                    )
                ))
            
        return JSONResponse({"success": True})
    
    @decode_token
    @inject
    async def trigger_page_ocr_v4(self, request:Request):
        from paperglass.usecases.v4.ocr import init_page_ocr
        app_id = request["app_id"]
        tenant_id = request["tenant_id"]
        patient_id = request["patient_id"]
        document_id = request.path_params["document_id"]
        page_number = request.path_params["page_number"]
        result:Result = await init_page_ocr(
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            document_id=document_id,
            page_number=page_number
        )
        return JSONResponse({"success":result.success, "message":result.return_data})
    
    @decode_token
    @inject
    async def process_page_ocr_v4(self, request:Request):
        from paperglass.usecases.v4.ocr import process_page_ocr
        app_id = request["app_id"]
        tenant_id = request["tenant_id"]
        patient_id = request["patient_id"]
        document_id = request.path_params["document_id"]
        page_number = request.path_params["page_number"]
        result:Result = await process_page_ocr(
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            document_id=document_id,
            page_number=page_number
        )
        return JSONResponse({"success":result.success, "message":result.return_data})

    @decode_token
    @inject
    async def get_ocr_v4_status(self, request:Request):
        from paperglass.usecases.v4.ocr import get_page_ocr_status
        from paperglass.domain.values import PageOcrStatus
        app_id = request["app_id"]
        tenant_id = request["tenant_id"]
        patient_id = request["patient_id"]
        document_id = request.path_params["document_id"]
        page_number = request.path_params["page_number"]
        page_ocr_status:PageOcrStatus = await get_page_ocr_status(
            app_id=app_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            document_id=document_id,
            page_number=page_number
        )
        return JSONResponse({"status":page_ocr_status.value}  )

    @decode_token
    @inject
    async def add_platform_annotation(self, request: Request):
        name = request.query_params.get('name')
        description = request.query_params.get('description')

        annotation_labels = {
            "owner": "balki",
            "business-unit": "viki",
            "environment": "stage",
            "application": "",
            "service": ""
        }        

        from google.cloud import monitoring_v3
        from google.protobuf.timestamp_pb2 import Timestamp
        from datetime import datetime

        project_id = GCP_PROJECT_ID
        client = monitoring_v3.NotificationChannelServiceClient()
        project_name = f"projects/{project_id}"
        now = now_utc()
        timestamp = Timestamp()
        timestamp.FromDatetime(now)

        annotation = monitoring_v3.NotificationChannel(
            display_name="Load Test",
            description=description,
            labels=annotation_labels,
            creation_record=monitoring_v3.MutationRecord(mutate_time=timestamp)
        )
        
        client.create_notification_channel(name=project_name, notification_channel=annotation)              

        return JSONResponse({"success": True})

    #@decode_token  #TODO: Add verify token is signed and not expired
    @verify_service_okta
    @inject        
    async def on_document_external_create(self, request: Request, commands: ICommandHandlingPort, query:IQueryPort):
        from starlette.responses import Response
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        extra = {}
        try:

            body = await request.body()
            LOGGER2.debug('Received document external create event raw message event: %s', body, extra=extra)
            
            data = json.loads(body)  # Body will be of the type GenericExternalDocumentCreateEventRequestApi or a varient of GenericExternalDocumentCreateEventRequestBase

            # Determine the repositoryType
            repository_type = data.get("repositoryType")
            if not repository_type:
                raise ValueError("Missing repositoryType in the data")

            # Get the corresponding class based on repositoryType
            event_class = REPOSITORY_TYPE_MAP.get(repository_type, GenericExternalDocumentCreateEventRequestBase)

            # Instantiate the class
            event = event_class(**data)

            if event.repositoryType != ExternalDocumentRepositoryType.API:                
                raise ValueError("Unsupported repositoryType %s", event.repositoryType)

            # This will call ExternalCreateDocumentTask which will in turn call the ImportHostAttachmentFromExternalApi
            command = ImportHostAttachmentFromExternalApiTask.from_request(event)
            
            await commands.handle_command(command)

            extra = {
                "data": data,
                "repository_type": repository_type,
            }
            LOGGER2.debug('Received document external create event: %s', json.dumps(data, indent=2), extra=extra)

            return Response(status_code=201)
        
        except ValidationError as e:
            extra = {
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Validation error processing external document create event', exc_info=True, extra=extra)

            msg = GenericMessage("Validation error processing external document create event", str(e))
            return JSONResponse(msg.to_dict(), status_code=400)

        except ValueError as e:
            extra = {
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Validation error processing external document create event', exc_info=True, extra=extra)

            msg = GenericMessage("Validation error processing external document create event", str(e))
            return JSONResponse(msg.to_dict(), status_code=400)

        except Exception as e:
            extra = {                
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Error processing external document create event', exc_info=True, extra=extra)            
            
            msg = GenericMessage("Error processing external document create event", str(e))
            return JSONResponse(msg.to_dict(), status_code=500)
    
    
    @require_service_auth
    @inject        
    async def on_document_internal_create(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        """
        Internal endpoint for VIKI service-to-service document creation.
        This endpoint is used by Admin API and other internal services to submit documents for processing.
        Uses the same logic as external endpoint but with service authentication.
        """
        from starlette.responses import Response
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        extra = {}
        try:
            body = await request.body()
            LOGGER2.debug('Received document internal create event raw message: %s', body, extra=extra)
            
            data = json.loads(body)  # Body will be of the type GenericExternalDocumentCreateEventRequestApi or a variant of GenericExternalDocumentCreateEventRequestBase
            
            # Determine the repositoryType
            repository_type = data.get("repositoryType")
            if not repository_type:
                raise ValueError("Missing repositoryType in the data")
                
            # Get the corresponding class based on repositoryType
            event_class = REPOSITORY_TYPE_MAP.get(repository_type, GenericExternalDocumentCreateEventRequestBase)
            
            # Instantiate the class
            event = event_class(**data)
            
            # Validate supported repository types (same as external)
            if event.repositoryType not in [ExternalDocumentRepositoryType.API, ExternalDocumentRepositoryType.URI]:                
                raise ValueError(f"Unsupported repositoryType {event.repositoryType}")
            
            # Create command for processing (same logic as external)
            command = ImportHostAttachmentFromExternalApiTask.from_request(event)
            
            await commands.handle_command(command)
            
            extra.update({
                "data": data,
                "repository_type": repository_type,
            })
            LOGGER2.debug('Received document internal create event: %s', json.dumps(data, indent=2), extra=extra)

            # Return same response format as external API
            response_data = ExternalDocumentCreateResponse(
                message="Document creation request processed successfully",
                status="created",
                hostFileId=event.hostFileId
            )
            return JSONResponse(response_data.dict(), status_code=201)
        
        except ValidationError as e:
            extra = {
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Validation error processing internal document create event', exc_info=True, extra=extra)

            msg = GenericMessage("Validation error processing internal document create event", str(e))
            return JSONResponse(msg.to_dict(), status_code=400)

        except ValueError as e:
            extra = {
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Validation error processing internal document create event', exc_info=True, extra=extra)

            msg = GenericMessage("Validation error processing internal document create event", str(e))
            return JSONResponse(msg.to_dict(), status_code=400)

        except Exception as e:
            extra = {                
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Error processing internal document create event', exc_info=True, extra=extra)            
            
            msg = GenericMessage("Error processing internal document create event", str(e))
            return JSONResponse(msg.to_dict(), status_code=500)
    
    
    @decode_token  #TODO: Add verify token is signed and not expired
    @inject        
    async def on_document_external_create_task(self, request: Request, commands: ICommandHandlingPort):
        from starlette.responses import Response
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        extra = {}
        try:
            body = await request.body()  # body will be of type GenericExternalDocumentCreateEventRequestApi
            LOGGER2.debug('Received document external create raw message from cloud task: %s', body, extra=extra)
            
            data = json.loads(body) # Body will be of type ImportHostAttachmentFromExternalApi            

            command = ImportHostAttachmentFromExternalApi(**data)

            extra = {
                "command": command.dict(),
            }            

            await commands.handle_command(command)

            LOGGER2.debug('Processed document external create task %s', json.dumps(data, indent=2), extra=extra)

            return Response(status_code=201)
        
        except ValidationError as e:
            extra = {
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Validation error processing CreateDocument from on_document_external_create_task', exc_info=True, extra=extra)

            msg = GenericMessage("Validation error processing CreateDocument from on_document_external_create_task", str(e))
            return JSONResponse(msg.to_dict(), status_code=400)

        except ValueError as e:
            extra = {
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Value error processing CreateDocument from on_document_external_create_task', exc_info=True, extra=extra)

            msg = GenericMessage("Value error processing CreateDocument from on_document_external_create_task", str(e))
            return JSONResponse(msg.to_dict(), status_code=400)

        except Exception as e:
            extra = {                
                "error": exceptionToMap(e),
            }
            LOGGER2.error('Error processing CreateDocument from on_document_external_create_task', exc_info=True, extra=extra)            
            
            msg = GenericMessage("Error processing CreateDocument from on_document_external_create_task", str(e))
            return JSONResponse(msg.to_dict(), status_code=500)

    @inject
    async def create_entity_schema(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        """Delegate to AdminAdapter for entity schema creation."""
        admin_adapter = AdminAdapter()
        return await admin_adapter.create_entity_schema(request, commands, query)

    @inject
    async def get_entity_schema_by_fqn(self, request: Request, query: IQueryPort):
        """Delegate to AdminAdapter for entity schema retrieval by FQN."""
        admin_adapter = AdminAdapter()
        return await admin_adapter.get_entity_schema(request, query)

    @inject
    async def get_entity_schema(self, request: Request, query: IQueryPort):
        """Get an entity schema by app_id and schema_id with optional usecase parameter for scope-specific JSON schema format."""
        from paperglass.domain.models_common import GenericMessage
        from paperglass.usecases.entityschema import get_entity_schema_for_usecase
                
        app_id = request.path_params['app_id']
        schema_id = request.path_params['schema_id']
        usecase = request.query_params.get('usecase')

        extra = {
            "app_id": app_id,
            "schema_id": schema_id,
            "usecase": usecase,
        }
        
        try:
            LOGGER2.debug("Retrieving entity schema for app_id: %s, schema_id: %s with usecase: %s", app_id, schema_id, usecase, extra=extra)
            schema_dict = await get_entity_schema_for_usecase(app_id, schema_id, usecase, query)
            return JSONResponse(schema_dict)
            
        except ValueError as e:
            # Handle schema not found
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.warning("Entity schema not found for app_id: %s, schema_id: %s", app_id, schema_id, extra=extra)
            msg = GenericMessage("Entity schema not found")
            return JSONResponse(msg.to_dict(), status_code=404)
            
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error retrieving entity schema: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False, 
                'error': 'Error retrieving entity schema',
                'details': str(e)
            }, status_code=500)

    #@verify_gcp_service_account
    @inject
    async def create_entities_v5(self, request: Request, commands: ICommandHandlingPort):
        """
        Handle POST /v5/entities endpoint.
        Receives EntityWrapper objects from entity_extraction and calls CommandHandler with ImportEntities command.
        Validates GCP service account identity token in Authorization header.
        """
        try:
            payload = await request.json()
            
            # Log the received EntityWrapper data
            extra = {
                "endpoint": "/v5/entities",
                "payload": payload
            }
            LOGGER2.info("Received EntityWrapper data from entity_extraction", extra=extra)
            
            # Create and execute ImportEntities command
            command = ImportEntities(entity_wrapper=payload)
            await commands.handle_command(command)
            
            return JSONResponse({
                'success': True,
                'message': 'EntityWrapper data processed successfully'
            })
            
        except json.JSONDecodeError as e:
            LOGGER.error("Invalid JSON in POST /v5/entities request: %s", str(e))
            return JSONResponse({
                'success': False,
                'error': 'Invalid JSON format'
            }, status_code=400)
            
        except Exception as e:
            LOGGER.error("Error processing POST /v5/entities request: %s", str(e))
            return JSONResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)

    @inject
    async def create_or_update_app_config(self, request: Request, commands: ICommandHandlingPort):
        """Delegate to AdminAdapter for app config creation/update."""
        admin_adapter = AdminAdapter()
        return await admin_adapter.create_or_update_app_config(request, commands)

    @inject
    async def process_onboarding_wizard(self, request: Request, commands: ICommandHandlingPort):
        """Delegate to AdminAdapter for onboarding wizard processing."""
        admin_adapter = AdminAdapter()
        return await admin_adapter.process_onboarding_wizard(request, commands)

    @decode_token
    @inject
    async def create_or_update_entity_schema(self, request: Request, commands: ICommandHandlingPort, query: IQueryPort):
        """Create or update an entity schema by app_id and schema_id."""
        from paperglass.domain.models_common import GenericMessage
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        app_id = request.path_params['app_id']
        schema_id = request.path_params['schema_id']
        
        # Remove .json extension if present
        if schema_id.endswith('.json'):
            schema_id = schema_id[:-5]
        
        extra = {
            "app_id": app_id,
            "schema_id": schema_id,
            "endpoint": "POST /admin/schemas/{app_id}/{schema_id}.json"
        }
        
        try:
            payload = await request.json()
            
            # Validate required fields
            if not payload.get('schema'):
                return JSONResponse({
                    'success': False,
                    'error': 'Missing required field: schema'
                }, status_code=400)
            
            # Create the entity schema data structure for the command
            entity_schema_dict = {
                'app_id': app_id,
                'schema_id': schema_id,
                'title': payload.get('title', ''),
                'label': payload.get('label', ''),
                'description': payload.get('description', ''),
                'version': payload.get('version', '1.0'),
                'schema': payload['schema']
            }
            
            extra.update({
                "entity_schema_dict": entity_schema_dict
            })
            
            LOGGER2.debug("Creating/updating entity schema for app_id: %s, schema_id: %s", app_id, schema_id, extra=extra)
            
            # Use the CreateEntitySchema command with the correct parameter name
            command = CreateEntitySchema(entity_schema_dict=entity_schema_dict)
            result = await commands.handle_command(command)
            
            return JSONResponse({
                'success': True,
                'message': 'Entity schema created/updated successfully',
                'schema_id': schema_id,
                'app_id': app_id
            })
            
        except ValidationError as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Validation error creating entity schema: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False,
                'error': 'Validation error',
                'details': e.errors()
            }, status_code=400)
            
        except json.JSONDecodeError as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Invalid JSON in entity schema request: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False,
                'error': 'Invalid JSON format'
            }, status_code=400)
            
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error creating/updating entity schema: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)

    @inject
    async def list_entity_schemas(self, request: Request, query: IQueryPort):
        """List all entity schemas with optional app_id filter."""
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        # Get app_id from query string if provided
        app_id = request.query_params.get('app_id')
        
        extra = {
            "app_id": app_id,
            "endpoint": "GET /admin/schemas"
        }
        
        try:
            LOGGER2.debug("Listing entity schemas with app_id filter: %s", app_id, extra=extra)
            
            # Get all schemas, optionally filtered by app_id
            schemas = await query.get_all_entity_schemas(app_id=app_id)
            
            # Convert to dicts for JSON response
            schema_list = []
            for schema in schemas:
                # Get description and version from the schema data if available
                schema_data = schema.get_schema_dict()
                schema_dict = {
                    'id': schema.id,
                    'schema_id': schema.schema_id,
                    'app_id': schema.app_id,
                    'title': schema.title,
                    'label': schema.label,
                    'description': schema_data.get('description'),
                    'version': schema_data.get('version'),
                    'fqn': schema.fqn,
                    'active': schema.active,
                    'created_at': schema.created_at.isoformat() if schema.created_at else None,
                    'modified_at': schema.modified_at.isoformat() if schema.modified_at else None
                }
                schema_list.append(schema_dict)
            
            LOGGER2.info("Successfully listed %d entity schemas", len(schema_list), extra=extra)
            
            return JSONResponse({
                'success': True,
                'schemas': schema_list,
                'count': len(schema_list),
                'app_id_filter': app_id
            })
            
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error listing entity schemas: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)

    @inject
    async def get_entity_schema_by_id(self, request: Request, query: IQueryPort):
        """Get an entity schema by its schema_id."""
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        schema_id = request.path_params['schema_id']
        
        extra = {
            "schema_id": schema_id,
            "endpoint": "GET /admin/schemas/{schema_id}"
        }
        
        try:
            LOGGER2.debug("Getting entity schema by ID: %s", schema_id, extra=extra)
            
            # Get schema by ID
            schema = await query.get_entity_schema_by_id(schema_id)
            
            if not schema:
                return JSONResponse({
                    'success': False,
                    'error': 'Schema not found',
                    'schema_id': schema_id
                }, status_code=404)
            
            # Convert to dict for JSON response
            schema_data = schema.get_schema_dict()
            schema_dict = {
                'id': schema.id,
                'schema_id': schema.schema_id,
                'app_id': schema.app_id,
                'title': schema.title,
                'label': schema.label,
                'description': schema_data.get('description'),
                'version': schema_data.get('version'),
                'fqn': schema.fqn,
                'active': schema.active,
                'created_at': schema.created_at.isoformat() if schema.created_at else None,
                'modified_at': schema.modified_at.isoformat() if schema.modified_at else None,
                'schema': schema_data
            }
            
            LOGGER2.info("Successfully retrieved entity schema: %s", schema_id, extra=extra)
            
            return JSONResponse({
                'success': True,
                'schema': schema_dict
            })
            
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error getting entity schema: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)

    @inject
    async def delete_entity_schema_by_id(self, request: Request, commands: ICommandHandlingPort):
        """Delete an entity schema by its schema_id."""
        from paperglass.domain.utils.exception_utils import exceptionToMap
        
        schema_id = request.path_params['schema_id']
        
        extra = {
            "schema_id": schema_id,
            "endpoint": "DELETE /admin/schemas/{schema_id}"
        }
        
        try:
            LOGGER2.debug("Deleting entity schema by ID: %s", schema_id, extra=extra)
            
            # Create delete command
            command = DeleteEntitySchema(schema_id=schema_id)
            result = await commands.handle_command(command)
            
            LOGGER2.info("Successfully deleted entity schema: %s", schema_id, extra=extra)
            
            return JSONResponse({
                'success': True,
                'message': 'Entity schema deleted successfully',
                'schema_id': schema_id,
                'result': result
            })
            
        except CommandError as e:
            # Check if the underlying cause is a ValueError (schema not found)
            if "not found" in str(e):
                extra.update({'error': exceptionToMap(e)})
                LOGGER2.error("Schema not found for deletion: %s", str(e), extra=extra)
                return JSONResponse({
                    'success': False,
                    'error': 'Schema not found',
                    'details': str(e)
                }, status_code=404)
            else:
                extra.update({'error': exceptionToMap(e)})
                LOGGER2.error("Command error deleting entity schema: %s", str(e), extra=extra)
                return JSONResponse({
                    'success': False,
                    'error': 'Command error',
                    'details': str(e)
                }, status_code=400)
            
        except Exception as e:
            extra.update({'error': exceptionToMap(e)})
            LOGGER2.error("Error deleting entity schema: %s", str(e), extra=extra)
            return JSONResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status_code=500)
