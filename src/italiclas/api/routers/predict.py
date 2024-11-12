"""Predict endpoint."""

import asyncio

from fastapi import APIRouter, HTTPException, status

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
    logger.info("[API] POST /predict payload: %s", payload)
    try:
        prediction = ml.predict(payload.text)
    except FileNotFoundError as e:
        # if a race condition where the model could not be load is met
        # retrain the model
        async with asyncio.TaskGroup() as tg:
            tg.create_task(asyncio.to_thread(ml.train))
        raise HTTPException(
            status_code=503,
            detail="Internal Data Temporarily Unavailable",
        ) from e
    return PredictResponse(is_italian=prediction)
