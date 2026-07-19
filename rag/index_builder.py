"""Build the FAISS index from the local knowledge base."""

from pathlib import Path
import logging

from rag.loader import MarkdownLoader
from rag.chunker import DocumentChunker
from rag.embeddings import SentenceTransformerEmbeddingService
from rag.vector_store import FAISSVectorStore, VectorRecord

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class IndexBuilder:
    """Builds and persists the RAG vector index."""

    def __init__(self):
        self.loader = MarkdownLoader()
        self.chunker = DocumentChunker()
        self.embedding_service = SentenceTransformerEmbeddingService()

        self.index_dir = Path("models/rag_index")
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.index_path = self.index_dir / "index.faiss"

    def build(self):
        logger.info("Loading documents...")

        documents = self.loader.load()
        logger.info("Loaded %d documents", len(documents))

        chunks = self.chunker.chunk(documents)
        logger.info("Created %d chunks", len(chunks))

        texts = [chunk.content for chunk in chunks]

        embeddings = self.embedding_service.embed_documents(texts)

        logger.info("Generated %d embeddings", len(embeddings))

        dimension = len(embeddings[0])

        store = FAISSVectorStore(dimension)

        records = []

        for chunk, embedding in zip(chunks, embeddings):
            records.append(
                VectorRecord(
                    id=chunk.id,
                    content=chunk.content,
                    embedding=embedding,
                    metadata=chunk.metadata,
                )
            )

        store.upsert(records)

        store.save(self.index_path)

        logger.info("FAISS index saved to %s", self.index_path)

        return store

    def rebuild(self):
        return self.build()

    def load(self):
        logger.info("Loading FAISS index...")

        return FAISSVectorStore.load(self.index_path)


if __name__ == "__main__":
    builder = IndexBuilder()
    builder.build()

    print("\n✅ RAG Index Successfully Built")