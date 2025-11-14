import pytest
from unittest.mock import MagicMock, patch
from src.utils.steps_logger import log_step
from src.models import Document, Page


@pytest.fixture
def mock_document():
    doc = MagicMock(spec=Document)
    doc.dict.return_value = {
        "document_id": "test-doc",
        "document_name": "test.pdf"
    }
    return doc

@pytest.fixture
def mock_page():
    page = MagicMock(spec=Page)
    page.dict.return_value = {
        "page_number": 1,
        "page_text": "test content"
    }
    return page

@pytest.mark.asyncio
@patch('src.utils.steps_logger.LOGGER')
async def test_log_step_with_all_params(mock_logger, mock_document, mock_page):
    # Test logging with all parameters
    await log_step(
        step_id="test-step",
        document=mock_document,
        page=mock_page,
        run_id="test-run",
        recovery_attempt=1,
        status="success",
        error="test error"
    )
    
    mock_logger.info.assert_called_once()
    log_message = mock_logger.info.call_args[0][0]
    assert "STEP_LOGGER|STEP:test-step" in log_message
    assert "test-doc" in log_message
    assert "test.pdf" in log_message
    assert "page_number" in log_message
    assert "test error" in log_message
    assert "test-run" in log_message

@pytest.mark.asyncio
@patch('src.utils.steps_logger.LOGGER')
async def test_log_step_without_page(mock_logger, mock_document):
    # Test logging without page
    await log_step(
        step_id="test-step",
        document=mock_document,
        page=None,
        run_id="test-run",
        recovery_attempt=0,
        status="success"
    )
    
    mock_logger.info.assert_called_once()
    log_message = mock_logger.info.call_args[0][0]
    assert "STEP_LOGGER|STEP:test-step" in log_message
    assert "test-doc" in log_message
    assert "page_number" not in log_message

@pytest.mark.asyncio
@patch('src.utils.steps_logger.LOGGER')
async def test_log_step_without_document(mock_logger, mock_page):
    # Test logging without document
    await log_step(
        step_id="test-step",
        document=None,
        page=mock_page,
        run_id="test-run",
        recovery_attempt=0,
        status="success"
    )
    
    mock_logger.info.assert_called_once()
    log_message = mock_logger.info.call_args[0][0]
    assert "STEP_LOGGER|STEP:test-step" in log_message
    assert "test-doc" not in log_message
    assert "page_number" in log_message

@pytest.mark.asyncio
@patch('src.utils.steps_logger.LOGGER')
async def test_log_step_minimal(mock_logger):
    # Test logging with minimal parameters
    await log_step(
        step_id="test-step",
        document=None,
        page=None,
        run_id="test-run",
        recovery_attempt=0,
        status="success"
    )
    
    mock_logger.info.assert_called_once()
    log_message = mock_logger.info.call_args[0][0]
    assert "STEP_LOGGER|STEP:test-step" in log_message
    assert "run_id" in log_message
    assert "status" in log_message