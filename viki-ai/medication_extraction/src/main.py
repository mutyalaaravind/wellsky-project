import base64
from datetime import datetime
from functools import wraps
import json
import time
import traceback
from uuid import uuid4
from utils.steps_logger import log_step
from settings import (
    CLASSIFY_ENABLED,
    PIPELINE_RETRY_COUNT,
    STAGE
)

import settings
from utils.exception import JobException
from services.page_service import PageService
from utils.custom_logger import getLogger, log_elapsed_time
from utils.date import now_utc
from utils.exception import exceptionToMap
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from models import Document, DocumentOperationStep, MedispanMatchConfig, OrchestrationPriority, Page
from model_metric import Metric
from jobs import DocumentJob
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

LOGGER = getLogger(__name__)

app = FastAPI(title="Medication Extraction API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def retry_logger(max_retry_count, logger):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                logger.info(f"Max retry count: {max_retry_count}")
                if kwargs and hasattr(kwargs.get("request"),"retry_attempt"):
                    retry_attempt = kwargs.get("request").retry_attempt
                    logger.info(f"retry attempt: {retry_attempt}")
                    if retry_attempt >= max_retry_count:
                        logger.error(f"Max retry count reached for {func.__name__}")
            except Exception as e:
                logger.error(f"Error in retry_logger: {str(e)}")
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def pubsub_interpretor():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            print(args)
            print(kwargs)
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator

class ExtractRequest(BaseModel):
    retry_attempt: Optional[int] = 0
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    storage_uri: str
    priority: Optional[str] = "default"
    wait_time_start: Optional[str] = None
    created_at: datetime
    ocr_processing_disabled: Optional[bool] = False
    medispan_adapter_settings: Optional[MedispanMatchConfig] = None
    
    def validate(self):
        if self.retry_attempt > 3:
            raise JobException("Max retry count reached")
        
    @property
    def wait_elapsed_time(self):
        try:
            if self.wait_time_start:
                queue_start = datetime.fromisoformat(self.wait_time_start)
                elapsed_time = now_utc() - queue_start                
                return elapsed_time.total_seconds()
            return None
        except Exception as e:
            extra = {
                "wait_time_start": self.wait_time_start,
                "error": exceptionToMap(e),
                "request": self.dict()
            }
            LOGGER.error(f"Error converting wait_time_start to datetime: {str(e)}", extra=extra)
            return None
    
    class Config:
        @staticmethod
        def json_schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["wait_elapsed_time"] = {"type": "number"}

        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClassifyRequest(BaseModel):
    retry_attempt: int = 0
    document: ExtractRequest
    page_storage_uri: str
    page_number: int
    total_pages: int
    run_id:str
    wait_time_start: Optional[str] = None
    ocr_processing_disabled: Optional[bool] = True

    @property
    def wait_elapsed_time(self):
        try:
            if self.wait_time_start:
                queue_start = datetime.fromisoformat(self.wait_time_start)
                elapsed_time = now_utc() - queue_start                
                return elapsed_time.total_seconds()
            return None
        except Exception as e:
            extra = {
                "wait_time_start": self.wait_time_start,
                "error": exceptionToMap(e),
                "request": self.dict()
            }
            LOGGER.error(f"Error converting wait_time_start to datetime: {str(e)}", extra=extra)
            return None
    
    class Config:
        @staticmethod
        def json_schema_extra(schema: Dict[str, Any]) -> None:
            schema["properties"]["wait_elapsed_time"] = {"type": "number"}

        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
class ExtractMedicationRequest(ClassifyRequest):
    document: ExtractRequest

@app.get("/")
async def root():
    return {"message": "Welcome to Medication Extraction API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
    

@app.post("/run_extraction")
@retry_logger(max_retry_count=PIPELINE_RETRY_COUNT, logger=LOGGER)
async def run_extraction(request: ExtractRequest):
    run_id=uuid4().hex
    try:
        document=Document(
            app_id=request.app_id,
            tenant_id=request.tenant_id,
            patient_id=request.patient_id,
            document_id=request.document_id,
            storage_uri=request.storage_uri,
            priority= OrchestrationPriority(request.priority), #OrchestrationPriority.HIGH if request.priority == "high" else OrchestrationPriority.DEFAULT,
            created_at=request.created_at,
            medispan_adapter_settings=request.medispan_adapter_settings
        )
        extra = {
            "step": DocumentOperationStep.SPLIT_PAGES.value,
            "run_id": run_id, 
            "priority": document.priority.value,
            "retry_attempt": request.retry_attempt,
            "wait_elapsed_time": request.wait_elapsed_time,
            "document": document.dict()
        }
        Metric.send(Metric.MetricType.MEDICATIONEXTRACTION_STEP_PREFIX + "START", tags=extra)
        
        job = DocumentJob()
        pages:List[Page] = await job.split_pages(document=document, run_id=run_id, wait_time_start=request.wait_time_start)
        await log_step(DocumentOperationStep.SPLIT_PAGES.value,document,page=None,run_id=run_id,recovery_attempt=request.retry_attempt,status="COMPLETED")
        if request.priority != "none":
            for page in pages:
                await job.run_classify(document, page, ocr_processing_disabled=request.ocr_processing_disabled)
        else:
            LOGGER.info("Detected priority is 'none'.  Halting extraction and returning document status to NOT_STARTED", extra=extra)
            await job.update_status(document, run_id, status="NOT_STARTED", metadata=extra)
        return {"result": True}
    
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e)
        })
        LOGGER.error(f"Error in run extraction: {str(e)}", extra=extra)
        if request.retry_attempt < PIPELINE_RETRY_COUNT:
            LOGGER.debug("Retrying run_extraction for document", extra=extra)
            await job.run_extraction(document, retry_attempt=request.retry_attempt + 1,ocr_processing_disabled=request.ocr_processing_disabled)
        else:
            LOGGER.debug("Retry attempts exceeded for run_extraction", extra=extra)
            await job.update_status(document, run_id, status="FAILED", metadata=extra)
            await log_step(DocumentOperationStep.SPLIT_PAGES.value,
                           document if document else None,
                           page=None,run_id=run_id,recovery_attempt=request.retry_attempt,
                           status="FAILED",
                           error=traceback.format_exc()
                           )
        return {"result": False}
    
