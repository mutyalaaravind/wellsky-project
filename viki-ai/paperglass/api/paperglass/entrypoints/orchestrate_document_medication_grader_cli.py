import asyncio
import sys, os
from typing import List
import json
import csv

from kink import inject

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.models import Document
from paperglass.domain.utils.exception_utils import exceptionToMap, getTrimmedStacktraceAsString
from paperglass.domain.utils.array_utils import chunk_array

from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IQueryPort, IPromptAdapter

from paperglass.domain.models_common import OrchestrationException
from paperglass.domain.models import (
    DocumentOperationDefinition,
    DocumentOperationInstance,
    DocumentOrchestrationAgent,
    OperationMeta,
)

from paperglass.domain.values import (
    DocumentOperationStatus,
    DocumentOperationType,
    DocumentOperationStep,
    MedicationValue,
)

from paperglass.usecases.commands import (
    PerformGrading,
    CreateDocumentOperationInstance,
    CreateOrUpdateDocumentOperation,
    AutoCreateDocumentOperationDefinition
)


from paperglass.domain.utils.opentelemetry_utils import OpenTelemetryUtils, bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)
opentelemetry = OpenTelemetryUtils("GraderOrchestrationAgent:")

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

idx = "4"
file_name = "/home/eric/code/scoring-output/input-group-" + idx + ".csv"
output_file_name = "/home/eric/code/scoring-output/output-group-" + idx + ".csv"

PROMPT = """
    As an expert medical clinician, please grade the medication list below for how complete and accurate it is.    
    Grade the results such that an overall score of 1.0 is perfect and 0.0 is the worst possible score.    
    Deduct points for each field that is missing or incorrect:    
    - Deduct 0.50 points if the medication name field is missing    
    - Deduct 0.50 points if the medication strength field is missing    
    - Deduct 0.25 points if the medication form field is missing    
    - Deduct 0.25 points if the medication route field is missing    
    - Deduct 0.25 points if the medication frequency field is missing    
    - Deduct 0.25 points if the medication dosage field is missing    
    
    Output the results in the following JSON format:    
    
    [
    {
    "extracted_medication_id": "**Id of the extracted medication in the medications list.  This will be the "id" field in the medication object",        
    "app_id": "**Id of the application",        
    "tenant_id": "**Id of the tenant",        
    "patient_id": "**Id of the patient",        
    "document_id": "**Id of the document",        
    "page_number": "**Page number of the document",        
    "document_operation_instance_id": "**Id of the document operation instance",        
    "medication": "**Copy the medication object here",
    "medispan_id": "**Medispan id of the medication",            
    "score": {            
        "overall": "**Overall score for the medication",    
    },        
    "fields_with_issues": ["**List each field that had an issue"]
    }
    ]        

    MEDICATIONS:    {{data}}    
"""

class GraderOrchestrationAgent(DocumentOrchestrationAgent):

    @inject
    async def orchestrate(self, document_id: str, commands: ICommandHandlingPort, query: IQueryPort):

        with await opentelemetry.getSpan("orchestrate_grader") as span: 

            try:
                #Get document
                document: Document = await query.get_document(document_id)
                document = Document(**document)

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

                return results

            except OrchestrationException as e:
                LOGGER.error("Error occured during Grader orchestration of documentId %s: %s", document.id, str(e))
                LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))
            except Exception as e:
                LOGGER.error("Error orchestrating Grader: %s", str(e))
                raise e

def toMedicationValue(row):
    if row["ai_medispan_name"] == None:
        return None
    
    med = MedicationValue(
        name = row["ai_medispan_name"],
        medispan_id = row["ai_medispan_id"],
        strength = row["ai_medispan_strength"],
        dosage = row["ai_medispan_dosage"],
        form = row["ai_medispan_form"],
        route= row["ai_medispan_route"],
        frequency = row["ai_medispan_frequency"],
        instructions = row["ai_medispan_instructions"]
    )
    return med

async def generate_medications():
    NUMBER_OF_MEDICATIONS = 100
    meds = []
    for i in range(NUMBER_OF_MEDICATIONS):

         
        med = MedicationValue(
            name = f"Medication {i}",
            medispan_id = f"{i}",
            strength = "100 MG",
            dosage = "1",
            form = "Capsule",
            route= "Oral",
            frequency = "daily",
            instructions = "As needed for pain"
        )

        meds.append(med)

    return meds

