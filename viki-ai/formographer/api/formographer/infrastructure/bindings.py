from kink import di

from formographer.infrastructure.adapters.textbison import TextBisonQNAAdapter
from formographer.infrastructure.ports import IQNAPort
from formographer.settings import GCS_BUCKET_NAME, GCP_PROJECT_ID

di[IQNAPort] = lambda _: TextBisonQNAAdapter(project=GCP_PROJECT_ID)
