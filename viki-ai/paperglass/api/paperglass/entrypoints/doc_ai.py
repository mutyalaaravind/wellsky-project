from typing import Dict, List, Optional
from pathlib import Path


#from google.cloud import documentai
from google.cloud import documentai_v1beta3 as documentai
from google.api_core.client_options import ClientOptions
from google.protobuf.json_format import MessageToDict

import asyncio

async def _process_document_with_document_parser(
        storage_uri: str,
        project_id: str = "viki-dev-app-wsky",
        location: str = "us",
        document_processor_id: str = "621fe166d8f57278",
        mime_type: str = 'application/pdf'
    ):
        client = documentai.DocumentProcessorServiceAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        )
        document_processor_version_path = client.processor_version_path(
            project_id, location, document_processor_id, "pretrained"
        )
        request = documentai.ProcessRequest(
            name=document_processor_version_path,
            # raw_document=documentai.RawDocument(content=image_content, mime_type=mime_type),
            gcs_document=documentai.GcsDocument(gcs_uri=storage_uri, mime_type=mime_type),
            # Only supported for Document OCR processor
            process_options={},  # type: documentai.ProcessOptions
        )
        
        result = await client.process_document(request=request)


        # Convert document protocol buffer to json
        document = MessageToDict(result.document._pb)

        print(document)
        return document

async def _process_document_with_layout_parser(
        storage_uri: str,
        project_id: str = "viki-dev-app-wsky",
        location: str = "us",
        layout_parser_id: str = "31d0f38c74a8a919",
        mime_type: str = 'application/pdf',
    ) -> Dict:
        client = documentai.DocumentProcessorServiceAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        )

        
        layout_processor_version_path = client.processor_path(
            project_id, location, layout_parser_id
        )

        request = documentai.ProcessRequest(
            name=layout_processor_version_path,
            gcs_document=documentai.GcsDocument(gcs_uri=storage_uri, mime_type=mime_type),
            # Only supported for Document OCR processor
            process_options={},  # type: documentai.ProcessOptions
        )

        result = await client.process_document(request=request)
        
        result = MessageToDict(result.document._pb)
        print(result)
        return result

if __name__ == "__main__":

    asyncio.run(_process_document_with_layout_parser(storage_uri='gs://viki-ai-provisional-dev/paperglass/documents/45678ba60c1a11ef8a8a0242ac120006/chunks/0.pdf'))

    # run with document parser to confirm the file is being read and parsed
    #asyncio.run(_process_document_with_document_parser(storage_uri='gs://viki-ai-provisional-dev/paperglass/documents/45678ba60c1a11ef8a8a0242ac120006/chunks/0.pdf'))