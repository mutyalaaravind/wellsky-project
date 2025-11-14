from paperglass.infrastructure.ports import ISearchAdapter,ISearchIndexer,ISearchFHIRAdapter
from kink import inject

@inject()
async def search(identifier, search_query, search_adapter:ISearchAdapter):
    return search_adapter.search(identifier, search_query)

@inject()
async def search_fhir(identifier, search_query, search_adapter:ISearchAdapter,search_fhir_adapter:ISearchFHIRAdapter):
    #doc_results = search_adapter.search(identifier, search_query)
    return search_fhir_adapter.search(identifier, search_query)
    #print(fhir_results)
    # final_results = fhir_results
    # return [result for result in final_results]

@inject()
async def index(identifier, doc_id, gcs_uri, mime_type, search_adapter:ISearchIndexer):
    return search_adapter.index(identifier, doc_id, gcs_uri, mime_type)