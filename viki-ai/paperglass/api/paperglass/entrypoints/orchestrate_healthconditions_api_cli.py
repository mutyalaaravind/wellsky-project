import asyncio
import sys, os
from typing import List

from kink import inject
from starlette.responses import JSONResponse

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
    DocumentOperationType,
    PageText
)
from paperglass.domain.models import DocumentOrchestrationAgent

from paperglass.usecases.commands import (
    CreateDocumentOperationInstance,
    AutoCreateDocumentOperationDefinition,
)


from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils, bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)
opentelemetry = OpenTelemetryUtils("GraderOrchestrationAgent:")

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

page_id = "078cafb08c9311efb2ff42004e494300"
page_number = 1
page_text = """
Page: 1Comprehensive Details:**HCA FL Capital Hospital (COCTL)EMERGENCY PROVIDER REPORT**REPORT#: REPORT STATUS: SignedDATE: 05/23/22 TIME: 1808PATIENT:ACCOUNT#:AGE: 49SEX: FUNIT #:ROOM/BED:PCP PHYS: Shamil MDSERVICE DT: 05/23/22AUTHOR: Brian MD* ALL edits or amendments must be made on the electronic/computer document ***HPI-Dyspnea/Wheezing****General**Confirmed Patient YesInitial Greet Date/Time 05/23/22 1456**Presentation**Chief Complaint Shortness of breathHx Obtained From PatientSudden in Onset? NoOnset Occurred TodaySymptom Duration Since onsetProgression since Onset Gradually worseningSeverity: Current No pain currentlyAssociated withDenies: Chest pain, Fever.Relieved by Nothing**Free Text HPI Notes**Free Text HPI Notes49-year-old female with history of AIDS, COPD, CVA, respiratory failure, bronchiectasis, deep vein thrombosis/pulmonary embolism, cerebellar lesions and bronchitis presents with increasing shortness of breath. She is normally on 4 L of oxygen home. Denies any chest pain. Denies any other symptoms. She presents on 4 L of oxygen with an O2 sat of 67%.**Review of Systems****ROS Statements**All systems rev & neg except as marked.**Focused Review of Systems****Constitutional**Denies: Fever.**Respiratory**Reports: Shortness of breath.Page 1 of 10 
"""
labels = [{'conditions': 'C0400 Recall:* A. Able to recall sock*  Could not recall*  Yes, after cueing (something to wear)*  Yes, no cue required*  Not Assessed / No Information* B. Able to recall blue*  Could not recall*  Yes, after cueing (a color)*  Yes, no cue required*  Not Assessed / No Information* C. Able to recall bed*  Could not recall*  Yes, after cueing (a piece of furniture)*  Yes, no cue required*  Not Assessed / No InformationC0500 BIMS Summary ScoreC1310 Signs and Symptoms of Delirium (from CAM©)* A. Acute Onset of Mental Status ChangeIs there evidence of an acute change in mental status from the patients baseline?*  No*  Yes*  Not Assessed / No Information* B. InattentionDid the patient have difficulty focusing attention, for example, being easily distractible or having difficulty keeping track of what is being said?*  Behavior Not Present*  Behavior continuously present, does not fluctuate*  Behavior present, fluctuates (comes and goes, changes in severity)*  Not Assessed / No Information* C. Disorganized ThinkingWas the patients thinking disorganized or incoherent (rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject)?*  Behavior Not Present*  Behavior continuously present, does not fluctuate*  Behavior present, fluctuates (comes and goes, changes in severity)*  Not Assessed / No Information* D. Altered level of consciousnessDid the patient have altered level of consciousness, as indicated by any of the following criteria?*  Vigilant - startled easily to any sound of touch*  Lethargic - repeatedly dozed off when being asked questions, but responded to voice or touch*  Stuporous - very difficult to arouse and keep aroused for the interview*  Comatose - could not be aroused*  Behavior Not Present*  Behavior continuously present, does not fluctuate*  Behavior present, fluctuates (comes and goes, changes in severity)*  Not Assessed / No InformationM1700 Cognitive Functioning: Patients current (day of assessment) level of alertness, orientation, comprehension, concentration, and immediate memory for simple commands.*  Alert/oriented, able to focus and shift attention, comprehends and recalls task directions independently*  Requires prompting (cuing, repetition, reminders) only under stressful or unfamiliar conditions*  Requires assistance and some direction in specific situations (for example, on all tasks involving shifting of attention) or consistently requires low stimulus environment due to distractibility*  Requires considerable assistance in routine situations. Is not alert and oriented or is unable to shift attention and recall directions more than half the time*  Totally dependent due to disturbances such as constant disorientation, coma, persistent vegetative state, or delirium'}]


class ConditionsOrchestrationAgent(DocumentOrchestrationAgent):

    @inject
    async def orchestrate(self, document_id: str, commands: ICommandHandlingPort, query: IQueryPort):

        with await opentelemetry.getSpan("orchestrate_conditions") as span: 

                #Get document
                document: Document = await query.get_document(document_id)
                document = Document(**document)

                # #Get document operation definition
                # doc_op_defs: List[DocumentOperationDefinition] = await query.get_document_operation_definition_by_op_type(DocumentOperationType.CONDITION_EXTRACTION)
                # if not doc_op_defs:
                #     doc_op_def = await commands.handle_command(AutoCreateDocumentOperationDefinition(document_operation_type=DocumentOperationType.CONDITION_EXTRACTION))
                # else:
                #     doc_op_def = doc_op_defs[0]

                command = CreateDocumentOperationInstance(app_id=document.app_id,
                                                        tenant_id=document.tenant_id,
                                                        patient_id=document.patient_id,
                                                        document_id=document_id, 
                                                        document_operation_definition_id="xpjsocmtgd3v4progefhbdf23") 
                doc_op_instance: DocumentOperationInstance = await commands.handle_command(command)

                page_texts  = []
                for doc_page in document.pages:
                    page:Page = Page(**await query.get_page(document_id, doc_page.number))
                    #Perform step
                    page_texts.append(PageText(text=page.text, pageNumber=page.number))
                from paperglass.usecases.orchestrator import ConditionPromptExtractionAgent
                await ConditionPromptExtractionAgent().orchestrate(
                                    document_id=document_id,
                                    document_operation_instance_id=doc_op_instance.id,
                                    document_operation_definition_id="xpjsocmtgd3v4progefhbdf23",
                                    page_id=page_id,
                                    labels=labels)

                return JSONResponse({'status': True})


def main(): 
    
    app_id = "007"
    tenant_id = "54321"
    patient_id = "242b7bfff8fb4f50b77cf1f7f61e91d3"
    document_id = "02b1059a8c9311efafee0242ac120004"

    agent = ConditionsOrchestrationAgent()   
    asyncio.run(agent.orchestrate(document_id))

if __name__ == "__main__":   
    main()
