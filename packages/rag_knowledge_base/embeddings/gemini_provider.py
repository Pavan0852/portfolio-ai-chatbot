
import os
import time

import httpx

from packages.rag_knowledge_base.embeddings.base import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Generate document and query embeddings using Google Gemini."""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-embedding-2",
        dimensions: int = 768,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("LLM_API_KEY")
        )

        if not self.api_key:
            raise ValueError("Gemini API key is not configured")

        if dimensions not in (768, 1536, 3072):
            raise ValueError(
                "Gemini Embedding 2 supports dimensions 768, 1536, or 3072"
            )

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        self.model = model
        self.dimensions = dimensions
        self.timeout = timeout
        self.max_retries = max_retries

    def embed_text(self, text: str) -> list[float]:
        """Generate a search-query embedding."""

        if not text.strip():
            raise ValueError("text must not be empty")

        prepared_text = f"task: search result | query: {text.strip()}"

        return self._embed(prepared_text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate individual document embeddings."""

        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError("texts must not contain empty strings")

        vectors = []

        for text in texts:
            prepared_text = f"title: none | text: {text.strip()}"
            vectors.append(self._embed(prepared_text))

        return vectors

    def _embed(self, text: str) -> list[float]:
        """Call the Gemini embedContent REST API."""

        url = f"{self.API_URL}/{self.model}:embedContent"

        payload = {
            "content": {
                "parts": [
                    {
                        "text": text,
                    }
                ]
            },
            "output_dimensionality": self.dimensions,
        }

        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code in (429, 500, 502, 503, 504):
                    if attempt < self.max_retries:
                        time.sleep(2**attempt)
                        continue

                response.raise_for_status()

                result = response.json()
                embedding = result.get("embedding", {})
                vector = embedding.get("values")

                if not isinstance(vector, list):
                    raise RuntimeError(
                        "Gemini returned an invalid embedding response"
                    )

                if len(vector) != self.dimensions:
                    raise RuntimeError(
                        f"Gemini returned {len(vector)} dimensions; "
                        f"expected {self.dimensions}"
                    )

                if any(
                    not isinstance(value, (int, float))
                    for value in vector
                ):
                    raise RuntimeError(
                        "Gemini returned non-numeric embedding values"
                    )

                return [float(value) for value in vector]

            except httpx.HTTPStatusError as exc:
                raise RuntimeError(
                    f"Gemini embedding API returned HTTP "
                    f"{exc.response.status_code}"
                ) from None

            except httpx.TimeoutException:
                if attempt < self.max_retries:
                    time.sleep(2**attempt)
                    continue

                raise RuntimeError(
                    "Gemini embedding request timed out"
                ) from None

            except httpx.RequestError as exc:
                if attempt < self.max_retries:
                    time.sleep(2**attempt)
                    continue

                raise RuntimeError(
                    f"Could not reach Gemini embedding API "
                    f"({type(exc).__name__})"
                ) from None

        raise RuntimeError(
            "Gemini embedding request failed after retries"
        )
