# # test for CreateDocumentVectorIndex command
# #  code will read the provided pdf, extract the text using gemini 1.5
# #  chunk using various methods, and index the chunks into vector database
# import sys, os

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
# import pytest
# from paperglass.domain.values import AnnotationType, PDFParsingStrategy, Section
# from paperglass.usecases.commands import (
#     CreateDocumentChunkSection,
#     CreateDocumentChunkSectionVectorIndex,
#     CreateDocumentChunkStructuredData,
#     CreateEvidenceCitationsCommand,
#     CreateExtractNamedEntityCommand,
#     GetDocumentChunkSectionsCommand,
#     SearchDocumentContextCommand,
# )
# from kink import inject
# from paperglass.infrastructure import bindings
# from paperglass.interface.ports import ICommandHandlingPort, IEventHandlingPort
# from paperglass.infrastructure.ports import IEmbeddingsAdapter
# from paperglass.domain.models import VectorIndex
# from paperglass.domain.events import PageLBILabelAdded
# import asyncio
# import pytest_asyncio


# @pytest.fixture
# def commands():
#     @inject
#     def get_commands(commands: ICommandHandlingPort):
#         return commands

#     return get_commands()


# @pytest.fixture
# def events():
#     @inject
#     def get_events(events: IEventHandlingPort):
#         return events

#     return get_events()


# @pytest.fixture
# def setup():
#     # this doc id exists in viki-dev gcs bucket
#     # we are testign with a real doc here
#     # ToDo: create adapters that mocks a pdf and injected before test suite runs
#     # return {"document_id": "0127d144e58711eea57cc3a190d5388c", "chunk_index": 3}
#     return {"document_chunk_id": "cca2eca8018111ef9b1e0242ac120008", "chunk_index": 2}
#     # return {"document_id": "0127d144e58711eea57cc3a190d5388c", "chunk_index": 1}


# # return {"document_id": "0127d144e58711eea57cc3a190d5388c", "chunk_index": 0}


# @pytest.fixture
# def patient_id():
#     return "c70ee241-126a-719b-4b53-c48e5ae3716c"


# # @pytest.mark.asyncio
# # async def page_lbi_label_added(events, patient_id):
# #     result = await events.handle_command(
# #         PageLBILabelAdded(document_id="f421bd00065811ef91420242ac120003", chunk_index=2, patient_id="michael-p-2", label="medications", content="medications")
# #     )
# #     assert result