@app.post("/run_extraction_pubsub")
async def run_extraction_pubsub(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
    except:
        data = body
    
    if data.get("message"):
        message = data.get("message").get("data")
        message = base64.b64decode(message).decode('utf-8')
    else:
        message = data
    
    try:
        message=json.loads(message)
    except:
        pass

    if "created_at" not in message:
        message["created_at"] = datetime.now().isoformat()

    extra={
        "message": message
    }
    LOGGER.debug("run_extraction_pubsub message: %s", json.dumps(message, indent=2), extra=extra)
    
    run_extraction_request = ExtractRequest(**message)
    return await run_extraction(run_extraction_request)

@app.post("/classify")
@retry_logger(max_retry_count=PIPELINE_RETRY_COUNT, logger=LOGGER)
@log_elapsed_time("GROUP.CLASSIFY", arg_types=[ClassifyRequest])
async def classify(request: ClassifyRequest):
    extra = {
        "step": DocumentOperationStep.CLASSIFICATION.value,
        "run_id": request.run_id,
        "retry_attempt": request.retry_attempt,
        "wait_elapsed_time": request.wait_elapsed_time,
    }
    try:
        job = DocumentJob()
        document=Document(
            app_id=request.document.app_id,
            tenant_id=request.document.tenant_id,
            patient_id=request.document.patient_id,
            document_id=request.document.document_id,
            storage_uri=request.document.storage_uri,
            priority= OrchestrationPriority(request.document.priority), #OrchestrationPriority.HIGH if request.document.priority == "high" else OrchestrationPriority.DEFAULT,
            created_at=request.document.created_at,
            medispan_adapter_settings=request.document.medispan_adapter_settings
        )
        page = Page(storage_uri=request.page_storage_uri,
                    page_number=request.page_number,
                    total_pages=request.total_pages,
                    run_id=request.run_id)
        extra.update({                         
            "priority": document.priority.value,            
            "document": document.dict(),
            "page": page.dict()
        })
        if CLASSIFY_ENABLED:
            classified_text = await job.classify(document, page)
            await log_step(DocumentOperationStep.CLASSIFICATION.value,document,page=page,run_id=request.run_id,recovery_attempt=request.retry_attempt,status="COMPLETED")
        if not request.ocr_processing_disabled:
            extra.update({
                "step": DocumentOperationStep.PERFORM_OCR.value
            })
            await job.perform_ocr(document, page)
            await log_step(DocumentOperationStep.PERFORM_OCR.value,document,page=page,run_id=request.run_id,recovery_attempt=request.retry_attempt,status="COMPLETED")
        await job.run_medications(document, page)
        return {"result": True}
    
    except Exception as e:
        extra.update({"error": exceptionToMap(e)})
        LOGGER.error(f"Error in Classify: {str(e)}", extra=extra)
        if request.retry_attempt < PIPELINE_RETRY_COUNT:
            if page:
                LOGGER.debug("Retrying run_extraction for page", extra=extra)
                await job.run_classify(document,page=page,retry_attempt=request.retry_attempt + 1, ocr_processing_disabled=request.ocr_processing_disabled)
            else:
                LOGGER.debug("Not retrying run_extraction for nonexistant page", extra=extra)
        else:
            LOGGER.debug("Retry attempts exceeded for run_extraction", extra=extra)
            await job.update_status(document, request.run_id,status="FAILED", metadata=extra)
            await log_step(DocumentOperationStep.PERFORM_OCR.value,
                            document if document else None,
                            page=page if page else None,
                            run_id=request.run_id,
                            recovery_attempt=request.retry_attempt,
                            status="FAILED",
                            error=traceback.format_exc()
                            )
        return {"result": False}
    
@app.post("/classify_pubsub")
async def classify_pubsub(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
    except:
        data = body
    
    if data.get("message"):
        message = data.get("message").get("data")
        message = base64.b64decode(message).decode('utf-8')
    else:
        message = data
    try:
        message=json.loads(message)
    except:
        pass
    classify_request = ClassifyRequest(**message)
    return await classify(classify_request)
    
@app.post("/medications")
@retry_logger(max_retry_count=3,logger=LOGGER)
@log_elapsed_time("GROUP.MEDICATIONS", arg_types=[ExtractMedicationRequest])
async def medications(request: ExtractMedicationRequest):
    extra = {
        "step": DocumentOperationStep.MEDICATIONS_EXTRACTION.value,
        "request": request.dict(),     
    }
    try:
        document=Document(
            app_id=request.document.app_id,
            tenant_id=request.document.tenant_id,
            patient_id=request.document.patient_id,
            document_id=request.document.document_id,
            storage_uri=request.document.storage_uri,
            priority= OrchestrationPriority(request.document.priority), #OrchestrationPriority.HIGH if request.document.priority == "high" else OrchestrationPriority.DEFAULT,
            created_at=request.document.created_at,
            medispan_adapter_settings=request.document.medispan_adapter_settings
        )
        job = DocumentJob()
        page=Page(storage_uri=request.page_storage_uri,
                  page_number=request.page_number,
                  total_pages=request.total_pages,
                  run_id=request.run_id)
        
        extra.update({
            "document": request.document.dict() if document else None,
            "page": page.dict() if page else None,
        })
        medications = await job.medications(document, page)
        await log_step(DocumentOperationStep.MEDICATIONS_EXTRACTION.value,document,page=page,run_id=request.run_id,recovery_attempt=request.retry_attempt,status="COMPLETED")
        medispan_matched_medications,medispan_search_results = await job.medispan_match(document, page)
        await job.run_create_medications(document, page,retry_attempt=request.retry_attempt)
        await log_step(DocumentOperationStep.MEDISPAN_MATCHING.value,document,page=page,run_id=request.run_id,recovery_attempt=request.retry_attempt,status="COMPLETED")
        await job.run_status_check(document,page)
        #await job.run_medispan_match(page)
        return {"result": True}
    
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e)
        })
        LOGGER.error(f"Error in medications: {traceback.format_exc()}", extra=extra)
        if page:
            if request.retry_attempt < 3:
                await job.run_medications(document = document, page=page,retry_attempt=request.retry_attempt + 1)
            else:
                await job.update_status(document = document, run_id=request.run_id,status="FAILED", metadata=extra)
                await log_step(DocumentOperationStep.MEDICATIONS_EXTRACTION.value,
                            document if document else None,
                            page=page if page else None,
                            run_id=request.run_id,
                            recovery_attempt=request.retry_attempt,
                            status="FAILED",
                            error=traceback.format_exc()
                            )
        return {"result": False}

