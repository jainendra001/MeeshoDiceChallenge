import pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

from ..config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(settings.MODEL_NAME)
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        if settings.INDEX_NAME not in pinecone.list_indexes():
            pinecone.create_index(
                settings.INDEX_NAME,
                dimension=settings.EMBEDDING_DIMENSION,
                metric="cosine"
            )
        self.index = pinecone.Index(settings.INDEX_NAME)

    def add_texts(self, texts: List[str], metadata: List[Dict[str, Any]]) -> None:
        """Add texts to the vector store with metadata"""
        embeddings = self.model.encode(texts)
        vectors = [(str(i), embedding.tolist(), meta) 
                  for i, (embedding, meta) in enumerate(zip(embeddings, metadata))]
        self.index.upsert(vectors=vectors)

    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts given a query"""
        query_embedding = self.model.encode(query)
        results = self.index.query(
            query_embedding.tolist(),
            top_k=k,
            include_metadata=True
        )
        return [{"id": match.id, "score": match.score, "metadata": match.metadata} 
                for match in results.matches]
