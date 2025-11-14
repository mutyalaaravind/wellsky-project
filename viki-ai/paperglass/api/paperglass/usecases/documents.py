import os
from io import BytesIO
import json
from typing import Dict, List, Any

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from kink import inject
from paperglass.usecases.configuration import get_config
import pypdf
from paperglass.log import getLogger

from paperglass.domain.values import (
    Configuration, DocumentOperationStatus, DocumentOperationType, OCRType, Page, Rect, Vector2,
    DocumentProgressState
)
from paperglass.infrastructure.ports import IQueryPort, IStoragePort
from paperglass.domain.models import Document, DocumentOperation, DocumentOperationDefinition, DocumentOperationInstance, DocumentOperationInstanceLog, DocumentOperationStatusSnapshot, DocumentStatus,Page as PageAggregate
from paperglass.domain.models_common import (
    EntityFilter,
    UnsupportedFileTypeException
)
from paperglass.domain.utils.exception_utils import exceptionToMap
from paperglass.domain.values import DOCUMENT_OPERATION_TYPES
from paperglass.usecases.document_operation_instance_log import DocumentOperationInstanceLogService
from paperglass.settings import AUTO_CONVERT_IMAGE_TYPES
from paperglass.infrastructure.adapters.entity_extraction_client import EntityExtractionClient

#OpenTelemetry instrumentation
SPAN_BASE: str = "CONTROLLER:rest_controller:"
from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils
from opentelemetry.trace.status import Status, StatusCode
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

LOGGER = getLogger(__name__)

register_heif_opener()

async def create_document(app_id, tenant_id, patient_id, file_name, uploaded_bytes, token,priority,storage:IStoragePort, metadata:Dict[str,Any]={}, source_sha256: str=None):
    final_filename = None
    final_data = None

    # Extract the file extension
    _, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()

    LOGGER.debug("File extension: %s", file_extension)
    LOGGER.debug("Autoconvert image types: %s  %s", AUTO_CONVERT_IMAGE_TYPES, file_extension in AUTO_CONVERT_IMAGE_TYPES)

    if file_extension == '.pdf':
        pdf_reader = pypdf.PdfReader(BytesIO(uploaded_bytes))
        page_count = len(pdf_reader.pages)
        LOGGER.info('Page count: %d', page_count)
        pages = []
        # IMPORTANT: Pages in pypdf are 0-indexed
        for page in pdf_reader.pages:
            page_number = page.page_number + 1
            #LOGGER.info(f'Page %d size: %s', page_number, page.mediabox)
            pages.append(
                Page(
                    number=page_number,
                    mediabox=Rect(
                        tl=Vector2(x=page.mediabox.left, y=page.mediabox.top),
                        br=Vector2(x=page.mediabox.bottom, y=page.mediabox.right),
                    ),
                )
            )
        final_filename = file_name
        final_data = uploaded_bytes
    elif file_extension in AUTO_CONVERT_IMAGE_TYPES:
        LOGGER.info('Page count: 1 (created from image): %s', file_name)
        image = Image.open(BytesIO(uploaded_bytes))
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image = image.rotate(0)
        LOGGER.info('Image size: %s', json.dumps(image.size))
        dpi = 100
        # Convert image size to mediabox size
        mediabox_w, mediabox_h = image.size[0] * 72 / dpi, image.size[1] * 72 / dpi
        pages = [
            Page(
                number=1,
                mediabox=Rect(
                    tl=Vector2(x=0, y=0),
                    br=Vector2(x=mediabox_w, y=mediabox_h),
                ),
            )
        ]
        # Save image to variable
        pdf_output = BytesIO()
        image.save(pdf_output, format='pdf', resolution=dpi)
        final_filename = file_name.rpartition('.')[0] + '.pdf'
        final_data = pdf_output.getvalue()
    else:
        raise UnsupportedFileTypeException('Unsupported file type: ' + file_name)

    if not source_sha256:
        # Supports use cases where the file is not processed through source api and sha256 is provided as input
        from paperglass.domain.utils.sha256 import get_sha256_hash
        source_sha256 = get_sha256_hash(uploaded_bytes)

    document:Document = Document.create(app_id, tenant_id, patient_id, final_filename, pages, priority, metadata=metadata, source_sha256=source_sha256)
    document.token = token
    uri = await storage.put_document(app_id, tenant_id, patient_id,document.id, final_data)
    document.mark_uploaded(uri)
    return document

