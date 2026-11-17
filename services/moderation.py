"""Naive advertisement moderation rules."""

from repositories.predictions import PredictionRecord, PredictionRepository
from schemas.prediction import PredictionRequest


class ModerationService:
    def __init__(self, repository: PredictionRepository) -> None:
        self.repository = repository

    def predict(self, item: PredictionRequest) -> bool:
        has_violations = not item.is_verified_seller and item.images_qty == 0
        self.repository.save(
            PredictionRecord(item_id=item.item_id, has_violations=has_violations)
        )
        return has_violations
