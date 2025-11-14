import asyncio
from functools import partial
import io
from typing import Optional

#import pandas as pd
from google.api_core import exceptions as google_exceptions
from gcloud.aio.storage import Blob, Storage
from google.cloud import storage 

from models import Document
from settings import GCP_PROJECT_ID
from utils.custom_logger import getLogger

LOGGER = getLogger(__name__)


class StorageAdapter:
    def __init__(self, storage_client: storage.Client = None):
        self.storage_client = storage_client if storage_client else storage.Client(project=GCP_PROJECT_ID)

    async def get_base_path(self, document:Document):
        return f"paperglass/documents/{document.app_id}/{document.tenant_id}/{document.patient_id}/{document.document_id}" 
    
    def validate_bucket(self, bucket_name: str) -> bool:
        """Validate if a bucket exists and is accessible"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.reload()
            return True
        except google_exceptions.NotFound:
            print(f"Bucket {bucket_name} not found")
            return False

    async def list_folder_entries(self, bucket_name, folder_path, extension):
        if not self.validate_bucket(bucket_name):
            return None
        bucket = self.storage_client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=folder_path)
        entries = [
            f"{blob.name}" for blob in blobs if blob.name.endswith(extension)]
        return entries

    async def read_text(self, bucket_name, file_path):
        """Read content of a file from storage"""
        try:
            if not self.validate_bucket(bucket_name):
                return None
            blob = self.storage_client.get_bucket(bucket_name).blob(file_path)
            return blob.download_as_text()
        except google_exceptions.NotFound:
            print(f"File {file_path} not found in bucket {bucket_name}")
            return None

    async def read_pdf(self, bucket_name, file_path):
        # Validate that the file is a PDF
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"The file '{file_path}' is not a PDF.")

        try:
            if not self.validate_bucket(bucket_name):
                return None
            blob = self.storage_client.get_bucket(bucket_name).blob(file_path)
            # blob_content = blob.download_as_bytes()
            # pdf_content = io.BytesIO(blob_content)
            # bucket = self.sync_client.bucket(self.bucket_name)
            # blob = bucket.blob(path)
            return await asyncio.get_event_loop().run_in_executor(None, blob.download_as_bytes)
            
        except google_exceptions.NotFound:
            print(f"File {file_path} not found in bucket {bucket_name}")
            return None

    async def write_text(self, bucket_name: str, path: str, content: str, content_type=None) -> bool:
        """Write content to a file in storage"""
        if not self.validate_bucket(bucket_name):
            return False

        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(path)
        # blob.upload_from_string(content)
        if not content_type:
            await asyncio.get_event_loop().run_in_executor(
                None,
                partial(blob.upload_from_string, content),
            )
        else:
            await asyncio.get_event_loop().run_in_executor(
                None,
                partial(blob.upload_from_string, content, content_type=content_type),
            )
        return True

    async def write_pdf(self, bucket_name, path, content: bytes) -> str:
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(path)
        await asyncio.get_event_loop().run_in_executor(
            None,
            partial(blob.upload_from_string, content, content_type="application/pdf"),
        )
        return self._gcs_uri(bucket_name, path)

    # def read_csv_df(self, bucket_name: str, blob_name: str) -> Optional[pd.DataFrame]:
    #     """Read CSV file from storage"""
    #     try:
    #         if not self.validate_bucket(bucket_name):
    #             return None

    #         bucket = self.storage_client.bucket(bucket_name)
    #         blob = bucket.blob(blob_name)
    #         content = blob.download_as_string()
    #         return pd.read_csv(pd.io.common.BytesIO(content))
    #     except google_exceptions.NotFound:
    #         print(f"File {blob_name} not found in bucket {bucket_name}")
    #         return None
    #     except Exception as e:
    #         print(
    #             f"Error reading file {blob_name} from bucket {bucket_name}: {str(e)}")
    #         return None

    # def write_csv_df(self, bucket_name: str, blob_name: str, df: pd.DataFrame) -> bool:
    #     """Write DataFrame to CSV in storage"""
    #     try:
    #         if not self.validate_bucket(bucket_name):
    #             print(f"Bucket {bucket_name} not found")
    #             return False

    #         bucket = self.storage_client.bucket(bucket_name)
    #         print(f"Saving csv as: {blob_name}")
    #         blob = bucket.blob(blob_name)

    #         # Convert DataFrame to CSV string
    #         csv_content = df.to_csv(index=False)

    #         # Upload to storage
    #         blob.upload_from_string(csv_content, content_type='text/csv')
    #         return True
    #     except Exception as e:
    #         print(
    #             f"Error writing file {blob_name} to bucket {bucket_name}: {str(e)}")
    #         return False

    def _gcs_uri(self,bucket_name,  path: str) -> str:
        return f"gs://{bucket_name}/{path}"
