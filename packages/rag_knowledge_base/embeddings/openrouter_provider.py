
import os
import time

import httpx

from packages.rag_knowledge_base.embeddings.base import EmbeddingProvider


class OpenRouterEmbeddingProvider(EmbeddingProvider):
    """Generate embeddings through OpenRouter's OpenAI-compatible API."""

    API_URL = "https://openrouter.ai/api/v1/embeddings"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "openai/text-embedding-3-small",
        dimensions: int = 1536,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured")

        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        self.model = model
        self.dimensions = dimensions
        self.timeout = timeout
        self.max_retries = max_retries

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("text must not be empty")
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise ValueError("texts must not contain empty strings")

        payload = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimensions,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        self.API_URL,
                        headers=headers,
                        json=payload,
                    )

                if response.status_code in (429, 500, 502, 503, 504):
                    if attempt < self.max_retries:
                        time.sleep(2**attempt)
                        continue

                response.raise_for_status()
                result = response.json()
                items = result.get("data")

                if not isinstance(items, list) or len(items) != len(texts):
                    raise RuntimeError(
                        "Embedding API returned an unexpected number of vectors"
                    )

                items.sort(key=lambda item: item["index"])
                vectors = [item["embedding"] for item in items]

                if any(len(vector) != self.dimensions for vector in vectors):
                    raise RuntimeError(
                        "Embedding API returned vectors with unexpected dimensions"
                    )

                return vectors

            except httpx.HTTPStatusError as exc:
                # Don't include response bodies; they may contain sensitive details.
                raise RuntimeError(
                    f"Embedding API returned HTTP {exc.response.status_code}"
                ) from None
            except httpx.RequestError as exc:
                if attempt < self.max_retries:
                    time.sleep(2**attempt)
                    continue
                raise RuntimeError(
                    f"Could not reach the embedding API ({type(exc).__name__})"
                ) from None

        raise RuntimeError("Embedding request failed after retries")
