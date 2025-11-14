from functools import singledispatch
import os
from typing import Dict

from kink import inject

from paperglass.usecases.configuration import get_config
from paperglass.usecases.queue_resolver import QueueResolver
from paperglass.domain.utils.auth_utils import get_token
from paperglass.settings import (
    CLOUD_PROVIDER, 
    CLOUD_TASK_QUEUE_NAME,
    CLOUD_TASK_QUEUE_NAME_2,
    GCP_LOCATION_2,
    MEDICATION_EXTRACTION_V4_TOPIC,
    SELF_API,
    SERVICE_ACCOUNT_EMAIL,
    MEDICATION_EXTRACTION_PRIORITY_NONE
)
from paperglass.domain.service import ResolveNamedEntityFromLabel
from paperglass.domain.values import (
    AnnotationType, 
    Configuration, 
    NamedEntityExtractionType,  
    PageOperationStatus,
    OrchestrationPriority
)
from paperglass.domain.models import Page

from paperglass.usecases.commands import (
    CheckForAllPageOperationExtractionCompletion,
    CreateDocument,
    CreateorUpdatePageOperation,
    ImportHostAttachmentFromExternalStorageUri,
    Orchestrate,
    SplitPages,
    Command,
    SendEmail,
)
from paperglass.usecases.orchestration_launcher import OrchestrationLauncher
from paperglass.usecases.command_actions import create_command

from paperglass.domain.models import Document
from paperglass.domain.events import (
    DocumentCreated,
    Event,
    NoteCreated,
    NoteUpdated,
    OnExternalFilesEvent,
    PageClassified,
    PageSplitCreated,
    UploadAttachment
)
from paperglass.interface.ports import IEventHandlingPort
from paperglass.infrastructure.ports import ICloudTaskPort, IMessagingPort, IQueryPort, IStoragePort, IUnitOfWork, IUnitOfWorkManagerPort
from paperglass.log import getLogger, labels, CustomLogger
import aiohttp

#LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)
LOGGER = LOGGER2

@singledispatch
async def dispatcher(event: Event, uow: IUnitOfWork):
    LOGGER.error('Don\'t know how to handle event %s', event)


# Real handlers

@dispatcher.register(DocumentCreated)
async def document_page_created(event: DocumentCreated, uow: IUnitOfWork, pubsub: IMessagingPort):
    
    extra = {
        "app_id": event.app_id,
        "tenant_id": event.tenant_id,
        "patient_id": event.patient_id,
        "document_id": event.document_id,
        "storage_uri": event.storage_uri,
        "priority": event.priority,
        "token": event.token,        
    }    

    LOGGER.info(
        'Got event that document was created (document_id=%s), we will start chunking.',
        event.document_id,
        extra=extra
    )

    orchestration_launcher = OrchestrationLauncher(event.document_id, priority=event.priority)
    await orchestration_launcher.launch()
    
    # orchestration_agent = MedicationExtractionOrchestrationAgent()
    # await orchestration_agent.orchestrate(event.document_id, priority=event.priority)
     
    
@dispatcher.register(UploadAttachment)
@inject()
async def upload_attachment(event: UploadAttachment, uow: IUnitOfWork, storage: IStoragePort, query: IQueryPort):
    
    extra = {
        "app_id": event.app_id,
        "tenant_id": event.tenant_id,
        "patient_id": event.patient_id,        
        "storage_uri": event.storage_uri,        
        "token": event.token,        
    }    

    LOGGER.info(
        'Got event that attachment was uploaded (attachment_id=%s), we will start processing.',
        event.storage_uri,
        extra=extra
    )

    #raw_bytes = await storage.get_external_document_raw(event.storage_uri)
    # call orchestration event if in cloud. if local call orchestrator directly
    # result = uow.create_command(CreateDocument(token=event.token,
    #                                                     app_id=event.app_id,
    #                                                     tenant_id=event.tenant_id,
    #                                                     file_name=event.file_name,
    #                                                     patient_id=event.patient_id,
    #                                                     source=event.source,
    #                                                     source_storage_uri=event.storage_uri))
    
    command = CreateDocument(token=event.token,
                            app_id=event.app_id,
                            tenant_id=event.tenant_id,
                            file_name=event.file_name,
                            patient_id=event.patient_id,
                            source=event.source,
                            source_storage_uri=event.storage_uri
                        )                                                
    await create_command(command, uow)
    
@dispatcher.register(OnExternalFilesEvent)
@inject()
async def external_file_arrived(event: OnExternalFilesEvent, uow: IUnitOfWork, storage: IStoragePort, query: IQueryPort, cloud_task_adapter:ICloudTaskPort):
    extra = {
        "app_id": event.app_id,
        "external_file_gcs_uri": event.external_file_gcs_uri,
        "raw_event": event.raw_event
    }   
    LOGGER.info(
        f'Got event that external file has arrived (external_file_gcs_uri={event.external_file_gcs_uri}), we will start processing.', extra=extra
    )
    
    # result = uow.create_command(ImportHostAttachmentFromExternalStorageUri(
    #     external_storage_uri=event.external_file_gcs_uri,
    #     app_id=event.app_id,
    #     raw_event=event.raw_event,
    # )) 

    command = ImportHostAttachmentFromExternalStorageUri(
        external_storage_uri=event.external_file_gcs_uri,
        app_id=event.app_id,
        raw_event=event.raw_event,
    )
    await create_command(command, uow)


class EventHandlingUseCase(IEventHandlingPort):
    @inject()
    async def handle_event(self, event: Event, uowm: IUnitOfWorkManagerPort):
        async with uowm.start() as uow:
            LOGGER.debug('Received event %s', repr(event), extra=labels(event_type=event.type))
            if not await uow.start_event_processing(event):
                LOGGER.error('Event already processed, event=%s', event)
                return
            await dispatcher(event, uow)
            uow.finish_event_processing(event)
