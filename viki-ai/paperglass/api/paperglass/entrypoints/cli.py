import asyncio
import base64
import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


from paperglass.domain.fhir import DocumentReference, Patient
from paperglass.usecases.search import search, index, search_fhir
from paperglass.infrastructure import bindings
from paperglass.infrastructure.ports import IEmbeddingsAdapter, ISearchIndexer, IStoragePort, IFhirStoreAdapter
from paperglass.domain.values import (
    Annotation,
    AnnotationType,
    Attachment,
    BlockAnnotation,
    Chunk,
    CodeableConcept,
    Coding,
    Content,
    Identifier,
    LineAnnotation,
    Name,
    Page,
    ParagraphAnnotation,
    Rect,
    Reference,
    TokenAnnotation,
    Vector2,
)
from kink import inject


async def index_document():
    await index("1234", "abc", "gs://viki-ai-provisional-dev/patient_charts/*", "application/pdf")


async def search_document():
    print(await search_fhir("1234", "covid"))


@inject()
async def search_embeddings(storage: IStoragePort, embedding_adapter: IEmbeddingsAdapter):
    identifier = "43faf426dddd11eea7b70242ac120008"
    import json

    gcs_uri = "viki-ai-provisional-dev/paperglass/page_results/hcc/16b8bf2ed4bf11ee830e0242ac17000c.json"
    result = await storage.get_page_result("hcc", identifier)
    tokens = json.loads(result).get("text").split("\n")
    print(str(tokens))

    # await embedding_adapter.upsert(identifier,tokens)
    neighbours = await embedding_adapter.search(identifier, ["biotin"])
    print(neighbours)


