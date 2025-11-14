import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from jobs import DocumentJob
from models import Document, Page
from utils.date import now_utc

@pytest.fixture
def mock_document():
    return Document(
        app_id="test-app",
        tenant_id="test-tenant",
        patient_id="test-patient",
        document_id="test-doc",
        storage_uri="gs://test-bucket/test.pdf",
        created_at=now_utc(),
        priority="default"  # Changed from 'LOW' to 'default'
    )

@pytest.fixture
def mock_page():
    return Page(
        page_number=1,
        total_pages=2,
        run_id="test-run",
        storage_uri="gs://test-bucket/test/1.pdf"
    )

@pytest.fixture
def document_job():
    with patch('jobs.PDFManager') as mock_pdf_manager, \
         patch('jobs.GooglePubSubAdapter') as mock_pubsub, \
         patch('jobs.StorageAdapter') as mock_storage, \
         patch('jobs.PaperglassAdapter') as mock_paperglass, \
         patch('jobs.CloudTaskAdapter') as mock_cloud_task:

        mock_pdf = MagicMock()
        mock_pdf.split_pages = AsyncMock()
        mock_pdf_manager.return_value = mock_pdf

        mock_pub = MagicMock()
        mock_pub.publish = AsyncMock()
        mock_pubsub.return_value = mock_pub

        mock_store = MagicMock()
        mock_store.get_base_path = AsyncMock(return_value="test/path")
        mock_store.list_folder_entries = AsyncMock()
        mock_storage.return_value = mock_store

        mock_paper = MagicMock()
        mock_paper.update_status = AsyncMock()
        mock_paperglass.return_value = mock_paper

        mock_task = MagicMock()
        mock_task.create_task = AsyncMock()
        mock_cloud_task.return_value = mock_task

        job = DocumentJob()
        job.pdf_manager = mock_pdf
        job.pubsub_adapter = mock_pub
        job.storage_adapter = mock_store
        job.paperglass_adapter = mock_paper
        job.cloud_task_adapter = mock_task
        return job

@pytest.mark.asyncio
async def test_split_pages(document_job, mock_document):
    # Arrange
    mock_pages = [
        Page(page_number=1, total_pages=2, run_id="test-run", storage_uri="gs://bucket/1.pdf"),
        Page(page_number=2, total_pages=2, run_id="test-run", storage_uri="gs://bucket/2.pdf")
    ]
    document_job.pdf_manager.split_pages.return_value = mock_pages

    # Act
    result = await document_job.split_pages(mock_document, "test-run", "2025-01-01T00:00:00Z")

    # Assert
    document_job.pdf_manager.split_pages.assert_called_once_with(mock_document, "test-run")
    assert result == mock_pages

@pytest.mark.asyncio
async def test_status_check_complete(document_job, mock_document, mock_page):
    # Arrange
    document_job.storage_adapter.list_folder_entries.return_value = ["file1.json", "file2.json"]

    # Act
    result = await document_job.status_check(mock_document, mock_page)

    # Assert
    assert result == True
    document_job.storage_adapter.list_folder_entries.assert_called_once()

@pytest.mark.asyncio
async def test_status_check_incomplete(document_job, mock_document, mock_page):
    # Arrange
    document_job.storage_adapter.list_folder_entries.return_value = ["file1.json"]

    # Act
    result = await document_job.status_check(mock_document, mock_page)

    # Assert
    assert result == False
    document_job.storage_adapter.list_folder_entries.assert_called_once()

@pytest.mark.asyncio
async def test_mktoken2(document_job):
    # Act
    result = document_job._mktoken2("app1", "tenant1", "patient1")

    # Assert
    assert isinstance(result, str)
    assert len(result) > 0