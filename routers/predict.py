"""Prediction endpoint and its dependencies."""

from typing import Annotated

from fastapi import APIRouter, Depends

from repositories.predictions import InMemoryPredictionRepository
from schemas.prediction import ErrorResponse, PredictionRequest, ValidationErrorResponse
from services.moderation import ModerationService

router = APIRouter()
repository = InMemoryPredictionRepository()


def get_moderation_service() -> ModerationService:
    return ModerationService(repository)


@router.post(
    "/predict",
    response_model=bool,
    summary="Predict whether an advertisement has violations",
    description="Returns true if the seller is unverified and there are no images.",
    responses={
        400: {"model": ValidationErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def predict(
    item: PredictionRequest,
    service: Annotated[ModerationService, Depends(get_moderation_service)],
) -> bool:
    return service.predict(item)
