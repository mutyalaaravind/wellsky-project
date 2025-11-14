import asyncio
import sys, os
from typing import List

from kink import inject # type: ignore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.settings import (
    CLOUD_PROVIDER,
    GCP_LOCATION_2,
    SERVICE_ACCOUNT_EMAIL,
    MEDICATION_EXTRACTION_RESPAWN_INFLIGHT_ENABLE,
    MEDICATION_EXTRACTION_PRIORITY_NONE,
    MEDICATION_EXTRACTION_V4_TOPIC,
    QUEUE_RESOLVER_VERSION
)

from paperglass.domain.models import Document
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.domain.time import now_utc
from paperglass.domain.utils.auth_utils import get_token

from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IQueryPort, IMessagingPort, IUnitOfWorkManagerPort, ICloudTaskPort

from paperglass.domain.models_common import OrchestrationException
from paperglass.domain.models import (
    DocumentOperationStatusSnapshot,
    DocumentOrchestrationAgent,
    Configuration
)

from paperglass.domain.values import (
    DocumentOperationStatus,
    DocumentOperationType,
    OrchestrationPriority
)

from paperglass.usecases.commands import (
    Orchestrate,
    UpdateDocumentStatusSnapshot,
    UpdateDocumentPriority,
    DocumentSpawnRevision,
)

from paperglass.usecases.queue_resolver import QueueResolver, QueueResolverV2, get_queue_resolver
from paperglass.usecases.orchestrator import orchestrate as v3_orchestrate

from paperglass.usecases.configuration import get_config

from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils, bootstrap_opentelemetry
from paperglass.log import getLogger

bootstrap_opentelemetry(__name__)
opentelemetry = OpenTelemetryUtils("GraderOrchestrationAgent:")

LOGGER = getLogger(__name__)

