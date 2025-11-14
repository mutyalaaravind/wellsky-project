from base64 import b64encode
from json import dumps
import time
from typing import Dict, List, Any
from adapters.pub_sub import GooglePubSubAdapter
from adapters.storage import StorageAdapter
from adapters.paperglass import PaperglassAdapter
from adapters.cloud_tasks import CloudTaskAdapter
from services.queue_resolver import get_queue_resolver
from utils.date import now_utc
from services.page_service import PageService
from settings import (
    CALLBACK_PAPERGLASS_ENABLED,
    CLOUD_PROVIDER,
    EXTRACTION_CLASSIFY_INTERNAL_TOPIC,
    EXTRACTION_DOCUMENT_STATUS_TOPIC,
    EXTRACTION_MEDICATION_INTERNAL_TOPIC,
    GCP_LOCATION_2,
    GCP_PROJECT_ID,
    GCP_PUBSUB_PROJECT_ID,
    GCS_BUCKET_NAME,
    MEDICATION_EXTRACTION_V4_TOPIC,
    PAPERGLASS_API_URL,
    PAPERGLASS_INTEGRATION_TOPIC,
    SELF_API_URL,
    SELF_API_URL_2,
    SERVICE_ACCOUNT_EMAIL
)
from services.pdf_manager import PDFManager
from models import Document, DocumentOperationStep, Page
from model_metric import Metric
from utils.custom_logger import getLogger, log_elapsed_time

LOGGER = getLogger(__name__)


