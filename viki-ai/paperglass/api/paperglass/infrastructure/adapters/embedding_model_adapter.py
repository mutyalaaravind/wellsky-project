from typing import List, Optional
from vertexai.preview.language_models import TextEmbeddingModel


class TextEmbeddingModelAdapter:

    async def get_embeddings(self, sentences):
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
        return await self._encode_texts_to_embeddings(model, sentences)

    async def _encode_texts_to_embeddings(
        self, model: TextEmbeddingModel, sentences: List[str]
    ) -> List[Optional[List[float]]]:
        try:
            embeddings = await model.get_embeddings_async(sentences)
            return [embedding.values for embedding in embeddings]
        except Exception:
            return [None for _ in range(len(sentences))]


class PubmMdBertBaseEmbeddings:

    async def get_embeddings(self, sentences):
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("neuml/pubmedbert-base-embeddings")
        embeddings = model.encode(sentences)
        return [e for e in embeddings]
