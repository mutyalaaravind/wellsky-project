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

from paperglass.domain.models import (
    MedispanDrug,
    DocumentOperationInstanceLog
)
from paperglass.domain.values import (
    OrchestrationPriority
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

LOGGER.setLevel(logging.INFO)
logging.getLogger('google.auth._default').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache.serializers').setLevel(logging.INFO)
logging.getLogger('aiocache').setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
logging.getLogger('grpc._cython.cygrpc').setLevel(logging.INFO)
logging.getLogger('google.auth.transport.requests').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)


def extract_data(data):
    o = {
        "type": data["metadata"]["type"],
        "step": data["metadata"]["step"],
        "page_number": data["metadata"]["page_number"],
        "iteration": data["metadata"]["iteration"],
        "elapsed_time": data["prompt_stats"]["elapsed_time"],
        "model": data["model"],
        "input": data["input_prompt"],
        "output": data["output"],
    }

    return o

def create_key(step_id, page_number, iteration):
    formatted_page_number = str(page_number).zfill(2)
    formatted_iteration = str(iteration).zfill(2)
    return f"{step_id}::{formatted_page_number}::{formatted_iteration}"

# Run once or in a loop based on mode provided
async def generate_mock_data():

    document_id = "880839ae9c6311ef811d42004e494300"

    client = firestore.AsyncClient(database=GCP_FIRESTORE_DB)
    log_coll = client.collection("paperglass_prompt_audit_log")

    query = log_coll.where("metadata.document_id","==",document_id)
    doc_list = await query.get()
    docs = [doc.to_dict() for doc in doc_list]

    LOGGER.debug("Found %s documents", len(docs))

    data = {}
    for doc in docs:
        step_id = doc["metadata"]["step"]
        page_number = doc["metadata"]["page_number"]
        iteration = doc["metadata"]["iteration"]

        key = create_key(step_id, page_number, iteration)

        data[key] = extract_data(doc)

    
    sorted_data = OrderedDict(sorted(data.items()))

    output_file_path = "/tmp/output.json"
    with open(output_file_path, "w") as output_file:
        json.dump(sorted_data, output_file, indent=2)

@inject()
async def test(prompt: IPromptAdapter):
    PROMPT = """                        Please study this context:# Document: 3b38575ba13e11efaa3a00155dd9de4c, page: 1OXYCODONE HCL (IR) 5 MG TABLETCYCLOBENZAPRIN 5 MG TABLETACETAMINOPHEN 500 MG TABLETTake 1 to 2 tablets by mouth every 4 to 6 hours as needed for pain.Take 1 tablet by mouth three times a day as needed for muscle spasms.Take 2 tablets by mouth every 6 hours.MAX DAILY DOSE: 12 TABLETMFR: KVK-TECH, INC.MFR: KVK-TECH, INC.MFR: TIME-CAP LABS                        please extract medications as array of JSON with keys as name, strength,dosage, route, form, discontinued_date, frequency, start_date, end_date, instructions,explanation, document_reference and page_number.                         Please do not include any markup other than JSON.                        Please format start_date and end_date as mm/dd/yyyy. """
    metadata = {
        "step": "CLASSIFICATION",
        "page_number": 1,
        "iteration": 0,
        "elapsed_time": 1.79215
    }
    results = await prompt.multi_modal_predict_2([PROMPT], model="gemini-1.5-flash-001", metadata=metadata)
    #results = await prompt.predict("test", "gemini-1.5-pro-001", metadata=metadata)

    LOGGER.info(results)

@inject
async def medispan_match_test(query: IQueryPort, relevancy_filter_adapter:IRelevancyFilterPort):
    document_id = "ebb9995a9ac611efaa3a00155d0ee567"
    
    op_defs = await query.get_document_operation_definition_by_op_type("medication_extraction")
    op_def = op_defs[0]
    step_config = op_def.dict()["step_config"]
    medispan_step_config = step_config["MEDISPAN_MATCHING"]

    prompt = medispan_step_config["prompt"]
    model = medispan_step_config["model"]

    PROMPT = """For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:                        
1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match                        
2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength                        
3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form                        
4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route                        
5) Otherwise, return "{}" and specific what attributes were not found                        

Only return the best match from the list. If no match is found, return "{}"                        
Only return the best match from the list. If no match is found, return "{}"                        

GIVEN MEDICATION:                        
{SEARCH_TERM}                        

MATCH LIST:
"""


    #LOGGER.debug(json.dumps(medispan_step_config, indent=2, cls=DateTimeEncoder))
    LOGGER.debug("model: %s", model)
    LOGGER.debug("prompt: %s", prompt)

    from paperglass.usecases.documents import get_document_logs

    ret = await get_document_logs(document_id)
    logs = ret["MEDICATION_EXTRACTION"]
    logs = [x.dict() for x in logs]
    for log in logs:
        if log.get("step_id")=="MEDISPAN_MATCHING":
            context = log.get("context")
            medispan_log_details = context["medispan_log_details"]            
            for detail in medispan_log_details:
                search_term = detail["medispan_search_term"]
                medispan_results_dict = json.loads(detail["medispan_results"])
                medispan_results = [MedispanDrug(**x) for x in medispan_results_dict]
                medispan_filter_results = detail["medispan_filter_results"]
                medispan_drug = detail["medispan_drug"]
                medispan_id = medispan_drug["id"]
                medispan_name = medispan_drug["NameDescription"]

                #LOGGER.debug("search_term: %s", search_term)
                #LOGGER.debug(json.dumps(medispan_results, indent=2))
                #LOGGER.debug(json.dumps(medispan_filter_results, indent=2))

                medispan_results_tuple = await relevancy_filter_adapter.re_rank(search_term, medispan_results, model=model, prompt=prompt, enable_llm=True, metadata={})
                medispan_port_result, context = medispan_results_tuple

                this_medispan_id = medispan_port_result.id
                this_medispan_name = medispan_port_result.NameDescription

                LOGGER.debug(medispan_port_result)
                LOGGER.debug(json.dumps(context, indent=2))
                LOGGER.warning("Target medispan: %s %s  This medispan: %s %s", medispan_id, medispan_name, this_medispan_id, this_medispan_name)


