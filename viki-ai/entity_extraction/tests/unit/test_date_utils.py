import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from util.date_utils import now_utc


class TestDateUtils:
    """Test suite for date_utils module."""

    def test_now_utc_returns_datetime_object(self):
        """Test that now_utc returns a datetime object."""
        result = now_utc()
        assert isinstance(result, datetime)

    def test_now_utc_returns_utc_timezone(self):
        """Test that now_utc returns a datetime with UTC timezone."""
        result = now_utc()
        assert result.tzinfo == timezone.utc

    def test_now_utc_returns_current_time(self):
        """Test that now_utc returns approximately the current time."""
        before = datetime.now(tz=timezone.utc)
        result = now_utc()
        after = datetime.now(tz=timezone.utc)
        
        # The result should be between before and after (within a reasonable time window)
        assert before <= result <= after

    @patch('util.date_utils.datetime')
    def test_now_utc_calls_datetime_now_with_utc_timezone(self, mock_datetime):
        """Test that now_utc calls datetime.now with UTC timezone."""
        mock_now = MagicMock()
        mock_datetime.now.return_value = mock_now
        mock_datetime.timezone = timezone
        
        result = now_utc()
        
        mock_datetime.now.assert_called_once_with(tz=timezone.utc)
        assert result == mock_now

    def test_now_utc_multiple_calls_different_times(self):
        """Test that multiple calls to now_utc return different times."""
        import time
        
        result1 = now_utc()
        time.sleep(0.001)  # Sleep for 1 millisecond
        result2 = now_utc()
        
        # The second call should return a time that's equal or later than the first
        assert result2 >= result1

    def test_now_utc_format_compatibility(self):
        """Test that the returned datetime can be formatted as expected by the docstring."""
        result = now_utc()
        
        # Test that we can format it as described in the docstring
        formatted = result.strftime('%Y-%m-%d %H:%M:%S')
        
        # Verify the format matches the expected pattern
        assert len(formatted) == 19  # 'YYYY-MM-DD HH:MM:SS' is 19 characters
        assert formatted[4] == '-'
        assert formatted[7] == '-'
        assert formatted[10] == ' '
        assert formatted[13] == ':'
        assert formatted[16] == ':'

    def test_now_utc_year_range(self):
        """Test that now_utc returns a reasonable year."""
        result = now_utc()
        current_year = datetime.now().year
        
        # Should be within a reasonable range of the current year
        assert current_year - 1 <= result.year <= current_year + 1

    def test_now_utc_microseconds_precision(self):
        """Test that now_utc includes microsecond precision."""
        result = now_utc()
        
        # Datetime objects should have microsecond precision
        assert hasattr(result, 'microsecond')
        assert 0 <= result.microsecond <= 999999
