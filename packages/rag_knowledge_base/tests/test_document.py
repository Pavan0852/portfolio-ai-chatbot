
import pytest
from pydantic import ValidationError

from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)


def test_valid_knowledge_document() -> None:
    document = KnowledgeDocument(
        id="incidentpilot-0",
        content="IncidentPilot uses a multi-agent incident analysis pipeline.",
        metadata=DocumentMetadata(
            source="incidentpilot.md",
            category="project",
            title="IncidentPilot",
        ),
    )

    assert document.id == "incidentpilot-0"
    assert document.metadata.source == "incidentpilot.md"
    assert document.metadata.chunk_index == 0
    assert document.metadata.total_chunks == 1


def test_empty_document_content_is_rejected() -> None:
    with pytest.raises(ValidationError):
        KnowledgeDocument(
            id="invalid-document",
            content="",
            metadata=DocumentMetadata(
                source="profile.md",
                category="profile",
                title="Profile",
            ),
        )


def test_negative_chunk_index_is_rejected() -> None:
    with pytest.raises(ValidationError):
        DocumentMetadata(
            source="profile.md",
            category="profile",
            title="Profile",
            chunk_index=-1,
        )
