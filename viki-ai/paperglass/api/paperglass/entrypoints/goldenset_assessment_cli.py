import asyncio
import sys, os

import json
import csv
import time
import urllib.parse
import requests as req
import re
from typing import List
import logging
import traceback
from kink import inject

from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from paperglass.infrastructure.ports import IMedispanPort, IRelevancyFilterPort, IPromptAdapter

from paperglass.domain.models import ExtractedMedication, MedispanDrug, MedicationValue

from paperglass.domain.string_utils import remove_multiple_spaces
from paperglass.domain.util_json import convertToJson

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARN)
logging.getLogger('google.auth.transport').setLevel(logging.WARN)


INPUT_IDX = "timeouts"
INPUT_FILE_PATH =  f"../../../eai-ai-poc/data/medispan/medications-extracted-stage-INPUT-group-{INPUT_IDX}.csv"
OUTPUT_FILE_PATH = f"../../../eai-ai-poc/data/medispan/output/medications-extracted-stage-OUTPUT-group-{INPUT_IDX}.csv"

MEDISPAN_MATCHING_PROMPT = """
                        For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:\n 1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match\n 2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength\n 3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form\n 4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route\n 5) Otherwise, return "{}" and specific what attributes were not found\n \n Only return the best match from the list. If no match is found, return "{}"\n \n Only return the best match from the list. If no match is found, return "{}"\n \n GIVEN MEDICATION:\n {SEARCH_TERM}\n \n MATCH LIST:\n
"""

NORMALIZE_PROMPT_TEXT = """
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
async def normalize(search_term: str,
                    prompt: IPromptAdapter):

    output = {
        "dosage": None,
        "instructions": None
    }

    this_prompt_text = [NORMALIZE_PROMPT_TEXT.replace("{search_term}", search_term)]

    raw_results = await prompt.multi_modal_predict_2(
        this_prompt_text,
        response_mime_type = "application/json",
        model="gemini-1.5-flash-001",
        metadata={}
    )
    LOGGER.debug("Normalized medication '%s' raw response from LLM: %s", search_term, raw_results)    

    if raw_results:
        try:
            LOGGER.debug("Normalized medication raw response from LLM: %s", raw_results)
            results = convertToJson(raw_results)
            normalized_medication = MedicationValue(**results)            

            if normalized_medication.dosage:
                output["dosage"] = normalized_medication.dosage                

            if normalized_medication.instructions:
                output["instructions"] = normalized_medication.instructions
            
        except:
            LOGGER.warn("Unable to parse normalized medication for medication %s with response from llm: %s", search_term, raw_results)            
    else:
        LOGGER.warn("No normalized medication found for medication %s", search_term)        

    return output


# Run once or in a loop based on mode provided
@inject
async def run(medispan_port: IMedispanPort, relevancy_filter_adapter: IRelevancyFilterPort ):
    LOGGER.debug("Assessing golden dataset: %s", INPUT_FILE_PATH)

    start_time = time.time()

    orig_header = None    
    new_header = [        
        "ai_medispan_status",
        "ai_medispan_id",
        "ai_medispan_name",
        "ai_medispan_route",
        "ai_medispan_strength",
        "ai_medispan_form",
        "ai_medispan_dosage",
        "ai_medispan_frequency",
        "ai_medispan_instructions",
        "ai_medispan_search_term",
        "ai_normalization_search_term",
    ]

    print(f"Output file: {OUTPUT_FILE_PATH}")
    print(f"Input file: {INPUT_FILE_PATH}")
    
    with open(OUTPUT_FILE_PATH, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        with open(INPUT_FILE_PATH, mode='r', newline='') as file:
            reader = csv.reader(file)
            idx = 0
            for row in reader:
                if idx == 0:
                    orig_header = row
                    writer.writerow(orig_header + new_header)
                else:
                    medication_name = row[22]
                    medication_route = row[23]
                    medication_form = row[26]
                    medication_strength = row[24]
                    medication_dosage = row[25]
                    medication_frequency = row[27]
                    medication_instructions = row[28]

                    LOGGER.debug(f"Medication {idx} =========================================================================================")                    
                   
                    try:

                        value = f'{medication_name} {medication_strength or ""} {medication_dosage or ""} {medication_form or ""} {medication_route or ""}'                        
                        medispan_search_term = remove_multiple_spaces(value)
                        
                        medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(medispan_search_term)

                        # If initial search does not return any results, try searching with just the first word of the medication name
                        if not medispan_port_result:                        
                            original_search_term = medispan_search_term
                            medispan_search_term = f"{medication_name.split(' ')[0]}"                            
                            LOGGER.debug("MedispanMatching: Initial search for medication '%s' did not yield any results.  Trying search with just the first word of the medication name: '%s'", original_search_term, medispan_search_term)
                            medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(medispan_search_term)                                                                                                  

                        medispan_results_tuple = await relevancy_filter_adapter.re_rank(medispan_search_term, medispan_port_result, model="gemini-1.5-pro-001", prompt=MEDISPAN_MATCHING_PROMPT, enable_llm=True)
                        medispan_port_result, context = medispan_results_tuple
                        medispan_drug:MedispanDrug = medispan_port_result
                      
                        new_data = []

                        if medispan_drug:

                            normalization_search_term = f"{medication_name} {medication_route} {medication_strength} {medication_form} {medication_frequency} {medication_instructions}"
                            normalized_data = await normalize(normalization_search_term)
                            medication_dosage = normalized_data["dosage"]
                            medication_instructions = normalized_data["instructions"]

                            new_data.append("MATCHED")
                            new_data.append(medispan_drug.id)
                            new_data.append(medispan_drug.GenericName)
                            new_data.append(medispan_drug.Route)
                            new_data.append(f"{medispan_drug.Strength} {medispan_drug.StrengthUnitOfMeasure}")
                            new_data.append(medispan_drug.Dosage_Form)
                            new_data.append(medication_dosage)
                            new_data.append(medication_frequency)
                            new_data.append(medication_instructions)
                            new_data.append(medispan_search_term)
                            new_data.append(normalization_search_term)
                        else:
                            new_data.append("UNMATCHED")
                            new_data.append("")
                            new_data.append("")
                            new_data.append("")
                            new_data.append("")
                            new_data.append("")
                            new_data.append("")
                            new_data.append("")
                            new_data.append("")
                            new_data.append(medispan_search_term)

                        writer.writerow(row + new_data)
                     
                    
                    except Exception as e:
                        LOGGER.error(f"Row: {idx} {medication_name} {medication_route} {medication_form} {medication_strength} {medication_frequency} {medication_instructions}")
                        LOGGER.error(f"EXCEPTION!!!!!  {e}")
                        LOGGER.error(traceback.format_exc())
                        new_data = ["ERROR", str(e)]                        
                        new_data.append("")
                        new_data.append("")
                        new_data.append("")
                        new_data.append("")
                        new_data.append("")
                        new_data.append("")
                        new_data.append("")
                        new_data.append(medispan_search_term)

                        writer.writerow(row + new_data)
                        continue

                idx += 1                

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    LOGGER.debug(f"Records processed: {idx}  Elapsed time: {elapsed_time_ms/1000} sec")
    LOGGER.debug("")
    LOGGER.debug("")
    LOGGER.debug("Done")


def main():
    
    asyncio.run(run())

if __name__ == "__main__":   
    main()