async def split_pages(app_id, tenant_id, patient_id,document:Document,document_operation_instance_id:str,document_operation_definition_id:str,storage:IStoragePort):
    raw_data = await storage.get_document(app_id, tenant_id, patient_id,document.id)
    pdf_reader = pypdf.PdfReader(BytesIO(raw_data))

    # Generate pages
    for i in range(0, len(pdf_reader.pages), 1):
        page_number = i + 1
        page = pdf_reader.pages[i]
        writer = pypdf.PdfWriter()
        writer.add_page(page)
        page_raw_data = BytesIO()
        writer.write(page_raw_data)
        page_raw_data.seek(0)
        LOGGER.warning('Uploading page %d of document %s (%d pages)', page_number, document.id, len(document.pages))
        uri = await storage.put_document_page(app_id, tenant_id, patient_id,document.id, page_number, page_raw_data.getvalue())
        document.add_page(page_number, uri,document_operation_instance_id,document_operation_definition_id)
    return document

async def perform_ocr(page:PageAggregate, raw_ocr:str, storage:IStoragePort):

    storage_uri = await storage.put_page_ocr(page.app_id, page.tenant_id, page.patient_id,page.document_id, page.id, raw_ocr, ocr_type=OCRType.raw)

    page.add_ocr(OCRType.raw, storage_uri)
    return page

async def get_documents(app_id:str, tenant_id:str, patient_id:str, start_at:str, end_at:str, limit:int, query:IQueryPort):
    thisSpanName = "get_documents"
    with await opentelemetry.getSpan(thisSpanName) as span:
        # Replace this with your logic to retrieve the documentId
        # For example, you can fetch it from a database or an API
        # Return None if no new documentId is available
        all_docs = []
        config:Configuration = await get_config(app_id, tenant_id, query)
        if (start_at or end_at) and limit:
            count = await query.list_documents_count(patient_id)
            docs = await query.list_documents_with_offset(patient_id, start_at,end_at, limit)
        else:
            docs = []

        for doc in docs:
            with await opentelemetry.getSpan(thisSpanName + ":get_document_status") as span1:
                try:
                    doc["status"] = await get_document_status(doc["app_id"], doc["tenant_id"], doc["patient_id"], doc["id"], query, document=doc)                    
                    doc["total_records"] = count #len(all_docs or docs)
                except Exception as e:
                    extra = {
                        "app_id": app_id,
                        "tenant_id": tenant_id,
                        "patient_id": patient_id,
                        "document_id": doc["id"],
                        "error": exceptionToMap(e)
                    }
                    LOGGER.error(f"Error getting document status for document {doc['id']}: {e}", extra=extra)
                    doc["status"] = {
                        "status":DocumentOperationStatus.NOT_STARTED.value,
                        "failed":0
                    }               

        return docs

async def transform_status(doc_operation_statuses:Dict[DocumentOperationType,DocumentOperationStatusSnapshot]):
    if doc_operation_statuses:
        doc_operation_status = doc_operation_statuses.get(DocumentOperationType.MEDICATION_EXTRACTION)
        if doc_operation_status:
            return {
                "failed": 0 if doc_operation_status.status != DocumentOperationStatus.FAILED else 1,
                "status": doc_operation_status.status.value,
                "pipelineStatuses": {
                    "end_date": doc_operation_status.end_time,
                    "start_date": doc_operation_status.start_time,
                    "type": doc_operation_status.operation_type.value,
                    "status": doc_operation_status.status.value
                }
            }
    else:
        return {
            "failed": 0,
            "status": DocumentOperationStatus.UNKNOWN.value,
            "pipelineStatuses": {
                "end_date": None,
                "start_date": None,
                "type": "",
                "status": DocumentOperationStatus.UNKNOWN.value
            }
        }

