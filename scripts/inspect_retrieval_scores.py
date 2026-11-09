
from dotenv import load_dotenv

from packages.rag_knowledge_base.embeddings.openrouter_provider import (
    OpenRouterEmbeddingProvider,
)
from packages.rag_knowledge_base.retrieval.retriever import KnowledgeRetriever
from packages.rag_knowledge_base.vector_store.qdrant_store import (
    QdrantVectorStore,
)


def main() -> None:
    load_dotenv()

    embedder = OpenRouterEmbeddingProvider()
    store = QdrantVectorStore()
    retriever = KnowledgeRetriever(embedder, store)

    questions = [
        "What technologies were used to build IncidentPilot?",
        "Tell me about the AI Research Scout project.",
        "What is Pavan's experience with Agentic AI?",
        "What is the weather in Hyderabad?",
        "What is Pavan's educational background?",
        "What degree is Pavan pursuing?",
        "What did Pavan study at university?",
    ]

    try:
        for question in questions:
            print(f"\nQuestion: {question}")

            for document, score in retriever.retrieve_with_scores(
                question,
                limit=3,
            ):
                print(
                    f"  score={score:.4f} | "
                    f"{document.metadata.title} | "
                    f"{document.metadata.source}"
                )
    finally:
        store.close()


if __name__ == "__main__":
    main()
