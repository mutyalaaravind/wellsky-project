import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import MagicMock, patch
from src.adapters.pgvector_adapter import MedispanPgVectorAdapter
from src import settings

@pytest.fixture
def mock_db_connection():
    with patch('psycopg2.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        yield mock_connect, mock_connection, mock_cursor

@pytest.fixture
def adapter():
    return MedispanPgVectorAdapter(app_id="test", catalog="medispan")

def test_init(adapter):
    assert adapter.app_id == "test"
    assert adapter.catalog == "medispan"
    assert adapter.connection_params == {
        "host": settings.PGVECTOR_HOST,
        "port": settings.PGVECTOR_PORT,
        "user": settings.PGVECTOR_USER,
        "password": settings.PGVECTOR_PASSWORD,
        "database": settings.PGVECTOR_DATABASE,
        "sslmode": settings.PGVECTOR_SSL_MODE,
        "connect_timeout": settings.PGVECTOR_CONNECTION_TIMEOUT
    }

def test_get_catalog_id(adapter):
    assert adapter._get_catalog_id("test") == "medispan"
    adapter.catalog = "merative"
    assert adapter._get_catalog_id("test") == "merative"

def test_get_tablename(adapter):
    assert adapter._get_tablename() == settings.PGVECTOR_TABLE_MEDISPAN
    adapter.catalog = "merative"
    assert adapter._get_tablename() == settings.PGVECTOR_TABLE_MERATIVE
    adapter.catalog = "unknown"
    assert adapter._get_tablename() == settings.PGVECTOR_TABLE_MEDISPAN

def test_get_functionname(adapter):
    assert adapter._get_functionname() == settings.PGVECTOR_SEARCH_FUNCTION_MEDISPAN
    adapter.catalog = "merative"
    assert adapter._get_functionname() == settings.PGVECTOR_SEARCH_FUNCTION_MERATIVE
    adapter.catalog = "unknown"
    assert adapter._get_functionname() == settings.PGVECTOR_SEARCH_FUNCTION_MEDISPAN

@pytest.mark.asyncio
async def test_keyword_search(adapter, mock_db_connection):
    _, _, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"id": "1", "namedescription": "Test Drug", "dosageform": "tablet", "route": "oral"}
    ]

    results = await adapter.keyword_search("test", "tablet", "oral")
    assert len(results) == 1
    assert results[0]["id"] == "1"

@pytest.mark.asyncio
async def test_search_by_vector(adapter, mock_db_connection):
    _, _, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {"id": "1", "namedescription": "Test Drug", "similarity": 0.9}
    ]

    embedding = [0.1, 0.2, 0.3]
    results = await adapter.search_by_vector(embedding, similarity_threshold=0.7, max_results=5)
    assert len(results) == 1
    assert results[0]["id"] == "1"

@pytest.mark.asyncio
async def test_execute_query(adapter, mock_db_connection):
    _, _, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [{"id": "1", "name": "test"}]

    results = await adapter.execute_query("SELECT * FROM table")
    assert len(results) == 1
    assert results[0]["id"] == "1"

@pytest.mark.asyncio
async def test_execute_query_error(adapter):
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.side_effect = Exception("Test error")
        with pytest.raises(Exception):
            await adapter.execute_query("SELECT * FROM table")

@pytest.mark.asyncio
async def test_search_medications_keyword_match(adapter, mock_db_connection):
    _, _, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {
            "id": "1",
            "namedescription": "Test Drug",
            "genericname": "Generic Test",
            "route": "oral",
            "strength": "10",
            "strengthunit": "mg",
            "dosageform": "tablet"
        }
    ]

    with patch('settings.PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH', False):
        results = await adapter.search_medications("test", "tablet", "oral")
        assert len(results) == 1
        assert str(results[0].id) == "1"
        assert results[0].NameDescription == "Test Drug"

@pytest.mark.asyncio
async def test_search_medications_vector_search(adapter, mock_db_connection):
    _, _, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {
            "id": "1",
            "namedescription": "Test Drug",
            "genericname": "Generic Test",
            "route": "oral",
            "strength": "10",
            "strengthunit": "mg",
            "dosageform": "tablet"
        }
    ]

    # Create mock embedding response
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1, 0.2, 0.3]
    mock_model = MagicMock()
    mock_model.get_embeddings.return_value = [mock_embedding]

    with (
        patch('settings.PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH', True),
        patch('adapters.gcp_embeddings.get_embeddings', return_value=[0.1, 0.2, 0.3]) as mock_get_embeddings
    ):
        
        results = await adapter.search_medications("test", "tablet", "oral")
        
        assert len(results) == 1
        assert str(results[0].id) == "1"
        assert results[0].NameDescription == "Test Drug"
        mock_get_embeddings.assert_called_once()