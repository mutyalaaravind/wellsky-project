import pytest
from datetime import datetime, timezone

from viki_shared.utils.date_utils import now_utc


def test_now_utc():
    """Test now_utc returns current UTC datetime."""
    result = now_utc()
    
    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
    
    # Should be very close to current time (within 1 second)
    current = datetime.now(tz=timezone.utc)
    diff = abs((result - current).total_seconds())
    assert diff < 1.0