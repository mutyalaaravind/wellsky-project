import pytest
import asyncio
from unittest.mock import patch
from adapters.pgvector_adapter import MedispanPgVectorAdapter
from adapters.firestore_vector_adapter import MedispanFirestoreVectorAdapter
from adapters.circuit_breaker_adapter import CircuitBreakerAdapter
from models import MedispanDrug

"""
Functional tests for vector search adapters.
These tests verify the adapters work correctly with actual services:
- AlloyDB with pgvector for vector search
- Firestore for vector search
- Circuit breaker with Singleton state management
"""

# Test data
TEST_APP_ID = "test-app"
TEST_CATALOG = "medispan"
TEST_SEARCH_TERM = "aspirin"
TEST_DOSAGE_FORM = "tablet"
TEST_ROUTE = "oral"

# Expected response structure
EXPECTED_DRUG_FIELDS = {
    "id",
    "NameDescription",
    "GenericName",
    "Route",
    "Strength",
    "StrengthUnitOfMeasure",
    "Dosage_Form"
}

@pytest.mark.asyncio
async def test_alloydb_search():
    """Test AlloyDB vector search adapter"""
    adapter = MedispanPgVectorAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    
    # Test basic search
    results = await adapter.search_medications(TEST_SEARCH_TERM)
    
    # Verify results
    assert results is not None
    assert len(results) > 0
    
    # Verify each result matches expected model
    for result in results:
        assert isinstance(result, MedispanDrug)
        # Check all required fields are present
        for field in EXPECTED_DRUG_FIELDS:
            assert hasattr(result, field)

    # Test search with filters
    filtered_results = await adapter.search_medications(
        TEST_SEARCH_TERM,
        dosage_form=TEST_DOSAGE_FORM,
        route=TEST_ROUTE
    )
    
    # Verify filtered results
    assert filtered_results is not None
    

@pytest.mark.asyncio
async def test_firestore_search():
    """Test Firestore vector search adapter"""
    adapter = MedispanFirestoreVectorAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    
    # Test basic search
    results = await adapter.search_medications(TEST_SEARCH_TERM)
    
    # Verify results
    assert results is not None
    assert len(results) > 0
    
    # # Verify each result matches expected model
    # for result in results:
    #     assert isinstance(result, MedispanDrug)
    #     # Check all required fields are present
    #     for field in EXPECTED_DRUG_FIELDS:
    #         assert hasattr(result, field)

    # # Test search with filters
    # filtered_results = await adapter.search_medications(
    #     TEST_SEARCH_TERM,
    #     dosage_form=TEST_DOSAGE_FORM,
    #     route=TEST_ROUTE
    # )
    
    # # Verify filtered results
    # assert filtered_results is not None
    # for result in filtered_results:
    #     assert isinstance(result, MedispanDrug)
    #     if result.Dosage_Form:
    #         assert TEST_DOSAGE_FORM.lower() in result.Dosage_Form.lower()
    #     if result.Route:
    #         assert TEST_ROUTE.lower() in result.Route.lower()

@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker adapter with fallback behavior"""
    adapter = CircuitBreakerAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    
    # Test normal operation (AlloyDB working)
    results = await adapter.search_medications(TEST_SEARCH_TERM)
    assert results is not None
    assert len(results) > 0
    
    # Verify results structure
    for result in results:
        assert isinstance(result, MedispanDrug)
        for field in EXPECTED_DRUG_FIELDS:
            assert hasattr(result, field)
    
    # Test fallback to Firestore when AlloyDB fails
    with patch.object(MedispanPgVectorAdapter, 'search_medications', side_effect=Exception("AlloyDB connection error")):
        fallback_results = await adapter.search_medications(TEST_SEARCH_TERM)
        
        # Verify fallback results
        assert fallback_results is not None
        assert len(fallback_results) > 0
        
        # Verify fallback results structure
        for result in fallback_results:
            assert isinstance(result, MedispanDrug)
            for field in EXPECTED_DRUG_FIELDS:
                assert hasattr(result, field)

@pytest.mark.asyncio
async def test_circuit_breaker_singleton():
    """Test circuit breaker Singleton pattern behavior"""
    # Create two instances with same app_id and catalog
    adapter1 = CircuitBreakerAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    adapter2 = CircuitBreakerAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    
    # Verify they are the same instance
    assert adapter1 is adapter2
    
    # Verify state is shared between instances
    with patch.object(MedispanPgVectorAdapter, 'search_medications', side_effect=Exception("AlloyDB error")):
        # This should set the failed state
        await adapter1.search_medications(TEST_SEARCH_TERM)
        
        # Verify adapter2 sees the same failed state
        is_failed, _ = adapter2._get_state()
        assert is_failed is True

@pytest.mark.asyncio
async def test_circuit_breaker_different_instances():
    """Test circuit breaker creates separate instances for different app_ids/catalogs"""
    adapter1 = CircuitBreakerAdapter(app_id="app1", catalog="catalog1")
    adapter2 = CircuitBreakerAdapter(app_id="app2", catalog="catalog1")
    adapter3 = CircuitBreakerAdapter(app_id="app1", catalog="catalog2")
    
    # Verify they are different instances
    assert adapter1 is not adapter2
    assert adapter1 is not adapter3
    assert adapter2 is not adapter3
    
    # Verify states are independent
    with patch.object(MedispanPgVectorAdapter, 'search_medications', side_effect=Exception("AlloyDB error")):
        await adapter1.search_medications(TEST_SEARCH_TERM)
        
        # Check states
        is_failed1, _ = adapter1._get_state()
        is_failed2, _ = adapter2._get_state()
        is_failed3, _ = adapter3._get_state()
        
        assert is_failed1 is True
        assert is_failed2 is False
        assert is_failed3 is False

@pytest.mark.asyncio
async def test_search_results_consistency():
    """Test consistency of search results across adapters"""
    alloydb_adapter = MedispanPgVectorAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    firestore_adapter = MedispanFirestoreVectorAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    
    # Get results from both adapters
    alloydb_results = await alloydb_adapter.search_medications(TEST_SEARCH_TERM)
    firestore_results = await firestore_adapter.search_medications(TEST_SEARCH_TERM)
    
    # Verify both adapters return results
    assert alloydb_results is not None
    assert firestore_results is not None
    
    # Verify result structures match
    assert len(alloydb_results) > 0
    assert len(firestore_results) > 0
    
    # Compare first result from each adapter to ensure consistent structure
    alloydb_first = alloydb_results[0]
    firestore_first = firestore_results[0]
    
    assert isinstance(alloydb_first, MedispanDrug)
    assert isinstance(firestore_first, MedispanDrug)
    
    # Verify all fields are present in both results
    for field in EXPECTED_DRUG_FIELDS:
        assert hasattr(alloydb_first, field)
        assert hasattr(firestore_first, field)
        # Verify field types match
        assert type(getattr(alloydb_first, field)) == type(getattr(firestore_first, field))
