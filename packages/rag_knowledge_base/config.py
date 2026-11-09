
from pydantic import BaseModel, Field, model_validator


class ChunkingConfig(BaseModel):
    chunk_size: int = Field(default=800, ge=100)
    chunk_overlap: int = Field(default=80, ge=0)

    @model_validator(mode="after")
    def validate_overlap(self) -> "ChunkingConfig":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return self


class EmbeddingConfig(BaseModel):
    provider: str = Field(default="openrouter", min_length=1)
    model: str = Field(
        default="openai/text-embedding-3-small",
        min_length=1,
    )
    dimensions: int = Field(default=1536, gt=0)
    batch_size: int = Field(default=32, ge=1, le=128)