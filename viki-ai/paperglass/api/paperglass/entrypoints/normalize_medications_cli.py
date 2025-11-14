import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kink import inject
from paperglass.settings import (
    STAGE,
    MEDISPAN_CLIENT_ID, 
    MEDISPAN_CLIENT_SECRET,
    MEDISPAN_VECTOR_SEARCH_REGION,
    MEDISPAN_LLM_SCORING_ENABLED,
    MULTIMODAL_MODEL
)

from paperglass.domain.models import MedispanDrug, ExtractedMedication, MedispanStatus, DocumentOperationDefinition
from paperglass.domain.values import MedicationValue, DocumentOperationType
from paperglass.domain.util_json import DateTimeEncoder

from paperglass.infrastructure.ports import IMedispanPort
from paperglass.infrastructure.ports import IQueryPort
from paperglass.infrastructure.adapters.medispan_vector_search import MedispanVectorSearchAdapter
from paperglass.infrastructure.adapters.google import FirestoreQueryAdapter

from paperglass.interface.ports import CommandError, ICommandHandlingPort
from paperglass.usecases.commands import NormalizeMedications



from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

getLogger("aiocache").setLevel("ERROR")
getLogger("asyncio").setLevel("ERROR")
getLogger("google.auth").setLevel("ERROR")

prompt_text_old = """
        MEDICATION:
        {search_term}

        As an expert healthcare worker, given the provided MEDICATION, extract from this string elements of the medication including:
        Name: Name of the medication
        Route: The way the medication is introduced to the patient and consists of values like Oral, Topical, Subcutaneous, Intravenous, Injection, Rectal, etc.
        Strength: The concentration of the medication expressed in weight or volume.  Examples include 100 MG, 300 MCG, 10 ML, 15 GM, 20 mEq, etc.
        Form: The medication form.  Examples include Tablet, Capsule, Solution, Capsule Delayed Release, Enema, etc.
        Dose: The amount of the medication to take.  This is the number or number range preceding the frequency.
        Frequency: How frequently the patient should take the medication
        Instructions: Any other data in the medication string not accounted by the other fields

        Here are examples of the medication string and how to parse into separate tokens:
            Medication:  Dexmethylphenidate HCl Oral 5 MG Tablet 1 Daily at breakfast
            Output:
                Name: Dexmethylphenidate HCl
                Route: Oral
                Strength: 5 MG
                Form: Tablet
                Dose: 1
                Frequency: Daily
                Instructions: at breakfast

            Medication:  Methylphenidate Oral 10mg Tablet 1-2 Daily as needed
            Output:
                Name: Dexmethylphenidate HCl
                Route: Oral
                Strength: 10 MG
                Form: Tablet
                Dose: 1
                Frequency: Daily
                Instructions: at breakfast

            Medication:  Lansoprazole Oral Capsule Delayed Release 15 MG 2-3 daily NOT TO EXCEED 2 CAPSULES IN AN 8 HOUR PERIOD
            Output:
                Name: Lansoprazole
                Route: Oral
                Strength: 15 MG
                Form: Capsule
                Dose: 2-3
                Frequency: Daily
                Instructions: NOT TO EXCEED 2 CAPSULES IN AN 8 HOUR PERIOD

        Output the normalized medication in the following json format:
        {
            "name": "**Name",
            "route": "**Route",
            "strength": "**Strength",
            "form": "**Form",
            "dosage": "**Dose",
            "frequency": "**Frequency",
            "instructions": "**Instructions"
        }
    """

@inject
async def run( commands: ICommandHandlingPort, query: IQueryPort ):

    patient_id = "7839790"
    document_id = "a21145b884c411efaac042004e494300"
    
    start_time = time.time()

    LOGGER.debug("Getting Document Operation Definition for %s", DocumentOperationType.MEDICATION_EXTRACTION)
    doc_op_def = await query.get_document_operation_definition_by_op_type(DocumentOperationType.MEDICATION_EXTRACTION.value)
    #LOGGER.debug("Document Operation Definition: %s", json.dumps([x.dict() for x in doc_op_def], indent=2, cls=DateTimeEncoder))
    config = doc_op_def[0].step_config["NORMALIZE_MEDICATIONS"]
    LOGGER.debug("Config: %s", json.dumps(config, indent=2, cls=DateTimeEncoder))

    model = config["model"]
    prompt_text = config["prompt"]
    prompt_text = prompt_text.replace("{{search_term}}", "{search_term}")

    #Get Doc Op Instance for documnet
    op_type = DocumentOperationType.MEDICATION_EXTRACTION.value
    LOGGER.debug("Getting Document Operation Instance for %s", op_type)
    doc_op: DocumentOperationDefinition = await query.get_document_operation_by_document_id(document_id, op_type)
    doc_op_inst_id = doc_op.active_document_operation_instance_id
    LOGGER.debug("Doc op instance_id: %s", doc_op_inst_id)
    LOGGER.debug("DocOp: %s", doc_op)

    
    extracted_meds = await query.get_extracted_medications_by_operation_instance_id(document_id, doc_op_inst_id)
    LOGGER.debug("Extracted Meds: %s", json.dumps([x.dict() for x in extracted_meds], indent=2, cls=DateTimeEncoder))

    command = NormalizeMedications(
        app_id="",
        tenant_id="",
        patient_id="",
        document_id="",
        document_operation_instance_id="",
        document_operation_definition_id="",        
        extracted_medications=extracted_meds,

        model=MULTIMODAL_MODEL,        
        prompt=prompt_text,
        page_number= -1,
    )

    #results = None
    results = await commands.handle_command(command)
    LOGGER.debug("Results: \n%s", json.dumps([x.dict() for x in results], indent=2, cls=DateTimeEncoder))

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    LOGGER.debug("Elapsed time: %.2f ms", elapsed_time_ms)

    return results

if __name__ == "__main__":    
    asyncio.run(run())   
