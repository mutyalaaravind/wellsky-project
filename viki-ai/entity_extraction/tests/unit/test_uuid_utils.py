import pytest
import os
import sys
import re
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Import test environment setup first
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import test_env

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from util.uuid_utils import generate_id, generate_timeprefixed_id


class TestUuidUtils:
    """Test suite for UUID utility functions."""

    def test_generate_id_returns_string(self):
        """Test that generate_id returns a string."""
        result = generate_id()
        assert isinstance(result, str)

    def test_generate_id_returns_hex_uuid(self):
        """Test that generate_id returns a valid hex UUID."""
        result = generate_id()
        # UUID4 hex should be 32 characters long (no hyphens)
        assert len(result) == 32
        # Should only contain hex characters
        assert re.match(r'^[0-9a-f]{32}$', result)

    def test_generate_id_unique_values(self):
        """Test that generate_id returns unique values on multiple calls."""
        id1 = generate_id()
        id2 = generate_id()
        id3 = generate_id()
        
        # All IDs should be different
        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

    def test_generate_id_format_consistency(self):
        """Test that generate_id consistently returns hex format."""
        for _ in range(10):
            result = generate_id()
            assert len(result) == 32
            assert re.match(r'^[0-9a-f]{32}$', result)

    @patch('util.uuid_utils.now_utc')
    @patch('util.uuid_utils.generate_id')
    def test_generate_timeprefixed_id_format(self, mock_generate_id, mock_now_utc):
        """Test that generate_timeprefixed_id returns correct format."""
        # Mock the current time
        mock_time = datetime(2024, 12, 24, 10, 32, 29, tzinfo=timezone.utc)
        mock_now_utc.return_value = mock_time
        
        # Mock the UUID generation
        mock_generate_id.return_value = "a1b2c3d4e5f67890abcdef1234567890"
        
        result = generate_timeprefixed_id()
        
        # Should be in format: YYYYMMddTHHmmss-UUID
        expected = "20241224T103229-a1b2c3d4e5f67890abcdef1234567890"
        assert result == expected

    @patch('util.uuid_utils.now_utc')
    @patch('util.uuid_utils.generate_id')
    def test_generate_timeprefixed_id_components(self, mock_generate_id, mock_now_utc):
        """Test that generate_timeprefixed_id correctly combines time and UUID."""
        # Mock the current time
        mock_time = datetime(2023, 5, 15, 14, 25, 37, tzinfo=timezone.utc)
        mock_now_utc.return_value = mock_time
        
        # Mock the UUID generation
        mock_uuid = "fedcba0987654321abcdef1234567890"
        mock_generate_id.return_value = mock_uuid
        
        result = generate_timeprefixed_id()
        
        # Verify the format
        assert result.startswith("20230515T142537-")
        assert result.endswith(mock_uuid)
        assert len(result) == 15 + 1 + 32  # timestamp + dash + uuid (YYYYMMddTHHmmss = 15 chars)

    @patch('util.uuid_utils.now_utc')
    def test_generate_timeprefixed_id_calls_dependencies(self, mock_now_utc):
        """Test that generate_timeprefixed_id calls required dependencies."""
        # Mock the current time
        mock_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        mock_now_utc.return_value = mock_time
        
        result = generate_timeprefixed_id()
        
        # Verify now_utc was called
        mock_now_utc.assert_called_once()
        
        # Verify the result has the correct structure
        parts = result.split('-')
        assert len(parts) == 2
        assert parts[0] == "20240101T000000"
        assert len(parts[1]) == 32

    def test_generate_timeprefixed_id_real_time(self):
        """Test generate_timeprefixed_id with real time (integration test)."""
        result = generate_timeprefixed_id()
        
        # Should match the expected format
        pattern = r'^\d{8}T\d{6}-[0-9a-f]{32}$'
        assert re.match(pattern, result)
        
        # Extract and validate timestamp part
        timestamp_part = result.split('-')[0]
        assert len(timestamp_part) == 15  # YYYYMMddTHHmmss
        
        # Extract and validate UUID part
        uuid_part = result.split('-')[1]
        assert len(uuid_part) == 32
        assert re.match(r'^[0-9a-f]{32}$', uuid_part)

    def test_generate_timeprefixed_id_unique_values(self):
        """Test that generate_timeprefixed_id returns unique values."""
        # Generate multiple IDs quickly
        ids = [generate_timeprefixed_id() for _ in range(5)]
        
        # All should be unique (UUID part should differ even if timestamp is same)
        assert len(set(ids)) == len(ids)

    @patch('util.uuid_utils.now_utc')
    def test_generate_timeprefixed_id_different_times(self, mock_now_utc):
        """Test generate_timeprefixed_id with different timestamps."""
        # Test with different times
        times_and_expected = [
            (datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc), "20241231T235959"),
            (datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc), "20200101T000000"),
            (datetime(2023, 7, 4, 12, 30, 45, tzinfo=timezone.utc), "20230704T123045"),
        ]
        
        for mock_time, expected_prefix in times_and_expected:
            mock_now_utc.return_value = mock_time
            result = generate_timeprefixed_id()
            assert result.startswith(expected_prefix + "-")

    def test_generate_timeprefixed_id_integration_with_generate_id(self):
        """Test that generate_timeprefixed_id properly integrates with generate_id."""
        result = generate_timeprefixed_id()
        
        # Extract UUID part
        uuid_part = result.split('-')[1]
        
        # Should be same format as generate_id output
        direct_uuid = generate_id()
        assert len(uuid_part) == len(direct_uuid)
        assert re.match(r'^[0-9a-f]{32}$', uuid_part)
