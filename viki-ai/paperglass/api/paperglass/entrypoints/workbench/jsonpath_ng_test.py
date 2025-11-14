import asyncio
import sys, os
import json
from collections import OrderedDict
from kink import inject
from jsonpath_ng import parse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.models_common import EntityFilter

from paperglass.usecases.commands import GetDocumentLogs
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import IPromptAdapter


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

@inject
async def do_something(commands: ICommandHandlingPort, prompt_adapter: IPromptAdapter):
    LOGGER.info("testing jsonpath_ng")

    filter_data = {
        "filterCriterion": [
            {
                "entity_name": "step_id",
                "values": ["MEDISPAN_MATCHING"]
            }
        ]
    }

    filter = EntityFilter(**filter_data)
    LOGGER.debug("Filter: %s", filter)

    app_id="007"
    tenant_id="54321"
    patient_id="77ab107aacfd4e2c93353c7444463098"
    document_id="1480d1eeb41e11ef905342004e494300"

    command = GetDocumentLogs(app_id=app_id, tenant_id=tenant_id, patient_id=patient_id, document_id=document_id, filter=filter)
    response = await commands.handle_command(command)
    
    entities = response["MEDICATION_EXTRACTION"]

    filtered_entities = filter.filter(entities)    
    LOGGER.debug("Filtered entity count: %s", len(filtered_entities))            
    LOGGER.debug("Filtered entities: %s", json.dumps([x.dict() for x in filtered_entities], indent=2, cls=DateTimeEncoder))

    for log in filtered_entities:
        ctx = log.context
        model = ctx["model"]["name"]
        for item in ctx["batch_context"]:
            prompt = item["prompt"]
            prompt_response = await prompt_adapter.multi_modal_predict_2(items=[prompt], model=model)

            LOGGER.debug("Prompt Response: %s", prompt_response)

async def run():    
    results = await do_something()

def main():    
    asyncio.run(run())

if __name__ == "__main__":   
    main()