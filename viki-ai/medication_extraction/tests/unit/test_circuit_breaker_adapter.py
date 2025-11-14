import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from adapters.circuit_breaker_adapter import CircuitBreakerAdapter, RECOVERY_PROBE_INTERVAL
from utils.date import now_utc

@pytest.fixture
def mock_adapters():
    with patch('adapters.circuit_breaker_adapter.MedispanPgVectorAdapter') as mock_primary, \
         patch('adapters.circuit_breaker_adapter.MedispanFirestoreVectorAdapter') as mock_fallback:
        mock_primary.return_value.search_medications = AsyncMock()
        mock_fallback.return_value.search_medications = AsyncMock()
        yield mock_primary, mock_fallback

@pytest.fixture
def circuit_breaker(mock_adapters):
    # Reset the singleton state before each test
    CircuitBreakerAdapter._instances = {}
    CircuitBreakerAdapter._states = {}
    return CircuitBreakerAdapter("test_app", "test_catalog")

def test_singleton_pattern():
    """Test that CircuitBreakerAdapter maintains singleton instances per app_id:catalog pair"""
    adapter1 = CircuitBreakerAdapter("app1", "catalog1")
    adapter2 = CircuitBreakerAdapter("app1", "catalog1")
    adapter3 = CircuitBreakerAdapter("app2", "catalog1")
    
    assert adapter1 is adapter2  # Same app_id and catalog should return same instance
    assert adapter1 is not adapter3  # Different app_id should return different instance

def test_initialization(circuit_breaker, mock_adapters):
    """Test adapter initialization"""
    mock_primary, mock_fallback = mock_adapters
    
    assert circuit_breaker.app_id == "test_app"
    assert circuit_breaker.catalog == "test_catalog"
    assert circuit_breaker.instance_key == "test_app:test_catalog"
    assert mock_primary.called
    assert mock_fallback.called

@pytest.mark.asyncio
async def test_successful_primary_search(circuit_breaker, mock_adapters):
    """Test successful search using primary adapter"""
    mock_primary, _ = mock_adapters
    test_results = [MagicMock()]
    mock_primary.return_value.search_medications.return_value = test_results
    
    results = await circuit_breaker.search_medications("test_term")
    
    assert results == test_results
    mock_primary.return_value.search_medications.assert_called_once_with("test_term")
    assert not circuit_breaker._states[circuit_breaker.instance_key]["is_failed"]

@pytest.mark.asyncio
async def test_fallback_on_primary_failure(circuit_breaker, mock_adapters):
    """Test fallback to secondary adapter when primary fails"""
    mock_primary, mock_fallback = mock_adapters
    mock_primary.return_value.search_medications.side_effect = Exception("Primary failed")
    test_results = [MagicMock()]
    mock_fallback.return_value.search_medications.return_value = test_results
    
    results = await circuit_breaker.search_medications("test_term")
    
    assert results == test_results
    mock_primary.return_value.search_medications.assert_called_once()
    mock_fallback.return_value.search_medications.assert_called_once()
    assert circuit_breaker._states[circuit_breaker.instance_key]["is_failed"]

@pytest.mark.asyncio
async def test_recovery_probe_interval(circuit_breaker, mock_adapters):
    """Test that circuit breaker attempts recovery after interval"""
    mock_primary, mock_fallback = mock_adapters
    
    # First, make it fail
    mock_primary.return_value.search_medications.side_effect = Exception("Primary failed")
    await circuit_breaker.search_medications("test_term")
    assert circuit_breaker._states[circuit_breaker.instance_key]["is_failed"]
    
    # Set last_failure to be older than recovery interval
    old_time = now_utc() - RECOVERY_PROBE_INTERVAL - timedelta(seconds=1)
    circuit_breaker._set_state(True, old_time)
    
    # Make primary succeed this time
    mock_primary.return_value.search_medications.side_effect = None
    mock_primary.return_value.search_medications.return_value = [MagicMock()]
    
    # Should try primary again and succeed
    await circuit_breaker.search_medications("test_term")
    assert not circuit_breaker._states[circuit_breaker.instance_key]["is_failed"]
    assert mock_primary.return_value.search_medications.call_count == 2

@pytest.mark.asyncio
async def test_direct_fallback_when_failed(circuit_breaker, mock_adapters):
    """Test that adapter goes directly to fallback when in failed state"""
    mock_primary, mock_fallback = mock_adapters
    
    # Set failed state
    circuit_breaker._set_state(True, now_utc())
    
    # Should go directly to fallback
    await circuit_breaker.search_medications("test_term")
    
    mock_primary.return_value.search_medications.assert_not_called()
    mock_fallback.return_value.search_medications.assert_called_once()