"""Ping endpoint."""

from fastapi import APIRouter, status

from italiclas.api.models.responses import PingResponse
from italiclas.config import info

router = APIRouter()


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    response_model=PingResponse,
)
async def ping() -> PingResponse:
    """Ping to check if it is up and running, and get its version."""
    return PingResponse(message=info.version)
