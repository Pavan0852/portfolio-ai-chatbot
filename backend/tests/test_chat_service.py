
import httpx
import pytest

from backend.app.core.config import Settings
from backend.app.schemas.chat import ChatRequest
from backend.app.services.chat_service import ChatService
from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)


def make_document() -> KnowledgeDocument:
    return KnowledgeDocument(
        id="incidentpilot-1",
        content="IncidentPilot uses FastAPI, Next.js, Python, and LangGraph.",
        metadata=DocumentMetadata(
            source="projects/incidentpilot.md",
            category="project",
            title="IncidentPilot",
        ),
    )


class FakeRetriever:
    def __init__(self, documents=None):
        self.documents = documents if documents is not None else [make_document()]
        self.last_query = None
        self.last_limit = None

    def retrieve(self, query: str, limit: int = 5):
        self.last_query = query
        self.last_limit = limit
        return self.documents[:limit]

    def retrieve_with_scores(self, query: str, limit: int = 5):
        self.last_query = query
        self.last_limit = limit

        # Allow tests to provide explicit (document, score) pairs.
        if self.documents and isinstance(self.documents[0], tuple):
            return self.documents[:limit]

        # Default fixture represents a relevant portfolio result.
        return [
            (document, 0.65)
            for document in self.documents[:limit]
        ]


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request(
                "POST",
                "https://test.example.com/v1/chat/completions",
            )

            response = httpx.Response(
                self.status_code,
                request=request,
            )

            raise httpx.HTTPStatusError(
                "Mock HTTP error",
                request=request,
                response=response,
            )

    def json(self):
        return self.payload


class FakeHttpClient:
    def __init__(self, response=None):
        self.response = response or FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": (
                                "IncidentPilot uses FastAPI, Next.js, "
                                "Python, and LangGraph."
                            )
                        }
                    }
                ]
            }
        )
        self.last_request = None

    def post(self, url, **kwargs):
        self.last_request = {
            "url": url,
            **kwargs,
        }
        return self.response


def make_service(documents=None, response=None):
    settings = Settings(
        _env_file=None,
        llm_provider="google",
        llm_api_key="test-api-key",
        llm_model="test-model",
        llm_base_url="https://test.example.com/v1",
        llm_timeout=5,
        embedding_provider="openrouter",
        embedding_api_key="test-embedding-key",
        embedding_model="openai/text-embedding-3-small",
        retrieval_min_score=0.45,
        qdrant_url=None,
        qdrant_api_key=None,
    )

    retriever = FakeRetriever(documents)
    client = FakeHttpClient(response)

    service = ChatService(
        settings=settings,
        retriever=retriever,
        http_client=client,
    )

    return service, retriever, client


def test_answer_returns_generated_text_and_sources():
    service, retriever, client = make_service()

    try:
        result = service.answer(
            ChatRequest(
                message="What technologies does IncidentPilot use?"
            )
        )

        assert "FastAPI" in result.answer
        assert result.sources[0].source == "projects/incidentpilot.md"
        assert retriever.last_limit == 3

        assert client.last_request["json"]["model"] == "test-model"

        assert (
            client.last_request["headers"]["Authorization"]
            == "Bearer test-api-key"
        )

        assert (
            client.last_request["url"]
            == "https://test.example.com/v1/chat/completions"
        )

    finally:
        service.close()


def test_no_documents_returns_fallback_without_generation():
    service, _, client = make_service(documents=[])

    try:
        result = service.answer(
            ChatRequest(message="Tell me about the portfolio")
        )

        assert "couldn't find enough information" in result.answer
        assert result.sources == []
        assert client.last_request is None

    finally:
        service.close()


def test_upstream_http_error_is_sanitized():
    response = FakeResponse(
        {"error": "sensitive upstream details"},
        status_code=429,
    )

    service, _, _ = make_service(response=response)

    try:
        with pytest.raises(
            RuntimeError,
            match="HTTP 429",
        ) as exc_info:
            service.answer(
                ChatRequest(message="Tell me about IncidentPilot")
            )

        assert "sensitive upstream details" not in str(exc_info.value)
        assert "test-api-key" not in str(exc_info.value)

    finally:
        service.close()


def test_empty_model_response_is_rejected():
    response = FakeResponse(
        {
            "choices": [
                {
                    "message": {
                        "content": "   ",
                    }
                }
            ]
        }
    )

    service, _, _ = make_service(response=response)

    try:
        with pytest.raises(
            RuntimeError,
            match="Language model returned an empty answer",
        ):
            service.answer(
                ChatRequest(message="Tell me about IncidentPilot")
            )

    finally:
        service.close()


def test_low_relevance_returns_fallback_without_generation():
    document = make_document()
    service, _, client = make_service(documents=[])

    try:
        service.retriever.documents = [(document, 0.1346)]

        result = service.answer(
            ChatRequest(
                message="What is the weather in Hyderabad?"
            )
        )

        assert "couldn't find enough information" in result.answer
        assert result.sources == []
        assert client.last_request is None

    finally:
        service.close()
