from kink import inject

import paperglass.settings as settings
from paperglass.domain.model_metric import Metric
from paperglass.domain.models_common import InvalidStateException

from paperglass.domain.models import Document
from paperglass.domain.values import (
    Configuration,
    DocumentOperationType,
    DocumentOperationStatus,
)

from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IQueryPort

from paperglass.usecases.configuration import get_config
from paperglass.usecases.commands import (
    UpdateDocumentPriority,
    DocumentSpawnRevision,
)
from paperglass.usecases.orchestration_agent_medicationextraction import MedicationExtractionOrchestrationAgent
from paperglass.usecases.orchestration_agent_entity import EntityExtractionOrchestrationAgent


from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils, bootstrap_opentelemetry
from paperglass.log import getLogger

bootstrap_opentelemetry(__name__)
opentelemetry = OpenTelemetryUtils("OrchestrationLauncher:")

LOGGER = getLogger(__name__)

class OrchestrationLauncher:
    """
    This class is responsible for launching orchestrations based on the provided document_id and priority.
    It handles the orchestration logic and ensures that the correct orchestration agents are used.
    """

    IN_FLIGHT_STATES = [DocumentOperationStatus.IN_PROGRESS, DocumentOperationStatus.QUEUED]

    def __init__(self, document_id:str, priority:str, operation_type:DocumentOperationType=None):
        self.document_id = document_id
        self.priority = priority
        self.operation_type = operation_type

    def get_extra(self):
        extra =  {
            "document_id": self.document_id,
            "priority": self.priority,
            "operation_type": self.operation_type.value if self.operation_type else None,
        }

        if self.document:
            extra.update({
                "app_id": self.document.app_id,
                "tenant_id": self.document.tenant_id,
                "patient_id": self.document.patient_id,               
                "document": self.document.dict(),                
            })

        if self.config:
            extra.update({                
                "orchestration_engine_version": self.config.orchestration_engine_version
            })

        return extra

    async def launch(self):
        """
        Launches the orchestration based on the command.
        """        
        # Priority NONE means to not automatically start orchestration for this document
        if self.priority==settings.MEDICATION_EXTRACTION_PRIORITY_NONE:
            LOGGER.warning("Document priority is none.  Not automatically starting orchestration for this document.", extra=self.get_extra())
            return
        
        try:
            await self.prepare()

            LOGGER.debug("OrchestrationLauncher: Config: %s", self.config.dict() if self.config else None, extra=self.get_extra())
            is_started = False

            if self.config.medication_extraction and self.config.medication_extraction.enabled:
                Metric.send("ORCHESTRATION:LAUNCH:MEDICATION", tags=self.get_extra())               
                
                orchestration_agent = MedicationExtractionOrchestrationAgent(document=self.document, config=self.config)
                await orchestration_agent.orchestrate(self.document_id, priority=self.priority)
                is_started = True
                
            if self.config.entity_extraction and self.config.entity_extraction.enabled:
                Metric.send("ORCHESTRATION:LAUNCH:ENTITY", tags=self.get_extra())

                orchestration_agent = EntityExtractionOrchestrationAgent(document=self.document, config=self.config)
                await orchestration_agent.orchestrate(self.document_id, priority=self.priority)
                is_started = True

            if not is_started:
                extra = self.get_extra()
                extra.update({
                    "medication_extraction_enabled": self.config.medication_extraction.enabled if self.config else None,
                    "entity_extraction_enabled": self.config.entity_extraction.enabled if self.config else None
                })
                LOGGER.warning("No orchestration agent was started.  This may be due to the document's priority or configuration settings.", extra=extra)                
                Metric.send("ORCHESTRATION:LAUNCH:NOT_STARTED", tags=self.get_extra())

        except InvalidStateException as e:
            LOGGER.warning(e.message, extra=self.get_extra())
            return

        #orchestration_agent = MedicationExtractionOrchestrationAgent()
        #await orchestration_agent.orchestrate(event.document_id, priority=event.priority)

    @inject
    async def prepare(self, query: IQueryPort):
        """
        Prepares the orchestration by getting the document and configuration.
        """
        doc = await query.get_document(self.document_id)
        self.document = Document(**doc)

        extra = {
            "app_id": self.document.app_id,
            "tenant_id": self.document.tenant_id,
            "patient_id": self.document.patient_id,
            "document_id": self.document.id,
            "storage_uri": self.document.storage_uri,
            "priority": self.document.priority.value if self.document.priority else None,
            "document": self.document.dict(),
        }

        LOGGER.debug("OrchestrationLauncher: Prepare", extra=extra)

        # Get configuration for the document
        self.config:Configuration = await get_config(self.document.app_id, self.document.tenant_id)

        extra = self.get_extra()

        await self.update_document_priority()

        # Priority NONE means to not automatically start orchestration for this document
        if self.priority==settings.MEDICATION_EXTRACTION_PRIORITY_NONE:            
            raise InvalidStateException("Document priority is none.  Not automatically starting orchestration for this document.")

        # Need to perform a switcharoo if any document operation status is in an "in flight" state
        #TODO: This is a temporary brute force.  Needs a more cleaner solution for situations where muliple pipeline operations are in flight. 
        any_operation_in_flight = any(
            op_status.status in self.IN_FLIGHT_STATES 
            for op_status in self.document.operation_status.values()
        )
        if any_operation_in_flight:
            self.document = await self.respawn(self.document)
        else:
            LOGGER.debug("Document is not in an in-flight state.  Proceeding with orchestration.", extra=extra)
        

    @inject
    async def update_document_priority(self, commands: ICommandHandlingPort):

        extra = self.get_extra()
        extra.update({            
            "original_priority": self.document.priority,
        })

        # If priority is passed in and different from the doc's priority, it is an explicit override of the document's priority
        if self.priority != self.document.priority:
            LOGGER.debug("OrchestrationLauncher: Updating document priority to %s", self.priority, extra=extra)
            command = UpdateDocumentPriority(document_id=self.document_id, priority=self.priority)
            self.document = await commands.handle_command(command)                    
        else:
            LOGGER.debug("OrchestrationLauncher: Document priority is already set to %s, no update needed.", self.document.priority, extra=extra)            

    @inject
    async def respawn(self, document: Document, commands: ICommandHandlingPort):
        """
        Respawns the document.
        """
        extra = self.get_extra()

        if settings.MEDICATION_EXTRACTION_RESPAWN_INFLIGHT_ENABLE:
            LOGGER.info("Document is in an in-flight state.  Spawning a revision and re-orchestrating.", extra=extra)
            extra.update({
                "original_document_id": document.id
            })
            self.original_document = document

            command = DocumentSpawnRevision(document=document)
            document = await commands.handle_command(command)
            extra.update({
                "document_id": document.id,
                "cloned_document": document.dict()
            })

            return document
        else:            
            raise InvalidStateException("Document is in an in-flight state.  Not automatically starting orchestration for this document.")
