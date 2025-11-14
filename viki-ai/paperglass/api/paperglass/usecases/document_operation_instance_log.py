from kink import inject
from typing import List

from paperglass.settings import (
    DOCUMENT_OPERATION_INSTANCE_LOG_STRATEGY,
    DOCUMENT_OPERATION_INSTANCE_LOG_FALLBACK_ENABLED
)


from paperglass.domain.models import (
    DocumentOperationInstanceLog,    
)
from paperglass.domain.values import (
    DocumentOperationStatus,
    DocumentOperationStep,
)

from paperglass.infrastructure.ports import (
    IUnitOfWorkManagerPort,
    IStoragePort,
    IQueryPort,
    IUnitOfWork
)

#OpenTelemetry instrumentation
SPAN_BASE: str = "USECASE:DocumentOperationInstanceLogService:"
from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils
from opentelemetry.trace.status import Status, StatusCode
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

from paperglass.log import CustomLogger
LOGGER = CustomLogger(__name__)

class DocumentOperationInstanceLogService():
    
    def __init__(self):
        if DOCUMENT_OPERATION_INSTANCE_LOG_STRATEGY == "storage":
            self.service = DocumentOperationInstanceLogStorageService()
            self.fallbackService = DocumentOperationInstanceLogFirestoreService()
        elif DOCUMENT_OPERATION_INSTANCE_LOG_STRATEGY == "firestore":
            self.service = DocumentOperationInstanceLogFirestoreService()            
        else:
            raise Exception(f"Invalid DocumentOperationInstanceLog strategy: {DOCUMENT_OPERATION_INSTANCE_LOG_STRATEGY}")
        
    async def save(self, log: DocumentOperationInstanceLog, uow:IUnitOfWork) -> DocumentOperationInstanceLog:        
        await self.service.save(log, uow)
    
    async def list(self, document_id:str, document_operation_instance_id: str) -> List[DocumentOperationInstanceLog]:
        ret = await self.service.list(document_id, document_operation_instance_id)
        if not ret and DOCUMENT_OPERATION_INSTANCE_LOG_FALLBACK_ENABLED=="storage" and DOCUMENT_OPERATION_INSTANCE_LOG_FALLBACK_ENABLED:
            LOGGER.warning("No DocumentOperationInstanceLog entries found in Storage for document_id: %s, document_operation_instance_id: %s  Attempting to retrieve from Firestore", document_id, document_operation_instance_id)
            ret = await self.fallbackService.list(document_id, document_operation_instance_id)
            LOGGER.warning("Retrieved %s DocumentOperationInstanceLog entries from Firestore", len(ret) if ret else 0)

        return ret
    
    async def list_by_stepid(self, document_id:str, document_operation_instance_id: str, page_number: int, step_id: str):
        ret = await self.service.list_by_stepid(document_id, document_operation_instance_id, page_number, step_id)
        if not ret and DOCUMENT_OPERATION_INSTANCE_LOG_FALLBACK_ENABLED=="storage" and DOCUMENT_OPERATION_INSTANCE_LOG_FALLBACK_ENABLED:
            LOGGER.warning("No DocumentOperationInstanceLog entries found in Storage for document_id: %s, document_operation_instance_id: %s  Attempting to retrieve from Firestore", document_id, document_operation_instance_id)
            ret = await self.fallbackService.list_by_stepid(document_id, document_operation_instance_id, page_number, step_id)
            LOGGER.warning("Retrieved DocumentOperationInstanceLog entry from Firestore: %s", ret)
        return ret

