
from pathlib import Path

from packages.rag_knowledge_base.chunking.text_chunker import TextChunker
from packages.rag_knowledge_base.config import ChunkingConfig
from packages.rag_knowledge_base.ingestion.pipeline import (
    KnowledgeIngestionPipeline,
)


def test_pipeline_loads_and_chunks_knowledge(tmp_path: Path) -> None:
    knowledge_root = tmp_path / "knowledge"
    projects = knowledge_root / "projects"
    projects.mkdir(parents=True)

    (knowledge_root / "profile.md").write_text(
        "# Profile\n\n" + ("AI engineering and product development. " * 20),
        encoding="utf-8",
    )
    (projects / "incidentpilot.md").write_text(
        "# IncidentPilot\n\nA multi-agent incident analysis system.",
        encoding="utf-8",
    )

    pipeline = KnowledgeIngestionPipeline(
        chunker=TextChunker(
            ChunkingConfig(chunk_size=120, chunk_overlap=20)
        )
    )

    chunks = pipeline.ingest(knowledge_root)

    assert len(chunks) > 2
    assert any(chunk.metadata.source == "profile.md" for chunk in chunks)
    assert any(
        chunk.metadata.source == "projects/incidentpilot.md"
        for chunk in chunks
    )
    assert all(chunk.content.strip() for chunk in chunks)


def test_pipeline_handles_empty_knowledge_directory(tmp_path: Path) -> None:
    knowledge_root = tmp_path / "knowledge"
    knowledge_root.mkdir()

    chunks = KnowledgeIngestionPipeline().ingest(knowledge_root)

    assert chunks == []