@inject
async def create_embeddings(embedding_adapter: IEmbeddingsAdapter):
    text = "Patient\u0027s Medicare No.\nPatient\u0027s Name and Address:\nMINNIE MOUSE (123) 456-7890\n1234 MAIN ST\nANY CITY, USA 12345\nPhysician\u0027s Name \u0026 Address:\nICD-10\nDiagnoses:\nSOC Date\n1/10/2022\nJOHN DOE, MD\n8910 MAIN ST\nANY CITY USA 12345\nOrder Code\n195.1\nR65.21\n182.403\n1\n2\n3\nPatient\u0027s Expressed Goals:\nTO GET STRONGER AND IMPROVE ENDURANCE\nHOME HEALTH CERTIFICATION AND PLAN OF CARE\nMedical Record No.\n123456789\nNurse\u0027s Signature and Date of Verbal SOC Where Applicable: (deemed as electronic\nsignature) THERAPY THERAPIST PT/NANCY NURSE RN\nCertification Period\n1/10/2022 to 3/10/2022\nP: (386)409-6839\nFrequency/Duration of Visits:\nPT 2WK3,1WK3\nOT 1WK1\nDescription\nORTHOSTATIC HYPOTENSION\nProvider\u0027s Name, Address and Telephone Number:\nHOME HEALTH AGENCY\n4567 MAIN ST\nANY CITY, USA 12345\nF: (386)409-6916\n1/10/2022\nSEVERE SEPSIS WITH SEPTIC SHOCK\nACUTE EMBOLISM AND THOMBOS UNSP DEEP VEINS OF LOW EXTRM, BI\nProvider No.\n44444444\nPatient\u0027s Date of Birth:\nPatient\u0027s Gender:\nOrder Date:\nVerbal Order:\nPHYSICAL THERAPY TO PROVIDE NEUROMUSCULAR RE-ED AND BALANCE RETRAINING.\nF: (123)867-5309\nP: (123) 456-7899\n1/1/44\nFEMALE\n1/10/2022 1:56 PM\nPHYSICAL THERAPY TO ESTABLISH/PROGRESS HOME EXERCISE PROGRAM.\nAttending Physician\u0027s Signature and Date Signed\nY\nOrder Number:\n1111111\nVerbal Date:\nVerbal Time:\nDate HHA Received Signed POC\nOnset or\nExacerbation\nONSET\n1/10/2022\n4:55 PM\nONSET\nEXACERBATION\nOrders of Discipline and Treatments:\nPHYSICAL THERAPY TO EVALUATE/ASSESS AND DEVELOP PHYSICAL THERAPY PLAN OF CARE TO BE SIGNED BY THE PHYSICIAN.\nPHYSICAL THERAPY TO PROVIDE SKILLED TEACHING TO MINIMIZE AND MANAGE IDENTIFIED RISKS OF HOSPITALIZATION AND/OR ED VISIT\nLISTED IN SUPPORTING DOCUMENTATION FOR RISK OF HOSPITAL READMISSION SECTION OF THE PLAN OF CARE.\nPHYSICAL THERAPY TO PROVIDE FALL PREVENTION STRATEGIES TO REDUCE FALL RISK.\nO/E Date\n01/04/2022\n12/29/2021\n01/04/2022\nPHYSICAL THERAPY TO PROVIDE THERAPEUTIC ACTIVITY AND EXERCISE TO IMPROVE FUNCTIONAL STRENGTH AND POWER.\nPHYSICAL THERAPY TO PROVIDE GAIT TRAINING TO IMPROVE AMBULATION AND SAFETY WITH/WITHOUT ASSISTIVE DEVICE.\nPHYSICAL THERAPY TO PROVIDE INSTRUCTION IN ENERGY CONSERVATION TECHNIQUES DESIGNED TO MAXIMIZE PATIENT\u0027S\nPRODUCTIVITY WITH FUNCTIONAL ACTIVITIES.\nLICENSED PROFESSIONAL TO REPORT VITAL SIGNS FALLING OUTSIDE THE FOLLOWING ESTABLISHED PARAMETERS. TEMP\u003c95\u003e101\nPULSE\u003c60\u003e100 RESP\u003c12\u003e24 SYSTOLICBP\u003c90\u003e150 DIASTOLICBP\u003c50\u003e90 PAIN\u003e7 02SAT\u003c90\nGoals/Rehabilitation Potential/Discharge Plans:\nA PHYSICAL THERAPY PLAN OF CARE WILL BE ORDERED BY PHYSICIAN AND PROVIDED BY PHYSICAL THERAPY. ALL GOALS TO BE MET\nBY END OF CURRENTLY APPROVED PLAN OF CARE.\nPATIENT/CAREGIVER VERBALIZES/DEMONSTRATES ABILITY TO MANAGE THE RISK OF HOSPITALIZATION OR ED VISITS AS EVIDENCED BY\nNO HOSPITALIZATION OR ED VISITS DURING CARE.\nPOC GOAL: PATIENT WILL IMPROVE AWARENESS OF FALL RISK FACTORS AND DEMONSTRATE APPROPRIATE ACTIONS TO REDUCE RISK\nFACTORS AS EVIDENCED BY NO FALLS BY 1/28/22\nPATIENT WILL IMPROVE FUNCTIONAL STRENGTH AND POWER AS EVIDENCED BY POSITIVE CHANGE WITH IMPROVED ABILITY TO\nPERFORM SIT TO STAND TRANSFERS WITHOUT USING UES TO PUSH UP BY 2/18/22\nPATIENT WILL IMPROVE GAIT AND AMBULATION AS EVIDENCED BY IMPROVED TUG SCORE BY 2/18/22\nPATIENT WILL IMPROVE STATIC AND DYNAMIC, FUNCTIONAL BALANCE AS EVIDENCED BY IMPROVED STANDARDIZED BALANCE TEST\nSCORE BY 2/18/22\nI certify that this patient is confined to his/her home and needs intermittent skilled nursing care, physical therapy and/or speech therapy or continues to need\noccupational therapy. This patient is under my care, and I have authorized the services on this plan of care and will periodically review the plan.\nAnyone who misrepresents, falsifies, or conceals essential information required\nfor payment of federal funds may be subject to fine, imprisonment, or civil\npenalty under applicable federal laws.\nPage 1 of 4\nPatient\u0027s Medicare No.\nPatient\u0027s Name\nMINNIE MOUSE\nDME and Supplies:\nNONE\nRehab Potential:\nGOOD/MARKED IMPROVEMENT IN FUNCTIONAL STATUS IS EXPECTED\nPrognosis:\nGOOD\nFunctional Limitations:\nGoals/Rehabilitation Potential/Discharge Plans:\nPATIENT WILL ADOPT AND INTEGRATE HOME EXERCISE PROGRAM INTO DAILY ROUTINE AS EVIDENCED BY PROGRESSION OF ACTIVITIES\nAND/OR CONDITION SPECIFIC PROTOCOL BY 1/28/22\nPATIENT/CAREGIVER TO DEMONSTRATE UNDERSTANDING OF AND COMPLIANCE WITH ENERGY CONSERVATION MEASURES, AS\nEVIDENCED BY DYSPNEA RATING OF 4/10 FUNCTIONAL ACTIVITIES BY 2/18/22\nDC Plans:\nDC TO SELF CARE UNDER SUPERVISION OF MD WHEN GOALS ARE MET\nSOC Date\n1/10/2022\nActivities Permitted:\nENDURANCE; AMBULATION; BALANCE\nSafety Measures:\nCOVID-19 PRECAUTIONS, EMERGENCY PLAN, FALL PRECAUTIONS\nEXERCISES PRESCRIBED; WALKER\nNutritional Requirements:\nHEART HEALTHY DIET, LOW SODIUM DIET\nAdvance Directives:\nLIVING WILL\nCertification Period\n1/10/2022 to 3/10/2022\nMental Statuses:\nORIENTED\nProvider\u0027s Name\nHOME HEALTH AGENCY\nMedical Record No.\n123456789\nSignature of Physician\nSupporting Documentation for Cognitive Status:\n(C1) (QM) (PRA) (M1700) COGNITIVE FUNCTIONING: PATIENT\u0027S CURRENT (DAY OF ASSESSMENT) LEVEL OF ALERTNESS, ORIENTATION,\nCOMPREHENSION, CONCENTRATION, AND IMMEDIATE MEMORY FOR SIMPLE COMMANDS.\n0 - ALERT/ORIENTED, ABLE TO FOCUS AND SHIFT ATTENTION, COMPREHENDS AND RECALLS TASK DIRECTIONS INDEPENDENTLY.\n(QM) (M1710) WHEN CONFUSED (REPORTED OR OBSERVED) WITHIN THE LAST 14 DAYS:\n0 - NEVER\n(C1) (QM) (PRA) (M1740) COGNITIVE, BEHAVIORAL, AND PSYCHIATRIC SYMPTOMS THAT ARE DEMONSTRATED AT LEAST ONCE A WEEK\n(REPORTED OR OBSERVED): (MARK ALL THAT APPLY.)\n7- NONE OF THE ABOVE BEHAVIORS DEMONSTRATED\nProvider No.\n444444444\nSupporting Documentation for Psychosocial Status:\n(QM) (M1100B) PATIENT LIVES WITH OTHER PERSON(S) IN THE HOME: WHICH OF THE FOLLOWING BEST DESCRIBES THE PATIENT\u0027S\nAVAILABILITY OF ASSISTANCE AT THEIR RESIDENCE?\n06 - AROUND THE CLOCK\nPSYCHOSOCIAL ISSUES THAT COULD POTENTIALLY IMPACT THE PLAN OF CARE (MARK ALL THAT APPLY):\nNONE AT THIS TIME\nOptional Name/Signature Of\nTHERAPY THERAPIST, PT/NANCY NURSE, RN\nSupporting Documentation for Risk of Hospital Readmission:\n(PRA) (M1033) RISK FOR HOSPITALIZATION: WHICH OF THE FOLLOWING SIGNS OR SYMPTOMS CHARACTERIZE THIS PATIENT AS AT RISK\nFOR HOSPITALIZATION? (MARK ALL THAT APPLY.)\n3- MULTIPLE HOSPITALIZATIONS (2 OR MORE) IN THE PAST 6 MONTHS || 4 - MULTIPLE EMERGENCY DEPARTMENT VISITS (2 OR MORE)\nIN THE PAST 6 MONTHS || 5 - DECLINE IN MENTAL, EMOTIONAL, OR BEHAVIORAL STATUS IN THE PAST 3 MONTHS || 6 - REPORTED OR\nOBSERVED HISTORY OF DIFFICULTY COMPLYING WITH ANY MEDICAL INSTRUCTIONS (FOR EXAMPLE, MEDICATIONS, DIET, EXERCISE)\nIN THE PAST 3 MONTHS || 7 - CURRENTLY TAKING 5 OR MORE MEDICATIONS || 8 - CURRENTLY REPORTS EXHAUSTION\nAllergies:\nCOW MILK; MIRIPIN\nDate\nDate\n1/10/2022\nPage 2 of 4\nPatient\u0027s Medicare No.\nPatient\u0027s Name\nMINNIE MOUSE\nMedications:\nMedication/\nDose\nReason:\nInstructions:\nBIOTIN 1 MG CAPSULE\n1 capsule\nBETHANECHOL CHLORIDE 10 MG TABLET\n1 tablet\nReason:\nInstructions:\nIRBESARTAN 150 MG TABLET\n0.5 tablet\nReason:\nInstructions:\nSOC Date\n1/10/2022\nReason:\nInstructions:\nLABETALOL 100 MG TABLET\n1 tablet\n1 tablet\nBLADDER\nSUPPLEMENT\nReason:\nInstructions:\nMIRTAZAPINE 15 MG TABLET\n1 tablet\n1 tablet\nReason:\nInstructions:\nReason:\nInstructions:\nSignature of Physician\nBLOOD PRESSURE\nDEPRESSION\nReason:\nInstructions:\nSPIRONOLACTONE 25 MG TABLET\nFrequency\nBLOOD PRESSURE\n3 TIMES DAILY\nDAILY\nDAILY\nOXYCODONE-ACETAMINOPHEN 5 MG-325 MG TABLET\nAS NEEDED EVERY 4\nHOURS/PRN\nCertification Period\n1/10/2022 to 3/10/2022\nSUPPLEMENT\n3 TIMES DAILY\nDAILY\nBLOOD PRESSURE\nVITAMIN D3 25 MCG (1,000 UNIT) CAPSULE\n1 capsule\n2 TIMES DAILY\nDAILY\nOptional Name/Signature Of\nTHERAPY THERAPIST, PT/NANCY NURSE, RN\nProvider\u0027s Name\nHOME HEALTH AGENCY\nRoute\nPAIN AS NEEDED, NOT TO EXCEED 3 GM PER DAY\nORAL\nORAL\nORAL\nORAL\nORAL\nORAL\nORAL\nMedical Record No.\n123456789\nORAL\nStart Date/\nEnd Date\n01/10/2022\n01/10/2022\n01/10/2022\n01/10/2022\n01/10/2022\n01/10/2022\n01/10/2022\n01/10/2022\nProvider No.\n4444444\nDC Date\nDate\nNew/\nChanged\nDate\n1/10/2022\nPage 3 of 4\nPatient\u0027s Medicare No.\nPatient\u0027s Name\nMINNIE MOUSE\nSOC Date\n1/10/2022\nTherapy Short Term/Long Term Goals:\nDiscipline: PT\nBALANCE AND FUNCTIONAL CAPACITY (PT)\nBERG BALANCE SCALE (BBS) (SUM SCORE)\nSTG: 40\nTARGET DATE: 1/28/2022\nSupporting Documentation for Home Health Eligibility:\nFOCUS OF CARE (SUPPORTING CLINICAL INFORMATION, PERTINENT MEDICAL HISTORY, ADDITIONAL DIAGNOSIS, LAST\nREHOSPITALIZATION, ER, OR URGENCY CARE VISIT):\nPT REFERRED TO HOME S/P HOSPITALIZATION DUE TO HEADACHE, NECK PAIN, FOUND TO HAVE CNS INFECTION BACTERIAL\nMENINGITIS, SEPSIS, HAD SHUNT PLACED IN HEAD AND ALSO DVT BILATERAL LES AND HAD FILTER PLACED. DIAGNOSED WITH\nDEPRESSION. PT HAS HX OF HTN. PT HAS PITTING EDEMA BILATERAL LES AND WEARS COMPRESSION STOCKINGS. PT IS CURRENTLY\nUSING 2WW TO AMBULATE, HAS DECREASED GAIT SPEED. PT IS MOD I WITH SIT TO STAND TRASNFERS. PT FATIGUES EASILY WITH\nACTIVITY AND REQUIRES REST BREAKS TO RECOVER. TODAY, PT SCORED 19.3\" TUG, 8/12 SPPB AND 31/56 BEG, INDICATING THAT SHE IS\nA FALL RISK. PT LIVES IN 2 STORY HOME, BUT HER BEDROOM/KTICHEN/BATHROOM ARE ALL ON MAIN LEVEL, SO PT DOES NOT NEED TO\nASCEND/DESCEND STAIRS ON A DAILY BASIS. 2 STEPS TO ENTER HOME THROUGH GARAGE.\nPLOF: IND WITH ALL ACTIVITIES/ADLS AND AMBULATION, WOULD TAKE DOG ON WALK OUTSIDE FOR 45 MINUTES\nPT GOAL: TO RETURN TO FULL INDEPENDENCE\nPT WILL FOCUS ON: LE STRENGTHENING, GAIT TRAINING, BALANCE TRAINING\nPT FREQ: 2W3, 1W3\nPT PCP IS DR JOHN DOE FOLLOW UP ON FRIDAY\nHAD FOLLOW UP WITH NEPHROLOGIST, DR PICKLES, TODAY IS 10 POUNDS LIGHTER THAN HER LAST VISIT, BUT STILL HAS PITTING\nEDEMA BILATERAL LES. DR PICKLES CALLED IN PRESCRIPTION FOR BUMEX, WAITING ON PHARMACY.\nTHE PATIENT IS CONSIDERED HOMEBOUND/CONFINED TO HOME BECAUSE: (MARK ALL THAT APPLY)\nBECAUSE OF ILLNESS OR INJURY, PATIENT NEEDS AID OF SUPPORTIVE DEVICES - WALKER - LEVEL 1\nDOCUMENT PATIENT\u0027S CONDITION AND LIMITATIONS AS IT RELATES TO THEIR HOMEBOUND STATUS\nFATIGUE WITH AMBULATION \u003e 100FT USING 2WW AND REQUIRES SEATED REST BREAK TO RECOVER\nGAIT (ASSISTANCE)\nLEVEL SURFACE ASSISTANCE (ORTHO)\nSTG: SETUP OR CLEAN-UP\nASSISTANCE\nDOES THE PATIENT MEET LEVEL 2 CRITERIA - NORMAL INABILITY TO LEAVE THE HOME EXISTS AND LEAVING HOME REQUIRES A\nCONSIDERABLE AND TAXING EFFORT?\nTARGET DATE: 1/28/2022\nUNLEVEL SURFACE ASSISTANCE (ORTHO)\nSTG: SUPERVISION OR TOUCHING\nASSISTANCE\nCertification Period\n1/10/2022 to 3/10/2022\nWHERE A PHYSICIAN HAS DETERMINED THAT IT IS MEDICALLY CONTRAINDICATED FOR A BENEFICIARY TO LEAVE THE HOME BECAUSE\nTHE PATIENT HAS A CONDITION THAT MAY MAKE THE PATIENT MORE SUSCEPTIBLE TO CONTRACTING COVID-19\nTARGET DATE: 1/28/2022\nSTAIRS ASSISTANCE (ORTHO)\nSTG: SUPERVISION OR TOUCHING\nASSISTANCE\nTARGET DATE: 1/28/2022\nSignature of Physician\nMedical Record No.\n123456789\nProvider\u0027s Name\nHOME HEALTH AGENCY\nOptional Name/Signature Of\nTHERAPY THERAPIST, PT/NANCY NURSE, RN\nLTG: 45\nTARGET DATE: 2/18/2022\nLTG: INDEPENDENT\nTARGET DATE: 2/18/2022\nLTG: SETUP OR CLEAN-UP ASSISTANCE\nProvider No.\n444444\nTARGET DATE: 2/18/2022\nLTG: SETUP OR CLEAN-UP ASSISTANCE\nTARGET DATE: 2/18/2022\nDate\nDate\n1/10/2022\nPage 4 of 4\n"
    tokens = text.split("\n")
    for token in tokens:
        embedding_adapter.upsert("1234", ["Home Health Agency"])


