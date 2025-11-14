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
)

from paperglass.domain.models import MedispanDrug, ExtractedMedication, MedispanStatus
from paperglass.domain.values import MedicationValue

from paperglass.interface.ports import CommandError, ICommandHandlingPort
from paperglass.usecases.commands import MedispanMatching

from paperglass.infrastructure.ports import IMedispanPort, IRelevancyFilterPort
from paperglass.infrastructure.ports import IQueryPort
# from paperglass.infrastructure.adapters.medispan_vector_search import MedispanVectorSearchAdapter
# from paperglass.infrastructure.adapters.google import FirestoreQueryAdapter

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

getLogger("aiocache").setLevel("ERROR")
getLogger("asyncio").setLevel("ERROR")
getLogger("google.auth").setLevel("ERROR")

MEDISPAN_MATCH_MODEL = "gemini-1.5-pro-001"

@inject
async def run( commands: ICommandHandlingPort ):

    start_time = time.time()

    medications = []

    prompt_text = """
        For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions: 
        
        1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match 
        2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength 
        3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form 
        4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route 
        5) Otherwise, return "{}" and specific what attributes were not found  Only return the best match from the list. If no match is found, return "{}"  Only return the best match from the list. If no match is found, return "{}"  
        
        GIVEN MEDICATION: 
        {SEARCH_TERM}  
        
        MATCH LIST:
    """

    medvalue: MedicationValue = MedicationValue(
        name = "Gabapentin",
        medispan_id = None,
        classification = None,
        dosage="",
        strength="300 MG",
        form="Tablet",
        route="Oral",
        frequency = "1-2 Daily",
        instructions="Not to exceed 2 tablets daily",
        start_date = "",
        end_date = "",
        discontinued_date = "",
    )

    exMed = ExtractedMedication(
        app_id = "",
        tenant_id = "",
        patient_id = "",                
        id = "de081594-4ca8-4a12-a4e8-4d33836e5bd9",
        document_id = "",
        page_id = "",
        route = "",
        reason = "",
        explaination = "",
        document_reference = "",
        page_number = 1,
        active= True,
        change_sets = [],
        deleted = False,
        medication = medvalue,
        medispan_medication = None,
        medispan_status = MedispanStatus.MATCHED,
        medispan_id = None,
        score = None
    )

    medications.append(exMed)

    command = MedispanMatching(
        app_id="",
        tenant_id="",
        patient_id="",
        document_id="",
        document_operation_instance_id="",
        document_operation_definition_id="",        
        extracted_medications=medications,
        page_id="0",
        page_number=1,
        model=MEDISPAN_MATCH_MODEL,        
        prompt=prompt_text,
    )

    results = await commands.handle_command(command)

    LOGGER.debug("Results: \n%s", results)

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    LOGGER.debug("Elapsed time: %.2f ms", elapsed_time_ms)

    return results

if __name__ == "__main__":    
    asyncio.run(run())   