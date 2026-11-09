
import os
from collections.abc import Sequence
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)
from packages.rag_knowledge_base.vector_store.base import VectorStore


class QdrantVectorStore(VectorStore):
    """Qdrant Cloud implementation of the vector-store interface."""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_name: str | None = None,
        vector_size: int = 1536,
        timeout: float = 15.0,
    ) -> None:
        self.url = url or os.getenv("QDRANT_URL")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = (
            collection_name
            or os.getenv("QDRANT_COLLECTION")
            or "portfolio_knowledge"
        )

        if not self.url:
            raise ValueError("QDRANT_URL is not configured")
        if not self.api_key:
            raise ValueError("QDRANT_API_KEY is not configured")
        if vector_size <= 0:
            raise ValueError("vector_size must be greater than zero")

        self.vector_size = vector_size
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            timeout=timeout,
        )

    def ensure_collection(self) -> None:
        """Create the collection only when it is absent."""
        if self.client.collection_exists(self.collection_name):
            info = self.client.get_collection(self.collection_name)
            configured_size = info.config.params.vectors.size

            if configured_size != self.vector_size:
                raise ValueError(
                    f"Collection '{self.collection_name}' has vector size "
                    f"{configured_size}, expected {self.vector_size}"
                )
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    def upsert(
        self,
        documents: list[KnowledgeDocument],
        vectors: list[list[float]],
    ) -> None:
        if len(documents) != len(vectors):
            raise ValueError("Each document must have exactly one vector")

        if not documents:
            return

        points = []

        for document, vector in zip(documents, vectors, strict=True):
            if len(vector) != self.vector_size:
                raise ValueError(
                    f"Document '{document.id}' has a vector of length "
                    f"{len(vector)}; expected {self.vector_size}"
                )

            point_id = str(uuid5(NAMESPACE_URL, document.id))

            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "document_id": document.id,
                        "content": document.content,
                        "metadata": document.metadata.model_dump(),
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )


    def search_with_scores(
        self,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[tuple[KnowledgeDocument, float]]:
        """Return relevant documents with their Qdrant similarity scores."""
        if len(query_vector) != self.vector_size:
            raise ValueError(
                f"Query vector has length {len(query_vector)}; "
                f"expected {self.vector_size}"
            )
        if limit < 1:
            raise ValueError("limit must be at least 1")

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        ).points

        scored_documents: list[tuple[KnowledgeDocument, float]] = []

        for point in results:
            payload = point.payload or {}
            metadata = payload.get("metadata")
            content = payload.get("content")

            if not metadata or not content:
                continue

            document = KnowledgeDocument(
                id=payload.get("document_id", str(point.id)),
                content=content,
                metadata=DocumentMetadata.model_validate(metadata),
            )
            scored_documents.append((document, float(point.score)))

        return scored_documents

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[KnowledgeDocument]:
        """Return documents without exposing similarity scores."""
        return [
            document
            for document, _score in self.search_with_scores(
                query_vector=query_vector,
                limit=limit,
            )
        ]

    def close(self) -> None:
        """Release the client's HTTP resources."""
        self.client.close()
