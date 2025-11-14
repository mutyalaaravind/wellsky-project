import pytest
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock, call
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from adapters.storage import StorageAdapter, get_storage_adapter, STORAGE_SINGLETON_ENABLE


class TestStorageAdapter:
    """Test suite for StorageAdapter class."""

    def setup_method(self):
        """Set up test fixtures for each test."""
        self.project_id = "test-project"
        self.bucket_name = "test-bucket"
        
    @patch('adapters.storage.storage.Client')
    def test_init_with_parameters(self, mock_storage_client):
        """Test StorageAdapter initialization with custom parameters."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        assert adapter.project_id == self.project_id
        assert adapter.bucket_name == self.bucket_name
        assert adapter.client == mock_client
        assert adapter.bucket == mock_bucket
        assert isinstance(adapter.executor, ThreadPoolExecutor)
        
        mock_storage_client.assert_called_once_with(project=self.project_id)
        mock_client.bucket.assert_called_once_with(self.bucket_name)

    @patch('adapters.storage.GCP_PROJECT_ID', 'default-project')
    @patch('adapters.storage.GCS_BUCKET_NAME', 'default-bucket')
    @patch('adapters.storage.storage.Client')
    def test_init_with_defaults(self, mock_storage_client):
        """Test StorageAdapter initialization with default parameters."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter()
        
        assert adapter.project_id == 'default-project'
        assert adapter.bucket_name == 'default-bucket'
        
        mock_storage_client.assert_called_once_with(project='default-project')
        mock_client.bucket.assert_called_once_with('default-bucket')

    @patch('adapters.storage.storage.Client')
    async def test_save_document_string_content(self, mock_storage_client):
        """Test saving a document with string content."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.name = "test/document.txt"
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Test data
        document_path = "test/document.txt"
        content = "Hello, World!"
        content_type = "text/plain"
        metadata = {"author": "test"}
        
        # Execute
        result = await adapter.save_document(
            document_path=document_path,
            content=content,
            content_type=content_type,
            metadata=metadata
        )
        
        # Verify
        expected_uri = f"gs://{self.bucket_name}/{document_path}"
        assert result == expected_uri
        
        mock_bucket.blob.assert_called_once_with(document_path)
        assert mock_blob.metadata == metadata
        mock_blob.upload_from_string.assert_called_once_with(content, content_type=content_type)

    @patch('adapters.storage.storage.Client')
    async def test_save_document_bytes_content(self, mock_storage_client):
        """Test saving a document with bytes content."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.name = "test/document.bin"
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Test data
        document_path = "test/document.bin"
        content = b"Binary content"
        content_type = "application/octet-stream"
        
        # Execute
        result = await adapter.save_document(
            document_path=document_path,
            content=content,
            content_type=content_type
        )
        
        # Verify
        expected_uri = f"gs://{self.bucket_name}/{document_path}"
        assert result == expected_uri
        
        mock_blob.upload_from_string.assert_called_once_with(content, content_type=content_type)

    @patch('adapters.storage.storage.Client')
    async def test_save_document_error(self, mock_storage_client):
        """Test save_document error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_string.side_effect = Exception("Upload failed")
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error saving document 'test.txt' to GCS: Upload failed"):
            await adapter.save_document("test.txt", "content")

    @patch('adapters.storage.storage.Client')
    async def test_save_document_from_file(self, mock_storage_client):
        """Test saving a document from a local file."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.name = "test/document.txt"
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Test data
        document_path = "test/document.txt"
        file_path = "/tmp/test.txt"
        content_type = "text/plain"
        metadata = {"source": "file"}
        
        # Execute
        result = await adapter.save_document_from_file(
            document_path=document_path,
            file_path=file_path,
            content_type=content_type,
            metadata=metadata
        )
        
        # Verify
        expected_uri = f"gs://{self.bucket_name}/{document_path}"
        assert result == expected_uri
        
        mock_bucket.blob.assert_called_once_with(document_path)
        assert mock_blob.metadata == metadata
        mock_blob.upload_from_filename.assert_called_once_with(file_path, content_type=content_type)

    @patch('adapters.storage.storage.Client')
    async def test_save_document_from_file_error(self, mock_storage_client):
        """Test save_document_from_file error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_filename.side_effect = Exception("File upload failed")
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error saving file '/tmp/test.txt' to GCS path 'test.txt': File upload failed"):
            await adapter.save_document_from_file("test.txt", "/tmp/test.txt")

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_success(self, mock_storage_client):
        """Test successful document retrieval."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b"Document content"
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document("test/document.txt")
        
        # Verify
        assert result == b"Document content"
        mock_bucket.blob.assert_called_once_with("test/document.txt")
        mock_blob.exists.assert_called_once()
        mock_blob.download_as_bytes.assert_called_once()

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_not_found(self, mock_storage_client):
        """Test document retrieval when document doesn't exist."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document("nonexistent.txt")
        
        # Verify
        assert result is None
        mock_blob.exists.assert_called_once()
        mock_blob.download_as_bytes.assert_not_called()

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_not_found_exception(self, mock_storage_client):
        """Test document retrieval when NotFound exception is raised."""
        from google.cloud.exceptions import NotFound
        
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.side_effect = NotFound("Not found")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document("test.txt")
        
        # Verify
        assert result is None

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_error(self, mock_storage_client):
        """Test retrieve_document error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.side_effect = Exception("Download failed")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error retrieving document 'test.txt' from GCS: Download failed"):
            await adapter.retrieve_document("test.txt")

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_as_string_success(self, mock_storage_client):
        """Test successful document retrieval as string."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b"Hello, World!"
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document_as_string("test.txt")
        
        # Verify
        assert result == "Hello, World!"

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_as_string_not_found(self, mock_storage_client):
        """Test document retrieval as string when document doesn't exist."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document_as_string("nonexistent.txt")
        
        # Verify
        assert result is None

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_as_string_encoding_error(self, mock_storage_client):
        """Test document retrieval as string with encoding error."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b'\xff\xfe'  # Invalid UTF-8
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error decoding document 'test.txt' with encoding 'utf-8'"):
            await adapter.retrieve_document_as_string("test.txt")

    @patch('adapters.storage.USE_JSON_SAFE_LOADS', True)
    @patch('adapters.storage.safe_loads')
    @patch('adapters.storage.storage.Client')
    async def test_retrieve_json_document_safe_loads(self, mock_storage_client, mock_safe_loads):
        """Test JSON document retrieval using safe_loads."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b'{"key": "value"}'
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        mock_safe_loads.return_value = {"key": "value"}
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_json_document("test.json")
        
        # Verify
        assert result == {"key": "value"}
        mock_safe_loads.assert_called_once_with('{"key": "value"}')

    @patch('adapters.storage.USE_JSON_SAFE_LOADS', False)
    @patch('adapters.storage.JsonUtil')
    @patch('adapters.storage.storage.Client')
    async def test_retrieve_json_document_json_util(self, mock_storage_client, mock_json_util):
        """Test JSON document retrieval using JsonUtil."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b'{"key": "value"}'
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        mock_json_util.loads.return_value = {"key": "value"}
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_json_document("test.json")
        
        # Verify
        assert result == {"key": "value"}
        mock_json_util.loads.assert_called_once_with('{"key": "value"}')

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_json_document_not_found(self, mock_storage_client):
        """Test JSON document retrieval when document doesn't exist."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_json_document("nonexistent.json")
        
        # Verify
        assert result is None

    @patch('adapters.storage.USE_JSON_SAFE_LOADS', False)
    @patch('adapters.storage.JsonUtil')
    @patch('adapters.storage.storage.Client')
    async def test_retrieve_json_document_error(self, mock_storage_client, mock_json_util):
        """Test JSON document retrieval error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b'{"key": "value"}'
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        mock_json_util.loads.side_effect = Exception("JSON parse error")
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error retrieving JSON document 'test.json' from GCS: JSON parse error"):
            await adapter.retrieve_json_document("test.json")

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_to_file_success(self, mock_storage_client):
        """Test successful document retrieval to file."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document_to_file("test.txt", "/tmp/test.txt")
        
        # Verify
        assert result is True
        mock_bucket.blob.assert_called_once_with("test.txt")
        mock_blob.exists.assert_called_once()
        mock_blob.download_to_filename.assert_called_once_with("/tmp/test.txt")

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_to_file_not_found(self, mock_storage_client):
        """Test document retrieval to file when document doesn't exist."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document_to_file("nonexistent.txt", "/tmp/test.txt")
        
        # Verify
        assert result is False
        mock_blob.download_to_filename.assert_not_called()

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_to_file_not_found_exception(self, mock_storage_client):
        """Test document retrieval to file when NotFound exception is raised."""
        from google.cloud.exceptions import NotFound
        
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.side_effect = NotFound("Not found")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.retrieve_document_to_file("test.txt", "/tmp/test.txt")
        
        # Verify
        assert result is False

    @patch('adapters.storage.storage.Client')
    async def test_retrieve_document_to_file_error(self, mock_storage_client):
        """Test retrieve_document_to_file error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.download_to_filename.side_effect = Exception("Download failed")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error retrieving document 'test.txt' from GCS to file '/tmp/test.txt': Download failed"):
            await adapter.retrieve_document_to_file("test.txt", "/tmp/test.txt")

    @patch('adapters.storage.storage.Client')
    async def test_delete_document_success(self, mock_storage_client):
        """Test successful document deletion."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.delete_document("test.txt")
        
        # Verify
        assert result is True
        mock_bucket.blob.assert_called_once_with("test.txt")
        mock_blob.exists.assert_called_once()
        mock_blob.delete.assert_called_once()

    @patch('adapters.storage.storage.Client')
    async def test_delete_document_not_found(self, mock_storage_client):
        """Test document deletion when document doesn't exist."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.delete_document("nonexistent.txt")
        
        # Verify
        assert result is False
        mock_blob.delete.assert_not_called()

    @patch('adapters.storage.storage.Client')
    async def test_delete_document_not_found_exception(self, mock_storage_client):
        """Test document deletion when NotFound exception is raised."""
        from google.cloud.exceptions import NotFound
        
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.side_effect = NotFound("Not found")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.delete_document("test.txt")
        
        # Verify
        assert result is False

    @patch('adapters.storage.storage.Client')
    async def test_delete_document_error(self, mock_storage_client):
        """Test delete_document error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = Exception("Delete failed")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error deleting document 'test.txt' from GCS: Delete failed"):
            await adapter.delete_document("test.txt")

    @patch('adapters.storage.storage.Client')
    async def test_document_exists_true(self, mock_storage_client):
        """Test document_exists when document exists."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.document_exists("test.txt")
        
        # Verify
        assert result is True
        mock_bucket.blob.assert_called_once_with("test.txt")
        mock_blob.exists.assert_called_once()

    @patch('adapters.storage.storage.Client')
    async def test_document_exists_false(self, mock_storage_client):
        """Test document_exists when document doesn't exist."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.document_exists("nonexistent.txt")
        
        # Verify
        assert result is False

    @patch('adapters.storage.storage.Client')
    async def test_document_exists_error(self, mock_storage_client):
        """Test document_exists error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.side_effect = Exception("Exists check failed")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error checking if document 'test.txt' exists in GCS: Exists check failed"):
            await adapter.document_exists("test.txt")

    @patch('adapters.storage.storage.Client')
    async def test_list_documents_success(self, mock_storage_client):
        """Test successful document listing."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        
        mock_blob1 = MagicMock()
        mock_blob1.name = "file1.txt"
        mock_blob2 = MagicMock()
        mock_blob2.name = "file2.txt"
        
        mock_client.bucket.return_value = mock_bucket
        mock_client.list_blobs.return_value = [mock_blob1, mock_blob2]
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.list_documents(prefix="test/", delimiter="/")
        
        # Verify
        assert result == ["file1.txt", "file2.txt"]
        mock_client.list_blobs.assert_called_once_with(mock_bucket, prefix="test/", delimiter="/")

    @patch('adapters.storage.storage.Client')
    async def test_list_documents_no_prefix(self, mock_storage_client):
        """Test document listing without prefix."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.name = "file.txt"
        
        mock_client.bucket.return_value = mock_bucket
        mock_client.list_blobs.return_value = [mock_blob]
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.list_documents()
        
        # Verify
        assert result == ["file.txt"]
        mock_client.list_blobs.assert_called_once_with(mock_bucket, prefix=None, delimiter=None)

    @patch('adapters.storage.storage.Client')
    async def test_list_documents_error(self, mock_storage_client):
        """Test list_documents error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        
        mock_client.bucket.return_value = mock_bucket
        mock_client.list_blobs.side_effect = Exception("List failed")
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error listing documents in GCS bucket 'test-bucket': List failed"):
            await adapter.list_documents()

    @patch('adapters.storage.storage.Client')
    async def test_get_document_metadata_success(self, mock_storage_client):
        """Test successful document metadata retrieval."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        # Configure blob metadata
        mock_blob.exists.return_value = True
        mock_blob.name = "test.txt"
        mock_blob.size = 1024
        mock_blob.content_type = "text/plain"
        mock_blob.time_created = None
        mock_blob.updated = None
        mock_blob.etag = "etag123"
        mock_blob.md5_hash = "md5hash"
        mock_blob.crc32c = "crc32c"
        mock_blob.metadata = {"custom": "value"}
        mock_blob.generation = 1
        mock_blob.metageneration = 1
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.get_document_metadata("test.txt")
        
        # Verify
        expected_metadata = {
            "name": "test.txt",
            "size": 1024,
            "content_type": "text/plain",
            "created": None,
            "updated": None,
            "etag": "etag123",
            "md5_hash": "md5hash",
            "crc32c": "crc32c",
            "metadata": {"custom": "value"},
            "generation": 1,
            "metageneration": 1
        }
        assert result == expected_metadata
        mock_bucket.blob.assert_called_once_with("test.txt")
        mock_blob.exists.assert_called_once()
        mock_blob.reload.assert_called_once()

    @patch('adapters.storage.storage.Client')
    async def test_get_document_metadata_not_found(self, mock_storage_client):
        """Test document metadata retrieval when document doesn't exist."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = False
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.get_document_metadata("nonexistent.txt")
        
        # Verify
        assert result is None
        mock_blob.reload.assert_not_called()

    @patch('adapters.storage.storage.Client')
    async def test_get_document_metadata_not_found_exception(self, mock_storage_client):
        """Test document metadata retrieval when NotFound exception is raised."""
        from google.cloud.exceptions import NotFound
        
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.side_effect = NotFound("Not found")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute
        result = await adapter.get_document_metadata("test.txt")
        
        # Verify
        assert result is None

    @patch('adapters.storage.storage.Client')
    async def test_get_document_metadata_error(self, mock_storage_client):
        """Test get_document_metadata error handling."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_blob.reload.side_effect = Exception("Metadata failed")
        
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_storage_client.return_value = mock_client
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Execute and verify exception
        with pytest.raises(Exception, match="Error getting metadata for document 'test.txt' in GCS: Metadata failed"):
            await adapter.get_document_metadata("test.txt")

    @patch('adapters.storage.asyncio.get_event_loop')
    @patch('adapters.storage.storage.Client')
    async def test_run_in_executor(self, mock_storage_client, mock_get_loop):
        """Test _run_in_executor method."""
        # Setup mocks
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_storage_client.return_value = mock_client
        
        mock_loop = MagicMock()
        mock_get_loop.return_value = mock_loop
        mock_loop.run_in_executor.return_value = asyncio.Future()
        mock_loop.run_in_executor.return_value.set_result("test_result")
        
        adapter = StorageAdapter(project_id=self.project_id, bucket_name=self.bucket_name)
        
        # Test function
        def test_func(arg1, arg2):
            return f"{arg1}_{arg2}"
        
        # Execute
        result = await adapter._run_in_executor(test_func, "hello", "world")
        
        # Verify
        assert result == "test_result"
        mock_loop.run_in_executor.assert_called_once_with(adapter.executor, test_func, "hello", "world")


