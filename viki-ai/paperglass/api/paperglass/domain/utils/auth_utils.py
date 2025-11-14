from base64 import b64encode
from json import dumps
import google.auth
from google.auth.transport import requests

import requests,aiohttp,json

from ...log import getLogger
LOGGER = getLogger(__name__)

class GCPAuth(object):
    _credentials = None

    def auth_token(self, force_refresh=False):
        if GCPAuth._credentials and GCPAuth._credentials.token and not force_refresh:
            LOGGER.info(f"Cached token {GCPAuth._credentials.token}")
            return GCPAuth._credentials.token

        # getting the credentials and project details for gcp project
        GCPAuth._credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # getting request object
        auth_req = google.auth.transport.requests.Request()

        GCPAuth._credentials.refresh(auth_req)  # refresh token

        LOGGER.info(f"New token : {GCPAuth._credentials.token}")

        if GCPAuth._credentials.valid:
            return GCPAuth._credentials.token
        else:
            raise Exception("GCP Auth failed")  # prints token
        
def get_token(app_id, tenant_id, patient_id):
    return b64encode(dumps({'appId': app_id, 'tenantId': tenant_id, 'patientId': patient_id}).encode()).decode()