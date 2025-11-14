"""
Unit tests for AutoHeadersMiddleware.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.middleware.auto_headers import AutoHeadersMiddleware


class TestAutoHeadersMiddleware(unittest.TestCase):
    """Test cases for AutoHeadersMiddleware class."""

    def setUp(self):
        """Set up test fixtures."""
        self.middleware = AutoHeadersMiddleware(app=Mock())

    @pytest.mark.asyncio
    async def test_dispatch_adds_headers(self):
        """Test that dispatch adds required headers to response."""
        # Mock request
        request = Mock(spec=Request)
        
        # Mock response
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock call_next
        call_next = AsyncMock(return_value=response)
        
        with patch('src.middleware.auto_headers.settings') as mock_settings:
            mock_settings.VERSION = "1.0.0"
            mock_settings.STAGE = "test"
            mock_settings.DEBUG = True
            mock_settings.GCP_PROJECT_ID = "test-project"
            mock_settings.CLOUD_PROVIDER = "gcp"
            mock_settings.FIRESTORE_EMULATOR_HOST = None
            
            with patch('src.middleware.auto_headers.time.time', side_effect=[1000.0, 1000.1]):
                result = await self.middleware.dispatch(request, call_next)
                
                # Verify response is returned
                assert result == response
                
                # Verify headers are added
                assert response.headers["x-wsky-build"] == "1.0.0"
                assert response.headers["x-wsky-env"] == "test"
                assert response.headers["x-wsky-debug"] == "True"
                assert response.headers["x-wsky-project-id"] == "test-project"
                assert response.headers["x-wsky-cloud-provider"] == "gcp"
                assert "x-wsky-performance-elapsed-ms" in response.headers
                
                # Verify elapsed time calculation (100ms)
                elapsed_time = float(response.headers["x-wsky-performance-elapsed-ms"])
                assert elapsed_time == 100.0

    @pytest.mark.asyncio
    async def test_dispatch_with_firestore_emulator(self):
        """Test that dispatch adds firestore emulator header when enabled."""
        # Mock request
        request = Mock(spec=Request)
        
        # Mock response
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock call_next
        call_next = AsyncMock(return_value=response)
        
        with patch('src.middleware.auto_headers.settings') as mock_settings:
            mock_settings.VERSION = "1.0.0"
            mock_settings.STAGE = "development"
            mock_settings.DEBUG = False
            mock_settings.GCP_PROJECT_ID = "dev-project"
            mock_settings.CLOUD_PROVIDER = "gcp"
            mock_settings.FIRESTORE_EMULATOR_HOST = "localhost:8080"  # Emulator enabled
            
            with patch('src.middleware.auto_headers.time.time', side_effect=[2000.0, 2000.05]):
                result = await self.middleware.dispatch(request, call_next)
                
                # Verify response is returned
                assert result == response
                
                # Verify standard headers are added
                assert response.headers["x-wsky-build"] == "1.0.0"
                assert response.headers["x-wsky-env"] == "development"
                assert response.headers["x-wsky-debug"] == "False"
                assert response.headers["x-wsky-project-id"] == "dev-project"
                assert response.headers["x-wsky-cloud-provider"] == "gcp"
                
                # Verify firestore emulator header is added
                assert response.headers["x-wsky-firestore-emulator-enabled"] == "True"
                
                # Verify elapsed time calculation (50ms)
                elapsed_time = float(response.headers["x-wsky-performance-elapsed-ms"])
                assert elapsed_time == 50.0

    @pytest.mark.asyncio
    async def test_dispatch_without_firestore_emulator(self):
        """Test that dispatch does not add firestore emulator header when disabled."""
        # Mock request
        request = Mock(spec=Request)
        
        # Mock response
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock call_next
        call_next = AsyncMock(return_value=response)
        
        with patch('src.middleware.auto_headers.settings') as mock_settings:
            mock_settings.VERSION = "2.0.0"
            mock_settings.STAGE = "production"
            mock_settings.DEBUG = False
            mock_settings.GCP_PROJECT_ID = "prod-project"
            mock_settings.CLOUD_PROVIDER = "gcp"
            mock_settings.FIRESTORE_EMULATOR_HOST = None  # Emulator disabled
            
            with patch('src.middleware.auto_headers.time.time', side_effect=[3000.0, 3000.2]):
                result = await self.middleware.dispatch(request, call_next)
                
                # Verify response is returned
                assert result == response
                
                # Verify standard headers are added
                assert response.headers["x-wsky-build"] == "2.0.0"
                assert response.headers["x-wsky-env"] == "production"
                assert response.headers["x-wsky-debug"] == "False"
                assert response.headers["x-wsky-project-id"] == "prod-project"
                assert response.headers["x-wsky-cloud-provider"] == "gcp"
                
                # Verify firestore emulator header is NOT added
                assert "x-wsky-firestore-emulator-enabled" not in response.headers
                
                # Verify elapsed time calculation (200ms)
                elapsed_time = float(response.headers["x-wsky-performance-elapsed-ms"])
                assert elapsed_time == 200.0

    @pytest.mark.asyncio
    async def test_dispatch_time_calculation_precision(self):
        """Test elapsed time calculation precision."""
        # Mock request
        request = Mock(spec=Request)
        
        # Mock response
        response = Mock(spec=Response)
        response.headers = {}
        
        # Mock call_next
        call_next = AsyncMock(return_value=response)
        
        with patch('src.middleware.auto_headers.settings') as mock_settings:
            mock_settings.VERSION = "1.0.0"
            mock_settings.STAGE = "test"
            mock_settings.DEBUG = True
            mock_settings.GCP_PROJECT_ID = "test-project"
            mock_settings.CLOUD_PROVIDER = "gcp"
            mock_settings.FIRESTORE_EMULATOR_HOST = None
            
            # Test with precise timing (1.5567 seconds = 1556.7ms, should round to 1556.7)
            with patch('src.middleware.auto_headers.time.time', side_effect=[1000.0, 1001.5567]):
                result = await self.middleware.dispatch(request, call_next)
                
                elapsed_time = float(response.headers["x-wsky-performance-elapsed-ms"])
                assert elapsed_time == 1556.7

    def test_middleware_initialization(self):
        """Test middleware can be initialized."""
        app = Mock()
        middleware = AutoHeadersMiddleware(app=app)
        assert middleware.app == app