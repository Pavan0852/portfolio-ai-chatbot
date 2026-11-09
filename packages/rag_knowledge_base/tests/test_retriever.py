
import pytest

from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)
from packages.rag_knowledge_base.retrieval.context_builder import ContextBuilder
from packages.rag_knowledge_base.retrieval.retriever import KnowledgeRetriever


class FakeEmbedder:
    def __init__(self):
        self.last_query = None

    def embed_text(self, text: str) -> list[float]:
        self.last_query = text
        return [0.1, 0.2, 0.3]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeVectorStore:
    def __init__(self, documents):
        self.documents = documents
        self.last_query_vector = None
        self.last_limit = None

    def ensure_collection(self):
        pass

    def upsert(self, documents, vectors):
        pass

    def search(self, query_vector, limit=5):
        self.last_query_vector = query_vector
        self.last_limit = limit
        return self.documents[:limit]


def make_document(
    content="IncidentPilot uses FastAPI and LangGraph.",
    title="IncidentPilot",
):
    return KnowledgeDocument(
        id="test-1",
        content=content,
        metadata=DocumentMetadata(
            source="projects/incidentpilot.md",
            category="project",
            title=title,
        ),
    )


def test_retriever_embeds_query_and_searches_store():
    embedder = FakeEmbedder()
    document = make_document()
    store = FakeVectorStore([document])
    retriever = KnowledgeRetriever(embedder, store)

    results = retriever.retrieve(
        "  What technologies power IncidentPilot?  ",
        limit=3,
    )

    assert embedder.last_query == "What technologies power IncidentPilot?"
    assert store.last_query_vector == [0.1, 0.2, 0.3]
    assert store.last_limit == 3
    assert results == [document]


def test_retriever_rejects_empty_query():
    retriever = KnowledgeRetriever(FakeEmbedder(), FakeVectorStore([]))

    with pytest.raises(ValueError, match="Query must not be empty"):
        retriever.retrieve("   ")


def test_retriever_rejects_invalid_limit():
    retriever = KnowledgeRetriever(FakeEmbedder(), FakeVectorStore([]))

    with pytest.raises(ValueError, match="limit must be at least 1"):
        retriever.retrieve("IncidentPilot", limit=0)


def test_context_builder_includes_source_title_and_content():
    document = make_document()
    context = ContextBuilder().build([document])

    assert "projects/incidentpilot.md" in context
    assert "IncidentPilot" in context
    assert "FastAPI and LangGraph" in context


def test_context_builder_respects_character_limit():
    document = make_document(content="A" * 500)
    context = ContextBuilder().build([document], max_chars=100)

    assert len(context) <= 100
    assert context == ""


def test_context_builder_rejects_invalid_limit():
    with pytest.raises(ValueError, match="max_chars must be at least 1"):
        ContextBuilder().build([], max_chars=0)
