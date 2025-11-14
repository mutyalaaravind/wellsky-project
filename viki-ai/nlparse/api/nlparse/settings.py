import os


def getenv_or_die(key: str) -> str:
    """
    >>> getenv_or_die('DEBUG')
    'false'
    >>> import pytest
    >>> with pytest.raises(ValueError):
    ...     getenv_or_die('SOME_UNKNOWN_ENV_VARIABLE')
    """
    value = os.getenv(key)
    if value is None:  # pragma: no cover
        raise ValueError(f'{key} is missing in environment')

    return value


def to_bool(value: str) -> bool:
    return value is not None and value.lower() in ('1', 'y', 'yes', 't', 'true', 'on')


VERSION = getenv_or_die('VERSION')
SERVICE = getenv_or_die('SERVICE')
STAGE = getenv_or_die('STAGE')
DEBUG = to_bool(os.getenv('DEBUG'))
GCP_PROJECT_ID = getenv_or_die('GCP_PROJECT_ID')
GCP_REGION = getenv_or_die('GCP_REGION')

# OKTA_DISABLE = to_bool(os.getenv('OKTA_DISABLE'))
# OKTA_ISSUER = getenv_or_die('OKTA_ISSUER')
# OKTA_AUDIENCE = getenv_or_die('OKTA_AUDIENCE')
# OKTA_SCOPE = getenv_or_die('OKTA_SCOPE')
