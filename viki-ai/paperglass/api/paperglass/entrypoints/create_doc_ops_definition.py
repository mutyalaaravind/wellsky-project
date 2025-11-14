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
from paperglass.settings import APPLICATION_INTEGRATION_TRIGGER_ID, CLOUD_TASK_QUEUE_NAME, INTEGRATION_PROJECT_NAME, SELF_API, SERVICE_ACCOUNT_EMAIL
from paperglass.usecases.commands import CreateDefaultMedicationDocumentOperationDefinition, TriggerExtraction
from paperglass.infrastructure.ports import IApplicationIntegration, IQueryPort
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.domain.models import Document
from paperglass.domain.values import DocumentOperationStep, DocumentStatusType
from google.cloud import storage
from mktoken import mktoken, mktoken2
import csv

import math
from google.cloud import firestore
import csv
import csv

async def _get_token(self):
    import google.auth
    import google.auth.transport.requests
    SCOPE = "https://www.googleapis.com/auth/cloud-platform"
    credentials, project_id = google.auth.default(scopes=[SCOPE])
    # getting request object
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)  # refresh token
    token = credentials.token
    return token, project_id

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


@inject
async def create_doc_operation_definition(command:ICommandHandlingPort):
    await command.handle_command(CreateDefaultMedicationDocumentOperationDefinition(
        app_id="007", tenant_id="54321",
        step_config={
        DocumentOperationStep.TEXT_EXTRACTION.value:{
                "model":"gemini-1.5-flash-002",
                "prompt":"""
                            You are expert medical transcriber. 
                            Taking each page of the document attached, 
                            can you extract comprehensive details with all the text elements on the given page?
                            
                            Output expected:
                            Page: #X
                            Comprehensive Details:
                            **[section header]**
                                [section comprehensive details]
                            """,
                "description":"Extract text from the document",
            },
        DocumentOperationStep.TEXT_EXTRACTION_AND_CLASSIFICATION.value:{
                "model":"gemini-1.5-flash-002",
                "prompt":"""
                        You are expert medical transcriber. 
                        Taking each page of the document attached, 
                        can you extract comprehensive details with all the text elements on the given page?
                        Additionally, please extract medications in <MEDICATIONS> section and conditions in <CONDITIONS> section.
                        
                        Output expected:
                        <EXTRACT>
                        Page: #X
                        Comprehensive Details:
                        **[section header]**
                            [section comprehensive details]
                        </EXTRACT>
                        <MEDICATIONS>
                        </MEDICATIONS>
                        <CONDITIONS>
                        </CONDITIONS>
                        """,
                "description":"Extract text from the document and classify the document",
        },
        DocumentOperationStep.CLASSIFICATION.value:{
                "model":"gemini-1.5-flash-002",
                "prompt":"", #ToDo: make it null
                "description":"Classify the document",
            },
        DocumentOperationStep.EVIDENCE_CREATION.value:{
                "model":"gemini-1.5-flash-002",
                "prompt":"""
                'Below is the table that contains tokens found on page along with their normalized AABB coordinates (x1, y1, x2, y2)',
                'These texts are spatially arranged as a set of rows with consistent structure across all content on the page. ',
                'Therefore, when mapping, take into account the spatial arrangement and output the bounding box coordinates that are located close together and not something from different row.',
                '```',
                <table></table>,
                '```',
                'We are looking for a sequence of those blocks that are located close to each other and show the following texts:',
                *<medications></medications>,
                'RULES:',
                '- For each requested text, provide all table entries that show this text.',
                '- For each requested text, print result as markdown table with 6 columns: text, x1, y1, x2, y2.',
                '- Markdown tables must be headerless - only data.',
                '- Each row should look as follows: "| text | x1 | y1 | x2 | y2|"',
                '- Do not include any header titles or other markdown formatting: only markdown tables.',
                '- Separate tables from each other with a triple dash ("---").',
                        """,
                "description":"Extract Medications from the document",
            },
        DocumentOperationStep.MEDICATIONS_EXTRACTION.value:{
                "model":"gemini-1.5-flash-002",
                "prompt":"""
                        Please study this document:[Task]:      
                        please extract medications as array of JSON with keys as name, strength, dosage, route, form, discontinued_date, frequency, start_date, end_date, instructions,explanation, document_reference and page_number.      
                        Please do not include any markup other than JSON.      
                        Please format start_date and end_date as mm/dd/yyyy.      
                        **The 'name' field should include alias , punctuation if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')**     
                        **Distinguish between dosage (eg. 1 tab, 2-3 tablets) and strength of medication.     Dosage field does not have Unit of Measurement(MG, ML, GM, % , UT, ACT, UNIT), if it has considered as Strength, leave dosage blank**
                        """,
                "description":"Extract Medications from the document",
            },
        DocumentOperationStep.MEDISPAN_MATCHING.value:{
                "model":"gemini-1.5-flash-002",
                "prompt": """
                        For each GIVEN MEDICATIONS, can you find the best medication match from the MATCH LIST given below? Please follow these instructions:
                        1) The name of the GIVEN MEDICATION should be match the \"NameDescription\" field of the MATCH LIST entries. Otherwise no name match
                        2) Prefer the match if the MATCH LIST entry's \"NameDescription\" begins with the first word of the GIVEN MEDICATION name
                        3) Prefer the match if the name of the GIVEN MEDICATION exactly matches (case insensitive) the name of the MATCH LIST \"NameDescription\" entry.  
                        4) Lower the consideration for the match if the name of the GIVEN MEDICATION only matches the \"GenericName\" field and does not match the \"NameDescription\" field of the MATCH LIST entry.
                        5) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
                        6) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
                        7) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route

                        The list of GIVEN MEDICATIONS is a dictionary with the key being the index and the value being the name of the medication.

                        For each medication, only return the best match from the list. 

                        Return the response in the following json format:

                        [
                            {"**MEDICATION_ID": "**MATCHLIST id"}
                        ]

                        GIVEN MEDICATIONS:
                        {SEARCH_TERM}

                        MATCH LIST:
                        {DATA}
                        """,
                "description:":"Medispan matching step",
        },        
        DocumentOperationStep.NORMALIZE_MEDICATIONS.value:{
                "model":"gemini-1.5-flash-002",
                "prompt":"""
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
                                                """,
                "description":"Normalize medications (fine tuned extraction)",
            },
        DocumentOperationStep.ALLERGIES_EXTRACTION.value:{
            "model":"gemini-1.5-flash-002",
            "prompt":"""
                    Act as a intelligent healthcare extractor and Extract allergies information from <content></content> in separate JSON.
                    Extract Allergy profile for :
                    1. NKA (Food / Drug / Latex / Environmental)
                    2. Allergies and Sensitivities -Extract information on Substance and Reaction

                    Do not include any explanation in the reply. Only include the extracted information in the reply

                    The expcted JSON return type is as below:
                    [{
                        "reaction": "reaction1",
                        "substance": "substance1",
                    },
                    {
                        "reaction": "reaction2",
                        "substance": "substance2",
                    }
                    ]
                    """,
            "description":"Extract Allergies",
        },
        DocumentOperationStep.IMMUNIZATIONS_EXTRACTION.value:{
            "model":"gemini-1.5-flash-002",
            "prompt":"""
                    Act as a intelligent healthcare extractor and Extract Immunization information from <content></content> in separate JSON for below
                    1. Pneumonia
                    2. Flu
                    3. Tetanus
                    4. TB
                    5. TB Exposure
                    6. Hepatatis B

                    Below  Are the Rules:
                    1. Extract the Immunization details like Yes for taken and No for not taken/not known
                    2. Include the date of immunization (formated as mm/dd/yyyy)
                    3. In case of additional immunization which you don't see in above table add that under additional tab
                    4. Save original_extracted_string (shortened) string for each immunization. 

                    Do not include any explanation in the reply. Only include the extracted information in the reply
                    The expected JSON return type is as below (for example):
                    [{
                        "name": "Flu",
                        "status": "yes",
                        "date": "01/01/2022",
                        "orginal_extracted_string": ""
                    },
                    {
                        "name": "TB",
                        "status": "yes | no | unknown",
                        "date": "01/01/2022",
                        "original_extracted_string": ""
                    }
                    ]

                    """,
            "description":"Extract Immunizations",
        }
        }
    ))
    

if __name__ == "__main__":
    # run in shell: 
    # gcloud auth application-default login --impersonate-service-account=viki-ai-stage-sa@viki-stage-app-wsky.iam.gserviceaccount.com
    
    
    #asyncio.run(start_app_integration_execution_for_gcs_files())
    #asyncio.run(create_patients("viki-stage-app-wsky","./files_to_process.csv"))
    # asyncio.run(create_documents("viki-ai-provisional-stage","./files_to_process.csv",start_index=30,end_index=60))
    #asyncio.run(create_documents("viki-ai-provisional-stage","./files_to_process.csv",start_index=1,end_index=30,force_retrigger=False))
    #asyncio.run(get_patient_documents(project="viki-stage-app-wsky"))
    #asyncio.run(get_docs_by_patients())
    asyncio.run(create_doc_operation_definition())
    pass