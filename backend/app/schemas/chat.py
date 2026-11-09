
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message must not be blank")
        return value


class ChatSource(BaseModel):
    title: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)
