import time
import traceback
from typing import List

import settings
from models import MedispanDrug
import requests

import google.auth

from google.auth import compute_engine

from utils.custom_logger import getLogger
LOGGER = getLogger(__name__)

class MedispanAPIAdapter:
    def __init__(self):
        self.base_url = settings.MEDISPAN_API_BASE_URL

    async def search_medications(self, search_term: str, similarity_threshold:float=0.7,top_k=10) -> List[MedispanDrug]:
        try:
            LOGGER.info("Performing Medispan search for medications with search term: %s", search_term)
            header = get_id_token(impersonated_service_account=settings.SERVICE_ACCOUNT_EMAIL,target_audience=self.base_url.replace("/api/","")) #idtoken_from_metadata_server("https://ai-medispan-api-145042810266.us-east4.run.app") #self._get_headers()
            #LOGGER.info(f"Header: {header}")
            response = ""
            response = requests.get(
                f"{self.base_url}drugs/search",
                params={"query": search_term, "similarity_threshold": similarity_threshold,"top_k": top_k},
                headers = {'Authorization': f'Bearer {header}'},
            )

            response.raise_for_status()
            response = response.json()
            medications = [MedispanDrug(
                id=str(medication['id']),
                NameDescription=medication['nameDescription'],
                GenericName=medication['genericName'],
                Route=medication['route'],
                Strength=medication['strength'],
                StrengthUnitOfMeasure=medication['strengthUnit'],
                Dosage_Form=medication['dosageForm']
                ) for medication in response]
            
            return medications
        except Exception as e:
            LOGGER.error("Error occurred while searching medications from medispan api v2: %s", traceback.format_exc())
            
            raise Exception(f"Error occurred while searching medications: {e}")
        

import google.auth
from google.auth import impersonated_credentials
from google.auth.transport.requests import Request

def get_id_token(impersonated_service_account, target_audience, scopes=None):
    """
    Gets an ID token for a service account by impersonating it.

    Args:
        impersonated_service_account (str): The email of the service account to impersonate.
        target_audience (str): The audience for the ID token (e.g., a Cloud Run service URL).
        scopes (list, optional): A list of scopes to request. Defaults to None.

    Returns:
        str: The ID token.
    """
    credentials, _ = google.auth.default()

    target_credentials = impersonated_credentials.Credentials(
        source_credentials=credentials,
        target_principal=impersonated_service_account,
        target_scopes=scopes,
    )

    id_creds = impersonated_credentials.IDTokenCredentials(
        target_credentials,
        target_audience=target_audience,
        include_email=True
    )
    request = Request()
    id_creds.refresh(request)
    return id_creds.token
