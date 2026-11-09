
import pytest

from packages.rag_knowledge_base.embeddings.base import EmbeddingProvider


def test_embedding_provider_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        EmbeddingProvider()


def test_embedding_provider_requires_both_methods() -> None:
    class IncompleteProvider(EmbeddingProvider):
        def embed_text(self, text: str) -> list[float]:
            return [0.1, 0.2, 0.3]

    with pytest.raises(TypeError):
        IncompleteProvider()
