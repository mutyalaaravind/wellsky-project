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
#     GetDocumentChunkSectionsCommand,
#     SearchDocumentContextCommand,
# )
# from kink import inject
# from paperglass.infrastructure import bindings
# from paperglass.interface.ports import ICommandHandlingPort
# from paperglass.infrastructure.ports import IEmbeddingsAdapter
# from paperglass.domain.models import VectorIndex
# import asyncio
# import pytest_asyncio


# @pytest.fixture
# def commands():
#     @inject
#     def get_commands(commands: ICommandHandlingPort):
#         return commands

#     return get_commands()


# @pytest.fixture
# def setup():
#     # this doc id exists in viki-dev gcs bucket
#     # we are testign with a real doc here
#     # ToDo: create adapters that mocks a pdf and injected before test suite runs
#     # return {"document_id": "0127d144e58711eea57cc3a190d5388c", "chunk_index": 3}
#     return {"document_id": "cca2eca8018111ef9b1e0242ac120008", "chunk_index": 2}
#     # return {"document_id": "0127d144e58711eea57cc3a190d5388c", "chunk_index": 1}


# # return {"document_id": "0127d144e58711eea57cc3a190d5388c", "chunk_index": 0}


# @pytest.fixture
# def patient():
#     return "c70ee241-126a-719b-4b53-c48e5ae3716c"


# # @pytest.mark.asyncio
# # async def test_create_document_structured_data(commands, setup):
# #     document_id = setup.get("document_id")
# #     chunk_index = setup.get("chunk_index")
# #     result = await commands.handle_command(
# #         CreateDocumentChunkStructuredData(
# #             document_id=document_id, chunk_index=chunk_index, chunking_strategy=PDFParsingStrategy.UNSTRUCTURED
# #         )
# #     )
# #     assert result


# # # @pytest.mark.asyncio
# # # async def test_create_document_chunk_summary(commands, setup):
# # #     document_id = setup.get("document_id")
# # #     chunk_index = setup.get("chunk_index")
# # #     result = await commands.handle_command(CreateDocumentChunkSection(document_id=document_id, chunk_index=chunk_index))
# # #     assert result


# # @pytest.mark.asyncio
# # async def test_create_document_chunk_vector_index(commands, setup):
# #     document_id = setup.get("document_id")
# #     chunk_index = setup.get("chunk_index")
# #     sections = await commands.handle_command(GetDocumentChunkSectionsCommand(document_id=document_id, chunk_index=2))

# #     for section in sections:
# #         result = await commands.handle_command(
# #             CreateDocumentChunkSectionVectorIndex(document_id=document_id, chunk_index=chunk_index, section=section)
# #         )
# #     assert result


# # @pytest.mark.asyncio
# # async def test_search_vector_index(commands, setup, patient):
# #     document_id = setup.get("document_id")
# #     chunk_index = setup.get("chunk_index")
# #     search_term = "does patient take labetalol?"
# #     # Patient takes various medications including BETHANECHOL CHLORIDE, BIOTIN, IRBESARTAN, LABETALOL, MIRTAZAPINE, OXYCODONE-ACETAMINOPHEN, SPIRONOLACTONE and VITAMIN D3 with varying frequencies, routes and times
# #     contexts = await commands.handle_command(
# #         SearchDocumentContextCommand(distance_threshold=0.5, allow_list=[patient], search_terms=[search_term])
# #     )
# #     print(contexts)
# #     assert contexts != None


# @pytest.fixture
# def sample_sentences():
#     # return [
#     #     "patient takes Bethanechol chloride 1 10 MG Tablet orally 3 times daily for bladder",
#     #     "patient takes Biotin 1 MG capsule orally daily for supplement since 01/01/2022",
#     #     "patient takes 0.5 IRBESARTAN 150 MG TABLET orally daily for blood pressure since 01/01/2022",
#     # ]
#     sentences = [
#         {
#             "Medication/Dose": "BETHANECHOL CHLORIDE 10 MG TABLET (1 tablet)",
#             "Reason": "BLADDER",
#             "Frequency": "3 TIMES DAILY",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#         {
#             "Medication/Dose": "BIOTIN 1 MG CAPSULE (1 capsule)",
#             "Reason": "SUPPLEMENT",
#             "Frequency": "DAILY",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#         {
#             "Medication/Dose": "IRBESARTAN 150 MG TABLET (0.5 tablet)",
#             "Reason": "BLOOD PRESSURE",
#             "Frequency": "DAILY",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#         {
#             "Medication/Dose": "LABETALOL 100 MG TABLET (1 tablet)",
#             "Reason": "BLOOD PRESSURE",
#             "Frequency": "3 TIMES DAILY",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#         {
#             "Medication/Dose": "MIRTAZAPINE 15 MG TABLET (1 tablet)",
#             "Reason": "DEPRESSION",
#             "Frequency": "DAILY",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#         {
#             "Medication/Dose": "OXYCODONE-ACETAMINOPHEN 5 MG-325 MG TABLET (1 tablet)",
#             "Reason": "PAIN AS NEEDED, NOT TO EXCEED 3 GM PER DAY",
#             "Frequency": "AS NEEDED EVERY 4 HOURS/PRN",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#         {
#             "Medication/Dose": "SPIRONOLACTONE 25 MG TABLET (1 tablet)",
#             "Reason": "BLOOD PRESSURE",
#             "Frequency": "2 TIMES DAILY",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#         {
#             "Medication/Dose": "VITAMIN D3 25 MCG (1,000 UNIT) CAPSULE (1 capsule)",
#             "Reason": "SUPPLEMENT",
#             "Frequency": "DAILY",
#             "Route": "ORAL",
#             "Start Date/End Date": "01/10/2022",
#         },
#     ]

#     transformed_sentences = []
#     for sentence in sentences:
#         transformed_sentence = ""
#         for key, value in sentence.items():
#             transformed_sentence = transformed_sentence + f"{key}:{value},"
#         transformed_sentences.append(transformed_sentence)
#     return transformed_sentences


# # @pytest.mark.asyncio
# # async def test_vector_distance(sample_sentences):

# #     @inject
# #     def get_embeddings_adapter(embed_adapter: IEmbeddingsAdapter):
# #         return embed_adapter

# #     embed_adapter: IEmbeddingsAdapter = get_embeddings_adapter()
# #     patient_id = "dummy-test-patient"
# #     index = 0
# #     # for sentence in sample_sentences:
# #     #     await embed_adapter.upsert(VectorIndex(id=f"{index}", allow_list=[patient_id], data=sentence))
# #     #     index = index + 1

# #     results = await embed_adapter.search(
# #         allow_list=[patient_id], search_term=["what medications does patient take daily?"]
# #     )

# #     print(results)
