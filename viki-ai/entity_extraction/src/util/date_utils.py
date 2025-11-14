from datetime import datetime, timezone

def now_utc():
    """
    Returns the current UTC time as a string in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    
    return datetime.now(tz=timezone.utc)