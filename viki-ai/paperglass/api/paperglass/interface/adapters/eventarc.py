import asyncio
import base64
import json
from datetime import datetime,timedelta, timezone
import traceback
from typing import Any, List, Optional
from paperglass.usecases.queue_resolver import QueueResolver
from paperglass.domain.models import DocumentOperationStatusSnapshot, ExtractedMedication
from paperglass.usecases.configuration import get_config
from paperglass.domain.values import Configuration, DocumentOperationStatus, DocumentOperationType
from paperglass.usecases.command_handling import import_host_attachments, import_medications, orchestrate_handler
from paperglass.usecases.orchestration_launcher import OrchestrationLauncher
from paperglass.domain.utils.auth_utils import get_token
from paperglass.infrastructure.ports import ICloudTaskPort, IMessagingPort, IQueryPort
from paperglass.settings import CLOUD_PROVIDER, CLOUD_TASK_QUEUE_NAME, GCP_LOCATION_2, MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME, MEDICATION_EXTRACTION_V4_TOPIC, SELF_API, SERVICE_ACCOUNT_EMAIL,MEDICATION_EXTRACTION_V4_API_URL
from pydantic import parse_obj_as

from kink import inject

from google.cloud import firestore
from google.events.cloud.firestore import DocumentEventData
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from ...usecases.commands import Command, ImportHostAttachments, ImportMedications, Orchestrate, UpdateDocumentStatusSnapshot
from ...domain.events import DocumentCreated, Event, OnExternalFilesEvent, UploadAttachment
from ...log import getLogger, CustomLogger
from ...interface.ports import IEventHandlingPort, ICommandHandlingPort

LOGGER = getLogger(__name__)
LOGGER2 = CustomLogger(__name__)

#OpenTelemetry instrumentation
SPAN_BASE: str = "CONTROLLER:event_controller:"
from ...domain.utils.opentelemetry_utils import OpenTelemetryUtils
from opentelemetry.trace.status import Status, StatusCode
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

class DecoderThatHandlesStupidGoogleTypes:
    """
    Reason:
        - https://issuetracker.google.com/issues/128852268
        - https://groups.google.com/g/google-appengine/c/5UIcqGFtezE

    Source: https://stackoverflow.com/a/62983902/3455614
    """

    def __init__(self, client) -> None:
        self.client = client
        self._action_dict = {
            'geo_point_value': (lambda x: dict(x)),
            'string_value': (lambda x: str(x)),
            'array_value': (lambda x: [self._parse_value(value_dict) for value_dict in x.get("values", [])]),
            'boolean_value': (lambda x: bool(x)),
            'null_value': (lambda x: None),
            'timestamp_value': (lambda x: self._parse_timestamp(x)),
            'reference_value': (lambda x: self._parse_doc_ref(x)),
            'map_value': (lambda x: {key: self._parse_value(value) for key, value in x["fields"].items()}),
            'integer_value': (lambda x: int(x)),
            'double_value': (lambda x: float(x)),
        }

    def convert(self, data_dict: dict) -> dict:
        result_dict = {}
        for key, value_dict in data_dict.items():
            result_dict[key] = self._parse_value(value_dict)
        return result_dict

    def _parse_value(self, value_dict: dict) -> Any:
        data_type, value = value_dict.popitem()

        return self._action_dict[data_type](value)

    def _parse_timestamp(self, timestamp: str):
        try:
            return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError as e:
            return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

    def _parse_doc_ref(self, doc_ref: str) -> firestore.DocumentReference:
        path_parts = doc_ref.split('/documents/')[1].split('/')
        collection_path = path_parts[0]
        document_path = '/'.join(path_parts[1:])

        doc_ref = self.client.collection(collection_path).document(document_path)
        return doc_ref

# async def run_v4_extraction(event, extra, pubsub: IMessagingPort, cloud_task_adapter: ICloudTaskPort):
#     if CLOUD_PROVIDER == "local":
#         await pubsub.publish(MEDICATION_EXTRACTION_V4_TOPIC, {
#             "document_id": event.document_id,
#             "patient_id": event.patient_id,
#             "app_id": event.app_id,
#             "tenant_id": event.tenant_id,
#             "storage_uri": event.storage_uri,
#             "priority": event.priority.value,
#             "created_at": event.created,
#         })
#     else:
#         # queue=QueueResolver().resolve_queue_name("v4_extraction", event.priority.value)
#         # url=f"{MEDICATION_EXTRACTION_V4_API_URL}/run_extraction"
        
