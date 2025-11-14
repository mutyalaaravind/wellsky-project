import asyncio
from unittest.mock import patch
from adapters.pgvector_adapter import MedispanPgVectorAdapter
from adapters.firestore_vector_adapter import MedispanFirestoreVectorAdapter
from adapters.circuit_breaker_adapter import CircuitBreakerAdapter
from models import MedispanDrug


TEST_APP_ID = "test-app"
TEST_CATALOG = "medispan"
TEST_SEARCH_TERM = "aspirin"

async def run():
    print("HERE")
    adapter = MedispanFirestoreVectorAdapter(app_id=TEST_APP_ID, catalog=TEST_CATALOG)
    
    # Test basic search
    results = await adapter.search_medications(TEST_SEARCH_TERM)



def main():
    asyncio.run(run())
if __name__ == "__main__":
    main()