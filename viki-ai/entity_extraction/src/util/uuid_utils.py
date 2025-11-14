import uuid
from util.date_utils import now_utc

def generate_id() -> str:
    """
    Generate a new UUID string.

    Returns:
        str: A new UUID string.
    """
    return str(uuid.uuid4().hex)

def generate_timeprefixed_id() -> str:
    """
    Generate a time-prefixed UUID string in the format YYYYMMddTHHmmss-UUID.
    
    Returns:
        str: A time-prefixed UUID string (e.g., "20241224T103229-a1b2c3d4e5f67890abcdef1234567890")
    """
    current_time = now_utc()
    date_prefix = current_time.strftime("%Y%m%dT%H%M%S")
    uuid_part = generate_id()
    return f"{date_prefix}-{uuid_part}"
