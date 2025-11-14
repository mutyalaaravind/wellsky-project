from io import BytesIO
import json
from typing import List
from kink import inject
import pypdf

from paperglass.domain.models import (
    OperationMeta,
)
from paperglass.domain.values import (
    DocumentSettings, 
    EmbeddingChunkingStartegy, 
    EmbeddingStrategy, 
    ModelType, 
    PDFParsingStrategy, 
    Section
)
from paperglass.infrastructure.ports import (
    IPromptAdapter, 
    ISettingsPort
)


class PDFParsingService:

    async def get_chunked_content(self, pdf_parsing_strategy: PDFParsingStrategy, pdf_path: str,patient_id:str):
        if pdf_parsing_strategy == PDFParsingStrategy.MULTI_MODAL:
            return await MultiModalPDFParsingService().get_chunked_content(
                pdf_path, prompt_template="extract_structured_data.txt", patient_id=patient_id
            )
        elif pdf_parsing_strategy == PDFParsingStrategy.UNSTRUCTURED:
            return await UnstructuredPDFParsingService().get_chunked_content(pdf_path)
        else:
            raise ValueError("Invalid chunking strategy")


class MultiModalPDFParsingService:

    @inject
    async def get_chunked_content(self, pdf_path, prompt_template, patient_id,prompt_adapter: IPromptAdapter,settings_adapter: ISettingsPort):
        from vertexai.generative_models import GenerativeModel, Part, FinishReason
        import vertexai.preview.generative_models as generative_models

        opMeta:OperationMeta = OperationMeta(
            type = "adhoc",
            step = "MultiModalPDFParsingService.get_chunked_content",
        )

        with open(pdf_path, 'rb') as doc:
            doc_content = doc.read()
            pdf_reader = pypdf.PdfReader(BytesIO(doc_content))
            page_pdf_buffer = BytesIO()
            page_writer = pypdf.PdfWriter()
            page_writer.add_page(pdf_reader.pages[0])
            page_writer.write(page_pdf_buffer)
            page_pdf_buffer.seek(0)

            page_pdf_content = page_pdf_buffer.getvalue()

            prompt_text = await prompt_adapter.get_prompt_template(prompt_template)
            doc_settings:DocumentSettings = await settings_adapter.get_document_settings(patient_id)
            if doc_settings.page_text_extraction_model.model_type == ModelType.MULTI_MODAL:
                model = doc_settings.page_text_extraction_model.model
                result = await prompt_adapter.multi_modal_predict([prompt_text, (page_pdf_content, 'application/pdf')],model=model, metadata=opMeta.dict())
            else:
                result = await prompt_adapter.predict(prompt_text, model=doc_settings.page_text_extraction_model.model)
            # result = ""
            # for str in stream:
            #     if str and str.text:
            #         result = result + str.text

            return result


class UnstructuredPDFParsingService:

    @inject
    async def get_chunked_content(self, pdf_path):
        from typing import Any

        from pydantic import BaseModel
        from unstructured.partition.pdf import partition_pdf

        # Get elements
        raw_pdf_elements = partition_pdf(
            filename=pdf_path,
            # Unstructured first finds embedded image blocks
            extract_images_in_pdf=True,
            # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
            # Titles are any sub-section of the document
            infer_table_structure=True,
            # Post processing to aggregate text once we have the title
            chunking_strategy="by_title",
            # Chunking params to aggregate text blocks
            # Attempt to create a new chunk 3800 chars
            # Attempt to keep chunks > 2000 chars
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000,
            image_output_dir_path='/tmp/',
        )

        return [str(element) for element in raw_pdf_elements]


class EmbeddingChunkingService:

    async def get_chunks(
        self, large_text: str, embedding_chunking_strategy: EmbeddingChunkingStartegy
    ) -> List[Section]:
        # Embedding chunking service
        if embedding_chunking_strategy == EmbeddingChunkingStartegy.MULTI_MODAL:
            return await MultiModalChunkingService().get_chunks(large_text)

        if embedding_chunking_strategy == EmbeddingChunkingStartegy.MARKDOWN_TEXT_SPLITTER:
            return await MarkDownChunkingService().get_chunks(large_text)

        if embedding_chunking_strategy == EmbeddingChunkingStartegy.NLTK_TEXT_SPLITTER:
            return await NLTKChunkingService().get_chunks(large_text)


class NLTKChunkingService:

    @inject
    async def get_chunks(self, large_text: str):
        from langchain.text_splitter import NLTKTextSplitter

        nltk_splitter = NLTKTextSplitter()
        docs = nltk_splitter.split_text(large_text)
        sections = []
        index = 0
        for doc in docs:
            print(doc)
            sections.append(
                Section(
                    index=index,
                    name="Section" + str(index),
                    details=doc,
                    summary=None,
                    question=None,
                    embedding_chunk_strategy=EmbeddingChunkingStartegy.NLTK_TEXT_SPLITTER,
                )
            )
            index = index + 1
        return sections


class MarkDownChunkingService:

    @inject
    async def get_chunks(self, large_text: str):
        from langchain.text_splitter import MarkdownTextSplitter

        markdown_splitter = MarkdownTextSplitter(chunk_size=100, chunk_overlap=0)
        docs = markdown_splitter.create_documents([large_text])
        sections = []
        index = 0
        for doc in docs:
            print(doc)
            sections.append(
                Section(
                    index=index,
                    name=doc.metadata.get("name") or "Section" + str(index),
                    details=doc.page_content,
                    summary=None,
                    question=None,
                    embedding_chunk_strategy=EmbeddingChunkingStartegy.MARKDOWN_TEXT_SPLITTER,
                )
            )
            index = index + 1
        return sections


class MultiModalChunkingService:

    @inject
    async def get_chunks(self, large_text: str, prompt_adapter: IPromptAdapter):
        # Multimodal chunking service
        model = "gemini-1.0-pro-002"
        # model = "text-bison-32k@002"
        extract_sections_prompt = await prompt_adapter.get_prompt_template("extract_sections.txt")
        extract_sections_prompt = extract_sections_prompt.replace("<context></context>", large_text)

        opMeta:OperationMeta = OperationMeta(
            type = "adhoc",
            step = "MultiModalChunkingService.get_chunks",            
        )

        final_result = None
        result = ""
        # result = await prompt_adapter.predict(extract_sections_prompt, model)
        result = await prompt_adapter.multi_modal_predict([extract_sections_prompt], model, opMeta.dict())

        # async for str in stream:
        #     if str and str.text:
        #         result = result + str.text

        final_result = (
            result.replace("```json", "").replace("```", "").replace('## Extracted Sections:', '').replace("\n", "")
        )

        section_data_results = json.loads(final_result)

        index = 0
        sections = []
        for section in section_data_results:
            sections.append(
                Section(
                    index=index,
                    name=section.get("sectionName"),
                    details=json.dumps(section.get("sectionDetails")),
                    summary=section.get("summary") if section.get("summary") else "",
                    question=section.get("question") if section.get("question") else "",
                    embedding_chunk_strategy=EmbeddingChunkingStartegy.MULTI_MODAL,
                ),
            )
            index = index + 1

        return sections
