
import pytest
from pydantic import ValidationError

from packages.rag_knowledge_base.chunking.text_chunker import TextChunker
from packages.rag_knowledge_base.config import ChunkingConfig
from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)


def make_document(content: str) -> KnowledgeDocument:
    return KnowledgeDocument(
        id="profile",
        content=content,
        metadata=DocumentMetadata(
            source="profile.md",
            category="profile",
            title="Profile",
        ),
    )


def test_short_document_produces_one_chunk() -> None:
    chunker = TextChunker(ChunkingConfig(chunk_size=100, chunk_overlap=20))
    chunks = chunker.chunk_document(make_document("AI engineer building useful products."))

    assert len(chunks) == 1
    assert chunks[0].metadata.total_chunks == 1
    assert chunks[0].metadata.chunk_index == 0


def test_long_document_is_split_and_metadata_preserved() -> None:
    text = " ".join(["portfolio"] * 80)
    chunker = TextChunker(ChunkingConfig(chunk_size=100, chunk_overlap=20))

    chunks = chunker.chunk_document(make_document(text))

    assert len(chunks) > 1
    assert all(chunk.metadata.source == "profile.md" for chunk in chunks)
    assert all(chunk.metadata.total_chunks == len(chunks) for chunk in chunks)
    assert [chunk.metadata.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_empty_text_returns_no_chunks() -> None:
    # KnowledgeDocument disallows empty content, so test whitespace-only content
    # by creating a valid model and then supplying whitespace as the content.
    document = make_document("temporary content")
    document.content = "   "

    chunker = TextChunker()
    assert chunker.chunk_document(document) == []


def test_invalid_overlap_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ChunkingConfig(chunk_size=100, chunk_overlap=100)




def test_chunks_do_not_start_or_end_mid_word() -> None:
    words = [
        "alpha", "bravo", "charlie", "delta", "echo",
        "foxtrot", "golf", "hotel", "india", "juliet",
        "kilo", "lima", "mike", "november", "oscar",
        "papa", "quebec", "romeo", "sierra", "tango",
    ]
    text = " ".join(words)

    chunker = TextChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=20)
    )
    chunks = chunker.chunk_document(make_document(text))

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk.content == chunk.content.strip()
        assert chunk.content in text

    # Every chunk starts and ends at a complete word boundary.
    for chunk in chunks:
        assert chunk.content.split()[0] in words
        assert chunk.content.split()[-1] in words



def test_chunk_ids_and_metadata_are_consistent() -> None:
    chunker = TextChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=20)
    )
    chunks = chunker.chunk_document(
        make_document(" ".join(["portfolio"] * 50))
    )

    assert len(chunks) > 1
    assert [chunk.id for chunk in chunks] == [
        f"profile-chunk-{index}" for index in range(len(chunks))
    ]
    assert all(
        chunk.metadata.total_chunks == len(chunks) for chunk in chunks
    )



def test_paragraph_boundary_is_preferred() -> None:
    first = "First paragraph. " * 4
    second = "Second paragraph. " * 4
    text = first.strip() + "\n\n" + second.strip()

    chunker = TextChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=10)
    )
    chunks = chunker.chunk_document(make_document(text))

    assert len(chunks) >= 2
    assert chunks[0].content.startswith("First paragraph.")
    assert chunks[-1].content.endswith("paragraph.")


def test_chunk_content_is_preserved_with_overlap() -> None:
    words = [f"word{i}" for i in range(100)]
    text = " ".join(words)

    chunker = TextChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=20)
    )
    chunks = chunker.chunk_document(make_document(text))

    assert len(chunks) > 1

    # Every original word should occur in at least one chunk.
    combined = " ".join(chunk.content for chunk in chunks)
    for word in words:
        assert word in combined

    # Consecutive chunks should have some intentional overlap.
    assert any(
        set(left.content.split()) & set(right.content.split())
        for left, right in zip(chunks, chunks[1:])
    )



def test_markdown_headings_stay_with_their_sections() -> None:
    text = (
        "# Profile\n"
        "Profile introduction.\n\n"
        "## Technical Skills\n"
        "Python and LangChain.\n\n"
        "## Education\n"
        "Mechanical engineering degree."
    )

    chunks = TextChunker().chunk_document(make_document(text))

    combined = "\n".join(chunk.content for chunk in chunks)

    assert "# Profile" in combined
    assert "## Technical Skills" in combined
    assert "## Education" in combined
    assert "Python and LangChain." in combined
    assert "Mechanical engineering degree." in combined


def test_oversized_markdown_section_repeats_its_heading() -> None:
    body = " ".join(["engineering"] * 150)
    document = make_document(f"## Experience\n\n{body}")

    chunker = TextChunker(
        ChunkingConfig(chunk_size=100, chunk_overlap=20)
    )
    chunks = chunker.chunk_document(document)

    assert len(chunks) > 1
    assert all(
        chunk.content.startswith("## Experience")
        for chunk in chunks
    )
    assert all(chunk.metadata.total_chunks == len(chunks) for chunk in chunks)


def test_heading_only_section_merges_with_following_content() -> None:
    document = make_document(
        "# Profile\n\n"
        "## Professional Summary\n"
        "AI engineer building AI-powered applications."
    )

    chunks = TextChunker().chunk_document(document)

    assert len(chunks) == 1
    assert "# Profile" in chunks[0].content
    assert "## Professional Summary" in chunks[0].content
    assert "AI engineer building AI-powered applications." in chunks[0].content


def test_large_sections_remain_separate() -> None:
    first = "# Profile\n\n" + ("Profile information. " * 30)
    second = "## Education\n\n" + ("Education information. " * 30)

    document = make_document(first + "\n\n" + second)
    chunks = TextChunker().chunk_document(document)

    assert len(chunks) > 1
    assert all(chunk.content.strip() for chunk in chunks)
