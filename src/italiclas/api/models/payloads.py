"""Payload Models."""

from pydantic import BaseModel, Field


# ======================================================================
class PredictPayload(BaseModel):
    """Payload for POST /predict endpoint."""

    text: str = Field(
        ..., json_schema_extra={"example": "questa è una frase in italiano!"},
    )
