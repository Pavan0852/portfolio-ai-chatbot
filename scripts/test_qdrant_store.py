
from dotenv import load_dotenv
from qdrant_client import models

from packages.rag_knowledge_base.embeddings.openrouter_provider import (
    OpenRouterEmbeddingProvider,
)
from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)
from packages.rag_knowledge_base.vector_store.qdrant_store import (
    QdrantVectorStore,
)

load_dotenv()

store = QdrantVectorStore()
embedder = OpenRouterEmbeddingProvider()

test_document = KnowledgeDocument(
    id="qdrant-cloud-smoke-test",
    content=(
        "Integration test: the portfolio chatbot uses FastAPI, "
        "OpenRouter embeddings, and Qdrant Cloud for semantic retrieval."
    ),
    metadata=DocumentMetadata(
        source="integration-test",
        category="test",
        title="Qdrant Cloud Integration Test",
    ),
)

point_id = None

try:
    # Create the collection if needed; do not recreate existing collections.
    store.ensure_collection()
    print("Collection ready:", store.collection_name)

    # Generate and store the test document's embedding.
    vector = embedder.embed_text(test_document.content)
    store.upsert([test_document], [vector])
    print("Test document uploaded successfully")

    # Search using a natural-language query.
    query_vector = embedder.embed_text(
        "Which technologies power the portfolio chatbot's semantic search?"
    )
    results = store.search(query_vector, limit=3)

    match = next(
        (document for document in results
         if document.id == test_document.id),
        None,
    )

    if match is None:
        raise RuntimeError("The uploaded test document was not retrieved")

    print("Semantic search: successful")
    print("Retrieved document:", match.id)
    print("Retrieved content:", match.content)
    print("Integration test: PASSED")

finally:
    # Remove only the temporary test point; preserve the collection.
    try:
        point_id = str(
            __import__("uuid").uuid5(
                __import__("uuid").NAMESPACE_URL,
                test_document.id,
            )
        )
        store.client.delete(
            collection_name=store.collection_name,
            points_selector=models.PointIdsList(points=[point_id]),
            wait=True,
        )
        print("Temporary test point cleaned up")
    finally:
        store.close()
