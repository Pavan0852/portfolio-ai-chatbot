
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata used to identify and filter knowledge documents."""

    source: str = Field(
        ...,
        min_length=1,
        description="Source filename or logical source identifier.",
    )
    category: str = Field(
        ...,
        min_length=1,
        description="Knowledge category, such as profile, experience, skills, or project.",
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Human-readable document title.",
    )
    chunk_index: int = Field(default=0, ge=0)
    total_chunks: int = Field(default=1, ge=1)


class KnowledgeDocument(BaseModel):
    """A text document or chunk used by the portfolio RAG system."""

    id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    metadata: DocumentMetadata
