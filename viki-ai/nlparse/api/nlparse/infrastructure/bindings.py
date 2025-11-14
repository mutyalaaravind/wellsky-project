from kink import di

from nlparse.infrastructure.adapters.healthcare_nlp import HealthcareNLPAdapter
from nlparse.infrastructure.ports import IHealthcareNLPPort
from nlparse.settings import GCP_REGION, GCP_PROJECT_ID


di[IHealthcareNLPPort] = lambda _: HealthcareNLPAdapter(GCP_PROJECT_ID, GCP_REGION)