@inject
async def create_fhir_resource(fhir_store: IFhirStoreAdapter, storage: IStoragePort, search_indexer: ISearchIndexer):
    doc_url = "gs://viki-ai-provisional-dev/paperglass/documents/2e38db1aead211ee995d0242ac120004/document.pdf"
    doc_id = "2e38db1aead211ee995d0242ac120004"
    doc_file_name = "some doc"
    patient_id = "c70ee241-126a-719b-4b53-c48e5ae3714"
    patient_id = "dummy-patient-id-5"
    date_now = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    raw_data = await storage.get_document(doc_id)
    attachment_data = base64.b64encode(raw_data[0:10000]).decode('utf-8')

    fhir_patient = fhir_store.search("Patient", [{"key": "identifier", "value": patient_id}], Patient)
    if fhir_patient and not fhir_patient.get("items"):
        fhir_patient = fhir_store.post(
            "Patient",
            Patient(
                id=patient_id,
                name=[Name(family="unknown", given=["unknown"])],
                identifier=[Identifier(id=patient_id, system="paperglass", value=patient_id)],
                birthDate="1944-01-01",
            ).dict(),
            Patient,
        )
    else:
        print(fhir_patient)
        fhir_patient = fhir_patient.get("items")[0]

    fhir_doc = fhir_store.post(
        "DocumentReference",
        DocumentReference(
            id=doc_id,
            content=[
                Content(
                    attachment=Attachment(
                        contentType="application/pdf",
                        data=attachment_data,
                        creation=date_now,
                        size=len(attachment_data),
                        hash=attachment_data,
                        language="en",
                        url=doc_url,
                    )
                )
            ],
            identifier=[Identifier(system="paperglass", value=doc_id)],
            date=date_now,
            type=CodeableConcept(
                text="",
                coding=[
                    Coding(
                        code='paperglass',
                        display=doc_file_name,
                    )
                ],
            ),
            description=doc_file_name,
            docStatus="final",
            status="current",
            subject=Reference(reference=f'Patient/{fhir_patient.id}'),
            author=[Reference(reference=f'Patient/{fhir_patient.id}')],
        ).dict(),
        DocumentReference,
    )
    # print(response)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        # index_document()
        # search_document()
        create_fhir_resource()
    )
