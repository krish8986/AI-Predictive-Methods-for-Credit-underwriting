"""Response-generation contract for grounded RAG answers."""

from abc import ABC, abstractmethod

from .vector_store import SearchResult


class ResponseGenerator(ABC):
    """Generate answers grounded in retrieved credit-policy context."""

    @abstractmethod
    def generate(self, question: str, context: list[SearchResult]) -> str:
        """Return an answer using only the supplied retrieved context."""
