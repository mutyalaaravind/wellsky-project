from typing import List, Optional
import pinecone
from vertexai.preview.language_models import TextEmbeddingModel
from google.cloud import aiplatform
import vertexai

class PineconeAdapter(object):
    
    def __init__(self, project_id, location, api_key, env, index_name):
        self.api_key = api_key
        self.env = env
        self.index_name = index_name
        vertexai.init(project=project_id, location=location)
        aiplatform.init(project=project_id, location=location)
        pinecone.init(api_key=self.api_key, environment=self.env)
    
    def _create_embeddings_using_gecko_transformer(self, sentences):
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        
        def encode_texts_to_embeddings(sentences: List[str]) -> List[Optional[List[float]]]:
            try:
                embeddings = model.get_embeddings(sentences)
                return [embedding.values for embedding in embeddings]
            except Exception:
                return [None for _ in range(len(sentences))]

        return encode_texts_to_embeddings(sentences)
    
    # use this method to provision basic index only
    # prod ready index to be provisioned outside, preferrably via TF
    def create_index(self, dimension=768, metric="dotproduct"):
        pinecone.create(self.index, dimensions=dimension, metric=metric)
        
        
    def upsert(self, unique_identifier, sentences):
            
        index = pinecone.Index(self.index_name)
        
        if not index:
            self.create_index()    
        
        for sentence in sentences:
            if not sentence:
                continue
            
            embeddings = self._create_embeddings_using_gecko_transformer([sentence]) #model.encode(sentence)
            
            sample_doc = [
                {
                    "id": sentence[0:10],
                    "values": embeddings[0],
                    "metadata": {"id": unique_identifier}
                }
            ]
            index.upsert(sample_doc)
    
    # todo: filtering to be expanded in future
    def search(self, id, query_strings:[str], top_k=1):
        index = pinecone.Index(self.index_name)
        
        query_results = index.query(
            vector=self._create_embeddings_using_gecko_transformer(query_strings)[0],
            top_k=top_k,
            include_data=True,
            filter={
                "id": {"$eq": id}
            }
        )
        
        if query_results and query_results.get('matches'):
            return query_results.get('matches')[0].get('id') + "-" + str(query_results.get('matches')[0].get('score','0.0'))
        
        return "No Match Found"