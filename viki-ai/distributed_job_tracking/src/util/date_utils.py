from datetime import datetime, timezone

def now_utc():
    """
    Returns the current UTC time as a datetime object.
    """
    
    return datetime.now(tz=timezone.utc)