# @pytest.mark.asyncio
# async def test_extract_named_entity(commands, patient_id):
#     content = """
#     Page: 1Comprehensive Details:**Client**        MOUSE, MINNIE**Address**        21234 MAIN ST        ANY CITY, USA 12345**MR No:**        **Legacy MR No:**        **Admission Date:**        1/10/2022**ICD-10 Diagnoses/Procedures**    **Order**        **Code** : **Description**        1 : 195.1 : ORTHOSTATIC HYPOTENSION        2 : R65.21 : SEVERE SEPSIS WITH SEPTIC SHOCK**Client Allergies**        COW MILK        MIRIPIN**Patient Medications**    **Start Date / End Date Classification**        **Dose**        **Amount**        **Frequency**        **Route**        **Purpose**        **Directions for use**        **Side Effects/Interactions**        **New/Changed**        **Financial Resp.**        **Agency Administered**        **PRN**        **Entered By**        **Date**        1/10/2022 : BETHANECHOL CHLORIDE 10 MG TABLET        1 tablet            : 3 TIMES DAILY            : ORAL            : N            : N            : N            : O            : OTH            : N            : N            : NANCY NURSE, RN            : 01/10/2022            Reason: GENITOURINARY THERAPY            Reason: BLADDER        1/10/2022 : BIOTIN 1 MG CAPSULE        1 capsule            : DAILY            : ORAL            : N            : N            : N            : O            : OTH            : N            : N            : NANCY NURSE, RN            : 01/10/2022            Reason: ELECTROLYTE BALANCE- NUTRITIONAL PRODUCTS            Reason: SUPPLEMENT        1/10/2022 : IRBESARTAN 150 MG TABLET        0.5 tablet            : DAILY            : ORAL            : N            : N            : N            : O            : OTH            : N            : N            : NANCY NURSE, RN            : 01/10/2022            Reason: CARDIOVASCULAR THERAPY            Reason: BLOOD PRESSURE            AGENTS        1/10/2022 : LABETALOL 100 MG TABLET        1 tablet            : 3 TIMES DAILY            : ORAL            : N            : N            : N            : O            : OTH            : N            : N            : NANCY NURSE, RN            : 01/10/2022            Reason: CARDIOVASCULAR THERAPY            Reason: BLOOD PRESSURE            AGENTS**Insured ID:**        222222**Primary Payor:**        COMMERCIAL**Physician:**        JOHN DOE, MD**Address:**        14444 MAIN ST        ANY CITY USA, 12345**Onset / Exac.**        **O/E Date** : **Type**        ONSET : 01/04/2022 : DIAGNOSIS        EXACERBATION : 12/29/2021 : DIAGNOSIS**Phone:**        (123)456-7890
#     """
#     result = await commands.handle_command(
#         CreateExtractNamedEntityCommand(
#             patient_id="8d82189d39f941819e6dd3e7c76d3256",
#             labels=["medications"],
#             named_entity_type="medications",
#             extraction_input_prompt=f"""please extract all medications as a Array of JSON object 
#                 with keys as name, dosage, frequency, route, reason, start_date, end_date and reference from {content}
#                 reference is another dictionary with keys as document, chunk and page
#                 document:3f81f07813c711efada80242ac120004,chunk:0,page:1
#                 """,
#         )
#     )
#     assert result


# # @pytest.mark.asyncio
# # async def test_create_evidence_citations(commands, setup):
# #     evidence_requested_for = [
# #         {
# #             "name": "BETHANECHOL CHLORIDE",
# #             "dosage": "10 MG",
# #             "frequency": "1 tablet",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #         {
# #             "name": "BIOTIN",
# #             "dosage": "1 MG",
# #             "frequency": "1 capsule",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #         {
# #             "name": "IRBESARTAN",
# #             "dosage": "150 MG",
# #             "frequency": "0.5 tablet",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #         {
# #             "name": "LABETALOL",
# #             "dosage": "100 MG",
# #             "frequency": "1 tablet",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #         {
# #             "name": "MIRTAZAPINE",
# #             "dosage": "15 MG",
# #             "frequency": "1 tablet",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #         {
# #             "name": "OXYCODONE-ACETAMINOPHEN",
# #             "dosage": "5 MG-325 MG",
# #             "frequency": "1 tablet",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #         {
# #             "name": "SPIRONOLACTONE",
# #             "dosage": "25 MG",
# #             "frequency": "1 tablet",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #         {
# #             "name": "VITAMIN D3",
# #             "dosage": "25 MCG (1,000 UNIT)",
# #             "frequency": "1 capsule",
# #             "route": None,
# #             "reason": None,
# #             "start_date": None,
# #             "end_date": None,
# #             "reference": {"document": "86e1bce60c7e11ef8c390242ac120006", "chunk": 2, "page": 0},
# #         },
# #     ]

# #     results = []
# #     for evidence in evidence_requested_for:
# #         result = ""
# #         for key, value in evidence.items():
# #             if value and isinstance(value, str):
# #                 result = result + key + ": " + (value if value else "") + " "
# #         results.append(result)

# #     result = await commands.handle_command(
# #         CreateEvidenceCitationsCommand(
# #             document_chunk_id="91d264d010c911ef90930242ac120005.2",
# #             evidence_requested_for=results,
# #             annotation_type=AnnotationType.LINE,
# #         )
# #     )
# #     print(result)
# #     assert result