class DocumentJob:
    
    def __init__(self):
        self.pdf_manager = PDFManager()
        self.pubsub_adapter = GooglePubSubAdapter(project_id=GCP_PUBSUB_PROJECT_ID)
        self.storage_adapter = StorageAdapter()
        self.paperglass_adapter = PaperglassAdapter()
        self.cloud_task_adapter = CloudTaskAdapter(project_id=GCP_PROJECT_ID)
    
    def _mktoken2(self, app_id, tenant_id, patient_id):
        return b64encode(dumps({'appId': app_id, 'tenantId': tenant_id, 'patientId': patient_id}).encode()).decode()
    
    async def run_extraction(self,document,retry_attempt:int=0):
        payload = {
                        "document_id": document.document_id,
                        "patient_id": document.patient_id,
                        "app_id": document.app_id,
                        "tenant_id": document.tenant_id,
                        "storage_uri": document.storage_uri,
                        "priority": document.priority.value,
                        "retry_attempt":retry_attempt,
                        "wait_time_start": now_utc().isoformat(),
                        "created_at": document.created_at.isoformat()
                    }
        if CLOUD_PROVIDER == "local":
            LOGGER.warning(f"pubsub topic: {MEDICATION_EXTRACTION_V4_TOPIC}")
            await self.pubsub_adapter.publish(
                MEDICATION_EXTRACTION_V4_TOPIC,payload
            )
        else:
            # call cloud task
            queue_resolver = get_queue_resolver(app_id=document.app_id)
            queue_value = queue_resolver.resolve_queue_value("run_extraction", document.priority)
            queue = queue_value.queue_name
            url = queue_value.api_url

            await self.cloud_task_adapter.create_task(
                token=self._mktoken2(document.app_id, document.tenant_id, document.patient_id),
                location=GCP_LOCATION_2,
                service_account_email=SERVICE_ACCOUNT_EMAIL,
                queue=queue,
                url=f"{url}/run_extraction",
                payload = payload
            )
            Metric.send(Metric.MetricType.PIPELINE_CLOUDTASK_PREFIX + "RUN_EXTRACTION", tags={
                "priority": document.priority.value, 
                "category": "run_extraction", 
                "queueName": queue,
                "request": {
                    "location": GCP_LOCATION_2,
                    "service_account_email": SERVICE_ACCOUNT_EMAIL,
                    "queue": queue,
                    "url": url,
                    "payload": payload
                }
            })
    
    @log_elapsed_time(DocumentOperationStep.SPLIT_PAGES, arg_types=[Document])
    async def split_pages(self, document:Document, run_id:str, wait_time_start: str)->List[Page]:
        # pdf_manager: split pdf and write to gcs for each page
        # for each page, do below:
        # 1. classify (called via cloud task) and store result in gcs
        # 2. extract medications (called via cloud task) and store result in gcs
        # 3. medispan matching (called via cloud task) and store result in gcs
        # 4. commit to db
        
        pages:List[Page] = await self.pdf_manager.split_pages(document,run_id)
        
        return pages
    
    async def run_classify(self, document:Document, page:Page, retry_attempt:int=0, ocr_processing_disabled=True):
        LOGGER.warning(f"Page storage uri: {page.storage_uri}")
        payload = {
                        "document":document.dict(),
                        "page_storage_uri":page.storage_uri,
                        "page_number":page.page_number,
                        "total_pages":page.total_pages,
                        "run_id":page.run_id,
                        "retry_attempt":retry_attempt,
                        "wait_time_start": now_utc().isoformat(),
                        "ocr_processing_disabled": ocr_processing_disabled
                    }
        if CLOUD_PROVIDER == "local":
            LOGGER.warning(f"pubsub topic: {EXTRACTION_CLASSIFY_INTERNAL_TOPIC}")
            await self.pubsub_adapter.publish(
                EXTRACTION_CLASSIFY_INTERNAL_TOPIC,payload
            )
        else:
            # call cloud task
            url = f"{SELF_API_URL}/classify"
            queue_resolver = get_queue_resolver(app_id=document.app_id)
            queue_value = queue_resolver.resolve_queue_value("page_classification", document.priority)
            queue = queue_value.queue_name
            url = f"{queue_value.api_url}/classify"
            
            await self.cloud_task_adapter.create_task(
                    token=self._mktoken2(document.app_id, document.tenant_id, document.patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue,
                    url=url,
                    payload=payload
                )
            Metric.send(Metric.MetricType.PIPELINE_CLOUDTASK_PREFIX + "CLASSIFY", tags={
                "priority": document.priority.value, 
                "category": "classify", 
                "queueName": queue,
                "request": {
                    "location": GCP_LOCATION_2,
                    "service_account_email": SERVICE_ACCOUNT_EMAIL,
                    "queue": queue,
                    "url": url,
                    "payload": payload
                }
            })
    
    @log_elapsed_time(DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION, arg_types=[Document,Page])
    async def classify(self, document:Document, page:Page)->str:
        page_service = PageService(document=document, page=page)
        classified_text = await page_service.classify()
        
        LOGGER.warning(f"Classified text: {classified_text}")
        
        return classified_text
    
    async def run_medications(self, document:Document, page:Page, retry_attempt:int = 0):
        LOGGER.warning(f"Page storage uri: {page.storage_uri}")
        payload = {
                        "document":document.dict(),
                        "page_storage_uri":page.storage_uri,
                        "page_number":page.page_number,
                        "total_pages":page.total_pages,
                        "run_id":page.run_id,
                        "retry_attempt":retry_attempt,
                        "wait_time_start": now_utc().isoformat()
                    }
        if CLOUD_PROVIDER == "local":
            LOGGER.warning(f"pubsub topic: {EXTRACTION_MEDICATION_INTERNAL_TOPIC}")
            await self.pubsub_adapter.publish(EXTRACTION_MEDICATION_INTERNAL_TOPIC,payload)
        else:
            url = f"{SELF_API_URL_2}/medications"
            queue_resolver = get_queue_resolver(app_id=document.app_id)            
            queue_value = queue_resolver.resolve_queue_value("medication_extraction", document.priority)
            queue = queue_value.queue_name
            url = f"{queue_value.api_url}/medications"
            
            await self.cloud_task_adapter.create_task(
                    token=self._mktoken2(document.app_id, document.tenant_id, document.patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue,
                    url=url,
                    payload=payload
                )
            Metric.send(Metric.MetricType.PIPELINE_CLOUDTASK_PREFIX + "MEDICATIONS", tags={
                    "priority": document.priority.value, 
                    "category": "medications", 
                    "queueName": queue,
                    "request": {
                        "location": GCP_LOCATION_2,
                        "service_account_email": SERVICE_ACCOUNT_EMAIL,
                        "queue": queue,
                        "url": url,
                        "payload": payload
                    }
                })
    
    @log_elapsed_time(DocumentOperationStep.MEDICATIONS_EXTRACTION, arg_types=[Document,Page])
    async def medications(self, document:Document, page:Page)->Dict:
        page_service = PageService(document=document, page=page)
        medications = await page_service.medication()
        return medications
    
    @log_elapsed_time(DocumentOperationStep.MEDISPAN_MATCHING, arg_types=[Document,Page])
    async def medispan_match(self, document:Document, page:Page):
        page_service = PageService(document=document, page=page)
        medications,medispan_search_results = await page_service.medispan_match()
        
        return medications,medispan_search_results
    
    async def run_create_medications(self, document:Document, page:Page, retry_attempt:int=0):
        if not CALLBACK_PAPERGLASS_ENABLED:
            LOGGER.info(f"CALLBACK_PAPERGLASS_ENABLED is false. Skipping medication results submission to paperglass for document {document.document_id}, page {page.page_number}")
            return
            
        page_service = PageService(document=document, page=page)
        payload = {
                                        "document_id": document.document_id,
                                        "run_id": page.run_id,
                                        "medications_storage_uri": await page_service.get_medispan_matched_storage_uri(),
                                        "app_id": document.app_id,
                                        "tenant_id": document.tenant_id,
                                        "patient_id": document.patient_id,
                                        "page_number": page.page_number,
                                        "wait_time_start": now_utc().isoformat(),
                                    }
        if CLOUD_PROVIDER == "local":
            await self.pubsub_adapter.publish(
                    PAPERGLASS_INTEGRATION_TOPIC,{
                            "event_type":"medications",
                            "payload": payload
                        }
                )
        else:
            url = f"{PAPERGLASS_API_URL}/api/v4/create_medications"
            queue_resolver = get_queue_resolver(app_id=document.app_id)            
            queue_value = queue_resolver.resolve_queue_value("paperglass_integration", document.priority)
            queue = queue_value.queue_name
            url = f"{queue_value.api_url}/api/v4/create_medications"
            
            await self.cloud_task_adapter.create_task(
                    token=self._mktoken2(document.app_id, document.tenant_id, document.patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue,
                    url=url,
                    payload=payload
                )
            Metric.send(Metric.MetricType.PIPELINE_CLOUDTASK_PREFIX + "CREATE_MEDICATIONS", tags={
                    "priority": document.priority.value, 
                    "category": "medications", 
                    "queueName": queue,
                    "request": {
                        "location": GCP_LOCATION_2,
                        "service_account_email": SERVICE_ACCOUNT_EMAIL,
                        "queue": queue,
                        "url": url,
                        "payload": payload
                    }
                })
    
    @log_elapsed_time(DocumentOperationStep.PERFORM_OCR, arg_types=[Document,Page])
    async def perform_ocr(self, document:Document,page:Page):
        page_service = PageService(document=document, page=page)
        ocr_text = await page_service.perform_ocr()
        return ocr_text
    
    async def run_status_check(self, document:Document, page:Page, retry_attempt:int=0):
        LOGGER.warning(f"Medication exists in page {page.page_number}")
        payload = {
                        "document":document.dict(),
                        "page_storage_uri":page.storage_uri,
                        "page_number":page.page_number,
                        "total_pages":page.total_pages,
                        "run_id":page.run_id,
                        "wait_time_start": now_utc().isoformat(),
                        "retry_attempt":retry_attempt
                    }
        if CLOUD_PROVIDER == "local":
            await self.pubsub_adapter.publish(
                EXTRACTION_DOCUMENT_STATUS_TOPIC,payload
                #ordering_key=document.document_id
            )
        else:
            url = f"{SELF_API_URL}/update_status"
            queue_resolver = get_queue_resolver(app_id=document.app_id)
            queue_value = queue_resolver.resolve_queue_value("status_check", document.priority)
            queue = queue_value.queue_name
            url = f"{queue_value.api_url}/update_status"
            
            await self.cloud_task_adapter.create_task(
                    token=self._mktoken2(document.app_id, document.tenant_id, document.patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue,
                    url=url,
                    payload=payload
                )
            Metric.send(Metric.MetricType.PIPELINE_CLOUDTASK_PREFIX + "STATUS_CHECK", tags={
                    "priority": document.priority.value, 
                    "category": "medications", 
                    "queueName": queue,
                    "request": {
                        "location": GCP_LOCATION_2,
                        "service_account_email": SERVICE_ACCOUNT_EMAIL,
                        "queue": queue,
                        "url": url,
                        "payload": payload
                    }
                })
        
    async def status_check(self, document:Document, page:Page):
        entries = await self.storage_adapter.list_folder_entries(GCS_BUCKET_NAME, 
                                                       f"{await self.storage_adapter.get_base_path(document)}/extracted_medications/{page.run_id}/",
                                                       ".json")
        
        if len(entries) == page.total_pages:
            return True
        else:
            return False
        
    @log_elapsed_time(DocumentOperationStep.STATUS_UPDATE, arg_types=[Document])
    async def update_status(self,document:Document, run_id, status, metadata: dict[str, Any] = {}):
        # call paperglass api to update document status
        LOGGER.warning(f"Document {document.document_id} completed with status {status}")
        
        if not CALLBACK_PAPERGLASS_ENABLED:
            LOGGER.info(f"CALLBACK_PAPERGLASS_ENABLED is false. Skipping status update to paperglass for document {document.document_id}, status: {status}")
            return
            
        #return await self.paperglass_adapter.update_status(document, "medication_extraction",status)
        payload = {
                    "document_id": document.document_id,
                    "app_id": document.app_id,
                    "tenant_id": document.tenant_id,
                    "patient_id": document.patient_id,
                    "status": status,
                    "run_id": run_id,
                    "wait_time_start": now_utc().isoformat(),
                }
        if CLOUD_PROVIDER == "local":
            await self.pubsub_adapter.publish(
                        PAPERGLASS_INTEGRATION_TOPIC,{
                                "event_type":"status_update",
                                "payload": payload
                            }
                    )
        else:
            url = f"{PAPERGLASS_API_URL}/api/v4/status_update"
            queue_resolver = get_queue_resolver(app_id=document.app_id)            
            queue_value = queue_resolver.resolve_queue_value("status_update", document.priority)
            queue = queue_value.queue_name
            url = f"{queue_value.api_url}/api/v4/status_update"
            
            await self.cloud_task_adapter.create_task(
                    token=self._mktoken2(document.app_id, document.tenant_id, document.patient_id),
                    location=GCP_LOCATION_2,
                    service_account_email=SERVICE_ACCOUNT_EMAIL,
                    queue=queue,
                    url=url,
                    payload=payload
                )
        elapsed_time = (now_utc().replace(tzinfo=None) - document.created_at.replace(tzinfo=None)).total_seconds() # TODO:  This needs to be fixed to the actual start time of the orchestration run, not the document creation time.
        extra = {
            "status": status, 
            "elapsed_time": elapsed_time, 
            "priority": document.priority.value, 
            "document": document.dict()
        }
        if metadata:
            extra.update(metadata)            
        Metric.send(Metric.MetricType.MEDICATIONEXTRACTION_STEP_PREFIX + "STATUS." + status, branch=status.lower(), tags=extra)