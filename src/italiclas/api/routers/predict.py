"""Predict endpoint."""

from fastapi import APIRouter, status

from italiclas import ml
from italiclas.api.models.payloads import PredictPayload
from italiclas.api.models.responses import PredictResponse
from italiclas.logger import logger

router = APIRouter()


@router.post(
    "/predict",
    status_code=status.HTTP_200_OK,
    response_model=PredictResponse,
)
async def predict(payload: PredictPayload) -> PredictResponse:
    """Predict if the input language is Italian."""
    prediction = ml.predict(payload.text)
    response = PredictResponse(is_italian=prediction)
    logger.info("%s -> %s", payload, response)
    return response
