"""Response Models."""

from pydantic import BaseModel


# ======================================================================
class PingResponse(BaseModel):
    """Response of GET /ping endpoint."""

    message: str


# ======================================================================
class PredictResponse(BaseModel):
    """Response of POST /predict endpoint."""

    is_italian: bool