async def enrich_entity_extraction_status(ent_ex: DocumentProgressState, doc_operation_status: DocumentOperationStatusSnapshot) -> None:
    """
    Enriches the entity extraction progress state with detailed status from the entity extraction service.
    
    Args:
        ent_ex: The DocumentProgressState object to enrich
        doc_operation_status: The document operation status snapshot containing the operation instance ID
    """
    try:
        if doc_operation_status.operation_instance_id:
            entity_extraction_client = EntityExtractionClient()
            entity_extraction_status = await entity_extraction_client.get_status(doc_operation_status.operation_instance_id)
            
            LOGGER.debug("Retrieved entity extraction status: %s", entity_extraction_status)
            
            # Parse the entity extraction status and create nested children
            if entity_extraction_status and entity_extraction_status.get('pipelines'):
                for pipeline in entity_extraction_status['pipelines']:
                    pipeline_name = pipeline.get('id', 'Unknown Pipeline')
                    pipeline_status_str = pipeline.get('status', 'UNKNOWN')
                    
                    # Map entity extraction status to DocumentOperationStatus
                    if pipeline_status_str == 'COMPLETED':
                        pipeline_status = DocumentOperationStatus.COMPLETED
                    elif pipeline_status_str == 'FAILED':
                        pipeline_status = DocumentOperationStatus.FAILED
                    elif pipeline_status_str == 'IN_PROGRESS':
                        pipeline_status = DocumentOperationStatus.IN_PROGRESS
                    else:
                        pipeline_status = DocumentOperationStatus.IN_PROGRESS
                    
                    pipeline_progress = DocumentProgressState(
                        name=pipeline_name,
                        status=pipeline_status,
                        progress=1.0 if pipeline_status == DocumentOperationStatus.COMPLETED else 0.0
                    )
                    
                    # Add page-level children if tasks exist
                    if pipeline.get('tasks'):
                        for page_num, task in pipeline['tasks'].items():
                            task_status_str = task.get('status', 'UNKNOWN')
                            
                            # Map task status to DocumentOperationStatus
                            if task_status_str == 'COMPLETED':
                                task_status = DocumentOperationStatus.COMPLETED
                            elif task_status_str == 'FAILED':
                                task_status = DocumentOperationStatus.FAILED
                            elif task_status_str == 'IN_PROGRESS':
                                task_status = DocumentOperationStatus.IN_PROGRESS
                            else:
                                task_status = DocumentOperationStatus.IN_PROGRESS
                            
                            page_progress = DocumentProgressState(
                                name=f"Page {page_num}",
                                status=task_status,
                                progress=1.0 if task_status == DocumentOperationStatus.COMPLETED else 0.0
                            )
                            pipeline_progress.children.append(page_progress)
                    
                    ent_ex.children.append(pipeline_progress)
                
                # Calculate overall status based on children
                ent_ex.calculate()
            else:
                # No detailed status available, keep as in progress
                ent_ex.status = DocumentOperationStatus.IN_PROGRESS
        else:
            LOGGER.warning("No operation_instance_id found for entity extraction status")
            ent_ex.status = DocumentOperationStatus.IN_PROGRESS
            
    except Exception as e:
        extra = {
            "operation_instance_id": doc_operation_status.operation_instance_id,
            "error": exceptionToMap(e)
        }
        LOGGER.error("Error calling entity extraction service", extra=extra)
        # Fall back to in progress status if the call fails
        ent_ex.status = DocumentOperationStatus.IN_PROGRESS


