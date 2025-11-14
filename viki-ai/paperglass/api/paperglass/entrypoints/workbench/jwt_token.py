import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject

from google.cloud import firestore, storage  # type: ignore
from gcloud.aio.storage import Blob, Storage
import google.auth
from google.auth.transport import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.settings import GCP_FIRESTORE_DB
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.time import now_utc

from paperglass.usecases.configuration import get_config
from paperglass.interface.utils import validate_token_signature

from paperglass.domain.models import (
    MedispanDrug,
    DocumentOperationInstanceLog
)

from paperglass.infrastructure.ports import (
    IPromptAdapter,
    IQueryPort,
    IRelevancyFilterPort,
)


from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

import logging
from paperglass.log import getLogger
LOGGER = getLogger(__name__)

LOGGER.setLevel(logging.DEBUG)
logging.getLogger('google.auth._default').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('grpc._cython.cygrpc').setLevel(logging.INFO)
logging.getLogger('google.auth.transport.requests').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

async def do_something():
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InFWaXRxWlhsVC1OU3hGb3V5QW1rZHg3VTZSR2lORnBBOWg5ZUlna3dCbVEiLCJ0eXAiOiJKV1QifQ.eyJhcHBJZCI6Imx0YyIsInRlbmFudElkIjoiMDAyMzI5OkZDMzQiLCJwYXRpZW50SWQiOiIyODY2IiwidXNlcklkIjoiMG9hajF5OGNkN0xaQjB4Z0sxZDciLCJpc3MiOiJodHRwczovL21lZGV4dHJhY3QuZXhwZXJpZW5jZS5jYXJlL2FwaS92MS9tZWRleCIsImlhdCI6IjE3NTA2ODg0OTAiLCJleHAiOjE3NTA3MjQ0OTAsInN1YiI6IjBvYWoxeThjZDdMWkIweGdLMWQ3IiwibmJmIjoxNzUwNjg4NDkwfQ.nh9U0WPmv_x1Bcj0Yz8Xdb5pwCW8aa2ynDDULZAPwDNuVKB5h4p7uUaEYVCcxLhZIfYAW3xNEIrQ9IV8Uah-StBjXipeUdFOV4891j9DaNCilUR81ZWJxK2JNEiT7idQ53QG059JqKaI_H7mfLFEQdBTdtolAo685wzt4vKdsvag4fvTCN0_kmaydRDTe3bA3opwwkTESV-K08v1nulxzbqjBxacMRAeWCf4hdJv-F3BTxKhoZAC5-UmDlfHPab8KgkeiJqxBsP5WXYE5Vw9XT8JGm6Y2e59D9UQBQs7bjUFAtAqKOyD4z3-ZAb_OT4_xvD4d4y8vDasxVTqyzBB6w"
    app_id = "ltc"
    config = await get_config(app_id, "")

    LOGGER.info("Config loaded: %s", json.dumps(config.dict(), cls=DateTimeEncoder, indent=2))

    isValid = await validate_token_signature(token, config)
    if not isValid:
        LOGGER.error("Invalid token signature")
    else:
        LOGGER.info("Token signature is valid")
        
    return isValid


async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()