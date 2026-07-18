"""Retrieval orchestration over an embedding service and vector store."""

from .embeddings import EmbeddingService
from .vector_store import SearchResult, VectorStore


class Retriever:
    """Retrieve relevant knowledge chunks for a user question."""

    def __init__(self, embeddings: EmbeddingService, vector_store: VectorStore) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(self, query: str, limit: int = 4) -> list[SearchResult]:
        """Embed a non-empty query and return its most relevant chunks."""
        if not query.strip():
            raise ValueError("query must not be empty")
        if limit <= 0:
            raise ValueError("limit must be positive")
        return self.vector_store.search(self.embeddings.embed_query(query), limit=limit)
