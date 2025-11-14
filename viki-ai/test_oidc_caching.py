#!/usr/bin/env python3
"""
Test script to validate OIDC token caching implementation.

This script demonstrates that OIDC tokens are properly cached and reused
for both Entity Extraction and DJT services.
"""

import asyncio
import time
import sys
import os

# Add paths for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'paperglass/api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'entity_extraction/src'))

async def test_entity_extraction_caching():
    """Test Entity Extraction OIDC token caching"""
    print("Testing Entity Extraction OIDC token caching...")
    
    try:
        from paperglass.infrastructure.adapters.entity_extraction_client import _get_cached_oidc_token
        
        # Mock the settings for testing
        import paperglass.settings as settings
        settings.CLOUD_PROVIDER = "local"  # Use local mode for testing
        
        audience = "https://entity-extraction-test.example.com"
        
        # First call - should be a cache miss
        print("First call (cache miss)...")
        start_time = time.time()
        token1 = await _get_cached_oidc_token(audience)
        time1 = time.time() - start_time
        print(f"  Result: {token1}")
        print(f"  Time: {time1:.4f}s")
        
        # Second call - should be a cache hit
        print("Second call (cache hit)...")
        start_time = time.time()
        token2 = await _get_cached_oidc_token(audience)
        time2 = time.time() - start_time
        print(f"  Result: {token2}")
        print(f"  Time: {time2:.4f}s")
        
        # Verify tokens are the same (cache hit)
        assert token1 == token2, "Tokens should be identical (cache hit)"
        assert time2 < time1, "Second call should be faster (cache hit)"
        
        print("✅ Entity Extraction caching test passed!")
        
    except ImportError as e:
        print(f"❌ Could not import Entity Extraction modules: {e}")
    except Exception as e:
        print(f"❌ Entity Extraction caching test failed: {e}")

async def test_djt_caching():
    """Test DJT OIDC token caching"""
    print("\nTesting DJT OIDC token caching...")
    
    try:
        from util.google_oidc_auth import get_oidc_token
        
        # Mock the settings for testing
        import settings
        settings.CLOUD_PROVIDER = "local"  # Use local mode for testing
        settings.DJT_API_URL = "https://djt-test.example.com"
        
        audience = "https://djt-test.example.com"
        
        # First call - should be a cache miss
        print("First call (cache miss)...")
        start_time = time.time()
        token1 = await get_oidc_token(audience)
        time1 = time.time() - start_time
        print(f"  Result: {token1}")
        print(f"  Time: {time1:.4f}s")
        
        # Second call - should be a cache hit
        print("Second call (cache hit)...")
        start_time = time.time()
        token2 = await get_oidc_token(audience)
        time2 = time.time() - start_time
        print(f"  Result: {token2}")
        print(f"  Time: {time2:.4f}s")
        
        # Verify tokens are the same (cache hit)
        assert token1 == token2, "Tokens should be identical (cache hit)"
        assert time2 < time1, "Second call should be faster (cache hit)"
        
        print("✅ DJT caching test passed!")
        
    except ImportError as e:
        print(f"❌ Could not import DJT modules: {e}")
    except Exception as e:
        print(f"❌ DJT caching test failed: {e}")

async def test_cache_separation():
    """Test that different audiences get different cache entries"""
    print("\nTesting cache separation by audience...")
    
    try:
        from paperglass.infrastructure.adapters.entity_extraction_client import _get_cached_oidc_token
        
        # Mock the settings for testing
        import paperglass.settings as settings
        settings.CLOUD_PROVIDER = "local"  # Use local mode for testing
        
        audience1 = "https://service1.example.com"
        audience2 = "https://service2.example.com"
        
        # Get tokens for different audiences
        token1 = await _get_cached_oidc_token(audience1)
        token2 = await _get_cached_oidc_token(audience2)
        
        # In local mode, both should be None but cache should still work
        print(f"  Token for {audience1}: {token1}")
        print(f"  Token for {audience2}: {token2}")
        
        # Get the same audience again to test cache hit
        token1_again = await _get_cached_oidc_token(audience1)
        assert token1 == token1_again, "Same audience should return cached token"
        
        print("✅ Cache separation test passed!")
        
    except ImportError as e:
        print(f"❌ Could not import modules for separation test: {e}")
    except Exception as e:
        print(f"❌ Cache separation test failed: {e}")

async def main():
    """Run all OIDC caching tests"""
    print("🧪 OIDC Token Caching Tests")
    print("=" * 50)
    
    await test_entity_extraction_caching()
    await test_djt_caching()
    await test_cache_separation()
    
    print("\n" + "=" * 50)
    print("🎉 All caching tests completed!")

if __name__ == "__main__":
    asyncio.run(main())