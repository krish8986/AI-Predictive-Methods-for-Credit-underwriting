"""Vector-store contracts for persistent or in-memory retrieval backends."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
from threading import RLock
from typing import Any


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VectorRecord:
    """A chunk, its embedding, and traceability metadata."""

    id: str
    content: str
    embedding: list[float]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class SearchResult:
    """A retrieved vector record with its similarity score."""

    record: VectorRecord
    score: float


class VectorStore(ABC):
    """Persistence interface for embedded RAG document chunks."""

    @abstractmethod
    def upsert(self, records: list[VectorRecord]) -> None:
        """Insert or replace records using their stable identifiers."""

    @abstractmethod
    def search(self, query_embedding: list[float], limit: int = 4) -> list[SearchResult]:
        """Return the highest-scoring records for a query embedding."""


class FAISSVectorStore(VectorStore):
    """FAISS-backed cosine-similarity store for normalized embedding vectors.

    ``IndexFlatIP`` performs inner-product search. With normalized embeddings, its
    scores are cosine similarities. Upserts rebuild the flat index so replacing a
    record always preserves the FAISS-index-to-record mapping.
    """

    def __init__(self, dimension: int | None = None) -> None:
        if dimension is not None and dimension <= 0:
            raise ValueError("dimension must be positive")
        self._dimension = dimension
        self._index: Any | None = None
        self._records_by_id: dict[str, VectorRecord] = {}
        self._index_to_record: dict[int, VectorRecord] = {}
        self._lock = RLock()

    @property
    def dimension(self) -> int | None:
        """Return the expected embedding dimension, if known."""
        return self._dimension

    @staticmethod
    def _dependencies() -> tuple[Any, Any]:
        """Import optional FAISS dependencies only when the store is used."""
        try:
            import faiss
            import numpy as np
        except ImportError as error:
            logger.exception("FAISS dependencies are not installed.")
            raise RuntimeError(
                "FAISS vector storage requires the faiss-cpu and numpy packages."
            ) from error
        return faiss, np

    def _vector(self, embedding: list[float], expected_dimension: int | None) -> Any:
        """Convert and validate one finite, one-dimensional embedding."""
        _, np = self._dependencies()
        vector = np.asarray(embedding, dtype="float32")
        if vector.ndim != 1 or vector.size == 0:
            raise ValueError("embedding must be a non-empty one-dimensional vector")
        if not np.isfinite(vector).all():
            raise ValueError("embedding must contain only finite values")
        if expected_dimension is not None and vector.size != expected_dimension:
            raise ValueError(
                f"embedding dimension {vector.size} does not match {expected_dimension}"
            )
        return vector

    def _rebuild_index(self, records_by_id: dict[str, VectorRecord]) -> None:
        """Build an IndexFlatIP and its corresponding FAISS-position mapping."""
        faiss, np = self._dependencies()
        records = list(records_by_id.values())
        if not records:
            self._index = None
            self._index_to_record = {}
            return

        dimension = self._dimension
        vectors = [self._vector(record.embedding, dimension) for record in records]
        self._dimension = dimension or int(vectors[0].size)
        matrix = np.vstack(vectors).astype("float32", copy=False)
        index = faiss.IndexFlatIP(self._dimension)
        index.add(matrix)
        self._index = index
        self._index_to_record = {
            position: record for position, record in enumerate(records)
        }

    def upsert(self, records: list[VectorRecord]) -> None:
        """Insert or replace records and rebuild the immutable flat FAISS index."""
        if not records:
            return

        with self._lock:
            expected_dimension = self._dimension
            for record in records:
                if not record.id:
                    raise ValueError("record id must not be empty")
                vector = self._vector(record.embedding, expected_dimension)
                expected_dimension = expected_dimension or int(vector.size)

            updated_records = self._records_by_id.copy()
            for record in records:
                updated_records[record.id] = record

            previous_dimension = self._dimension
            self._dimension = expected_dimension
            try:
                self._rebuild_index(updated_records)
            except Exception as error:
                self._dimension = previous_dimension
                logger.exception("Failed to rebuild FAISS index during upsert.")
                raise RuntimeError("Unable to upsert records into the FAISS store.") from error

            self._records_by_id = updated_records
            logger.info("FAISS vector store now contains %d record(s).", len(updated_records))

    def search(self, query_embedding: list[float], limit: int = 4) -> list[SearchResult]:
        """Return the top cosine-similar records for a normalized query embedding."""
        if limit <= 0:
            raise ValueError("limit must be positive")

        with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return []
            query = self._vector(query_embedding, self._dimension).reshape(1, -1)

            try:
                scores, positions = self._index.search(query, min(limit, self._index.ntotal))
            except Exception as error:
                logger.exception("FAISS search failed.")
                raise RuntimeError("Unable to search the FAISS store.") from error

            results = []
            for score, position in zip(scores[0], positions[0]):
                record = self._index_to_record.get(int(position))
                if record is not None:
                    results.append(SearchResult(record=record, score=float(score)))
            return results

    @staticmethod
    def _metadata_path(index_path: Path) -> Path:
        """Return the sidecar file that stores records for a persisted index."""
        return index_path.with_name(f"{index_path.name}.records.json")

    def save(self, index_path: str | Path) -> None:
        """Persist the FAISS index and its index-to-record mapping to disk."""
        path = Path(index_path)
        metadata_path = self._metadata_path(path)

        with self._lock:
            if self._index is None or self._dimension is None:
                raise RuntimeError("Cannot save an empty FAISS vector store.")

            payload = {
                "dimension": self._dimension,
                "records": [
                    {
                        "id": record.id,
                        "content": record.content,
                        "embedding": record.embedding,
                        "metadata": record.metadata,
                    }
                    for record in self._index_to_record.values()
                ],
            }
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary_index = path.with_name(f"{path.name}.tmp")
                temporary_metadata = metadata_path.with_name(f"{metadata_path.name}.tmp")
                faiss, _ = self._dependencies()
                faiss.write_index(self._index, str(temporary_index))
                temporary_metadata.write_text(
                    json.dumps(payload, ensure_ascii=False), encoding="utf-8"
                )
                os.replace(temporary_index, path)
                os.replace(temporary_metadata, metadata_path)
            except Exception as error:
                logger.exception("Failed to save FAISS vector store to %s.", path)
                raise RuntimeError(f"Unable to save FAISS vector store to {path}.") from error

        logger.info("Saved FAISS vector store to %s.", path)

    @classmethod
    def load(cls, index_path: str | Path) -> "FAISSVectorStore":
        """Load a persisted FAISS index and reconstruct its record mapping."""
        path = Path(index_path)
        metadata_path = cls._metadata_path(path)
        if not path.is_file() or not metadata_path.is_file():
            raise RuntimeError(f"FAISS index or metadata file is missing for {path}.")

        try:
            faiss, _ = cls._dependencies()
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            store = cls(dimension=int(payload["dimension"]))
            records = [
                VectorRecord(
                    id=item["id"],
                    content=item["content"],
                    embedding=item["embedding"],
                    metadata=item["metadata"],
                )
                for item in payload["records"]
            ]
            for record in records:
                store._vector(record.embedding, store._dimension)

            index = faiss.read_index(str(path))
            if index.d != store._dimension or index.ntotal != len(records):
                raise ValueError("FAISS index does not match persisted record metadata")
            store._index = index
            store._records_by_id = {record.id: record for record in records}
            if len(store._records_by_id) != len(records):
                raise ValueError("Persisted records contain duplicate identifiers")
            store._index_to_record = {
                position: record for position, record in enumerate(records)
            }
        except Exception as error:
            logger.exception("Failed to load FAISS vector store from %s.", path)
            raise RuntimeError(f"Unable to load FAISS vector store from {path}.") from error

        logger.info("Loaded FAISS vector store with %d record(s).", len(records))
        return store
