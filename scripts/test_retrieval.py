
from dotenv import load_dotenv

from packages.rag_knowledge_base.embeddings.openrouter_provider import (
    OpenRouterEmbeddingProvider,
)
from packages.rag_knowledge_base.retrieval.context_builder import ContextBuilder
from packages.rag_knowledge_base.retrieval.retriever import KnowledgeRetriever
from packages.rag_knowledge_base.vector_store.qdrant_store import (
    QdrantVectorStore,
)


def main() -> None:
    load_dotenv()

    embedder = OpenRouterEmbeddingProvider()
    store = QdrantVectorStore()

    try:
        retriever = KnowledgeRetriever(
            embedder=embedder,
            vector_store=store,
        )

        questions = [
            "What is Pavan's experience with Agentic AI?",
            "What technologies were used to build IncidentPilot?",
            "Tell me about the AI Research Scout project.",
        ]

        context_builder = ContextBuilder()

        for question in questions:
            print(f"\n{'=' * 80}")
            print(f"QUESTION: {question}")

            documents = retriever.retrieve(question, limit=3)

            if not documents:
                print("No relevant documents found.")
                continue

            for rank, document in enumerate(documents, start=1):
                print(
                    f"\n{rank}. {document.metadata.title} "
                    f"[source={document.metadata.source}]"
                )
                print(document.content[:400])

            context = context_builder.build(documents)
            print("\n--- BUILT CONTEXT ---")
            print(context[:1500])

    finally:
        store.close()


if __name__ == "__main__":
    main()
