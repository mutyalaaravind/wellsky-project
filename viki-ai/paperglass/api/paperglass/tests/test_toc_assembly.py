import sys, os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
import json

from paperglass.usecases.toc import assemble, createFirstPageProfile
from paperglass.domain.model_toc import PageTOC
from paperglass.domain.models import PageModel, CustomPromptResult
from paperglass.domain.values import Rect, Vector2

def p(str):
    print(str)

P1_RESULT = """
    {"doc": {"name": "SKILLED NURSING FACILITY DISCHARGE SUMMARY", "documentType": "DischargeSummary", "internalPageNumber": "1", "internalPageCount": "4", "sections": [{"name": "Reason for Visit", "isContinued": false, "meds": []}, {"name": "Progress Notes", "isContinued": false, "meds": []}, {"name": "Issues to be Addressed at Follow-up", "isContinued": false, "meds": []}, {"name": "Discharge Diagnosis", "isContinued": false, "meds": []}, {"name": "Medication List", "isContinued": false, "meds": [{"name": "Atorvastatin", "dosage": "20 mg", "route": "Oral", "form": "Tab"}, {"name": "Meloxicam", "dosage": "15 mg", "route": "Oral", "form": "Tab"}, {"name": "metFORMIN", "dosage": null, "route": null, "form": null}]}]}}    
    """    

P2_RESULT = """
    {"doc": {"name": null, "documentType": "DischargeSummary", "internalPageNumber": "2", "internalPageCount": "4", "sections": [{"name": "Reason for Visit", "isContinued": false, "meds": []}, {"name": "Progress Notes", "isContinued": false, "meds": []}, {"name": "Issues to be Addressed at Follow-up", "isContinued": false, "meds": []}, {"name": "Discharge Diagnosis", "isContinued": false, "meds": []}, {"name": "Medication List", "isContinued": false, "meds": [{"name": "Atorvastatin", "dosage": "20 mg", "route": "Oral", "form": "Tab"}, {"name": "Meloxicam", "dosage": "15 mg", "route": "Oral", "form": "Tab"}, {"name": "metFORMIN", "dosage": null, "route": null, "form": null}]}]}}    
    """    

P3_RESULT = """
    {
    "doc": {
        "name": null,
        "documentType": "DischargeSummary",
        "internalPageNumber": "2",
        "internalPageCount": "4",
        "sections": [
            {
                "name": "Medication List",
                "meds": [
                    {
                        "name": "stuff 1",
                        "dosage": "20 mg",
                        "route": "Oral",
                        "form": "Tab"
                    },
                    {
                        "name": "something 5",
                        "dosage": "15 mg",
                        "route": "Oral",
                        "form": "Tab"
                    },
                    {
                        "name": "foobar",
                        "dosage": null,
                        "route": null,
                        "form": null
                    }
                ]
            },
            {
                "name": "Reason for Visit",
                "meds": []
            },
            {
                "name": "Progress Notes",
                "meds": []
            },
            {
                "name": "Issues to be Addressed at Follow-up",
                "meds": []
            },
            {
                "name": "Discharge Diagnosis",
                "meds": []
            }            
        ]
    }
}
    """    

P4_RESULT = """
    {
    "doc": {
        "name": "DRY EYES REPORT",
        "documentType": "ProgressNote",
        "internalPageNumber": null,
        "internalPageCount": null,
        "sections": [
            {
                "name": "Medication List",
                "meds": [
                    {
                        "name": "stuff 1",
                        "dosage": "20 mg",
                        "route": "Oral",
                        "form": "Tab"
                    },
                    {
                        "name": "something 5",
                        "dosage": "15 mg",
                        "route": "Oral",
                        "form": "Tab"
                    },
                    {
                        "name": "foobar",
                        "dosage": null,
                        "route": null,
                        "form": null
                    }
                ]
            },
            {
                "name": "Huh?",
                "meds": []
            }            
        ]
    }
}
"""

P5_RESULT = """
    {
    "doc": {
        "name": "DRY EYES REPORT",
        "documentType": "ProgressNote",
        "internalPageNumber": null,
        "internalPageCount": null,
        "sections": [
            {
                "name": "Huh?",
                "meds": []
            },
            {
                "name": "Medication List",
                "meds": [
                    {
                        "name": "stuff 1",
                        "dosage": "20 mg",
                        "route": "Oral",
                        "form": "Tab"
                    },
                    {
                        "name": "something 5",
                        "dosage": "15 mg",
                        "route": "Oral",
                        "form": "Tab"
                    },
                    {
                        "name": "foobar",
                        "dosage": null,
                        "route": null,
                        "form": null
                    }
                ]
            }                     
        ]
    }
}
"""

async def test_assemble_2():
    print("Assemble Test 2")
    await common_assemble(P1_RESULT, P2_RESULT)   

    
async def test_assemble_3():
    print("Assemble Test 3")
    await common_assemble(P1_RESULT, P3_RESULT)

async def test_assemble_4():
    print("Assemble Test 4")
    await common_assemble(P1_RESULT, P4_RESULT)

async def test_assemble_5():
    print("Assemble Test 5")
    await common_assemble(P1_RESULT, P5_RESULT)


async def common_assemble(prompt_output_1, prompt_output_2):

    app_id="app1"
    tenant_id="tenant1"
    patient_id="patient1"
    document_id="doc1"

    pages = []    
    pages.append(getPage(1, prompt_output_1))    
    pages.append(getPage(2, prompt_output_2))
    ret = await assemble(app_id, tenant_id, patient_id, document_id, pages)

    p("======================================================")
    #p(json.dumps(ret.dict(), indent=4))
    p(ret)
    p("======================================================")


def getPage(page_number:int, results:str):

    app_id="app1"
    tenant_id="tenant1"
    patient_id="patient1"
    document_id="doc1"

    toc_results = CustomPromptResult.create(
                app_id = app_id,
                tenant_id = tenant_id,
                patient_id = patient_id, 
                document_id = document_id,
                page_number = page_number,
                context = {},
                prompt_input = "prompt_input", 
                prompt_output = results,
                document_operation_instance_id = "inst1",
    )

    p:PageModel = PageModel(
        number = page_number,
        mediabox = Rect(
            tl = Vector2(x=0, y=0),
            br = Vector2(x=0, y=0)
        ),
        storage_uri = ""
    )

    o:PageTOC = PageTOC(
        document_id="doc1",
        page_number=page_number,
        page=p,
        toc=toc_results
    )


    return o


def test_createFirstPageProfile():
    o = createFirstPageProfile("Test Medication")


def main():
    #asyncio.run(test_assemble_5())
    test_createFirstPageProfile()

if __name__ == "__main__":
    main()
