
from backend.app.core.config import get_settings
from packages.rag_knowledge_base.embeddings.gemini_provider import (
    GeminiEmbeddingProvider,
)
from packages.rag_knowledge_base.vector_store.qdrant_store import (
    QdrantVectorStore,
)
from packages.rag_knowledge_base.retrieval.retriever import (
    KnowledgeRetriever,
)


def main():
    settings = get_settings()

    embedder = GeminiEmbeddingProvider(
        api_key=settings.llm_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )

    store = QdrantVectorStore(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
        vector_size=settings.embedding_dimensions,
    )

    retriever = KnowledgeRetriever(
        embedder=embedder,
        vector_store=store,
    )

    questions = [
        "What AI projects has Pavan developed?",
        "Explain the architecture and workflow of IncidentPilot.",
        "What is AI Research Scout?",
        "What are Pavan's technical skills in cloud and DevOps?",
        "What is Pavan's educational background?",
        "What recommendation system has Pavan built?",
        "What technologies does Pavan use for Agentic AI development?",
    ]

    try:
        for index, question in enumerate(questions, start=1):
            print("\n" + "=" * 75)
            print(f"QUESTION {index}: {question}")
            print("=" * 75)

            results = retriever.retrieve_with_scores(
                question,
                limit=3,
            )

            if not results:
                print("No documents retrieved.")
                continue

            for rank, (document, score) in enumerate(results, start=1):
                print(
                    f"\nRank: {rank}"
                    f"\nScore: {score:.4f}"
                    f"\nSource: {document.metadata.source}"
                    f"\nTitle: {document.metadata.title}"
                )

    finally:
        store.close()


if __name__ == "__main__":
    main()
