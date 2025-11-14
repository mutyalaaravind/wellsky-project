import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.infrastructure.ports import IMessagingPort
from paperglass.log import getLogger
LOGGER = getLogger(__name__)

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from kink import inject

@inject
async def pubsub_test(messaging_port: IMessagingPort):
    await messaging_port.publish('orchestraction-extraction-topic', {"document_id": "23b51f5090f911ef9b3542004e494300", "document_operation_instance_id": "2518751890f911efaf6842004e494300", "document_operation_definition_id": "bda2081860f611ef91b73e3297f4bd07", "page_number": 1, "page_storage_uri": "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/1562ea9dbfa649f3b328a6cb332016f3/23b51f5090f911ef9b3542004e494300/pages/1.pdf", "event_type": "page_classification"},'medication_extraction')
    print('published message')
    
if __name__ == '__main__':
    import asyncio

    asyncio.run(pubsub_test())