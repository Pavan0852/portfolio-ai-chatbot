
from abc import ABC, abstractmethod

from packages.rag_knowledge_base.models.document import KnowledgeDocument


class VectorStore(ABC):
    """Abstract interface for storing and retrieving knowledge vectors."""

    @abstractmethod
    def ensure_collection(self) -> None:
        """Create the collection if it does not already exist."""
        raise NotImplementedError

    @abstractmethod
    def upsert(
        self,
        documents: list[KnowledgeDocument],
        vectors: list[list[float]],
    ) -> None:
        """Insert or update documents and their corresponding vectors."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[KnowledgeDocument]:
        """Return the most relevant documents for a query vector."""
        raise NotImplementedError