class TestGetStorageAdapter:
    """Test suite for get_storage_adapter function."""

    @patch('adapters.storage.STORAGE_SINGLETON_ENABLE', True)
    @patch('adapters.storage.StorageAdapter')
    def test_get_storage_adapter_singleton_enabled_first_call(self, mock_storage_adapter):
        """Test get_storage_adapter with singleton enabled on first call."""
        # Reset the global singleton
        import adapters.storage
        adapters.storage._storage_adapter = None
        
        mock_adapter = MagicMock()
        mock_storage_adapter.return_value = mock_adapter
        
        # Execute
        result = get_storage_adapter()
        
        # Verify
        assert result == mock_adapter
        mock_storage_adapter.assert_called_once()

    @patch('adapters.storage.STORAGE_SINGLETON_ENABLE', True)
    @patch('adapters.storage.StorageAdapter')
    def test_get_storage_adapter_singleton_enabled_subsequent_call(self, mock_storage_adapter):
        """Test get_storage_adapter with singleton enabled on subsequent calls."""
        # Set up existing singleton
        import adapters.storage
        existing_adapter = MagicMock()
        adapters.storage._storage_adapter = existing_adapter
        
        # Execute
        result = get_storage_adapter()
        
        # Verify
        assert result == existing_adapter
        mock_storage_adapter.assert_not_called()

    @patch('adapters.storage.STORAGE_SINGLETON_ENABLE', False)
    @patch('adapters.storage.GCP_PROJECT_ID', 'test-project')
    @patch('adapters.storage.GCS_BUCKET_NAME', 'test-bucket')
    @patch('adapters.storage.StorageAdapter')
    def test_get_storage_adapter_singleton_disabled(self, mock_storage_adapter):
        """Test get_storage_adapter with singleton disabled."""
        mock_adapter = MagicMock()
        mock_storage_adapter.return_value = mock_adapter
        
        # Execute
        result = get_storage_adapter()
        
        # Verify
        assert result == mock_adapter
        mock_storage_adapter.assert_called_once_with(
            project_id='test-project',
            bucket_name='test-bucket'
        )
