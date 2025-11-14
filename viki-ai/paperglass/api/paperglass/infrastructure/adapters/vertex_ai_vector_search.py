import time
from typing import List, Optional
import uuid
from paperglass.infrastructure.adapters.embedding_model_adapter import (
    TextEmbeddingModelAdapter,
    PubmMdBertBaseEmbeddings,
)
from paperglass.domain.models import VectorIndex, VectorSearchResult
from vertexai.preview.language_models import TextEmbeddingModel
from google.cloud import aiplatform, storage
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import Namespace
from google.cloud import aiplatform_v1beta1 as vertexai_beta
from pydantic import BaseModel
import vertexai
from google.cloud import aiplatform_v1
from google.cloud import aiplatform

from paperglass.infrastructure.ports import IEmbeddingsAdapter
from paperglass.log import getLogger, labels

from google.cloud.firestore import AsyncClient as AsyncFirestoreClient

LOGGER = getLogger(__name__)

EMBEDDING_QPM = 100
EMBEDDING_NUM_BATCH = 5


class VertexAIVectorAdapter(IEmbeddingsAdapter):

    def __init__(self, project_id, location, api_key, env, gcs_uri, index_name, index_endpoint, deployed_index_id):
        self.project_id = project_id
        self.location = location
        self.api_key = api_key
        self.env = env
        vertexai.init(project=project_id, location=location)
        aiplatform.init(project=project_id, location=location)
        self.gcs_client = storage.Client(project=project_id)
        self.gcs_uri = gcs_uri
        self.index_name = index_name
        self.index_endpoint_name = index_endpoint
        self.deployed_index_id = deployed_index_id
        self.index_client = aiplatform_v1.IndexServiceAsyncClient(
            client_options=dict(api_endpoint=f"{self.location}-aiplatform.googleapis.com")
        )

    async def _create_embeddings(self, sentences):
        return await TextEmbeddingModelAdapter().get_embeddings(sentences)
        # return await PubmMdBertBaseEmbeddings().get_embeddings(sentences)

    # async def _create_embeddings_using_gecko_transformer(self, sentences):
    #     model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    #     return await self._encode_texts_to_embeddings(model, sentences)

    # async def _encode_texts_to_embeddings(
    #     self, model: TextEmbeddingModel, sentences: List[str]
    # ) -> List[Optional[List[float]]]:
    #     try:
    #         embeddings = await model.get_embeddings_async(sentences)
    #         return [embedding.values for embedding in embeddings]
    #     except Exception:
    #         return [None for _ in range(len(sentences))]

    async def upsert(self, vector_index: VectorIndex):

        embed = await self._create_embeddings([vector_index.data])

        insert_datapoints_payload = aiplatform_v1.IndexDatapoint(
            datapoint_id=vector_index.id,
            feature_vector=embed[0],
            restricts=[{"namespace": "class", "allow_list": vector_index.allow_list}],
        )

        upsert_request = aiplatform_v1.UpsertDatapointsRequest(
            index=self.index_name, datapoints=[insert_datapoints_payload]
        )
        LOGGER.debug(f"Upserting allow_list:{vector_index.allow_list} id:{vector_index.id} data: {vector_index.data}")
        await self.index_client.upsert_datapoints(request=upsert_request)
        await EmbeddingLog().add(vector_index)

    async def remove(self, sentences):

        from google.cloud import aiplatform_v1

        index_client = aiplatform_v1.IndexServiceAsyncClient(
            client_options=dict(api_endpoint=f"{self.location}-aiplatform.googleapis.com")
        )

        # contents_delta_uri
        for sentence in sentences:
            remove_datapoints_request = aiplatform_v1.RemoveDatapointsRequest(
                datapoint_ids=[sentence.get("id")], index=self.index_name
            )

            await index_client.remove_datapoints(request=remove_datapoints_request)

    # todo: filtering to be expanded in future
    async def search(self, allow_list: list[str], search_term: list[str], top_k=1) -> List[VectorSearchResult]:
        # new
        query_terms = [x for x in search_term if x]
        embedding = await self._create_embeddings(query_terms)
        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=f'{self.index_endpoint_name}')
        neighbors = my_index_endpoint.find_neighbors(
            filter=[Namespace("class", allow_list)],
            # filter=[{"namespace": "class", "allow_list": allow_list}],
            deployed_index_id=my_index_endpoint.deployed_indexes[0].id,
            queries=[embedding[0]],
            num_neighbors=10,
        )
        # old
        results: List[VectorSearchResult] = []
        # matcher = Matcher(self.index_endpoint_name, self.deployed_index_id)
        LOGGER.debug(f"searching for {search_term} in {allow_list}")
        # neighbors = await matcher.find_neighbors(embedding[0], allow_list)
        LOGGER.debug(f"got neighbors: {neighbors}")
        # for neighbor in neighbors:
        #     results.append(
        #         VectorSearchResult(
        #             id=neighbor.datapoint.datapoint_id, allow_list=allow_list, distance=neighbor.distance
        #         )
        #     )
        for neighbor in neighbors[0]:
            LOGGER.debug(f"got neighbor: {neighbor}")
            results.append(VectorSearchResult(id=neighbor.id, allow_list=allow_list, distance=neighbor.distance))
        LOGGER.debug(f"results: {results}")
        return results


# https://zenn.dev/google_cloud_jp/articles/getting-started-matching-engine
class Matcher:
    def __init__(self, index_endpoint_name: str, deployed_index_id: str):
        self._index_endpoint_name = index_endpoint_name
        self._deployed_index_id = deployed_index_id

        self._client = vertexai_beta.MatchServiceAsyncClient(client_options={"api_endpoint": self._public_endpoint()})

    # Matching Engine にリクエストして、
    # 与えられたエンベディングの近似最近傍探索を行う
    async def find_neighbors(self, embedding: list[float], allow_list: list[str], neighbor_count: int = 1):
        datapoint = vertexai_beta.IndexDatapoint(
            datapoint_id="dummy-id",
            feature_vector=embedding,
            restricts=[{"namespace": "class", "allow_list": allow_list}],
        )
        query = vertexai_beta.FindNeighborsRequest.Query(datapoint=datapoint)
        request = vertexai_beta.FindNeighborsRequest(
            index_endpoint=self._index_endpoint_name,
            deployed_index_id=self._deployed_index_id,
            queries=[query],
        )

        resp = await self._client.find_neighbors(request)

        return resp.nearest_neighbors[0].neighbors

    # IndexEndpoint の public endpoint を取得する
    def _public_endpoint(self) -> str:
        endpoint = MatchingEngineIndexEndpoint(index_endpoint_name=self._index_endpoint_name)
        return endpoint.gca_resource.public_endpoint_domain_name


class EmbeddingLog:

    EMBEDDING_LOG = u"paperglass_embeddings_log"

    def __init__(self):
        self.db = AsyncFirestoreClient()

    async def add(self, vector_index: VectorIndex):
        try:
            await self.db.collection(self.EMBEDDING_LOG).document(vector_index.id).set(vector_index.dict())
        except Exception as e:
            LOGGER.error("error logggin embedding", str(e))

    async def get_embeddings(self, allow_list: List[str]):
        async for doc in self.schema_chunks_ref.whereArrayContains('allow_list', allow_list).stream():
            yield VectorIndex(**doc.to_dict())