@inject
async def process_try_to_break(prompt: IPromptAdapter):

    """
    Errored at 40:
        Length: 38280
        Tokens: 4800

    Errored at 45:
        Length: 26980
        Tokens: 2900
        
    """

    meds = await generate_medications()
    meds_dict = [x.dict() for x in meds]

    meds_super_list = chunk_array(meds_dict, 40)
    super_response = []

    for med_chunk in meds_super_list:

        meds_str = json.dumps(med_chunk)

        LOGGER.info("Med_str length: %s", len(meds_str))
        LOGGER.info("med_str tokens: %s", len(meds_str.split(" ")))

        llmPrompt = PROMPT.replace("{{data}}", meds_str)

        response_text = await prompt.multi_modal_predict_2([llmPrompt], model="gemini-1.5-pro", response_mime_type = "application/json", metadata={})

        try:
            response = json.loads(response_text)
            super_response.extend(response)
            LOGGER.debug("Response: %s", json.dumps(response, indent=2))
        except Exception as e1:
            LOGGER.error("Error converting response to json: %s", str(e1))
            LOGGER.error("Response: %s", response_text)

    LOGGER.info("Super Response count: %s", len(super_response))

@inject
async def process_all_new(prompt: IPromptAdapter):

    data = await gather()

    headers = []

    with open(output_file_name, mode='w', newline='', encoding='utf-8') as output_file:
        fieldnames = headers + ['document_id', 
                                "name",
                                "medispan_id",
                                "dosage",
                                "strength",
                                "form",
                                "route",
                                "frequency",
                                "instructions",
                                'score',
                                'fields_with_issues',
                                'exception']
        csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        superbatch = {}        
        thisbatch = []

        lastkey = None
        max_batch_size = 20
        i = 0
        for key in data:

            for med in data[key]:
            
                if key not in superbatch:
                    # flush this batch to last docid
                    if lastkey and thisbatch and len(thisbatch) > 0:
                        superbatch[lastkey].append(thisbatch)
                    thisbatch = []

                    superbatch[key] = []                

                lastkey = key

                if i % max_batch_size == 0:
                    if thisbatch:
                        superbatch[key].append(thisbatch)
                    thisbatch = []

                thisbatch.append(med)
                i += 1

        if thisbatch:
            superbatch[lastkey].append(thisbatch)

        idx = 0
        for key in superbatch:

            document_id = key

            for batch in superbatch[key]:

                lastgrade = None

                try:

                    LOGGER.debug("SUPERBATCH: %s", len(superbatch[key]))
                    LOGGER.debug("Batch: %s", len(batch))

                    opMeta:OperationMeta = OperationMeta(
                        type = DocumentOperationType.MEDICATION_GRADER,
                        step = DocumentOperationStep.PERFORM_GRADING,
                        document_id = document_id,
                        iteration = idx
                    )

                    for b in superbatch[key]:
                        LOGGER.debug("\tBatch: %s", len(b))
                    
                    med_values = [x.dict() for x in batch]
                    llmPrompt = PROMPT.replace("{{data}}", json.dumps(med_values))

                    response_text = await prompt.multi_modal_predict_2([llmPrompt], model="gemini-1.5-pro", response_mime_type = "application/json", metadata=opMeta.dict())

                    try:
                        response = json.loads(response_text)
                    except Exception as e1:
                        LOGGER.error("Error converting response to json: %s", str(e1))
                        LOGGER.error("Response: %s", response_text)
                        response = None

                        outrow = {}
                        outrow["document_id"] = document_id
                        outrow['exception'] = str(e1)

                        continue


                    if response:
                        for grade in response:
                            lastgrade = grade
                            outrow = {}
                            outrow["document_id"] = document_id
                            outrow['name'] = grade["medication"]["name"]
                            outrow['medispan_id'] = grade["medication"]["medispan_id"]
                            outrow['dosage'] = grade["medication"]["dosage"]
                            outrow['strength'] = grade["medication"]["strength"]
                            outrow['form'] = grade["medication"]["form"]
                            outrow['route'] = grade["medication"]["route"]
                            outrow['frequency'] = grade["medication"]["frequency"]
                            outrow['instructions'] = grade["medication"]["instructions"]
                            outrow['score'] = grade["score"]["overall"]
                            outrow['fields_with_issues'] = json.dumps(grade["fields_with_issues"])

                            csv_writer.writerow(outrow)
                            output_file.flush()

                except Exception as e:
                    LOGGER.error("Error occurred during processing: %s", str(e))
                    LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))
                    LOGGER.error("Last grade: %s", lastgrade)
                    outrow = {}
                    outrow["document_id"] = document_id
                    outrow['exception'] = str(e)

                idx += 1

    