async def transform_status_v2(doc_operation_statuses:Dict[DocumentOperationType,DocumentOperationStatusSnapshot]):

    # Convert doc_operation_statuses to dict of dictionaries
    doc_operation_statuses_dict = {}
    if doc_operation_statuses:
        for operation_type, status_snapshot in doc_operation_statuses.items():
            doc_operation_statuses_dict[operation_type.value] = status_snapshot.dict() if hasattr(status_snapshot, 'dict') else status_snapshot
    
    extra = {
        "operationStatuses": doc_operation_statuses_dict
    }
    
    status = DocumentProgressState(
        name="Overall",
        children=[]
    )

    LOGGER.debug("Transforming document operation statuses (v2): %s", doc_operation_statuses_dict, extra=extra)

    if doc_operation_statuses:

        # Handle the legacy Medication Extraction status
        doc_operation_status = doc_operation_statuses.get(DocumentOperationType.MEDICATION_EXTRACTION)
        if doc_operation_status:
            # For medication extraction, set progress to -1 when IN_PROGRESS to show indeterminate spinner
            progress = -1.0 if doc_operation_status.status == DocumentOperationStatus.IN_PROGRESS else 0.0
            med_ex = DocumentProgressState(
                name=DocumentOperationType.MEDICATION_EXTRACTION.value,
                status = doc_operation_status.status,
                progress = progress
            )
            status.children.append(med_ex)
        
        # Handle Entity Extraction status
        doc_operation_status = doc_operation_statuses.get(DocumentOperationType.ENTITY_EXTRACTION)
        if doc_operation_status:

            LOGGER.debug("Found Entity Extraction status: %s", doc_operation_status, extra=extra)
            
            ent_ex = DocumentProgressState(
                name=DocumentOperationType.ENTITY_EXTRACTION.value,
                status = doc_operation_status.status,
                progress = 0.0  # Will be set properly in calculate() based on status
            )
            
            if doc_operation_status.status == DocumentOperationStatus.IN_PROGRESS:                
                # Call the entity extraction service to get detailed status
                await enrich_entity_extraction_status(ent_ex, doc_operation_status)
            # For completed status without children, the calculate() method will set progress to 1.0
            
            status.children.append(ent_ex)

        else:
            LOGGER.debug("No Entity Extraction status found in document operation statuses: %s", doc_operation_statuses_dict, extra=extra)

        status.calculate()

    return status


@inject
async def get_document_status(app_id, tenant_id, patient_id, document_id, query:IQueryPort, document: dict = None):

    config:Configuration = await get_config(app_id, tenant_id, query)

    extra = {
        "app_id": app_id,
        "tenant_id": tenant_id,
        "patient_id": patient_id,
        "document_id": document_id
    }

    doc = None
    if not document:
        LOGGER.debug("Getting document by id: %s", document_id, extra=extra)
        doc = await query.get_document(document_id)
    elif isinstance(document, Document):
        #LOGGER.debug("Converting Document to dict: %s", document.dict(), extra=extra)
        doc = document.dict()    
    elif isinstance(document, dict):
        extra.update({
            "document": document
        })
        #LOGGER.debug("Using document dict: %s", document, extra=extra)
        doc = document
    else:
        raise ValueError("Invalid document object.  Should be a Document or dict:  %s", type(document))

    if not doc:
        LOGGER.error("Document not found: %s", doc, extra=extra)
        return {
            "status": DocumentOperationStatus.NOT_STARTED.name,
            "failed": 0
        }

    status = {}
    try:
        if config.use_async_document_status:
            doc_status = await transform_status_v2(Document(**doc).operation_status)
            status = doc_status.dict()
        else:
            status = await get_document_status_v3(doc["app_id"], doc["tenant_id"], doc["patient_id"], doc["id"], query)
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e)
        })
        LOGGER.error(f"Error getting document status for document {doc['id']}: {e}", extra=extra)
        status = {
            "status":DocumentOperationStatus.NOT_STARTED.value,
            "failed":0
        }

    return status