async def test_list_documentoperationinstancelogs():
    LOGGER.info("Starting test")
    from paperglass.usecases.document_operation_instance_log import DocumentOperationInstanceLogService
    
    start_time = now_utc()

    #Storage logs
    storage_data = {
        "document_id": "8f402eb6a76711ef8c920242ac140005",
        "document_operation_instance_id": "90ae5c82a76711efb43e0242ac140007"
    }
    
    firestore_data = {
        "document_id": "f5af6786a3f011ef82b842004e494300",
        "document_operation_instance_id": "f750ac8aa3f011ef82b842004e494300"
    }

    #data = storage_data
    data = firestore_data

    #Firestore logs    
    doc_service = DocumentOperationInstanceLogService()
    try:
        logs = await doc_service.list(data["document_id"], data["document_operation_instance_id"])
    except Exception as e:
        LOGGER.error("Error: %s", e)
        
    elapsed_time = (now_utc() - start_time).total_seconds()
    
    LOGGER.info("Logs: %s", logs)
    LOGGER.info("Elapsed time: %s", elapsed_time)

    return logs


async def run_query():
    document_id = "f5af6786a3f011ef82b842004e494300"
    doc_operation_instance_id = "f750ac8aa3f011ef82b842004e494300"

    client = firestore.AsyncClient(database=GCP_FIRESTORE_DB)
    log_coll = client.collection("paperglass_document_operation_instance_log")
    ref = log_coll.where('document_id','==',document_id).where('document_operation_instance_id','==',doc_operation_instance_id)

    docs = await ref.get()
    doc_operation_instance_logs= [DocumentOperationInstanceLog(**doc.to_dict()) for doc in docs]
    doc_operation_instance_logs.sort(key=lambda x: x.created_at, reverse=True) if doc_operation_instance_logs else None

    LOGGER.info("Logs: %s", doc_operation_instance_logs)

async def test_a():
    from paperglass.usecases.queue_resolver import QueueResolver
    qr = QueueResolver()
    print(qr.resolve_queue_name("page_classification", OrchestrationPriority.HIGH.value))
    print(qr.resolve_queue_name("page_classification", OrchestrationPriority.DEFAULT.value))
    print(qr.resolve_queue_name("page_classification", "unknown"))
    print(qr.resolve_queue_name("extraction", OrchestrationPriority.HIGH.value))
    print(qr.resolve_queue_name("extraction", OrchestrationPriority.DEFAULT.value))
    print(qr.resolve_queue_name("extraction", "unknown"))

    exit()

    print(qr.resolve_queue_name("unknown", OrchestrationPriority.HIGH.value))
    print(qr.resolve_queue_name("unknown", "unknown"))
    print(qr.resolve_queue_name("", OrchestrationPriority.HIGH.value))
    print(qr.resolve_queue_name("", OrchestrationPriority.DEFAULT.value))
    print(qr.resolve_queue_name("", "unknown"))
    print(qr.resolve_queue_name("page_classification", ""))
    print(qr.resolve_queue_name("", ""))
    print(qr.resolve_queue_name("page_classification", None))
    print(qr.resolve_queue_name(None, OrchestrationPriority.HIGH.value))
    print(qr.resolve_queue_name(None, None))
    print(qr.resolve_queue_name(None, ""))
    print(qr.resolve_queue_name("", None))
    print(qr.resolve_queue_name(None, ""))

async def run():
    #await medispan_match_test()
    LOGGER.info("Running test")
    #results = await test_list_documentoperationinstancelogs()
    await test_a()
    #await run_query()
    



def main():
    
    asyncio.run(run())

if __name__ == "__main__":   
    main()






