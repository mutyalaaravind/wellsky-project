from base64 import b64encode
from json import dumps
import requests

from models import Document
from settings import PAPERGLASS_API_URL

from utils.custom_logger import getLogger

LOGGER = getLogger(__name__)

class PaperglassAdapter:
    
    def __init__(self):
        pass
    
    def mktoken2(self, app_id, tenant_id, patient_id):
        return b64encode(dumps({'appId': app_id, 'tenantId': tenant_id, 'patientId': patient_id}).encode()).decode()
    
    async def update_status(self, document:Document, operation_type:str, status:str):
        url = PAPERGLASS_API_URL + "/document/update_status"
        payload = {
            "document_id": document.document_id,
            "operation_type": operation_type,
            "status": status,
            "orchestration_engine_version": "v4"
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.mktoken2(document.app_id, document.tenant_id, document.patient_id)
        }
        LOGGER.warning(f"Updating document status: {url} {payload}")
        response = requests.post(url, json=payload, headers=headers)

        return response