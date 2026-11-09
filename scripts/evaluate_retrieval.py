
from collections import defaultdict

from backend.app.core.config import get_settings
from packages.rag_knowledge_base.embeddings.openrouter_provider import (
    OpenRouterEmbeddingProvider,
)
from packages.rag_knowledge_base.retrieval.retriever import KnowledgeRetriever
from packages.rag_knowledge_base.vector_store.qdrant_store import (
    QdrantVectorStore,
)


# Each query has an expected category and relevant knowledge topics.
EVALUATION_CASES = [
    {
        "question": "What technologies were used to build IncidentPilot?",
        "expected_topics": ["incidentpilot"],
        "should_be_relevant": True,
    },
    {
        "question": "Tell me about the AI Research Scout project.",
        "expected_topics": ["ai research scout"],
        "should_be_relevant": True,
    },
    {
        "question": "What is Pavan's experience with Agentic AI?",
        "expected_topics": ["profile", "experience"],
        "should_be_relevant": True,
    },
    {
        "question": "What are Pavan's technical skills?",
        "expected_topics": ["profile", "experience"],
        "should_be_relevant": True,
    },
    {
        "question": "What is Pavan's educational background?",
        "expected_topics": ["profile", "education"],
        "should_be_relevant": True,
    },
    {
        "question": "What is the weather in Hyderabad?",
        "expected_topics": [],
        "should_be_relevant": False,
    },
    {
        "question": "Who won the latest football world championship?",
        "expected_topics": [],
        "should_be_relevant": False,
    },
    {
        "question": "How do I bake a chocolate cake?",
        "expected_topics": [],
        "should_be_relevant": False,
    },
]


def main() -> None:
    settings = get_settings()

    if not settings.llm_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    if not settings.qdrant_url or not settings.qdrant_api_key:
        raise RuntimeError("Qdrant Cloud configuration is incomplete")

    vector_store = QdrantVectorStore(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
    )

    embedder = OpenRouterEmbeddingProvider(
        api_key=settings.llm_api_key,
        model=settings.embedding_model,
    )

    retriever = KnowledgeRetriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    total = len(EVALUATION_CASES)
    relevant_cases = 0
    irrelevant_cases = 0
    topic_matches = 0
    topic_checks = 0
    reciprocal_ranks = []

    try:
        print(f"Retrieval threshold: {settings.retrieval_min_score:.2f}")
        print(f"Evaluation cases: {total}\n")

        for index, case in enumerate(EVALUATION_CASES, start=1):
            results = retriever.retrieve_with_scores(
                case["question"],
                limit=5,
            )

            filtered = [
                (document, score)
                for document, score in results
                if score >= settings.retrieval_min_score
            ]

            expected_relevant = case["should_be_relevant"]
            passed = bool(filtered) == expected_relevant

            if expected_relevant and filtered:
                relevant_cases += 1
            elif not expected_relevant and not filtered:
                irrelevant_cases += 1

            expected_topics = case["expected_topics"]
            matched_rank = None

            for rank, (document, _) in enumerate(filtered, start=1):
                title = document.metadata.title.lower()
                source = document.metadata.source.lower()
                searchable = f"{title} {source}"

                if any(topic in searchable for topic in expected_topics):
                    matched_rank = rank
                    break

            if expected_relevant:
                topic_checks += 1
                if matched_rank is not None:
                    topic_matches += 1
                    reciprocal_ranks.append(1 / matched_rank)
                else:
                    reciprocal_ranks.append(0.0)

            status = "PASS" if passed else "FAIL"

            print(f"[{index}/{total}] {status}: {case['question']}")
            print(
                f"  Top score: "
                f"{results[0][1]:.4f}" if results else "  No results"
            )
            print(f"  Above threshold: {len(filtered)}")
            if expected_relevant:
                print(f"  Expected topic found: {matched_rank is not None}")
            print()

        relevant_recall = (
            relevant_cases
            / sum(case["should_be_relevant"] for case in EVALUATION_CASES)
        )
        irrelevant_rejection = (
            irrelevant_cases
            / sum(not case["should_be_relevant"] for case in EVALUATION_CASES)
        )
        topic_hit_rate = topic_matches / topic_checks if topic_checks else 0.0
        mean_reciprocal_rank = (
            sum(reciprocal_ranks) / len(reciprocal_ranks)
            if reciprocal_ranks
            else 0.0
        )

        print("=== Summary ===")
        print(f"Relevant-query acceptance: {relevant_recall:.1%}")
        print(f"Out-of-scope rejection:     {irrelevant_rejection:.1%}")
        print(f"Expected-topic hit rate:    {topic_hit_rate:.1%}")
        print(f"Mean reciprocal rank:       {mean_reciprocal_rank:.3f}")

    finally:
        vector_store.close()


if __name__ == "__main__":
    main()