@inject
async def get_document_status_v3(app_id, tenant_id, patient_id, document_id, query:IQueryPort):
    #LOGGER.debug("For each DocumentOperationType...")

    pipelineStatuses = []
    status: dict = {}
    status["pipelineStatuses"] = pipelineStatuses

    allowed_operation_types = [DocumentOperationType.MEDICATION_EXTRACTION, DocumentOperationType.ENTITY_EXTRACTION]

    for documentOperationType in allowed_operation_types:
        doc_operation_definition:List[DocumentOperationDefinition] = await query.get_document_operation_definition_by_op_type(documentOperationType.value)
        doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(document_id, documentOperationType.value)
        active_document_operation_instance_id = None
        if doc_operation:
            active_document_operation_instance_id = doc_operation.active_document_operation_instance_id
        if len(doc_operation_definition)==0 and not active_document_operation_instance_id:
            msg: str = "Document Operation Instance for " + documentOperationType.value + " could not be found for document " + document_id
            if documentOperationType == DocumentOperationType.TOC:
                LOGGER.debug(msg)
            else:
                LOGGER.error(msg)

            thisStatus = {
                "type": documentOperationType.name,
                "status": DocumentOperationStatus.NOT_STARTED.name,
                "start_date": None,
                "end_date": None,
                "failed": 0,
                "details": "msg"
            }
            status["pipelineStatuses"].append(thisStatus)
        else:
            
            doc_operation_instances:List[DocumentOperationInstance] = await query.get_document_operation_instances_by_document_id(document_id, doc_operation_definition[0].id)

            active_document_operation_instance:DocumentOperationInstance = await query.get_document_operation_instance_by_id(active_document_operation_instance_id)
            
            if doc_operation_instances and active_document_operation_instance:
                deduped_doc_operation_instances = [x for x in doc_operation_instances if x.id != active_document_operation_instance.id]
            
                doc_operation_instances = deduped_doc_operation_instances + [active_document_operation_instance]
            elif active_document_operation_instance:
                doc_operation_instances = [active_document_operation_instance]
            
            
            if doc_operation_instances and len(doc_operation_instances)>0:
                #LOGGER.debug("Has doc operation instance")
                doc_operation_instances.sort(key=lambda x: x.created_at, reverse=True)
                most_recent_doc_operation_instance = doc_operation_instances[0]

                outStatus = None
                if most_recent_doc_operation_instance.status:
                    outStatus = most_recent_doc_operation_instance.status.name

                thisStatus = {
                    "type": documentOperationType.name,
                    "status": outStatus,
                    "start_date": most_recent_doc_operation_instance.start_date,
                    "end_date": most_recent_doc_operation_instance.end_date,
                    "failed": 0
                }

                status["pipelineStatuses"].append(thisStatus)

                # TODO: This is a temporary solution to get the failed logs for legacy instances which don't have a status
                if most_recent_doc_operation_instance.status == DocumentOperationStatus.FAILED or most_recent_doc_operation_instance.status == None:
                    # Retrieve the details from the logs
                    success, failed = await get_document_status_logs_summarized(app_id, tenant_id, patient_id, document_id, most_recent_doc_operation_instance.id)
                    thisStatus["failed"] = len(failed)

                if most_recent_doc_operation_instance.status == None:
                    if thisStatus["failed"] > 0:
                        thisStatus["status"] = DocumentOperationStatus.FAILED.name
                    else:
                        thisStatus["status"] = DocumentOperationStatus.COMPLETED.name
            else:
                LOGGER.info("No doc operation instance found")
                thisStatus = {
                    "type": documentOperationType.name,
                    "status": DocumentOperationStatus.NOT_STARTED.name,
                    "start_date": None,
                    "end_date": None,
                    "failed": 0,
                    "details": "No Operation Instances found for this document"
                }
                status["pipelineStatuses"].append(thisStatus)

    status["status"] = resolve_most_important_status(status["pipelineStatuses"])
    status["failed"] = resolve_most_fails(status["pipelineStatuses"])

    #LOGGER.debug("Document statuses: %s", status)
    return status

def resolve_most_important_status(statuses:List[dict]):
    bestStatus = None
    if statuses == None or len(statuses) == 0:
        return DocumentOperationStatus.NOT_STARTED.name
    for status in statuses:
        if status["type"].lower() == DocumentOperationType.MEDICATION_EXTRACTION.value.lower():
            if status["status"] == DocumentOperationStatus.FAILED.name:
                bestStatus = DocumentOperationStatus.FAILED.name
            elif status["status"] == DocumentOperationStatus.IN_PROGRESS.name and bestStatus not in [DocumentOperationStatus.FAILED.name]:
                bestStatus = DocumentOperationStatus.IN_PROGRESS.name
            elif status["status"] == DocumentOperationStatus.NOT_STARTED.name and bestStatus not in [DocumentOperationStatus.FAILED.name, DocumentOperationStatus.IN_PROGRESS.name]:
                bestStatus = DocumentOperationStatus.NOT_STARTED.name
            elif status["status"] == DocumentOperationStatus.COMPLETED.name and bestStatus not in [DocumentOperationStatus.FAILED.name, DocumentOperationStatus.IN_PROGRESS.name, DocumentOperationStatus.NOT_STARTED.name]:
                bestStatus = DocumentOperationStatus.COMPLETED.name
            else:
                LOGGER.debug("No overall status change for status: %s  Current best status: %s", status, bestStatus)
                bestStatus = None

    if bestStatus == None:
        bestStatus = DocumentOperationStatus.IN_PROGRESS.name
    return bestStatus

