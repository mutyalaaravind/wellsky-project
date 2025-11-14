from datetime import datetime, timezone, timedelta
from google.protobuf import timestamp_pb2
import pytz

def now_utc():
    """
    Do NOT use datetime.utcnow! Use this function instead.

    Motivation:
    https://aaronoellis.com/articles/python-datetime-utcnow-considered-harmful
    """
    return datetime.now(tz=timezone.utc)


def defer_until_after_time(defer_time: str):
    time_toks = defer_time.split(":")
    hour = int(time_toks[0])
    minute = int(time_toks[1])

    current_date = now_utc()
    schedule_datetime = current_date.replace(hour=hour, minute=minute, second=0)

    if schedule_datetime < current_date:
        schedule_datetime += timedelta(days=1)

    return schedule_datetime


def get_ct_schedule_datetime(start_time: str, end_time: str):
    """
    Calculate schedule datetime based on CT timezone rules:
    - If current time is between 7PM to 5AM CT, execute immediately
    - Otherwise schedule between 7PM to 5AM CT
    
    Returns:
        datetime: Scheduled execution time in UTC
    """

    time_toks = start_time.split(":")
    hour = int(time_toks[0])
    minute = int(time_toks[1])

    central_tz = pytz.timezone('America/Chicago')
    now_central = datetime.now(central_tz)

    # Define today's 8 PM Central explicitly
    today_8pm = now_central.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # If the current time is between 8 PM and 6 AM, schedule immediately
    if now_central.hour >= int(start_time.split(":")[0]) or now_central.hour < int(end_time.split(":")[0]):
        schedule_time_central = now_central
    # Otherwise, if before 8 PM today, schedule explicitly for today 8 PM
    else:
        schedule_time_central = today_8pm

    # Convert the scheduled Central time to UTC for Cloud Tasks
    schedule_time_utc = schedule_time_central.astimezone(pytz.utc)
    
    return schedule_time_utc
