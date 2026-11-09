
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Portfolio AI Chatbot API"
    app_env: str = "development"
    log_level: str = "INFO"

    # Frontend CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Qdrant Cloud
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_collection: str = "portfolio_knowledge_gemini"

    # Google Gemini - Chat generation
    llm_provider: str = Field(
        default="google",
        validation_alias="LLM_PROVIDER",
    )

    llm_api_key: str | None = Field(
        default=None,
        validation_alias="LLM_API_KEY",
    )

    llm_model: str = Field(
        default="gemini-3.8-flash",
        validation_alias="LLM_MODEL",
    )

    llm_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai",
        validation_alias="LLM_BASE_URL",
    )

    llm_timeout: float = Field(
        default=45.0,
        validation_alias="LLM_TIMEOUT",
        gt=0,
    )

    # Google Gemini - Embeddings
    embedding_provider: str = Field(
        default="google",
        validation_alias="EMBEDDING_PROVIDER",
    )

    embedding_model: str = Field(
        default="gemini-embedding-2",
        validation_alias="EMBEDDING_MODEL",
    )

    embedding_dimensions: int = Field(
        default=768,
        validation_alias="EMBEDDING_DIMENSIONS",
        gt=0,
    )

    # RAG retrieval
    retrieval_min_score: float = Field(
        default=0.45,
        validation_alias="RETRIEVAL_MIN_SCORE",
        ge=-1.0,
        le=1.0,
    )

    # Environment configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