@app.post("/medications_pubsub")
async def medications_pubsub(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
    except:
        data = body
    
    if data.get("message"):
        message = data.get("message").get("data")
        message = base64.b64decode(message).decode('utf-8')
    else:
        message = data
    try:
        message=json.loads(message)
    except:
        pass
    medications_request = ExtractMedicationRequest(**message)
    return await medications(medications_request)


@app.post("/update_status")
@retry_logger(max_retry_count=3,logger=LOGGER) 
async def update_status(request: ExtractMedicationRequest):
    extra = {}
    try:
        document=Document(
            app_id=request.document.app_id,
            tenant_id=request.document.tenant_id,
            patient_id=request.document.patient_id,
            document_id=request.document.document_id,
            storage_uri=request.document.storage_uri,
            priority= OrchestrationPriority(request.document.priority), #OrchestrationPriority.HIGH if request.document.priority == "high" else OrchestrationPriority.DEFAULT,
            created_at=request.document.created_at
        )
        job = DocumentJob()
        page=Page(storage_uri=request.page_storage_uri,
                  page_number=request.page_number,
                  total_pages=request.total_pages,
                  run_id=request.run_id)
        
        extra = {            
            "request": request.dict(),
            "document": request.document.dict() if document else None,
            "page": page.dict() if page else None
        }

        if await job.status_check(document, page):
            await job.update_status(document, request.run_id,status="COMPLETED", metadata=extra)
            await log_step(DocumentOperationStep.STATUS_UPDATE.value,document,page=None,run_id=request.run_id,recovery_attempt=request.retry_attempt,status="COMPLETED")
        return {"result": True}
    except Exception as e:
        extra.update({
            "error": exceptionToMap(e)
        })
        LOGGER.error(f"Error in update_status: {traceback.format_exc()}")
        if page:
            if request.retry_attempt < 3:
                await job.run_status_check(document, page=page,retry_attempt=request.retry_attempt + 1)
            else:
                await job.update_status(document, request.run_id,status="FAILED", metadata=extra)
                await log_step(DocumentOperationStep.STATUS_UPDATE.value,document if document else None,
                               page=page if page else None,
                               run_id=request.run_id,
                               recovery_attempt=request.retry_attempt,
                               status="FAILED",
                               error=traceback.format_exc())
        return {"result": False}

@app.post("/update_status_pubsub")
async def update_status_pubsub(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
    except:
        data = body
    
    if data.get("message"):
        message = data.get("message").get("data")
        message = base64.b64decode(message).decode('utf-8')
    else:
        message = data
    try:
        message=json.loads(message)
    except:
        pass
    medications_request = ExtractMedicationRequest(**message)
    return await update_status(medications_request)


@app.get("/api/medispan/loadtest/poke")
async def medispan_loadtest_poke(request: Request, search_strategy: str = "alloydb", medication_count: int = 15):
    if STAGE == "prod":
        raise HTTPException(status_code=403, detail="Forbidden in production environment")

    medications = [
        "OXYGEN 02 - CONTINUOUS OXYGEN",
        "OXYBUTYNIN CHLORIDE ER TABLET, EXTENDED RELEASE 10 MG TABLET ORAL",
        "CITALOPRAM 40MG TABLET ORAL",
        "BASAGLAR KWIKPEN U-100 INSULIN 100 UNIT/ML SUBCUTANEOUS",
        "IPRATROPIUM-ALBUTEROL 0.5 MG-ALBUTEROL 3 MG (2.5 MG BASE)/3 ML NEBULIZATION SOLN INHALATION",
        "BREO ELLIPTA 200 MCG-25 MCG/DOSE POWDER FOR INHALATION INHALATION",
        "AMLODIPINE 5 MG TABLET ORAL",
        "GABAPENTIN 800 mg TABLET ORAL",
        "LASIX 40 MG TABLET ORAL",
        "ACETAMINOPHEN 325 MG TABLET ORAL",
        "Claritin 10 mg tablet Oral",
        "ATORVASTATIN 80 MG TABLET ORAL",
        "CARVEDILOL 25 MG TABLET ORAL",
        "LATANOPROST EYE DROPS 0.005% DROPS OPHTHALMIC (EYE)",
        "DOCUSATE SODIUM 100 MG CAPSULE ORAL"
    ]    

    from adapters.pgvector_adapter import MedispanPgVectorAdapter
    from adapters.medispan_firestore_vector_search import MedispanFireStoreVectorSearchAdapter
    
    medispan_port = None
    if search_strategy=="alloydb":
        medispan_port = MedispanPgVectorAdapter()
    elif search_strategy=="firestore":
        medispan_port = MedispanFireStoreVectorSearchAdapter()
    else:
        return {"error": "Unsupported search_strategy " + search_strategy }

    LOGGER.debug("Medispan load test poke endpoint called")

    try:
        results = []
        
        start_time = time.time()

        idx = 0
        for medication in medications:
            LOGGER.debug("Medispan search: %s", medication)
            drugs = await medispan_port.search_medications(medication)            

            if drugs:
                results.append(drugs[0])
            else:
                results.append("Not found: " + medication)
            idx += 1
        
        total_time = time.time() - start_time

        LOGGER.debug("Medispan load test poke complete")

        return {
            "search_strategy": search_strategy,
            "results": results,
            "elapsed_time": total_time
        }
    
    except Exception as e:
        return {"error": str(e)}
