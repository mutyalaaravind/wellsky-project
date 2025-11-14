import json
import traceback
from paperglass.domain.models import Document
from paperglass.usecases.configuration import get_config
from paperglass.infrastructure.repositories.ocr import PageOCRRepository
from paperglass.usecases.queue_resolver import QueueResolver
from paperglass.infrastructure.ports import ICloudTaskPort, IDocumentAIAdapter, IMessagingPort, IQueryPort, IStoragePort
from paperglass.domain.values import  Configuration, DocumentOperationType, OrchestrationPriority, PageOcrStatus, Result
from paperglass.settings import CLOUD_PROVIDER, GCP_LOCATION_2, GCS_BUCKET_NAME, PAGE_OCR_TOPIC, SELF_API, SERVICE_ACCOUNT_EMAIL
from paperglass.domain.utils.token_utils import mktoken2

from paperglass.log import labels, CustomLogger

from kink import inject

LOGGER2 = CustomLogger(__name__)
LOGGER = LOGGER2

@inject()
async def get_page_uri(app_id:str, tenant_id:str, patient_id:str,document_id:str, page_number:int, query:IQueryPort)->str:
    document:Document = Document(**await query.get_document(document_id))
    page_uri = None
    if document.operation_status and document.operation_status[DocumentOperationType.MEDICATION_EXTRACTION].orchestration_engine_version == "v4":
        page_uri = f"gs://{GCS_BUCKET_NAME}/paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}/{page_number}.pdf"
    else:
        page = [page for page in document.pages if page.number == int(page_number)]
        
        if page:
            page_uri = page[0].storage_uri
            print(page_uri)
    return page_uri

@inject
async def init_page_ocr(app_id:str,
                        tenant_id:str,
                        patient_id:str,
                        document_id:str, 
                        page_number:int,
                        pubsub_adapter: IMessagingPort,
                        cloud_task_adapter: ICloudTaskPort
                        )->Result:
    page_uri = await get_page_uri(app_id, tenant_id, patient_id, document_id, page_number)
    page_ocr_repo = PageOCRRepository()
    config:Configuration = await get_config(app_id, tenant_id)
    page_ocr_status:PageOcrStatus = await page_ocr_repo.get_ocr_status(document_id, page_number)
    if page_ocr_status not in (PageOcrStatus.NOT_STARTED, PageOcrStatus.FAILED):
        return Result(success=True, return_data=f"Ocr for Page {page_number}, document {document_id} status: {page_ocr_status.value}")
    else:
        await page_ocr_repo.create_or_update_ocr_status(document_id, 
                                                page_number, 
                                                page_uri, 
                                                PageOcrStatus.NOT_STARTED)
        payload = {
                    "event_type": "page_ocr_process_request",
                    "document_id": document_id,
                    "page_number": page_number,
                    "page_uri": page_uri,
                    "app_id": app_id,
                    "tenant_id": tenant_id,
                    "patient_id": patient_id
                }
        
        queue = QueueResolver().resolve_queue_name(category="page_ocr",priority=OrchestrationPriority.HIGH.value)
        url = f"{SELF_API}/v4/ocr/{document_id}/{page_number}/process"
        if config.ocr_trigger_config and config.ocr_trigger_config.processing_mode_async:
            if CLOUD_PROVIDER == "local":
                await pubsub_adapter.publish(
                    topic=PAGE_OCR_TOPIC,
                    message=payload
                )
            else:
                await cloud_task_adapter.create_task(
                    token=mktoken2(app_id, tenant_id, patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue,
                    url=url,
                    payload=payload
                )
        else:
            await process_page_ocr(app_id, tenant_id, patient_id, 
                                   document_id, page_number, page_uri)
        return Result(success=True, return_data=f"Ocr for Page {page_number}, document {document_id} status: {page_ocr_status.value}")

@inject
async def get_page_ocr_status(app_id:str,
                        tenant_id:str,
                        patient_id:str,
                        document_id:str, 
                        page_number:int,
                        query:IQueryPort
                        )->Result:
    
    page_ocr_repo = PageOCRRepository()
    page_ocr_status:PageOcrStatus = await page_ocr_repo.get_ocr_status(document_id, page_number)
    return page_ocr_status
    
    
@inject
async def process_page_ocr(app_id:str, tenant_id:str, patient_id:str,
                           document_id:str, page_number:int, page_uri:str, 
                           docai: IDocumentAIAdapter, 
                           storage_adapter:IStoragePort) -> Result:
    page_ocr_repo = PageOCRRepository()
    ocr_status:PageOcrStatus = PageOcrStatus.QUEUED

    billing_metadata = {
        "business_unit": "unknown",
        "solution_code": "unknown",
        "app_id": app_id,
        "tenant_id": tenant_id,
        "patient_id": patient_id,
        "document_id": document_id,
        "page_number": page_number,
        "page_uri": page_uri
    }

    app_config = await get_config(app_id, tenant_id)
    if app_config and app_config.accounting:
        accounting = app_config.accounting
        billing_metadata.update({
            "business_unit": accounting.business_unit if accounting.business_unit else "unknown",
            "solution_code": accounting.solution_code if accounting.solution_code else "unknown"
        })    

    extra = {"document_id": document_id, "page_number": page_number, "page_uri": page_uri}
    
    try:
        doc_ai_output = await docai.process_document(page_uri, metadata=billing_metadata)
                
        if doc_ai_output:
            # Identify page rotation
            LOGGER.debug('PerformOCR: Persisting OCR output for documentId %s', document_id, extra=extra)
            results = json.dumps(doc_ai_output[0]).encode('utf-8')
            base_path = f"paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}"
            await storage_adapter.write_text(GCS_BUCKET_NAME, 
                                        f"{base_path}/ocr/{page_number}/raw.json", 
                                        results, 
                                        content_type="application/json")
            
            LOGGER.debug('PerformOCR: Identifying page rotation for documentId %s', document_id, extra=extra)
            rotation = docai.identify_rotation(doc_ai_output[0]['page'])
                    
            await page_ocr_repo.create_or_update_ocr_status(document_id, 
                                                    page_number, 
                                                    page_uri, 
                                                    PageOcrStatus.COMPLETED)
    except Exception as e:
        await page_ocr_repo.create_or_update_ocr_status(document_id, 
                                                    page_number, 
                                                    page_uri, 
                                                    PageOcrStatus.FAILED)
        LOGGER.error('PerformOCR: Error processing documentId %s %s', document_id,traceback.format_exc() ,  extra=extra)
    return Result(success=True, return_data=f"Ocr for Page {page_number}, document {document_id} processed")