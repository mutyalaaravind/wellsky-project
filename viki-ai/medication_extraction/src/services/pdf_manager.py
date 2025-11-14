import time
from typing import List
from settings import GCS_BUCKET_NAME
from models import Document, DocumentOperationStep, Page
from adapters.storage import StorageAdapter
import pypdf
from io import BytesIO
from utils.custom_logger import getLogger
from model_metric import Metric

LOGGER = getLogger(__name__)

class PDFManager:
    
    def __init__(self):
        self.storage_adapter = StorageAdapter()
        self.bucket = GCS_BUCKET_NAME
       

    async def split_pages(self, document:Document, run_id:str)->List[Page]:
        pages = []
        base_path = await self.storage_adapter.get_base_path(document)
        # split pdf into pages
        raw_data = await self.storage_adapter.read_pdf(self.bucket, document.storage_uri.replace("gs://"+self.bucket+"/", ""))
        pdf_reader = pypdf.PdfReader(BytesIO(raw_data))
        
        start_time = time.time()
        for i in range(0, len(pdf_reader.pages), 1):
            page_number = i + 1
            page = pdf_reader.pages[i]
            writer = pypdf.PdfWriter()
            writer.add_page(page)
            page_raw_data = BytesIO()
            writer.write(page_raw_data)
            page_raw_data.seek(0)
            LOGGER.warning('Uploading page %d of document %s (%d pages)', page_number, document.document_id, len(pdf_reader.pages))
            uri = await self.storage_adapter.write_pdf(self.bucket, f"{base_path}/{page_number}.pdf",page_raw_data.getvalue())
            LOGGER.warning('page uri: %s', uri)
            pages.append(Page(storage_uri=uri, page_number=page_number, total_pages=len(pdf_reader.pages), run_id=run_id))

            end_time = time.time()    
            Metric.send(Metric.MetricType.DOCUMENT_PAGE_CREATED, {
                "page_number":i, 
                "page_count":len(pdf_reader.pages),
                "elapsed_time":end_time-start_time,
                "priority": document.priority.value,
                "request": {
                    "document": document.dict(), 
                    "run_id": run_id
                }
            })  # New metric logging statement

        end_time = time.time()
        LOGGER.info("Step::%s completed",
                    DocumentOperationStep.SPLIT_PAGES,
                    extra={
                            "page_count":len(pdf_reader.pages),
                            "elapsed_time":end_time-start_time,**document.dict()
                        }
                    )
        return pages
    
    