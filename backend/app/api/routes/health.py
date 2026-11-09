
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health/live")
def liveness() -> dict[str, str]:
    """Check whether the API process is running."""
    return {"status": "ok"}


@router.get("/health/ready")
def readiness() -> dict[str, str]:
    """Report application readiness during the foundation stage."""
    return {"status": "ok", "stage": "foundation"}