class MedicationExtractionOrchestrationAgent(DocumentOrchestrationAgent):

    operation_type = DocumentOperationType.MEDICATION_EXTRACTION
    IN_FLIGHT_STATES = [DocumentOperationStatus.IN_PROGRESS, DocumentOperationStatus.QUEUED]

    def __init__(self, document: Document = None, config: Configuration = None):
        config_dict = None
        if config:
            config_dict = config.dict()
        import json

        LOGGER.debug("Initializing MedicationExtractionOrchestrationAgent with document: %s, config: %s", document, json.dumps(config_dict, indent=2) if config_dict else None)
        super().__init__(document, config)
        self.operation_type = DocumentOperationType.MEDICATION_EXTRACTION

    @inject
    async def _get_document(self, document_id: str, query: IQueryPort) -> Document:
        """
        Fetch the document from the query port.
        """
        if not self.document:
            doc = await query.get_document(document_id)
            if not doc:
                raise OrchestrationException(f"Document with id {document_id} not found.")
            
            self.document = Document(**doc)
            
        return self.document

    @inject
    async def orchestrate(self, document_id: str, commands: ICommandHandlingPort, query: IQueryPort, pubsub: IMessagingPort, uowm: IUnitOfWorkManagerPort, priority: OrchestrationPriority=OrchestrationPriority.DEFAULT):

        with await opentelemetry.getSpan("orchestrate_medicationextraction") as span: 
            extra = {
                "document_id": document_id,
                "priority": priority
            }
            LOGGER.debug("Orchestrating document %s with priority %s", document_id, priority, extra=extra)
            try:
                # overridden_priority = False
                # document:Document = None

                # doc = await query.get_document(document_id)
                # document = Document(**doc)

                # # If priority is passed in and different from the doc's priority, it is an explicit override of the document's priority
                # if priority != document.priority:
                #     LOGGER.debug("Starting orchestration.  Updating document priority to %s", priority, extra=extra)
                #     command = UpdateDocumentPriority(document_id=document_id, priority=priority)
                #     document = await commands.handle_command(command)                    
                #     overridden_priority = True
                
                # LOGGER.debug("Starting orchestration.  Using document's priority of %s", document.priority, extra=extra)                

                # config:Configuration = await get_config(document.app_id, document.tenant_id)
                # # call orchestration event if in cloud. if local call orchestrator directly
                
                # extra.update({
                #     "document": document.dict(),
                #     "overridden_priority": overridden_priority,
                #     "config": {
                #         "orchestration_engine_version": config.orchestration_engine_version,
                #     }
                # })

                # # Priority NONE means to not automatically start orchestration for this document
                # if priority==MEDICATION_EXTRACTION_PRIORITY_NONE:
                #     LOGGER.warning("Document priority is none.  Not automatically starting orchestration for this document.", extra=extra)
                #     return

                # # Need to perform a switcharoo if the document status is in an "in flight" state
                # if self.operation_type in document.operation_status and document.operation_status[self.operation_type].status in self.IN_FLIGHT_STATES:
                #     if MEDICATION_EXTRACTION_RESPAWN_INFLIGHT_ENABLE:
                #         LOGGER.info("Document is in an in-flight state.  Spawning a revision and re-orchestrating.", extra=extra)
                #         extra.update({
                #             "original_document_id": document.id
                #         })
                #         command = DocumentSpawnRevision(document=document)
                #         document = await commands.handle_command(command)
                #         extra.update({
                #             "document_id": document.id,
                #             "cloned_document": document.dict()
                #         })
                #     else:
                #         LOGGER.warning("Document is in an in-flight state.  Not automatically starting orchestration for this document.", extra=extra)
                #         return
                # else:
                #     LOGGER.debug("Document is not in an in-flight state.  Proceeding with orchestration.", extra=extra)

                await self._get_document(document_id)

                async with uowm.start() as uow:
                    if self.config.orchestration_engine_version == "v3":
                        await self.orchestrate_v3(self.document, self.config)
                    elif self.config.orchestration_engine_version == "v4":
                        LOGGER.debug("Queueing command to orchestration document using v4 engine", extra=extra)

                        await self.orchestrate_v4(self.document, self.config)
                    else:
                        LOGGER.warning("Refusing to start orchestration for this document.  Invalid orchestration engine version: %s", self.config.orchestration_engine_version, extra=extra)                            
                
            except OrchestrationException as e:
                extra.update({
                    "error": exceptionToMap(e)
                })
                LOGGER.error("Error occured during %s orchestration of documentId %s: %s", self.operation_type, self.document.id, str(e), extra=extra)                
            except Exception as e:
                extra.update({
                    "error": exceptionToMap(e)
                })
                LOGGER.error("Error orchestrating %s: %s", self.operation_type, str(e), extra=extra)
                raise e

    @inject
    async def orchestrate_v3(self, document:Document, config:Configuration):
        extra={
            "app_id": document.app_id,
            "tenant_id": document.tenant_id,
            "patient_id": document.patient_id,
            "document_id": document.id,
            "priority": document.priority            
        }

        force_new_instance = False
        
        # This is copied over from the command_handling.py orchestrate_handler function.  That function switches between local and cloud, but in both cases it
        # calls the v3_orchestrate function (???).  This needs to be cleaned up.

        if os.environ.get('CLOUD_PROVIDER') == 'local':
            LOGGER.warning("Running locally")
            from paperglass.usecases.configuration import get_config
            config:Configuration = await get_config(document.app_id, document.tenant_id)
            
            # if not config:
            #     LOGGER.error(f'No configuration found for app_id {document.app_id} and tenant_id {document.tenant_id}')
                #config = await create_app_configuration(CreateAppConfiguration(app_id=command.app_id,config=Configuration()))
            
            LOGGER.debug("Orchestrating document %s using v3", document.id)
            await v3_orchestrate(document.id, force_new_instance, priority=document.priority)
            
            # if config and config.use_v3_orchestration_engine:
            #     LOGGER.debug("Orchestrating document %s using v3", document.id)
            #     await v3_orchestrate(document.id, force_new_instance, priority=document.priority)
            
            return
        else:
            from paperglass.usecases.configuration import get_config
            
            # if not config:
            #     LOGGER.error(f'No configuration found for app_id {document.app_id} and tenant_id {document.tenant_id}', extra=extra)
            #     #config = await create_app_configuration(CreateAppConfiguration(app_id=command.app_id,config=Configuration()))
            
            LOGGER.debug("Orchestrating document %s using v3", document.id, extra=extra)
            await v3_orchestrate(document.id, force_new_instance, priority=document.priority)

            # REMOVED CODE FOR OLD V2 ORCHESTRATION ENGINE -------------------------------------------------------------------------
            #if config and config.use_v3_orchestration_engine:
                # LOGGER.debug("Orchestrating document %s using v3", document.id, extra=extra)
                # await v3_orchestrate(document.id, force_new_instance, priority=document.priority)

            # else:
            #     url = f"{SELF_API}/orchestrate"
            #     queue = CLOUD_TASK_QUEUE_NAME
            #     payload = {"document_id": document.document_id}

            #     LOGGER.debug("Orchestrating document %s using v2", command.document_id, extra=extra)
            #     integration_project_name=INTEGRATION_PROJECT_NAME
            #     json_payload={
            #         "START_CLOUD_TASK_API":f"{SELF_API}/start_cloud_task",
            #         "CLOUD_TASK_ARGS":{
            #             "location":"us-east4",
            #             "url":url,
            #             "queue":queue,
            #             "service_account_email":SERVICE_ACCOUNT_EMAIL,
            #             "payload":payload
            #         },
            #         "TOKEN":f"Bearer {document.token}"
            #     }

            #     extra.update({
            #         "cloudtask": json_payload
            #     }
            #     )                
            #     LOGGER.debug("Application integration start payload", extra=extra)
            #     trigger_id = APPLICATION_INTEGRATION_TRIGGER_ID
            #     result = await app_integration_adapter.start(integration_project_name, json_payload, trigger_id)                
            #     LOGGER.info("application integration result: %s", result, extra=extra)
            #     return result

        if config.enable_v4_orchestration_engine_parallel_processing:
            await self.orchestrate_v4(document, config)

    @inject
    async def orchestrate_v4(self, document:Document, config:Configuration, commands: ICommandHandlingPort, pubsub: IMessagingPort, cloud_task_adapter: ICloudTaskPort):
        
        payload = {
                "document_id": document.id,
                "patient_id": document.patient_id,
                "app_id": document.app_id,
                "tenant_id": document.tenant_id,
                "storage_uri": document.storage_uri,
                "priority": document.priority.value,
                "created_at": document.created_at,
                "ocr_processing_disabled": True if config.ocr_trigger_config and config.ocr_trigger_config.disable_orchestration_processing else False,
                "medispan_adapter_settings": config.medispan_match_config.dict() if config.medispan_match_config else None,
            }
        
        if CLOUD_PROVIDER == "local":
            await pubsub.publish(MEDICATION_EXTRACTION_V4_TOPIC, payload)
        else:
            # queue=QueueResolver().resolve_queue_name("v4_extraction", event.priority.value)
            # url=f"{MEDICATION_EXTRACTION_V4_API_URL}/run_extraction"
            
            queue_resolver = get_queue_resolver(document.app_id)
            queue_value = queue_resolver.resolve_queue_value("v4_extraction", document.priority.value)
            
            url = f"{queue_value.api_url}/run_extraction"
            queue = queue_value.queue_name

            extra = {
                "app_id": document.app_id,
                "tenant_id": document.tenant_id,
                "patient_id": document.patient_id,
                "document_id": document.id,
                "queue": queue,
                "url": url,
                "payload": payload,
                "queue_resolver_version": QUEUE_RESOLVER_VERSION
            }            
            
            LOGGER.debug("Creating CloudTask...", extra=extra)
            await cloud_task_adapter.create_task(
                token=get_token(document.app_id, document.tenant_id, document.patient_id),
                location=GCP_LOCATION_2,
                service_account_email=SERVICE_ACCOUNT_EMAIL,
                queue=queue,
                url=url,
                payload=payload
            )

            # We will also send to quarantine if parallel test is enabled in app_config
            await self.run_quarantine(document, config, commands, pubsub, cloud_task_adapter)

        if DocumentOperationType.MEDICATION_EXTRACTION.value not in document.operation_status or document.operation_status[self.operation_type.value].status != DocumentOperationStatus.IN_PROGRESS:
            await commands.handle_command(UpdateDocumentStatusSnapshot(
                document_id=document.id,
                patient_id=document.patient_id,
                app_id=document.app_id,
                tenant_id=document.tenant_id,
                doc_operation_status_snapshot=DocumentOperationStatusSnapshot(
                    operation_type=DocumentOperationType.MEDICATION_EXTRACTION,
                    status=DocumentOperationStatus.IN_PROGRESS,
                    start_time=now_utc().isoformat(),
                    orchestration_engine_version="v4"
                )
            ))

    @inject
    async def run_quarantine(self, document:Document, config:Configuration, commands: ICommandHandlingPort, pubsub: IMessagingPort, cloud_task_adapter: ICloudTaskPort):

        if CLOUD_PROVIDER != "local" and config.medication_extraction and config.medication_extraction.parallel_test_enabled:
            
            priority = "quarantine"

            extra = {
                "app_id": document.app_id,
                "tenant_id": document.tenant_id,
                "patient_id": document.patient_id,
                "document_id": document.id,
                "priority": priority,                
                "queue_resolver_version": QUEUE_RESOLVER_VERSION
            }
            
            LOGGER.debug("Running parallel quarantine for document %s with parallel test enabled", document.id, extra=extra)            

            payload = {
                "document_id": document.id,
                "patient_id": document.patient_id,
                "app_id": document.app_id,
                "tenant_id": document.tenant_id,
                "storage_uri": document.storage_uri,
                "priority": priority,
                "created_at": document.created_at,
                "ocr_processing_disabled": True if config.ocr_trigger_config and config.ocr_trigger_config.disable_orchestration_processing else False,
                "medispan_adapter_settings": config.medispan_match_config.dict() if config.medispan_match_config else None,
            }
            
            queue_resolver = get_queue_resolver(document.app_id)
            queue_value = queue_resolver.resolve_queue_value("v4_extraction", priority)
            
            url = f"{queue_value.api_url}/run_extraction"
            queue = queue_value.queue_name

            extra.update({
                "queue": queue,
                "url": url,
                "payload": payload
            })
            
            LOGGER.debug("Creating CloudTask for parallel quarantine...", extra=extra)
            await cloud_task_adapter.create_task(
                token=get_token(document.app_id, document.tenant_id, document.patient_id),
                location=GCP_LOCATION_2,
                service_account_email=SERVICE_ACCOUNT_EMAIL,
                queue=queue,
                url=url,
                payload=payload
            )
