
import argparse
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from backend.app.core.config import get_settings
from packages.rag_knowledge_base.ingestion.pipeline import (
    KnowledgeIngestionPipeline,
)


def main() -> None:
    load_dotenv()
    settings = get_settings()

    parser = argparse.ArgumentParser(
        description="Preview or index portfolio knowledge for RAG."
    )
    parser.add_argument(
        "--knowledge-dir",
        type=Path,
        default=Path("knowledge"),
        help="Path to the Markdown knowledge directory.",
    )
    parser.add_argument(
        "--show-content",
        action="store_true",
        help="Print a short preview of each generated chunk.",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Generate Gemini embeddings and index chunks in Qdrant.",
    )
    args = parser.parse_args()

    knowledge_dir = args.knowledge_dir.resolve()
    pipeline = KnowledgeIngestionPipeline()
    chunks = pipeline.ingest(knowledge_dir)

    if not chunks:
        print(f"No knowledge chunks found in: {knowledge_dir}")
        return

    source_counts = Counter(chunk.metadata.source for chunk in chunks)

    print(f"\nKnowledge directory: {knowledge_dir}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Source files: {len(source_counts)}")

    print("\nChunks by source:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count}")

    if args.show_content:
        print("\nChunk previews:")
        for chunk in chunks:
            preview = " ".join(chunk.content.split())
            if len(preview) > 180:
                preview = preview[:177] + "..."

            print(
                f"\n[{chunk.id}] "
                f"category={chunk.metadata.category} "
                f"chunk={chunk.metadata.chunk_index + 1}/"
                f"{chunk.metadata.total_chunks}"
            )
            print(f"  {preview}")

    if not args.index:
        print("\nPreview only. Run with --index to store chunks in Qdrant.")
        return

    if settings.embedding_provider.lower() != "google":
        raise ValueError(
            "This ingestion script expects EMBEDDING_PROVIDER=google."
        )

    if not settings.llm_api_key:
        raise ValueError("LLM_API_KEY is not configured.")

    if not settings.qdrant_url or not settings.qdrant_api_key:
        raise ValueError("Qdrant Cloud configuration is incomplete.")

    from packages.rag_knowledge_base.embeddings.gemini_provider import (
        GeminiEmbeddingProvider,
    )
    from packages.rag_knowledge_base.vector_store.qdrant_store import (
        QdrantVectorStore,
    )

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

    try:
        print("\nIndex configuration:")
        print(f"  Embedding provider: {settings.embedding_provider}")
        print(f"  Embedding model: {settings.embedding_model}")
        print(f"  Vector dimensions: {settings.embedding_dimensions}")
        print(f"  Qdrant collection: {settings.qdrant_collection}")

        store.ensure_collection()

        batch_size = 32
        total = len(chunks)

        for start in range(0, total, batch_size):
            batch = chunks[start : start + batch_size]

            vectors = embedder.embed_texts(
                [document.content for document in batch]
            )

            if len(vectors) != len(batch):
                raise RuntimeError(
                    "Embedding count does not match document count."
                )

            store.upsert(batch, vectors)

            indexed = min(start + len(batch), total)
            print(f"Indexed {indexed}/{total} chunks")

        print(
            f"\nIndexing complete: {total} chunks stored in "
            f"'{store.collection_name}'."
        )

    finally:
        store.close()


if __name__ == "__main__":
    main()
