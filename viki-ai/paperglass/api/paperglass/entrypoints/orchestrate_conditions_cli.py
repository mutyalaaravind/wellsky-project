import asyncio
import sys, os
from typing import List

from kink import inject

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.models import Document, Page
from paperglass.domain.utils.exception_utils import exceptionToMap, getTrimmedStacktraceAsString

from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IQueryPort

from paperglass.domain.models_common import OrchestrationException
from paperglass.domain.models import (
    DocumentOperationDefinition,
    DocumentOperationInstance
)

from paperglass.domain.values import (
    DocumentOperationStatus,
    DocumentOperationType,
    DocumentOperationStep,
    PageText
)
from paperglass.domain.models import DocumentOrchestrationAgent

from paperglass.usecases.commands import (
    PerformGrading,
    CreateDocumentOperationInstance,
    CreateOrUpdateDocumentOperation,
    AutoCreateDocumentOperationDefinition,
    ExtractConditionsData,
)


from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils, bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)
opentelemetry = OpenTelemetryUtils("GraderOrchestrationAgent:")

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

page_id = "1"
page_number = 0
page_text = """
Page: 10 of 10Comprehensive Details:**Patient:**[redacted]**Unit#:**[redacted]**Date:** 05/23/22**Acct#:**[redacted]**Clinical Impression****Clinical Impression****Primary Impression:** Acute bronchospasm**Secondary Impressions:** Bronchiectasis, Hypoxia**Disposition Decision****Admit****Admit Physician Hospitalist****)(** Admission Accepts Yes**)(** Accepted Time 1935**)(** Accepted Date 05/23/22**Call Information** will see patient**Discharge/Care Plan****Counseled Regarding** Diagnosis, Need for admission**Referrals****Provider Referral:** Shamil MD**Address:**[redacted]**Critical Care****Time Spent (minutes):** 45**Services Performed** Patient management by me, Time spent at bedside, Reviewing test results, Reviewing imaging, Discussing patient care, Documentation in record**Patient was critically ill due to:**Acute respiratory distress with hypoxia**My treatment and management were:**Multiple breathing treatments, non-rebreather oxygen, steroids**Electronically Signed by** Brian MD on 05/23/22 at 2008**RPT #:**[redacted]***END OF REPORT*** 
"""


class ConditionsOrchestrationAgent(DocumentOrchestrationAgent):

    @inject
    async def orchestrate(self, document_id: str, commands: ICommandHandlingPort, query: IQueryPort):

        with await opentelemetry.getSpan("orchestrate_conditions") as span: 

            try:
                #Get document
                document: Document = await query.get_document(document_id)
                document = Document(**document)

                #Get document operation definition
                doc_op_defs: List[DocumentOperationDefinition] = await query.get_document_operation_definition_by_op_type(DocumentOperationType.MEDICATION_EXTRACTION)
                if not doc_op_defs:
                    doc_op_def = await commands.handle_command(AutoCreateDocumentOperationDefinition(document_operation_type=DocumentOperationType.MEDICATION_EXTRACTION))
                else:
                    doc_op_def = doc_op_defs[0]

                #Create a document operation instance
                command = CreateDocumentOperationInstance(app_id=document.app_id,
                                                        tenant_id=document.tenant_id,
                                                        patient_id=document.patient_id,
                                                        document_id=document_id, 
                                                        document_operation_definition_id=doc_op_def.id) 
                doc_op_instance: DocumentOperationInstance = await commands.handle_command(command)

                page_texts  = []
                for doc_page in document.pages:
                    page:Page = Page(**await query.get_page(document_id, doc_page.number))
                    #Perform step
                    page_texts.append(PageText(text=page.text, pageNumber=page.number))
                command = ExtractConditionsData(app_id=document.app_id,
                                                tenant_id=document.tenant_id,
                                                patient_id=document.patient_id,
                                                document_id=document_id,
                                                document_operation_definition_id=doc_op_def.id,
                                                document_operation_instance_id=doc_op_instance.id,
                                                page_texts=page_texts,
                                                step_id= DocumentOperationStep.CONDITIONS_EXTRACTION
                                                )

                results = await commands.handle_command(command)
                LOGGER.debug("Results of PerformGrading step: %s", results)

                #Upsert Document Operation
                command = CreateOrUpdateDocumentOperation(app_id=document.app_id,
                                                        tenant_id=document.tenant_id,
                                                        patient_id=document.patient_id,
                                                        document_id=document_id,
                                                        operation_type=DocumentOperationType.MEDICATION_GRADER.value,
                                                        active_document_operation_definition_id=doc_op_def.id,
                                                        active_document_operation_instance_id=doc_op_instance.id,
                                                        status = DocumentOperationStatus.COMPLETED
                                                        )
                await commands.handle_command(command)
            except OrchestrationException as e:
                LOGGER.error("Error occured during Grader orchestration of documentId %s: %s", document.id, str(e))
                LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))
            except Exception as e:
                LOGGER.error("Error orchestrating Grader: %s", str(e))
                raise e


def main(): 
    
    app_id = "007"
    tenant_id = "54321"
    patient_id = "242b7bfff8fb4f50b77cf1f7f61e91d3"
    document_id = "b696ce346c7011ef9b9842004e494300"

    agent = ConditionsOrchestrationAgent()   
    asyncio.run(agent.orchestrate(document_id))

if __name__ == "__main__":   
    main()
