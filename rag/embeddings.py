"""Embedding provider contract for the RAG subsystem."""

from abc import ABC, abstractmethod
import logging
from threading import Lock
from typing import Any, ClassVar


logger = logging.getLogger(__name__)


class EmbeddingService(ABC):
    """Create compatible vector representations for documents and queries."""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed document text in the configured vector space."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed one user query in the same vector space as documents."""


class SentenceTransformerEmbeddingService(EmbeddingService):
    """Embed text with a lazily loaded, process-wide SentenceTransformer model."""

    model_name = "all-MiniLM-L6-v2"
    _model: ClassVar[Any | None] = None
    _model_lock: ClassVar[Lock] = Lock()

    @classmethod
    def _get_model(cls) -> Any:
        """Load and cache the embedding model on its first use."""
        if cls._model is not None:
            return cls._model

        with cls._model_lock:
            if cls._model is not None:
                return cls._model

            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as error:
                logger.exception("SentenceTransformers is not installed.")
                raise RuntimeError(
                    "SentenceTransformers is required for RAG embeddings. "
                    "Install the sentence-transformers package."
                ) from error

            try:
                logger.info("Loading SentenceTransformer model: %s", cls.model_name)
                cls._model = SentenceTransformer(cls.model_name)
            except Exception as error:
                logger.exception("Failed to load embedding model: %s", cls.model_name)
                raise RuntimeError(
                    f"Unable to load embedding model '{cls.model_name}'."
                ) from error

        return cls._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return normalized embeddings for document text in input order."""
        if not texts:
            return []
        if any(not isinstance(text, str) for text in texts):
            raise TypeError("texts must contain only strings")

        try:
            embeddings = self._get_model().encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        except Exception as error:
            logger.exception("Failed to embed %d document(s).", len(texts))
            raise RuntimeError("Document embedding failed.") from error

        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Return a normalized embedding for one non-empty user query."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")

        return self.embed_documents([text])[0]
