from rag.index_builder import IndexBuilder
from rag.embeddings import SentenceTransformerEmbeddingService
from rag.vector_store import FAISSVectorStore
from rag.retriever import Retriever

INDEX_PATH = "models/rag_index/index.faiss"

builder = IndexBuilder()

store = FAISSVectorStore.load(INDEX_PATH)

embedding_service = SentenceTransformerEmbeddingService()

retriever = Retriever(embedding_service, store)

results = retriever.retrieve(
    "Why was my loan rejected?"
)

print("\n==========================")

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}")
    print(f"Score : {result.score:.4f}")
    print(result.record.content[:500])

print("\n==========================")