import asyncio
import datetime
import json
import sys,os
import time
from typing import Dict
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kink import inject
from paperglass.settings import (
    APPLICATION_INTEGRATION_TRIGGER_ID, 
    CLOUD_TASK_QUEUE_NAME, 
    INTEGRATION_PROJECT_NAME, 
    SELF_API, 
    SERVICE_ACCOUNT_EMAIL,    
)

from paperglass.infrastructure.ports import IMedispanPort, IRelevancyFilterPort

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

# Legacy one
@inject
async def search(searchTerm: str, medispan: IMedispanPort, medispan_filter: IRelevancyFilterPort):

    # ToDo: dont inject
    start_time = time.time()

    LOGGER.debug("executing legacy medispan search %s", searchTerm)
    LOGGER.debug("Searching for %s", searchTerm)
    
    results = await medispan.search_medications(searchTerm)

    LOGGER.debug("Medispan results: \n%s", results)

    filtered_results_tuple = await medispan_filter.filter(searchTerm, results, enable_llm=True)
    filtered_results, context = filtered_results_tuple

    ret = []
    for med in filtered_results:
        ret.append(json.loads(med.json()))
    LOGGER.debug("Number of results: %d", len(ret))
    LOGGER.debug("Number of filtered results: %d", len(filtered_results))
    LOGGER.debug("Search results for %s: \n%s", searchTerm, json.dumps(ret, indent=2))

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    LOGGER.debug("Elapsed time: %.2f ms", elapsed_time_ms)


DEFAULT_SEARCH_TERM = "Omeprazole Capsule Delayed Release 20 MG"

if __name__ == "__main__":
    searchTerm: str = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SEARCH_TERM    
    asyncio.run(search(searchTerm))    