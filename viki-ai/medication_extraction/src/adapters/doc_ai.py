from typing import Dict, List, Optional
from pathlib import Path
from math import atan2
from statistics import median

from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.protobuf.json_format import MessageToDict

from settings import GCP_DOCAI_DOC_PROCESSOR_ID, GCP_DOCAI_DOC_PROCESSOR_VERSION, GCP_LOCATION, GCP_PROJECT_ID

skip_rotation_identification = False

class DocumentAIAdapter:
    def __init__(
        self,
        project_id: str = GCP_PROJECT_ID,
        location: str = GCP_LOCATION,
        document_processor_id:str = GCP_DOCAI_DOC_PROCESSOR_ID,
        document_processor_version:str = GCP_DOCAI_DOC_PROCESSOR_VERSION
    ) -> Dict:
        self.location = location
        self.project_id = project_id
        # You must set the `api_endpoint` if you use a location other than "us".
        self.client = documentai.DocumentProcessorServiceAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        )

        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        # You must create a processor before running this sample.
        # self.hcc_processor_version_path = self.client.processor_version_path(
        #     project_id, location, hcc_processor_id, hcc_processor_version
        # )
        # self.summarizer_processor_version_path = self.client.processor_version_path(
        #     project_id, location, summarizer_processor_id, summarizer_processor_version
        # )

        self.document_processor_version_path = self.client.processor_version_path(
            project_id, location, document_processor_id, document_processor_version
        )

        # self.processor_map = {
        #     'hcc': self._process_document_with_hcc,
        #     'summarizer': self._process_document_with_summarizer,
        # }

    async def process_document(
        self,
        storage_uri: str,
        mime_type: str = 'application/pdf',
    ) -> List[Dict]:
        # if processor_type not in self.processor_map:
        #     raise ValueError(
        #         f'Invalid processor type: {processor_type}, must be one of {list(self.processor_map.keys())}'
        #     )

        #return await self.processor_map[processor_type](storage_uri, mime_type)
        return await self._process_document_with_document_parser(storage_uri, mime_type)

    # async def _process_document_with_hcc(
    #     self,
    #     storage_uri: str,
    #     mime_type: str = 'application/pdf',
    # ) -> List[Dict]:
    #     # Read the file into memory
    #     # with open(file_path, "rb") as image:
    #     #     image_content = image.read()

    #     # Configure the process request
    #     request = documentai.ProcessRequest(
    #         name=self.hcc_processor_version_path,
    #         # raw_document=documentai.RawDocument(content=image_content, mime_type=mime_type),
    #         gcs_document=documentai.GcsDocument(gcs_uri=storage_uri, mime_type=mime_type),
    #         # Only supported for Document OCR processor
    #         process_options={},  # type: documentai.ProcessOptions
    #     )

    #     result = await self.client.process_document(request=request)

    #     # print(result)
    #     #
    #     # import ipdb; ipdb.set_trace()

    #     # For a full list of `Document` object attributes, reference this page:
    #     # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document

    #     # Convert document protocol buffer to json
    #     document = MessageToDict(result.document._pb)

    #     # `document` has the following keys (as far as I can tell from the testing):
    #     # `text`, `pages`, `mimeType`, `uri`
    #     # There's one text that's shared across all pages, so we'll split document into sub-documents,
    #     # each having original text and page data
    #     text = document['text']
    #     pages = document['pages']
    #     sub_documents = []
    #     for page in pages:
    #         sub_documents.append({'text': text, 'page': page})

    #     # Original data:
    #     # {"text": "...", "pages": [{...}, {...}, {...}], "mimeType": "application/pdf", "uri": "gs://..."}
    #     # Now we have:
    #     # [
    #     #     {"text": "...", "page": {...}},
    #     #     {"text": "...", "page": {...}},
    #     #     {"text": "...", "page": {...}}
    #     # ]

    #     return sub_documents

    # async def _process_document_with_summarizer(
    #     self,
    #     storage_uri: str,
    #     mime_type: str = 'application/pdf',
    # ) -> Dict:
    #     request = documentai.ProcessRequest(
    #         name=self.summarizer_processor_version_path,
    #         gcs_document=documentai.GcsDocument(gcs_uri=storage_uri, mime_type=mime_type),
    #         # Only supported for Document OCR processor
    #         process_options={},  # type: documentai.ProcessOptions
    #     )

    #     result = await self.client.process_document(request=request)

    #     document = MessageToDict(result.document._pb)

    #     text = document['text']
    #     pages = document['pages']
    #     entities = document['entities']
    #     sub_documents = []
    #     for page in pages:
    #         sub_documents.append({'text': text, 'page': page, 'entities': entities})

    #     return sub_documents

    async def _process_document_with_layout_parser(
        self,
        storage_uri: str,
        mime_type: str = 'application/pdf',
    ) -> Dict:
        self.client = documentai.DocumentProcessorServiceAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
        )

        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        # You must create a processor before running this sample.
        # self.layout_processor_version_path = self.client.processor_version_path(
        #     self.project_id, self.location, "31d0f38c74a8a919", "pretrained"
        # )
        self.layout_processor_version_path = self.client.processor_path(
            self.project_id, self.location, "31d0f38c74a8a919"
        )

        request = documentai.ProcessRequest(
            name=self.layout_processor_version_path,
            gcs_document=documentai.GcsDocument(gcs_uri=storage_uri, mime_type=mime_type),
            # Only supported for Document OCR processor
            process_options={},  # type: documentai.ProcessOptions
        )

        result = await self.client.process_document(request=request)
        print(result)
        return MessageToDict(result.document._pb)

        text = document['text']
        pages = document['pages']
        entities = document['entities']
        sub_documents = []
        for page in pages:
            sub_documents.append({'text': text, 'page': page, 'entities': entities})

        return sub_documents

    async def _process_document_with_document_parser(
        self,
        storage_uri: str,
        mime_type: str = 'application/pdf'
    ):

        request = documentai.ProcessRequest(
            name=self.document_processor_version_path,
            # raw_document=documentai.RawDocument(content=image_content, mime_type=mime_type),
            gcs_document=documentai.GcsDocument(gcs_uri=storage_uri, mime_type=mime_type),
            # Only supported for Document OCR processor
            process_options={},  # type: documentai.ProcessOptions
        )

        result = await self.client.process_document(request=request)

        # print(result)
        #
        # import ipdb; ipdb.set_trace()

        # For a full list of `Document` object attributes, reference this page:
        # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document

        # Convert document protocol buffer to json
        document = MessageToDict(result.document._pb)

        # `document` has the following keys (as far as I can tell from the testing):
        # `text`, `pages`, `mimeType`, `uri`
        # There's one text that's shared across all pages, so we'll split document into sub-documents,
        # each having original text and page data
        text = document.get('text')
        pages = document.get('pages')
        sub_documents = []
        for page in pages:
            sub_documents.append({'text': text, 'page': page})

        # Original data:
        # {"text": "...", "pages": [{...}, {...}, {...}], "mimeType": "application/pdf", "uri": "gs://..."}
        # Now we have:
        # [
        #     {"text": "...", "page": {...}},
        #     {"text": "...", "page": {...}},
        #     {"text": "...", "page": {...}}
        # ]

        return sub_documents

    def identify_rotation(self, page) -> float:
        # Return page rotation in radians (positive angle = clockwise rotation)
        # E. g. if a page is rotated 45 degrees clockwise, it returns 0.7853981633974483
        if skip_rotation_identification:
            return 0.0
        angles = []
        if page.get('tokens'):
            for token in page.get('tokens'):
                try:
                    # print(token['layout']['orientation'])
                    vertices = token['layout']['boundingPoly']['vertices']
                    tl, tr = vertices[0], vertices[1]
                    if 'x' in tl and 'y' in tl and 'x' in tr and 'y' in tr:
                        x1, y1, x2, y2 = tl['x'], tl['y'], tr['x'], tr['y']
                        angle = atan2(y2 - y1, x2 - x1)
                        angles.append(angle)
                except Exception as exc:
                    print('Error while identifying rotation', exc)
                    continue
        # Return median value
        if not angles:
            return 0.0
        return median(angles)

