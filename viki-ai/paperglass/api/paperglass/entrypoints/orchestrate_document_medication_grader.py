import asyncio
import sys, os
from typing import List

from kink import inject

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.models import Document
from paperglass.domain.utils.exception_utils import exceptionToMap, getTrimmedStacktraceAsString

from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IQueryPort

from paperglass.domain.models_common import OrchestrationException
from paperglass.domain.models import (
    DocumentOperationDefinition,
    DocumentOperationInstance,
    DocumentOrchestrationAgent,
    Configuration
)

from paperglass.domain.values import (
    DocumentOperationStatus,
    DocumentOperationType,
    OrchestrationPriority
)

from paperglass.usecases.commands import (
    PerformGrading,
    CreateDocumentOperationInstance,
    CreateOrUpdateDocumentOperation,
    AutoCreateDocumentOperationDefinition
)

from paperglass.usecases.configuration import get_config

from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils, bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)
opentelemetry = OpenTelemetryUtils("GraderOrchestrationAgent:")

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

class GraderOrchestrationAgent(DocumentOrchestrationAgent):

    @inject
    async def orchestrate(self, document_id: str, commands: ICommandHandlingPort, query: IQueryPort, priority: OrchestrationPriority=None):

        with await opentelemetry.getSpan("orchestrate_grader") as span: 
            extra = {
                "document_id": document_id,
            }
            try:
                #Get document
                document: Document = await query.get_document(document_id)
                document = Document(**document)

                extra.update({
                    "app_id": document.app_id,
                    "tenant_id": document.tenant_id,
                    "patient_id": document.patient_id,
                    "document_id": document.id,
                    "document": document.dict()})

                #Get document operation definition
                doc_op_defs: List[DocumentOperationDefinition] = await query.get_document_operation_definition_by_op_type(DocumentOperationType.MEDICATION_GRADER)
                if not doc_op_defs:
                    doc_op_def = await commands.handle_command(AutoCreateDocumentOperationDefinition(document_operation_type=DocumentOperationType.MEDICATION_GRADER))
                else:
                    doc_op_def = doc_op_defs[0]

                #Create a document operation instance
                command = CreateDocumentOperationInstance(app_id=document.app_id,
                                                        tenant_id=document.tenant_id,
                                                        patient_id=document.patient_id,
                                                        document_id=document_id, 
                                                        document_operation_definition_id=doc_op_def.id) 
                doc_op_instance: DocumentOperationInstance = await commands.handle_command(command)

                #Perform grading step
                command = PerformGrading(app_id=document.app_id,
                                                        tenant_id=document.tenant_id,
                                                        patient_id=document.patient_id,
                                                        document_id=document_id,
                                                        document_operation_instance_id=doc_op_instance.id)

                results = await commands.handle_command(command)
                LOGGER.debug("Results of PerformGrading step: %s", results, extra=extra)

                #Upsert Document Operation
                command = CreateOrUpdateDocumentOperation(app_id=document.app_id,
                                                        tenant_id=document.tenant_id,
                                                        patient_id=document.patient_id,
                                                        document_id=document_id,
                                                        operation_type=DocumentOperationType.MEDICATION_GRADER.value,
                                                        active_document_operation_definition_id=doc_op_def.id,
                                                        active_document_operation_instance_id=doc_op_instance.id,
                                                        status = DocumentOperationStatus.COMPLETED)
                await commands.handle_command(command)

                return results
            
            except OrchestrationException as e:
                extra.update({"error": exceptionToMap(e)})
                LOGGER.error("Error occured during Grader orchestration of documentId %s: %s", document.id, str(e), extra=extra)                
            except Exception as e:
                extra.update({"error": exceptionToMap(e)})
                LOGGER.error("Error orchestrating Grader: %s", str(e), extra=extra)
                raise e
