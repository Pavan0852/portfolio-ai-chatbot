
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Provider-independent interface for text embeddings."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Convert a single text into an embedding vector."""
        raise NotImplementedError

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Convert multiple texts into embedding vectors."""
        raise NotImplementedError