if __name__ == '__main__':
    storage_uri = 'gs://viki-ai-provisional-dev/paperglass/documents/45678ba60c1a11ef8a8a0242ac120006/chunks/0.pdf'

    async def main():
        # await DocumentAIAdapter(
        #     'viki-dev-app-wsky',
        #     'us',
        #     '7359477870825dbb',
        #     'pretrained',
        #     'fcaac0296ec91273',
        #     'pretrained-foundation-model-v1.0-2023-08-22',
        # ).process_document_with_hcc(storage_uri)
        result = await DocumentAIAdapter(
            'viki-dev-app-wsky',
            'us',
            '31d0f38c74a8a919',
            'pretrained',
            '31d0f38c74a8a919',
            'pretrained-foundation-model-v1.0-2023-08-22',
            'projects/viki-dev-app-wsky/locations/us/processors/621fe166d8f57278',
            'process'
        )._process_document_with_layout_parser(storage_uri)
        print(result)

        # result =  await DocumentAIAdapter(
        #     'viki-dev-app-wsky',
        #     'us',
        #     '31d0f38c74a8a919',
        #     'pretrained',
        #     '31d0f38c74a8a919',
        #     'pretrained-foundation-model-v1.0-2023-08-22',
        #     '621fe166d8f57278',
        #     'pretrained'
        # )._process_document_with_document_parser(storage_uri)
        # print(result)

    import asyncio

    print(asyncio.run(main()))