class DocumentOperationInstanceLogStorageService():

    def __init__(self):
        pass

    @inject
    async def save(self, log: DocumentOperationInstanceLog, uow: IUnitOfWork, storage: IStoragePort) -> DocumentOperationInstanceLog:        
        with await opentelemetry.getSpan("save") as span:
            
            # Always save to Cloud Storage
            LOGGER.debug("Saving DocumentOperationInstanceLog entry to Cloud Storage")
            await storage.put_documentoperationinstancelog(log)            
                        
            # Only save to Firestore if the log entry is Failed    
            if log.status == DocumentOperationStatus.FAILED:
                uow.register_new(log)                
    
    @inject
    async def list(self, document_id:str, document_operation_instance_id: str, storage: IStoragePort, query: IQueryPort) -> List[DocumentOperationInstanceLog]:
        with await opentelemetry.getSpan("list") as span:
            ret = await storage.list_documentoperationinstancelogs(document_id, document_operation_instance_id)        
            LOGGER.debug("Retrieved %s DocumentOperationInstanceLog entries from Storage", len(ret))

            if not ret:
                LOGGER.warning("No DocumentOperationInstanceLog entries found in Storage for document_id: %s, document_operation_instance_id: %s  Attempting to retrieve from deprecated Firestore collection", document_id, document_operation_instance_id)
                doc_operation_instance_logs:DocumentOperationInstanceLog = await query.get_document_operation_instance_logs_by_document_id(document_id, document_operation_instance_id)   
                ret = doc_operation_instance_logs
                LOGGER.warning("Retrieved %s DocumentOperationInstanceLog entries from Firestore", len(ret) if ret else 0)

            return ret
    
    @inject
    async def list_by_stepid(self, document_id:str, document_operation_instance_id: str, page_number: int, step_id: str, storage: IStoragePort, query: IQueryPort):
        with await opentelemetry.getSpan("list_by_stepid") as span:
            filtered_results = []
            logs: List[DocumentOperationInstanceLog] = await self.list(document_id, document_operation_instance_id)

            if not logs:
                LOGGER.warning("No DocumentOperationInstanceLog entries found in Storage for document_id: %s, document_operation_instance_id: %s  Attempting to retrieve from deprecated Firestore collection", document_id, document_operation_instance_id)
                doc_operation_instance_log:DocumentOperationInstanceLog = await query.get_document_operation_instance_log_by_step_id(document_id=document_id,
                                                                                                                                    document_operation_instance_id=document_operation_instance_id,
                                                                                                                                    page_number=page_number,
                                                                                                                                    step_id=step_id
                        )
                LOGGER.warning("Retrieved DocumentOperationInstanceLog entry from Cloud Storage: %s", doc_operation_instance_log)
                return doc_operation_instance_log

            for log in logs:
                if log.step_id == step_id and page_number == log.page_number:
                    filtered_results.append(log)

            if filtered_results:
                return filtered_results
            else:
                return None            
        
class DocumentOperationInstanceLogFirestoreService():

    def __init__(self):
        pass

    @inject
    async def save(self, log: DocumentOperationInstanceLog, uow: IUnitOfWork, storage: IStoragePort) -> DocumentOperationInstanceLog:        
        with await opentelemetry.getSpan("save") as span:
            LOGGER.debug("Saving DocumentOperationInstanceLog entry to Firestore")
            uow.register_new(log)
    
    @inject
    async def list(self, document_id:str, document_operation_instance_id: str, storage: IStoragePort, query: IQueryPort) -> List[DocumentOperationInstanceLog]:
        with await opentelemetry.getSpan("list") as span:
            LOGGER.debug("Retrieving DocumentOperationInstanceLog entries from Firestore")
            doc_operation_instance_logs:DocumentOperationInstanceLog = await query.get_document_operation_instance_logs_by_document_id(document_id, document_operation_instance_id)   
            ret = doc_operation_instance_logs
            return ret
    
    @inject
    async def list_by_stepid(self, document_id:str, document_operation_instance_id: str, page_number: int, step_id: str, storage: IStoragePort, query: IQueryPort):
        with await opentelemetry.getSpan("list_by_stepid") as span:
            LOGGER.debug("Retrieving DocumentOperationInstanceLog entry from Firestore by stepid")
            doc_operation_instance_log:DocumentOperationInstanceLog = await query.get_document_operation_instance_log_by_step_id(document_id=document_id,
                                                                                                                                document_operation_instance_id=document_operation_instance_id,
                                                                                                                                page_number=page_number,
                                                                                                                                step_id=step_id
                    )        
            return doc_operation_instance_log

                    
@inject
async def does_success_operation_instance_exist(document_id:str, document_operation_instance_id:str,page_number:int,step_id:DocumentOperationStep,query:IQueryPort):
    from paperglass.usecases.document_operation_instance_log import DocumentOperationInstanceLogService
    doc_logger = DocumentOperationInstanceLogService()
    doc_operation_instance_log:DocumentOperationInstanceLog = await doc_logger.list_by_stepid(document_id=document_id,
                                                                                               document_operation_instance_id=document_operation_instance_id,
                                                                                               page_number=page_number,
                                                                                               step_id=step_id.value)
    
    #doc_operation_instance_log:DocumentOperationInstanceLog = await query.get_document_operation_instance_log_by_step_id(document_id=document_id,
    #                                                                                                                        document_operation_instance_id=document_operation_instance_id,
    #                                                                                                                        page_number=page_number,
    #                                                                                                                        step_id=step_id.value
    #                                                                                                                        )

    if doc_operation_instance_log and doc_operation_instance_log.status == DocumentOperationStatus.COMPLETED:
        LOGGER.debug("Success operation instance log found for document_id: %s, document_operation_instance_id: %s, page_number: %s, step_id: %s", document_id, document_operation_instance_id, page_number, step_id)
        return True,doc_operation_instance_log
    return False,doc_operation_instance_log
        
        