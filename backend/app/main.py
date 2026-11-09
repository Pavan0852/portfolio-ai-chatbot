
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.chat import router as chat_router
from backend.app.api.routes.health import router as health_router
from backend.app.core.config import get_settings

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.core.rate_limit import limiter


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="API for the Portfolio AI Chatbot.",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    )

    application.include_router(health_router)
    application.include_router(chat_router)


    #/Application rate limiting/

    application.state.limiter = limiter
    application.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,
    )

    return application


app = create_app()
