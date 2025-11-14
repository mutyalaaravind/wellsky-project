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
    STAGE,
    MEDISPAN_CLIENT_ID,
    MEDISPAN_CLIENT_SECRET,
    MEDISPAN_VECTOR_SEARCH_REGION,
    MEDISPAN_LLM_SCORING_ENABLED
)

from paperglass.domain.models import MedispanDrug

from paperglass.infrastructure.ports import IPromptAdapter
from paperglass.infrastructure.ports import IMedispanPort
from paperglass.infrastructure.ports import IQueryPort
from paperglass.infrastructure.adapters.medispan_vector_search import MedispanVectorSearchAdapter
from paperglass.infrastructure.adapters.medispan_llm_filter import MedispanLLMFilterAdapter
from paperglass.infrastructure.adapters.google import FirestoreQueryAdapter

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry
bootstrap_opentelemetry(__name__)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

getLogger("aiocache").setLevel("ERROR")
getLogger("asyncio").setLevel("ERROR")
getLogger("google.auth").setLevel("ERROR")

#async def search(searchTerm: str, medispan: IMedispanPort, query: IQueryPort, medfilter: IRelevancyFilterPort ):

@inject
async def search(searchTerm: str,query:IQueryPort, prompt_adapter:IPromptAdapter,medispan_port:IMedispanPort):
    medispan = MedispanVectorSearchAdapter(client_id=MEDISPAN_CLIENT_ID, client_secret=MEDISPAN_CLIENT_SECRET, query=query)
    medfilter = MedispanLLMFilterAdapter(prompt=prompt_adapter, medispan_port=medispan_port, query=query)
    start_time = time.time()

    context = {}

    LOGGER.debug("%s Performing vector search for '%s'", STAGE, searchTerm)

    results = await medispan.search_medications(searchTerm)
    LOGGER.debug("Results for %s: %s", searchTerm, json.dumps([x.dict() for x in results], indent=2))


    """ medispan_id: str = "197011"
    LOGGER.debug("Getting Medispan data for %s", medispan_id)
    results = await query.get_medispan_by_id(medispan_id)

    del results["embedding"]
    LOGGER.debug("Results for %s: %s", medispan_id, json.dumps(results, indent=2))
    drug = MedispanDrug(**results)

    LOGGER.debug("Results for %s: %s", medispan_id, drug)
    LOGGER.debug("Results for %s: %s", medispan_id, json.dumps(drug.to_dict(), indent=2))
 """
    LOGGER.debug("Filtering results for %s", searchTerm)
    filtered_results = await medfilter.filter(searchTerm, results, enable_llm=True)
    LOGGER.debug("Filter tuple: %s", json.dumps(filtered_results.to_dict()))


    LOGGER.debug("Filtered results for %s: %s", searchTerm, json.dumps(filtered_results.to_dict(), indent=2))

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    LOGGER.debug("Elapsed time: %.2f ms", elapsed_time_ms)

DEFAULT_SEARCH_TERM = "Omeprazole Capsule Delayed Release 500 MG"

if __name__ == "__main__":
    searchTerm: str = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SEARCH_TERM
    asyncio.run(search(searchTerm))