def resolve_most_fails(statuses:List[dict]):
    mostFails = 0
    for status in statuses:
        if status["failed"] > mostFails:
            mostFails = status["failed"]
    return mostFails

@inject
async def get_document_status_logs_summarized(app_id, tenant_id, patient_id, document_id, doc_operation_instance_id, query:IQueryPort):
    # query document operation to see if any new operation in progress
    # if not, return the previous status
    # if yes, return the new status by query operation instance
    doc_logger = DocumentOperationInstanceLogService()
    doc_operation_instance_logs:DocumentOperationInstanceLog = await doc_logger.list(document_id, doc_operation_instance_id)
    #doc_operation_instance_logs:DocumentOperationInstanceLog = await query.get_document_operation_instance_logs_by_document_id(document_id,doc_operation_instance_id)
    failed_logs = filter(lambda x: x.status == "FAILED", doc_operation_instance_logs)
    success_logs = filter(lambda x: x.status == "COMPLETED", doc_operation_instance_logs)
    return [x for x in success_logs], [x for x in failed_logs]


@inject
async def get_document_logs(document_id, query:IQueryPort, filter:EntityFilter=filter):

    results = {}
    for documentOperationType in DOCUMENT_OPERATION_TYPES:

        logs = []

        document_operation = await query.get_document_operation_by_document_id(document_id, documentOperationType.value)

        if document_operation:
            doc_operation_instance_id: DocumentOperation = document_operation.active_document_operation_instance_id
            doc_logger = DocumentOperationInstanceLogService()
            doc_operation_instance_logs:DocumentOperationInstanceLog = await doc_logger.list(document_id, doc_operation_instance_id)
            #doc_operation_instance_logs:DocumentOperationInstanceLog = await query.get_document_operation_instance_logs_by_document_id(document_id, doc_operation_instance_id)

            if filter:
                logs = filter.filter(doc_operation_instance_logs)
                results[documentOperationType.name] = logs
            else:
                results[documentOperationType.name] = doc_operation_instance_logs
        else:
            LOGGER.warning("No doc operation found for document %s", document_id)
            results[documentOperationType.name] = []

    return results


@inject
async def get_document_status_by_host_attachment_id(app_id: str, tenant_id: str, patient_id: str, host_attachment_id: str, query: IQueryPort):
    """
    Get document status by host_attachment_id.
    
    Args:
        app_id: The application ID
        tenant_id: The tenant ID  
        patient_id: The patient ID
        host_attachment_id: The host attachment ID (stored as source_id in Document)
        query: Query port for database operations
        
    Returns:
        DocumentStatusResponse containing the document status information
        
    Raises:
        ValueError: If no document is found for the given host_attachment_id
    """
    from paperglass.domain.values import DocumentStatusResponse
    
    # Find document by source_id (which corresponds to host_attachment_id)
    document = await query.get_document_by_source_id(host_attachment_id, app_id=app_id, tenant_id=tenant_id, patient_id=patient_id)
    
    if not document:
        raise ValueError(f"No document found for host_attachment_id: {host_attachment_id}")
    
    # Get the document status using the existing logic
    status = await get_document_status(
        app_id, 
        tenant_id, 
        patient_id, 
        document["id"], 
        query, 
        document=document
    )
    
    # Ensure status is always a DocumentProgressState object
    if isinstance(status, dict):
        # Convert dictionary status to DocumentProgressState
        from paperglass.domain.values import DocumentProgressState, DocumentOperationStatus
        
        # Handle legacy v3 status format
        if "pipelineStatuses" in status:
            progress_state = DocumentProgressState(
                name="Overall",
                status=DocumentOperationStatus(status.get("status", "UNKNOWN")),
                progress=1.0 if status.get("status") == "COMPLETED" else 0.0,
                children=[]
            )
            
            # Add pipeline statuses as children
            for pipeline_status in status.get("pipelineStatuses", []):
                child_status = DocumentProgressState(
                    name=pipeline_status.get("type", "Unknown"),
                    status=DocumentOperationStatus(pipeline_status.get("status", "UNKNOWN")),
                    progress=1.0 if pipeline_status.get("status") == "COMPLETED" else 0.0
                )
                progress_state.children.append(child_status)
            
            progress_state.calculate()
            status = progress_state
        else:
            # Handle other dictionary formats by creating a basic DocumentProgressState
            status = DocumentProgressState(
                name="Overall",
                status=DocumentOperationStatus(status.get("status", "UNKNOWN")),
                progress=1.0 if status.get("status") == "COMPLETED" else 0.0
            )
    elif not isinstance(status, DocumentProgressState):
        # Fallback for any other type
        from paperglass.domain.values import DocumentProgressState, DocumentOperationStatus
        status = DocumentProgressState(
            name="Overall",
            status=DocumentOperationStatus.UNKNOWN,
            progress=0.0
        )

    return DocumentStatusResponse(
        app_id=app_id,
        tenant_id=tenant_id,
        patient_id=patient_id,
        document_id=document["id"],
        host_attachment_id=host_attachment_id,
        status=status,
        metadata=document.get("metadata", {})
    )


