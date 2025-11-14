from typing import List

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.protobuf.json_format import MessageToDict

from paperglass.infrastructure.ports import ISearchFHIRAdapter


class SearchFHIRAdapter(ISearchFHIRAdapter):

    def __init__(self, project_id: str, location: str, data_store_id: str):
        self.project_id = project_id
        self.location = location
        self.data_store_id = data_store_id

    def search(
        self, identifier: str, search_query: str, serving_config="default_config"
    ) -> List[discoveryengine.SearchResponse]:
        print(f"Searching fhir for: {search_query}")
        #  For more information, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
        client_options = (
            ClientOptions(api_endpoint=f"{self.location}-discoveryengine.googleapis.com")
            if self.location != "global"
            else None
        )

        # Create a client
        client = discoveryengine.SearchServiceClient(client_options=client_options)

        # The full resource name of the search engine serving config
        # e.g. projects/{project_id}/locations/{location}/dataStores/{data_store_id}/servingConfigs/{serving_config_id}
        serving_config = client.serving_config_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            serving_config=serving_config,
        )

        # Optional: Configuration options for search
        # Refer to the `ContentSearchSpec` reference for all supported fields:
        # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
            # For information about snippets, refer to:
            # https://cloud.google.com/generative-ai-app-builder/docs/snippets
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(return_snippet=True),
            # For information about search summaries, refer to:
            # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=5,
                include_citations=True,
                ignore_adversarial_query=True,
                ignore_non_summary_seeking_query=True,
            ),
        )

        # Refer to the `SearchRequest` reference for all supported fields:
        # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=search_query,
            page_size=30,
            content_search_spec=content_search_spec,
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
            filter=f"patient_id:ANY(\"{identifier}\") AND resource_type:ANY(\"MedicationRequest\",\"DiagnosticReport\",\"AllergyIntolerance\",\"DocumentReference\")",  # https://cloud.google.com/generative-ai-app-builder/docs/filter-search-metadata
        )

        response = client.search(request)

        results = []
        medication_results = {"type": "MedicationRequest", "results": []}
        diagnostic_report = {"type": "DiagnosticReport", "results": []}
        allergy_intollerance = {"type": "AllergyIntolerance", "results": []}
        document_reference = {"type": "DocumentReference", "results": []}
        count = 0
        response = MessageToDict(response._pb)

        for x in response.get("results", []):
            resource = None
            # if count > 10:
            #     break

            document = x.get("document", {})

            results.append(
                {
                    "document": document,
                    "id": document["id"],
                    "title": "",  # x.document.derived_struct_data["title"],
                    "doc_url": "",  # x.document.derived_struct_data["link"],
                    "snippets": document["derivedStructData"]["snippets"][0]["snippet"],
                    "type": document["structData"]["resource_type"],
                    "resource": {
                        document["structData"]["resource_type"]: document["structData"][
                            document["structData"]["resource_type"]
                        ]
                    },
                }
            )

        for result in results:
            print(result.get("type"))
            if result.get("type") == "MedicationRequest":
                medication_results["results"].append(result)
            if result.get("type") == "DiagnosticReport":
                diagnostic_report["results"].append(result)
            if result.get("type") == "AllergyIntolerance":
                allergy_intollerance["results"].append(result)
            if result.get("type") == "DocumentReference":
                document_reference["results"].append(result)

        return {
            "results": [medication_results, diagnostic_report, allergy_intollerance, document_reference],
            "summary": response.get("summary"),
        }
