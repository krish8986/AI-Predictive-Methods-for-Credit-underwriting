"""Document chunking utilities for retrieval-friendly context windows."""

from dataclasses import dataclass
from typing import Any

from .loader import Document


@dataclass(frozen=True)
class DocumentChunk:
    """A traceable fragment of a source document."""

    id: str
    content: str
    metadata: dict[str, Any]


class DocumentChunker:
    """Split documents into overlapping, whitespace-aware character chunks."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("chunk_overlap must be at least 0 and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: list[Document]) -> list[DocumentChunk]:
        """Split documents while retaining source metadata and stable chunk identifiers."""
        chunks: list[DocumentChunk] = []
        for document in documents:
            text = " ".join(document.content.split())
            start = 0
            index = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                if end < len(text):
                    boundary = text.rfind(" ", start, end)
                    if boundary > start:
                        end = boundary

                content = text[start:end].strip()
                if content:
                    metadata = {**document.metadata, "chunk_index": index}
                    chunks.append(
                        DocumentChunk(
                            id=f"{document.id}:{index}",
                            content=content,
                            metadata=metadata,
                        )
                    )
                    index += 1

                if end >= len(text):
                    break
                start = max(end - self.chunk_overlap, start + 1)
        return chunks
