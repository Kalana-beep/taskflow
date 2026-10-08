"""Health check route."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health Check",
    description="Operational health probe to confirm service readiness and liveness.",
)
async def health_check() -> dict[str, str]:
    """Return healthy status."""
    return {"status": "healthy"}