#         queue_value = QueueResolver().resolve_queue_value("v4_extraction", event.priority.value)
#         url = f"{queue_value.api_url}/run_extraction"
#         queue = queue_value.queue_name
        
#         payload = {
#             "document_id": event.document_id,
#             "patient_id": event.patient_id,
#             "app_id": event.app_id,
#             "tenant_id": event.tenant_id,
#             "storage_uri": event.storage_uri,
#             "priority": event.priority.value,
#             "created_at": event.created,
#         }
#         extra["app_id"] = event.app_id
#         extra["tenant_id"] = event.tenant_id
#         extra["patient_id"] = event.patient_id
#         extra["queue"] = queue
#         extra["url"] = url
#         extra["payload"] = payload
#         LOGGER2.debug("Creating CloudTask...", extra=extra)

#         await cloud_task_adapter.create_task(
#             token=get_token(event.app_id, event.tenant_id, event.patient_id),
#             location=GCP_LOCATION_2,
#             service_account_email=SERVICE_ACCOUNT_EMAIL,
#             queue=queue,
#             url=url,
#             payload=payload
#         )

class EventarcAdapter(Starlette):
    @inject
    async def process_message(
        self,
        collection_name: str,
        document_id: str,
        before: Optional[dict],
        after: Optional[dict],
        events: IEventHandlingPort,
        commands: ICommandHandlingPort,
        pubsub: IMessagingPort,
        query: IQueryPort,
        cloud_task_adapter: ICloudTaskPort
    ):
        extra = {
            "collection_name": collection_name,
            "document_id": document_id,
        }
        try:
            LOGGER2.info(
                'Collection = %s, doc = %s, before = %s, after = %s',
                collection_name,
                document_id,
                json.dumps(before)[:256],
                json.dumps(after)[:256],
                extra=extra,
            )
        except Exception as e:
            extra.update({
                "error": str(e),
            })
            LOGGER2.error('Failed to log message', extra=extra)
        # Returning 4xx will cause Eventarc to retry the message.
        if collection_name.endswith('_events'):
            with await self.opentelemetry.getSpan("process_message:events") as span:
                event = parse_obj_as(Event, after)
                span.set_attribute("event_type", event.type)
                LOGGER2.debug('EventArc Event: %s', event, extra=extra)
                if event.type == "document_created":
                    
                    LOGGER2.debug('EventArc Event: document_created', extra=extra)
                    orchestration_launcher = OrchestrationLauncher(event.document_id, priority=event.priority)
                    await orchestration_launcher.launch()

                    #agent = MedicationExtractionOrchestrationAgent()
                    #await agent.orchestrate(event.document_id, priority=event.priority)
                    
                else:    
                    await events.handle_event(event)
                return Response(status_code=204)
        elif collection_name.endswith('_commands'):
            with await self.opentelemetry.getSpan("process_message:commands") as span:
                command = parse_obj_as(Command, after)
                span.set_attribute("command_type", command.type)
                LOGGER2.debug('Command: %s', command, extra=extra)
                await commands.handle_command(command)
                return Response(status_code=204)
        else:
            LOGGER2.warning('Unknown collection_name: %s', collection_name, extra=extra)

    async def on_eventarc_firestore(self, request: Request):
        """
        This endpoint is called by real Eventarc (in GCP) when a Firestore document is created, updated or deleted.
        """
        thisSpanName = "on_eventarc_firestore"        
        with await self.opentelemetry.getSpan(thisSpanName) as span:
            body = await request.body()
            proto: DocumentEventData = DocumentEventData.deserialize(body)
            data: dict = DocumentEventData.to_dict(proto)
            extra = {
                "method": thisSpanName,
                "data": data
            }
            LOGGER2.info('Received message from eventarc', extra=extra)

            full_path = (proto.value or proto.old_value).name
            path_parts = full_path.split('/documents/')[1].split('/')  # e. g. ["fide_events", "foobar"]
            collection_name, document_id = path_parts

            span.set_attribute("collection_name", collection_name)
            span.set_attribute("document_id", document_id)
            span.set_attribute("full_path", full_path)

            before = (
                DecoderThatHandlesStupidGoogleTypes(firestore.Client()).convert(data['old_value']['fields'])
                if proto.old_value
                else None
            )
            after = (
                DecoderThatHandlesStupidGoogleTypes(firestore.Client()).convert(data['value']['fields'])
                if proto.value
                else None
            )
            return await self.process_message(collection_name, document_id, before, after)

    async def on_eventarc_firestore_json(self, request: Request):
        """
        This endpoint is called by JS function in local Firebase emulator to simulate actual Pub/Sub push subscription.
        """
        data = await request.json()
        return await self.process_message(
            data['collection_name'],
            data['document_id'],
            data.get('before'),
            data.get('after'),
        )

    @inject()
    async def on_pubsub_external_files(self, request: Request, events: IEventHandlingPort):
        extra = {
            "method": "on_pubsub_external_files"
        }
        try:
            body = await request.body()

            LOGGER2.info('Received raw message from eventarc: %s', body, extra=extra)
            data = json.loads(body)
            
            message = data.get("message").get("data")
            message = base64.b64decode(message).decode('utf-8')
            
            if message:
                
                message = json.loads(message)

                extra["message"] = message                
                LOGGER2.info('Received message from eventarc', extra=extra)

                if message.get("timeCreated") and message.get("updated"):
                    if message.get("timeCreated") == message.get("updated"): #for new events, timeCreated and updated are the same
                    # if message.get("timeCreated") > (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat():
                        # this is a new file
                        await events.handle_event(OnExternalFilesEvent(
                            external_file_gcs_uri=f'gs://{message.get("bucket")}/{message.get("name")}',
                            raw_event = message,
                            app_id = "hhh" if "wsh-monolith_attachment" in message.get("bucket") else "hhh" #todo: create mapping between bucket and app_id and use it here
                        ))
                        return Response(status_code=204)
                LOGGER2.info("Skipping since its update/older event: %s", message, extra=extra)
                    
            
        except Exception as e:
            extra["error"] = str(e)
            LOGGER2.error('Error processing pubsub messages', exc_info=True, extra=extra)
        return Response(status_code=204)
    
    @inject()
    async def on_pubsub_events(self, request: Request, events: IEventHandlingPort,cloud_task_adapter:ICloudTaskPort,commands: ICommandHandlingPort):
        extra = {
            "method": "on_pubsub_events"
        }
        try:
            body = await request.body()
            LOGGER2.info('Received raw message from pubsub: %s', body, extra=extra)
            try:
                data = json.loads(body)
            except:
                data = body
            
            if data.get("message"):
                message = data.get("message").get("data")
                message = base64.b64decode(message).decode('utf-8')
            else:
                message = data

            extra["message"] = message
            
            if message:
                LOGGER2.info('Received message from pubsub', extra=extra)
                try:
                    message = json.loads(message)
                    extra["message"] = message
                except:
                    pass
                
                if message.get("event_type") == "recover":
                    failed_doc_operation_instance_log_id = message.get("failed_doc_operation_instance_log_id")
                    if CLOUD_PROVIDER == "local":
                        from ...usecases.orchestrator import recover
                        LOGGER2.debug("Pubsub message is for recovery.  Is local so invoking recover directly", extra=extra)
                        await recover(failed_doc_operation_instance_log_id)
                    else:
                        queue=CLOUD_TASK_QUEUE_NAME
                        url=f"{SELF_API}/orchestrate_v3_recover"
                        payload = {
                            "failed_doc_operation_instance_log_id": failed_doc_operation_instance_log_id
                        }
                        extra["app_id"] = message.get("app_id")
                        extra["tenant_id"] = message.get("tenant_id")
                        extra["patient_id"] = message.get("patient_id")
                        extra["queue"] = queue
                        extra["url"] = url
                        extra["payload"] = payload
                        LOGGER2.debug("Pubsub message is for recovery.  Creating CloudTask...", extra=extra)

                        await cloud_task_adapter.create_task(
                            token=get_token(message.get("app_id"), message.get("tenant_id"), message.get("patient_id")),
                            location=GCP_LOCATION_2,
                            service_account_email=SERVICE_ACCOUNT_EMAIL,
                            queue=queue,
                            url=url,
                            payload=payload
                        )
                if message.get("event_type") == "import_medications":
                    await commands.handle_command_with_explicit_transaction(ImportMedications(patient_id=message.get("patient_id"),
                                        tenant_id=message.get("tenant_id"),
                                        app_id=message.get("app_id"),
                                        ehr_token=message.get("ehr_token"),
                                        created_by=message.get("created_by"),
                                        modified_by=message.get("modified_by")))
                    # await import_medications(
                    #     ImportMedications(patient_id=message.get("patient_id"),
                    #                     tenant_id=message.get("tenant_id"),
                    #                     app_id=message.get("app_id"),
                    #                     ehr_token=message.get("ehr_token"),
                    #                     created_by=message.get("created_by"),
                    #                     modified_by=message.get("modified_by"))
                    # )
                    return Response(status_code=204)
                if message.get("event_type") == "import_attachments":
                    await commands.handle_command_with_explicit_transaction(ImportHostAttachments(
                                                app_id=message.get("app_id"), 
                                              tenant_id=message.get("tenant_id"), 
                                              patient_id=message.get("patient_id"),
                                              ehr_token=message.get("ehr_token"),
                                              api_token=message.get("api_token")))
                    # await import_host_attachments(
                    #     ImportHostAttachments(app_id=message.get("app_id"), 
                    #                           tenant_id=message.get("tenant_id"), 
                    #                           patient_id=message.get("patient_id"),
                    #                           ehr_token=message.get("ehr_token"),
                    #                           api_token=message.get("api_token")))
                    
                    return Response(status_code=204)
                if message.get("event_type") == "page_ocr_process_request":
                    from paperglass.usecases.v4.ocr import process_page_ocr
                    payload = message
                    document_id = payload.get("document_id")
                    page_number = payload.get("page_number")
                    page_uri = payload.get("page_uri")
                    patient_id = payload.get("patient_id")
                    app_id = payload.get("app_id")
                    tenant_id = payload.get("tenant_id")
                    
                    await process_page_ocr(
                        app_id=app_id, tenant_id=tenant_id, patient_id=patient_id,
                        document_id=document_id, page_number=page_number, page_uri=page_uri
                    )
                        
        except:
            LOGGER2.error('Error processing pubsub messages', exc_info=True, extra=extra)
        return Response(status_code=200)
    
    @inject()
    async def on_medications_event(self, request: Request, events: IEventHandlingPort, commands: ICommandHandlingPort, query:IQueryPort):
        extra = {
            "method": "on_medications_event"
        }
        try:
            body = await request.body()
            LOGGER2.info('Received raw message from pubsub: %s', body, extra=extra)
            try:
                data = json.loads(body)
            except:
                data = body
                
            if data.get("message"):
                message = data.get("message").get("data")
                message = base64.b64decode(message).decode('utf-8')
            else:
                message = data

            extra["message"] = message
            
            if message:
                LOGGER2.info('Received message from pubsub', extra=extra)
                try:
                    message = json.loads(message)
                    extra["message"] = message
                except:
                    pass
                
                if message.get("event_type") == "medications":
                    from paperglass.usecases.v4.medications import create_medications
                    payload = message.get("payload")
                    document_id = payload.get("document_id")
                    medications_storage_uri = payload.get("medications_storage_uri")
                    run_id = payload.get("run_id")
                    patient_id = payload.get("patient_id")
                    app_id = payload.get("app_id")
                    tenant_id = payload.get("tenant_id")
                    page_number = payload.get("page_number")
                    
                    try:
                        LOGGER2.debug("Processing medications from %s", medications_storage_uri, extra=extra)
                        await create_medications(document_id,page_number,run_id, medications_storage_uri)
                    except Exception as e:
                        LOGGER2.error(f"Error processing medications from {medications_storage_uri}: {traceback.format_exc()}",extra=extra)
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
                
                if message.get("event_type") == "status_update":
                    
                    payload = message.get("payload")
                    document_id = payload.get("document_id")
                    patient_id = payload.get("patient_id")
                    app_id = payload.get("app_id")
                    tenant_id = payload.get("tenant_id")
                    status = payload.get("status")
                    operation_instance_id = payload.get("run_id")
                    
                    config:Configuration = await get_config(tenant_id=tenant_id, app_id=app_id,query=query)
                    
                    if not config.enable_v4_orchestration_engine_parallel_processing:
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
        except:
            LOGGER2.error('Error processing medications pubsub messages', exc_info=True, extra=extra)
        return Response(status_code=200)
    
    def __init__(self):
        super().__init__(
            debug=True,
            routes=[
                Route('/pubsub/external_files', self.on_pubsub_external_files, methods=['POST']),
                Route('/pubsub/json', self.on_pubsub_events, methods=['POST']),
                Route('/firestore', self.on_eventarc_firestore, methods=['POST']),
                Route('/firestore/json', self.on_eventarc_firestore_json, methods=['POST']),
                Route('/medications', self.on_medications_event, methods=['POST']),
            ],
        )
        self.opentelemetry = opentelemetry
        
        

