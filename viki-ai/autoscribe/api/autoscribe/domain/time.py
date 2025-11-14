from datetime import datetime, timezone


def now_utc():
    """
    Do NOT use datetime.utcnow! Use this function instead.

    Motivation:
    https://aaronoellis.com/articles/python-datetime-utcnow-considered-harmful
    """
    return datetime.now(tz=timezone.utc)