@inject
async def get_document_logs_by_instace_id(document_id:str, doc_operation_instance_id:str, query:IQueryPort):
    doc_logger = DocumentOperationInstanceLogService()
    doc_operation_instance_logs:DocumentOperationInstanceLog = await doc_logger.list(document_id, doc_operation_instance_id)
    #doc_operation_instance_logs:DocumentOperationInstanceLog = await query.get_document_operation_instance_logs_by_document_id(document_id,doc_operation_instance_id)
    return doc_operation_instance_logs


async def on_document_processing_complete(document: Document, query: IQueryPort):
    """
    Handle document processing completion by invoking configured callbacks.
    
    :param document: The document that completed processing
    :param query: Query port for database operations
    """
    from paperglass.usecases.callback_invoker import CallbackInvoker
    
    extra = {
        "app_id": document.app_id,
        "tenant_id": document.tenant_id,
        "patient_id": document.patient_id,
        "document_id": document.id
    }
    
    try:
        LOGGER.info("Document processing complete - invoking callbacks", extra=extra)
        
        # Create callback invoker and invoke document processing complete callback
        callback_invoker = CallbackInvoker()
        success = await callback_invoker.invoke_document_processing_complete(document, query)
        
        if success:
            LOGGER.info("Document processing complete callbacks invoked successfully", extra=extra)
        else:
            LOGGER.warning("Document processing complete callbacks failed", extra=extra)
            
    except Exception as e:
        LOGGER.error("Error invoking document processing complete callbacks", extra={
            **extra,
            "error": str(e)
        })


async def get_entity_toc(document_id: str, run_id:str, query: IQueryPort):
    """
    Retrieve the Table of Contents (TOC) for a document if available.
    
    :param document: The document to retrieve TOC for
    :param query: Query port for database operations
    :return: List of TOC entries or empty list if not available
    """
    extra = {        
        "document_id": document_id,
        "run_id": run_id
    }
    
    entity_toc_data = {}
    entity_toc_data_list = await query.get_document_entity_toc_by_document_id_and_run_id(document_id, run_id)

    idx = 0
    for toc_item in entity_toc_data_list:

        if idx == 0:
            entity_toc_data = toc_item
            idx += 1
            continue

        # For each toc_item after the first one, merge toc_item.categories with entity_toc_data.categories
        if hasattr(toc_item, 'categories') and hasattr(entity_toc_data, 'categories'):
            entity_toc_data.categories.extend(toc_item.categories)
        elif hasattr(toc_item, 'categories') and toc_item.categories:
            # If entity_toc_data doesn't have categories but toc_item does, initialize it
            entity_toc_data.categories = toc_item.categories

    return entity_toc_data
