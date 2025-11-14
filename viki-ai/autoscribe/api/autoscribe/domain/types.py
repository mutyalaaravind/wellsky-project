from datetime import datetime, timezone

from pydantic.validators import parse_datetime


class UTCDatetime(datetime):
    def __init__(self):
        pass

    @classmethod
    def __get_validators__(cls):
        yield parse_datetime
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not value.tzinfo:
            raise ValueError('Naive timestamps are not allowed')
        if value.tzinfo != timezone.utc:
            raise ValueError('Timestamp must be in UTC timezone')
        return value
