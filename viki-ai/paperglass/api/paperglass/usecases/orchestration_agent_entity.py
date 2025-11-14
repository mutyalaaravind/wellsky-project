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
    ENTITY_EXTRACTION_API_URL,
    ENTITY_EXTRACTION_LAUNCH_QUEUE_NAME
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
    UpdateDocumentStatusSnapshot,
)

from paperglass.usecases.configuration import get_config

from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils, bootstrap_opentelemetry
from paperglass.log import getLogger

bootstrap_opentelemetry(__name__)
opentelemetry = OpenTelemetryUtils("EntityExtractionOrchestrationAgent:")

LOGGER = getLogger(__name__)

class EntityExtractionOrchestrationAgent(DocumentOrchestrationAgent):

    operation_type = DocumentOperationType.ENTITY_EXTRACTION
    IN_FLIGHT_STATES = [DocumentOperationStatus.IN_PROGRESS, DocumentOperationStatus.QUEUED]

    def __init__(self, document: Document=None, config: Configuration=None):
        super().__init__(document, config)
        self.operation_type = DocumentOperationType.ENTITY_EXTRACTION

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

        with await opentelemetry.getSpan("orchestrate_entity_extraction") as span: 
            extra = {
                "document_id": document_id,
                "priority": priority
            }
            LOGGER.debug("Orchestrating entity extraction for document %s with priority %s", document_id, priority, extra=extra)
            
            try:
                document = await self._get_document(document_id, query)
                
                extra.update({
                    "app_id": document.app_id,
                    "tenant_id": document.tenant_id,
                    "patient_id": document.patient_id,
                    "document_id": document.id,
                    "document": document.dict(),
                    "config": {
                        "entity_extraction": self.config.entity_extraction.dict() if self.config.entity_extraction else None,
                    }
                })

                # Check if entity extraction is enabled in configuration
                if not self.config.entity_extraction or not self.config.entity_extraction.enabled:
                    LOGGER.warning("Entity extraction is not enabled for this tenant. Skipping orchestration.", extra=extra)
                    return

                # Extract scope and pipeline_id from configuration
                pipeline_default = self.config.entity_extraction.pipeline_default if self.config.entity_extraction and self.config.entity_extraction.pipeline_default else "default.start"
                
                # Split pipeline_default to get scope and pipeline_id
                if "." in pipeline_default:
                    scope, pipeline_id = pipeline_default.split(".", 1)
                else:
                    scope = "default"
                    pipeline_id = pipeline_default

                extra.update({
                    "scope": scope,
                    "pipeline_id": pipeline_id,
                    "pipeline_default": pipeline_default
                })

                async with uowm.start() as uow:
                    await self.orchestrate_entity_extraction(document, scope, pipeline_id, self.config, commands, pubsub)
                
            except OrchestrationException as e:
                extra.update({
                    "error": exceptionToMap(e)
                })
                LOGGER.error("Error occurred during %s orchestration of documentId %s: %s", self.operation_type, document_id, str(e), extra=extra)                
            except Exception as e:
                extra.update({
                    "error": exceptionToMap(e)
                })
                LOGGER.error("Error orchestrating %s: %s", self.operation_type, str(e), extra=extra)
                raise e

    @inject
    async def orchestrate_entity_extraction(self, document: Document, scope: str, pipeline_id: str, config: Configuration, commands: ICommandHandlingPort, pubsub: IMessagingPort, cloud_task_adapter: ICloudTaskPort = None):
        
        context = document.metadata if document.metadata else {}        

        params = {
            "licenses": config.licenses,
            "config": config.entity_extraction.dict() if config.entity_extraction else None,
        }

        payload = {
            "business_unit": config.accounting.business_unit if config.accounting and config.accounting.business_unit else "unknown",
            "solution_code": config.accounting.solution_code if config.accounting and config.accounting.solution_code else "unknown",
            "app_id": document.app_id,
            "tenant_id": document.tenant_id,
            "patient_id": document.patient_id,
            "document_id": document.id,
            "page_count": document.page_count,
            "priority": document.priority.value,
            "params": params,
            "context": context,
        }
        
        extra = {
            "app_id": document.app_id,
            "tenant_id": document.tenant_id,
            "patient_id": document.patient_id,
            "document_id": document.id,
            "priority": document.priority.value,
            "payload": payload,
            "cloud_provider": CLOUD_PROVIDER
        }
                
        LOGGER.debug("Creating CloudTask for entity extraction", extra=extra)
        
        url = f"{ENTITY_EXTRACTION_API_URL}/api/pipeline/{scope}/{pipeline_id}/start"
        queue = ENTITY_EXTRACTION_LAUNCH_QUEUE_NAME

        extra.update({
            "queue": queue,
            "url": url
        })
        
        await cloud_task_adapter.create_task(
            token=get_token(document.app_id, document.tenant_id, document.patient_id),
            location=GCP_LOCATION_2,
            service_account_email=SERVICE_ACCOUNT_EMAIL,
            queue=queue,
            url=url,
            payload=payload
        )

        # Update document status to IN_PROGRESS
        if DocumentOperationType.ENTITY_EXTRACTION.value not in document.operation_status or document.operation_status[self.operation_type.value].status != DocumentOperationStatus.IN_PROGRESS:
            await commands.handle_command(UpdateDocumentStatusSnapshot(
                document_id=document.id,
                patient_id=document.patient_id,
                app_id=document.app_id,
                tenant_id=document.tenant_id,
                doc_operation_status_snapshot=DocumentOperationStatusSnapshot(
                    operation_type=DocumentOperationType.ENTITY_EXTRACTION,
                    status=DocumentOperationStatus.IN_PROGRESS,
                    start_time=now_utc().isoformat(),
                    orchestration_engine_version=config.entity_extraction.version if config.entity_extraction else "1"
                )
            ))
            
        LOGGER.info("Entity extraction orchestration completed for document %s", document.id, extra=extra)
