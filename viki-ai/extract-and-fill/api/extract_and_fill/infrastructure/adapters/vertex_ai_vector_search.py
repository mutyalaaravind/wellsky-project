import time
from typing import List, Optional
import pinecone
from vertexai.preview.language_models import TextEmbeddingModel
from google.cloud import aiplatform, storage
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
from google.cloud import aiplatform_v1beta1 as vertexai_beta
from langchain.embeddings import VertexAIEmbeddings
from pydantic import BaseModel
import vertexai

from extract_and_fill.infrastructure.ports import IEmbeddingsAdapter

EMBEDDING_QPM = 100
EMBEDDING_NUM_BATCH = 5

class VertexAIVectorAdapter(IEmbeddingsAdapter):
    
    def __init__(self, 
                    project_id, 
                    location, 
                    api_key, 
                    env,
                    gcs_uri,
                    index_name,
                    index_endpoint,
                    deployed_index_id
                 ):
        self.project_id = project_id
        self.location = location
        self.api_key = api_key
        self.env = env
        vertexai.init(project=project_id, location=location)
        aiplatform.init(project=project_id, location=location)
        self.gcs_client  = storage.Client(project=project_id)
        self.gcs_uri = gcs_uri
        self.index_name = index_name
        self.index_endpoint_name = index_endpoint
        self.deployed_index_id = deployed_index_id
    
    async def _create_embeddings_using_gecko_transformer(self, sentences):
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        return await self._encode_texts_to_embeddings(model,sentences)
    
    async def _encode_texts_to_embeddings(self, model: TextEmbeddingModel, sentences: List[str]) -> List[Optional[List[float]]]:
            try:
                embeddings = await model.get_embeddings_async(sentences)
                return [embedding.values for embedding in embeddings]
            except Exception:
                return [None for _ in range(len(sentences))]
            
    async def upsert(self, sentence_group_id, sentences):
            
        from google.cloud import aiplatform_v1
        from google.cloud import aiplatform
        
        index_client = aiplatform_v1.IndexServiceAsyncClient(
            client_options=dict(api_endpoint=f"{self.location}-aiplatform.googleapis.com")
        )
        
        # contents_delta_uri
        for sentence in sentences:
            if not sentence.get("sentence"):
                continue
            
            embed = await self._create_embeddings_using_gecko_transformer([sentence.get("sentence")])
            
            if embed[0]:
                insert_datapoints_payload = aiplatform_v1.IndexDatapoint(
                    datapoint_id=sentence.get("sentence_id") or sentence.get("id"),
                    feature_vector=embed[0],
                    restricts=[{"namespace": "class", "allow_list": [sentence_group_id]}]
                )
                
                upsert_request = aiplatform_v1.UpsertDatapointsRequest(
                    index=self.index_name, datapoints=[insert_datapoints_payload]
                )
                
                await index_client.upsert_datapoints(request=upsert_request)
    
    async def remove(self, sentences):
            
        from google.cloud import aiplatform_v1
        
        index_client = aiplatform_v1.IndexServiceAsyncClient(
            client_options=dict(api_endpoint=f"{self.location}-aiplatform.googleapis.com")
        )
        
        # contents_delta_uri
        for sentence in sentences:
            remove_datapoints_request = aiplatform_v1.RemoveDatapointsRequest(
                datapoint_ids=[sentence.get("id")],
                index = self.index_name
            )
            
            await index_client.remove_datapoints(request=remove_datapoints_request)
    
    # todo: filtering to be expanded in future
    async def search(self, id, query_strings:[str], top_k=1):
        results = []
        query_terms = [x for x in query_strings if x]
        embedding = await self._create_embeddings_using_gecko_transformer(query_terms)

        matcher = Matcher(self.index_endpoint_name, self.deployed_index_id)
        neighbors = await matcher.find_neighbors(embedding[0], id)

        for neighbor in neighbors:
            results.append({"id":neighbor.datapoint.datapoint_id,"distance":neighbor.distance})
        
        return results
    
    def search_with_langchain(self, id, query_strings:[str], top_k=1):
        #embedding = await self._create_embeddings_using_gecko_transformer(query_strings)
        embeddings = CustomVertexAIEmbeddings(
            requests_per_minute=EMBEDDING_QPM,
            num_instances_per_batch=EMBEDDING_NUM_BATCH,
        )

        from langchain.vectorstores import MatchingEngine
        
        vector_store = MatchingEngine.from_components(
            embedding=embeddings,
            project_id=self.project_id,
            region=self.location,
            gcs_bucket_name="gs://extraction-index-dev",
            index_id=self.index_name,
            endpoint_id=self.index_endpoint_name,
        )
        
        retreiver = vector_store.as_retriever()
        
        # TODO: THIS WILL BLOCK THE EVENT LOOP.
        # Does MatchingEngine support asyncio?
        print(retreiver.get_relevant_documents(query_strings[0])[0])
        
        return None, None
        
        
        
            
#https://zenn.dev/google_cloud_jp/articles/getting-started-matching-engine           
class Matcher:
    def __init__(self, index_endpoint_name: str, deployed_index_id: str):
        self._index_endpoint_name = index_endpoint_name
        self._deployed_index_id = deployed_index_id

        self._client = vertexai_beta.MatchServiceAsyncClient(
            client_options={"api_endpoint": self._public_endpoint()}
        )

    # Matching Engine にリクエストして、
    # 与えられたエンベディングの近似最近傍探索を行う
    async def find_neighbors(self, embedding: list[float],  sentence_group_id: str, neighbor_count: int=1):
        datapoint = vertexai_beta.IndexDatapoint(
            datapoint_id="dummy-id",
            feature_vector=embedding,
            restricts=[{"namespace": "class", "allow_list": [sentence_group_id]}]
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
        endpoint = MatchingEngineIndexEndpoint(
            index_endpoint_name=self._index_endpoint_name
        )
        return endpoint.gca_resource.public_endpoint_domain_name
    
class CustomVertexAIEmbeddings(VertexAIEmbeddings, BaseModel):
    requests_per_minute: int
    num_instances_per_batch: int

    # Overriding embed_documents method
    def embed_documents(self, texts: List[str]):
        # TODO: THIS WILL BLOCK THE EVENT LOOP.
        limiter = rate_limit(self.requests_per_minute)
        results = []
        docs = list(texts)

        while docs:
            # Working in batches because the API accepts maximum 5
            # documents per request to get embeddings
            head, docs = (
                docs[: self.num_instances_per_batch],
                docs[self.num_instances_per_batch :],
            )
            chunk = self.client.get_embeddings(head)
            results.extend(chunk)
            next(limiter)

        return [r.values for r in results]
    
# Utility functions for Embeddings API with rate limiting
def rate_limit(max_per_minute):
    period = 60 / max_per_minute
    print("Waiting")
    while True:
        before = time.time()
        yield
        after = time.time()
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
            print(".", end="")
            # TODO: THIS WILL BLOCK THE EVENT LOOP.
            time.sleep(sleep_time)
