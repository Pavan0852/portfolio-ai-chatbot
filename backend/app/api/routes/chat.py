
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.chat_service import ChatService


from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter
from slowapi.middleware import SlowAPIMiddleware

from backend.app.core.rate_limit import limiter

router = APIRouter(prefix="/api", tags=["chat"])


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService()

@limiter.limit("10/minute")
@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        return service.answer(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service configuration is incomplete.",
        ) from exc
    except RuntimeError as exc:
        # The service deliberately sanitizes upstream error messages.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
