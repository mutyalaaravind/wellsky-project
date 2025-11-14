import time
from typing import List, Dict, Any
from io import BytesIO
import pypdf

from modules.imodule import IModule
from models.general import TaskParameters, TaskResults
from models.metric import Metric
from adapters.storage import StorageAdapter
from util.custom_logger import getLogger
from util.exception import exceptionToMap
import settings


LOGGER = getLogger(__name__)


class Page:
    """
    Represents a single page extracted from a PDF document.
    """
    def __init__(self, storage_uri: str, page_number: int, total_pages: int, run_id: str):
        self.storage_uri = storage_uri
        self.page_number = page_number
        self.total_pages = total_pages
        self.run_id = run_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Page object to dictionary."""
        return {
            "storage_uri": self.storage_uri,
            "page_number": self.page_number,
            "total_pages": self.total_pages,
            "run_id": self.run_id
        }


class SplitPages(IModule):
    """
    Module for splitting PDF documents into individual pages.
    
    This module retrieves a PDF document from Google Cloud Storage,
    splits it into individual pages, and saves each page back to GCS.
    """

    def __init__(self):
        super().__init__()
        self.storage_adapter = StorageAdapter()

    def _get_base_path(self, task_params: TaskParameters) -> str:
        """
        Build the base path for storing pages in GCS.
        
        Format: paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}
        """
        return f"paperglass/documents/{task_params.app_id}/{task_params.tenant_id}/{task_params.patient_id}/{task_params.document_id}"

    def _get_document_path(self, task_params: TaskParameters) -> str:
        """
        Build the document path for the source PDF in GCS.
        
        Format: paperglass/documents/{app_id}/{tenant_id}/{patient_id}/{document_id}.pdf
        """
        base_path = self._get_base_path(task_params)

        return f"{base_path}/document.pdf"

    async def run(self, task_params: TaskParameters) -> TaskResults:
        """
        Split a PDF document into individual pages.

        Args:
            task_params: Task parameters containing document information
            
        Returns:
            TaskResults with information about the split pages
        """
        start_time = time.time()
        
        extra = {
            "app_id": task_params.app_id,
            "tenant_id": task_params.tenant_id,
            "patient_id": task_params.patient_id,
            "document_id": task_params.document_id,
            "run_id": task_params.run_id,
            "module_name": "split_pages"
        }

        try:
            LOGGER.info("Starting PDF page splitting", extra=extra)

            # Build the document path from task parameters
            document_path = self._get_document_path(task_params)
            bucket_name = settings.GCS_BUCKET_NAME
            document_storage_uri = f"gs://{bucket_name}/{document_path}"
            
            extra.update({
                "document_storage_uri": document_storage_uri,
                "bucket_name": bucket_name,
                "document_path": document_path
            })

            LOGGER.debug("Retrieving PDF document from GCS", extra=extra)

            # Read the PDF document from GCS
            raw_data = await self.storage_adapter.retrieve_document(document_path)
            if raw_data is None:
                error_msg = f"Document not found at path: {document_path}"
                LOGGER.error(error_msg, extra=extra)
                return TaskResults(
                    success=False,
                    error_message=error_msg,
                    metadata=extra
                )

            # Parse the PDF
            try:
                pdf_reader = pypdf.PdfReader(BytesIO(raw_data))
                total_pages = len(pdf_reader.pages)
                
                extra.update({"total_pages": total_pages})
                LOGGER.info(f"PDF loaded successfully with {total_pages} pages", extra=extra)
                
            except Exception as e:
                error_msg = f"Failed to parse PDF document: {str(e)}"
                LOGGER.error(error_msg, extra=extra)
                return TaskResults(
                    success=False,
                    error_message=error_msg,
                    metadata=extra
                )

            # Split PDF into individual pages
            pages = []
            base_path = self._get_base_path(task_params)
            
            for i in range(total_pages):
                page_number = i + 1
                page_extra = {**extra, "page_number": page_number}
                
                try:
                    LOGGER.debug(f"Processing page {page_number} of {total_pages}", extra=page_extra)
                    
                    # Extract the page
                    page = pdf_reader.pages[i]
                    writer = pypdf.PdfWriter()
                    writer.add_page(page)
                    
                    # Convert to bytes
                    page_raw_data = BytesIO()
                    writer.write(page_raw_data)
                    page_raw_data.seek(0)
                    
                    # Build the page path
                    page_path = f"{base_path}/pages/{page_number}.pdf"
                    
                    # Save page to GCS
                    page_uri = await self.storage_adapter.save_document(
                        document_path=page_path,
                        content=page_raw_data.getvalue(),
                        content_type="application/pdf",
                        metadata={
                            "app_id": task_params.app_id,
                            "tenant_id": task_params.tenant_id,
                            "patient_id": task_params.patient_id,
                            "document_id": task_params.document_id,
                            "page_number": str(page_number),
                            "total_pages": str(total_pages),
                            "run_id": task_params.run_id,
                            "source_document": document_storage_uri
                        }
                    )
                    
                    # Create Page object
                    page_obj = Page(
                        storage_uri=page_uri,
                        page_number=page_number,
                        total_pages=total_pages,
                        run_id=task_params.run_id
                    )
                    pages.append(page_obj)
                    
                    # Emit page created metric for each individual page
                    page_end_time = time.time()
                    Metric.send(Metric.MetricType.DOCUMENT_PAGE_CREATED, {
                        "page_number": i,  # 0-based index like medication_extraction
                        "page_count": total_pages,
                        "elapsed_time": page_end_time - start_time,
                        "request": {
                            "app_id": task_params.app_id,
                            "tenant_id": task_params.tenant_id,
                            "patient_id": task_params.patient_id,
                            "document_id": task_params.document_id,
                            "run_id": task_params.run_id
                        }
                    })
                    
                    LOGGER.debug(f"Successfully saved page {page_number} to {page_uri}", extra=page_extra)
                    
                except Exception as e:
                    error_msg = f"Failed to process page {page_number}: {str(e)}"
                    LOGGER.error(error_msg, extra=page_extra)
                    return TaskResults(
                        success=False,
                        error_message=error_msg,
                        metadata=page_extra
                    )

            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Emit page split completion metric with total page count
            Metric.send(Metric.MetricType.DOCUMENT_PAGE_SPLIT, {
                "page_count": total_pages,
                "elapsed_time": elapsed_time,
                "request": {
                    "app_id": task_params.app_id,
                    "tenant_id": task_params.tenant_id,
                    "patient_id": task_params.patient_id,
                    "document_id": task_params.document_id,
                    "run_id": task_params.run_id
                }
            })
            
            # Prepare results
            results = {
                "pages": [page.to_dict() for page in pages],
                "total_pages": total_pages,
                "elapsed_time_seconds": elapsed_time,
                "base_path": base_path
            }
            
            final_extra = {
                **extra,
                "total_pages": total_pages,
                "elapsed_time_seconds": elapsed_time,
                "pages_created": len(pages)
            }
            
            LOGGER.info(f"Successfully split PDF into {total_pages} pages in {elapsed_time:.2f} seconds", extra=final_extra)
            
            return TaskResults(
                success=True,
                results=results,
                execution_time_ms=int(elapsed_time * 1000),
                metadata=final_extra
            )

        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            error_extra = {
                **extra,
                "error": exceptionToMap(e),
                "elapsed_time_seconds": elapsed_time
            }
            
            error_msg = f"Unexpected error during PDF splitting: {str(e)}"
            LOGGER.error(error_msg, extra=error_extra)
            
            return TaskResults(
                success=False,
                error_message=error_msg,
                execution_time_ms=int(elapsed_time * 1000),
                metadata=error_extra
            )