async def gather():

    data = {}

    with open(file_name, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        headers = csv_reader.fieldnames

        for row in csv_reader:
            document_id = row['x_document_id'].strip()

            if document_id not in data:
                data[document_id] = []

            med = toMedicationValue(row)
            if med:
                data[document_id].append(med)

    return data

async def process(document_id, med_values):

    results = []


    return results


async def process_all_old():
    file_name = "/home/eric/code/scoring-output/input.csv"
    output_file_name = "/home/eric/code/scoring-output/output.csv"

    import os

    # Print the current working directory
    print("Current working directory:", os.getcwd())

    agent = GraderOrchestrationAgent()   

    with open(file_name, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        headers = csv_reader.fieldnames

        with open(output_file_name, mode='w', newline='', encoding='utf-8') as output_file:
            fieldnames = headers + ['page_number', 
                                    'extracted_medication_id', 
                                    'medispan_id', 
                                    'name', 
                                    'dosage',
                                    'strength', 
                                    'form',
                                    'route',
                                    'frequency',
                                    'instructions',
                                    'startdate',
                                    'enddate',
                                    'score',
                                    'fields_with_issues',
                                    'exception']
            csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            for row in csv_reader:

                try:

                    document_id = row['document_id'].strip()

                    results = await agent.orchestrate(document_id)
                    #LOGGER.debug("Results: \n%s", results)

                    if results:

                        for grade in results:
                            outrow = {}
                            outrow["document_id"] = document_id
                            outrow['page_number'] = grade.page_number
                            outrow['extracted_medication_id'] = grade.id
                            outrow['medispan_id'] = grade.medispan_id
                            outrow['name'] = grade.medication.name
                            outrow['dosage'] = grade.medication.dosage
                            outrow['strength'] = grade.medication.strength
                            outrow['form'] = grade.medication.form
                            outrow['route'] = grade.medication.route
                            outrow['frequency'] = grade.medication.frequency
                            outrow['instructions'] = grade.medication.instructions
                            outrow['startdate'] = grade.medication.start_date
                            outrow['enddate'] = grade.medication.end_date
                            outrow['score'] = grade.score.overall
                            outrow['fields_with_issues'] = json.dumps(grade.fields_with_issues)

                            csv_writer.writerow(outrow)            
                    else:
                        outrow = {}
                        outrow["document_id"] = document_id
                        outrow['exception'] = "No grading results returned"
                    
                except Exception as e:
                    LOGGER.error("Error occurred during processing: %s", str(e))
                    LOGGER.error("Error details: %s", getTrimmedStacktraceAsString(e))

                    outrow = {}
                    outrow["document_id"] = document_id
                    outrow['page_number'] = ""
                    outrow['extracted_medication_id'] = ""
                    outrow['medispan_id'] = ""
                    outrow['name'] = ""
                    outrow['dosage'] = ""
                    outrow['strength'] = ""
                    outrow['form'] = ""
                    outrow['route'] = ""
                    outrow['frequency'] = ""
                    outrow['instructions'] = ""
                    outrow['startdate'] = ""
                    outrow['enddate'] = ""
                    outrow['score'] = ""
                    outrow['fields_with_issues'] = ""
                    outrow['exception'] = str(e)

                    csv_writer.writerow(outrow) 
                    output_file.flush()
@inject()
async def process_command(commands: ICommandHandlingPort, query: IQueryPort):
    
    document_id = "2c617f78615511efb3de42004e494300"
    doc = await query.get_document(document_id)
    
    doc_op_defs = await query.get_document_operation_definition_by_op_type(DocumentOperationType.MEDICATION_GRADER)
    doc_op_def = doc_op_defs[0]

    LOGGER.debug("Document Operation Definition: %s", doc_op_def)

    command = CreateDocumentOperationInstance(
        app_id=doc["app_id"],
        tenant_id=doc["tenant_id"],
        patient_id=doc["patient_id"],
        document_id=document_id, 
        document_operation_definition_id=doc_op_def.id
    )
    doc_op_inst: DocumentOperationInstance = await commands.handle_command(command)
    LOGGER.debug("Document Operation Instance: %s", doc_op_inst)    

    command = PerformGrading(
        app_id=doc["app_id"],
        tenant_id=doc["tenant_id"],
        patient_id=doc["patient_id"],
        document_id=document_id,
        document_operation_instance_id=doc_op_inst.id
    )
    results = await commands.handle_command(command)
    LOGGER.debug("Results: %s", results)

def main():   
    LOGGER.info("Starting Grader Orchestration Agent CLI")
    asyncio.run(process_command())    
    #asyncio.run(process_all_new())

if __name__ == "__main__":   
    main()
