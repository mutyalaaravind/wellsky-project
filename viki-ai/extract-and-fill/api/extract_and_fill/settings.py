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
GCS_BUCKET_NAME = getenv_or_die('GCS_BUCKET_NAME')
GCP_PROJECT_ID = getenv_or_die('GCP_PROJECT_ID')
GCP_PROJECT_LOCATION = getenv_or_die('GCP_PROJECT_LOCATION')
GCP_PROJECT_LOCATION_2 = getenv_or_die('GCP_PROJECT_LOCATION_2')
PINECONE_API_KEY = getenv_or_die('PINECONE_API_KEY')
PINECONE_ENV = getenv_or_die('PINECONE_ENV')
PINECONE_VECTOR_SEARCH_INDEX_NAME=getenv_or_die('PINECONE_VECTOR_SEARCH_INDEX_NAME')
GCP_VECTOR_SEARCH_INDEX_GCS_URI=getenv_or_die('GCP_VECTOR_SEARCH_INDEX_GCS_URI')
GCP_VECTOR_SEARCH_INDEX_NAME=getenv_or_die('GCP_VECTOR_SEARCH_INDEX_NAME')
GCP_VECTOR_SEARCH_INDEX_ENDPOINT=getenv_or_die('GCP_VECTOR_SEARCH_INDEX_ENDPOINT')
GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID=getenv_or_die('GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID')
VECTOR_SEARCH_PROVIDER=os.getenv('VECTOR_SEARCH_PROVIDER','vertexai') # pinecone or vertexai
FIRESTORE_DB=getenv_or_die('FIRESTORE_DB')