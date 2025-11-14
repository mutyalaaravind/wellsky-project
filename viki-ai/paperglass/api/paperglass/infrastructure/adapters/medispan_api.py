import time
import traceback
from typing import List

import settings

import requests

import google.auth

from google.auth import compute_engine
from google.auth import impersonated_credentials
from google.auth.transport.requests import Request

from paperglass.domain.utils.exception_utils import exceptionToMap
from ..ports import IMedispanPort

from ...log import getLogger
LOGGER = getLogger(__name__)

class MedispanAPIAdapter(IMedispanPort):
    def __init__(self, catalog: str = "medispan"):
        self.base_url = settings.MEDISPAN_API_BASE_URL
        self.catalog = catalog

    async def search_medications(self, search_term: str, similarity_threshold:float=0.7,top_k=10) -> List[dict]:
        
        url = f"{self.base_url}{self.catalog}/drugs/search"
        params = {"query": search_term, "similarity_threshold": similarity_threshold,"top_k": top_k}
        
        extra = {
            "base_url": self.base_url,
            "catalog": self.catalog,
            "search_term": search_term,
            "similarity_threshold": similarity_threshold,
            "top_k": top_k
        }
        try:
            header = get_id_token(impersonated_service_account=settings.SERVICE_ACCOUNT_EMAIL,target_audience=self.base_url.replace("/api/","")) #idtoken_from_metadata_server("https://ai-medispan-api-145042810266.us-east4.run.app") #self._get_headers()
            headers = {'Authorization': f'Bearer {header}'}

            extra.update({"http_request": {
                "method": "GET",
                "url": url,
                "headers": headers,
                "params": params
            }})

            LOGGER.debug("Performing Medispan search for medications with search term: %s", search_term, extra=extra)
            
            response = ""
            response = requests.get(
                url,
                params=params,
                headers = headers,
            )

            response.raise_for_status()
            response = response.json()
            
            extra.update({"http_response": response})
            LOGGER.debug("Response from Medispan search for medications with search term %s", search_term, extra=extra)

            medications = [
                self.Drug(
                        id = drug['id'],
                        brand_name="",
                        generic_name=drug['genericName'],
                        full_name=drug['nameDescription'],
                        route=drug['route'],
                        form=drug['dosageForm'],
                        strength=self.Drug.Strength(
                            value=drug['strength'],
                            unit=drug['strengthUnit'],
                        ),
                        package=None
                    ) for drug in response
            ]
            # medications = [self.Drug(
            #     id=str(medication['id']),
            #     brand_name=medication['nameDescription'],
            #     generic_name=medication['genericName'],
            #     route=medication['route'],
            #     strength=medication['strength'],
            #     strength=self.Drug.Strength(
            #         value=drug['strength'],
            #         unit=drug['strengthUnitOfMeasure'],
            #     ),
            #     StrengthUnitOfMeasure=medication['strengthUnit'],
            #     form=medication['dosageForm'],
                
            #     ) for medication in response]
            
            return medications
        except Exception as e:
            extra.update({"error": exceptionToMap(e)})
            LOGGER.error("Error occurred while searching medications from medispan api v2: %s", traceback.format_exc(), extra=extra)
            
            raise Exception(f"Error occurred while searching medications: {e}")
       

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
