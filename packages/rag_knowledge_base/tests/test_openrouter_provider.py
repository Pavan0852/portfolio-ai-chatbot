
import json

import httpx
import pytest

from packages.rag_knowledge_base.embeddings.openrouter_provider import (
    OpenRouterEmbeddingProvider,
)


def test_embed_texts_preserves_input_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/embeddings"
        assert request.headers["Authorization"] == "Bearer test-key"

        payload = json.loads(request.content)
        assert payload["model"] == "openai/text-embedding-3-small"
        assert payload["dimensions"] == 3
        assert payload["input"] == ["first", "second"]

        # Deliberately return vectors out of order.
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 1, "embedding": [0.4, 0.5, 0.6]},
                    {"index": 0, "embedding": [0.1, 0.2, 0.3]},
                ]
            },
            request=request,
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    def mocked_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "Client", mocked_client)

    provider = OpenRouterEmbeddingProvider(
        api_key="test-key",
        dimensions=3,
    )

    assert provider.embed_texts(["first", "second"]) == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]


def test_rejects_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        OpenRouterEmbeddingProvider(api_key=None)


def test_rejects_empty_text() -> None:
    provider = OpenRouterEmbeddingProvider(api_key="test-key")

    with pytest.raises(ValueError, match="empty"):
        provider.embed_text("   ")


def test_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError, match="dimensions"):
        OpenRouterEmbeddingProvider(api_key="test-key", dimensions=0)
