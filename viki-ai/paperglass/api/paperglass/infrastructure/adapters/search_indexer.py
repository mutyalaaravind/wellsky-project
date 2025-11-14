import json
import requests
from google.cloud import discoveryengine_v1alpha as discoveryengine_v1
import google.auth

from paperglass.infrastructure.ports import ISearchIndexer
from paperglass.log import getLogger

logger = getLogger(__name__)


class SearchIndexer(ISearchIndexer):

    def __init__(
        self,
        project_id: str,
        location: str,
        location3: str,
        data_store_id: str,
        fhir_datastore_id: str,
        fhir_dataset: str,
        fhir_search_store_id: str,
    ):
        self.project_id = project_id
        self.location = location
        self.location3 = location3
        self.data_store_id = data_store_id
        self.fhir_datastore_id = fhir_datastore_id
        self.fhir_dataset = fhir_dataset
        self.fhir_search_store_id = fhir_search_store_id

    def index(self, identifier: str, doc_identifier: str, gcs_uri: str, mime_type: str):
        print(
            f"Indexing document: {identifier} , {doc_identifier}, {gcs_uri}, {mime_type}, {self.data_store_id}, {self.location}..."
        )
        client = discoveryengine_v1.DocumentServiceClient()
        json_payload = {
            "id": "<your-id>",
            "jsonData": json.dumps({"identifier": identifier}),
            "content": {"mimeType": "application/pdf", "uri": gcs_uri},
        }
        # upload to metadata gcs bucket

        request = discoveryengine_v1.ImportDocumentsRequest(
            gcs_source={"input_uris": [gcs_uri], "data_schema": "document"},
            parent=f"projects/145042810266/locations/{self.location}/collections/default_collection/dataStores/{self.data_store_id}/branches/*",
            auto_generate_ids=False,
            id_field="id",
            # inline_source={
            #         "documents":[
            #             dict(
            #                 id=doc_identifier, # [TODO] This is not working, so we are using the id in the json_data
            #                 json_data=json.dumps({"identifier":identifier}),
            #                 content=discoveryengine_v1.Document.Content(
            #                     mime_type=mime_type,
            #                     uri=gcs_uri
            #                 )
            #             )
            #         ]
            #     }
        )

        operation = client.import_documents(request=request)

        print("Waiting for operation to complete...")

        response = operation.result()

        # Handle the response
        print(response)

    async def index_fhir(self, reconcillation_mode: str = "INCREMENTAL"):
        fhir_discovery_engine_url = f"https://us-discoveryengine.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/dataStores/{self.fhir_search_store_id}/branches/0/documents:import"
        response = requests.post(
            fhir_discovery_engine_url,
            json={
                "reconciliation_mode": reconcillation_mode,
                "fhir_store_source": {
                    "fhir_store": f"projects/{self.project_id}/locations/{self.location3}/datasets/{self.fhir_dataset}/fhirStores/{self.fhir_datastore_id}"
                },
            },
            headers=self._get_headers(),
        )
        return response.json()

    def _get_headers(self, for_patch=False):
        return {
            'Content-Type': 'application/json-patch+json' if for_patch else 'application/fhir+json; charset=utf-8',
            'Authorization': f'Bearer {self._get_gcp_auth_token()}',
        }

    def _get_gcp_auth_token(self, force_refresh=False):
        return GCPAuth().auth_token(force_refresh)


class GCPAuth(object):
    _credentials = None

    def auth_token(self, force_refresh=False):

        if GCPAuth._credentials and GCPAuth._credentials.token and not force_refresh:
            return GCPAuth._credentials.token

        if GCPAuth._credentials:
            logger.info(f"Current token {GCPAuth._credentials.token}")
        # getting the credentials and project details for gcp project
        GCPAuth._credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # getting request object
        auth_req = google.auth.transport.requests.Request()

        GCPAuth._credentials.refresh(auth_req)  # refresh token

        logger.info(GCPAuth._credentials.token)

        if GCPAuth._credentials.valid:
            return GCPAuth._credentials.token
        else:
            raise Exception("GCP Auth failed")  # prints token
