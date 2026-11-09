
from packages.rag_knowledge_base.embeddings.base import EmbeddingProvider
from packages.rag_knowledge_base.models.document import KnowledgeDocument
from packages.rag_knowledge_base.vector_store.base import VectorStore


class KnowledgeRetriever:
    """Retrieve relevant portfolio knowledge using semantic similarity."""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store

    @staticmethod
    def _validate_query(query: str, limit: int) -> str:
        """Validate and normalize retrieval inputs."""
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Query must not be empty")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        return normalized_query

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[KnowledgeDocument]:
        """Retrieve documents using the standard vector-store search."""
        normalized_query = self._validate_query(query, limit)
        query_vector = self.embedder.embed_text(normalized_query)

        return self.vector_store.search(
            query_vector=query_vector,
            limit=limit,
        )

    def retrieve_with_scores(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[KnowledgeDocument, float]]:
        """Retrieve knowledge chunks with their similarity scores."""
        normalized_query = self._validate_query(query, limit)
        query_vector = self.embedder.embed_text(normalized_query)

        search_with_scores = getattr(
            self.vector_store,
            "search_with_scores",
            None,
        )

        if not callable(search_with_scores):
            raise NotImplementedError(
                "The configured vector store does not support scored search"
            )

        return search_with_scores(
            query_vector=query_vector,
            limit=limit,
        )
