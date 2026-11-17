"""A replaceable repository with an in-memory implementation."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PredictionRecord:
    item_id: int
    has_violations: bool


class PredictionRepository(Protocol):
    def save(self, record: PredictionRecord) -> None: ...


class InMemoryPredictionRepository:
    def __init__(self) -> None:
        self._predictions: dict[int, PredictionRecord] = {}

    def save(self, record: PredictionRecord) -> None:
        self._predictions[record.item_id] = record

    def get(self, item_id: int) -> PredictionRecord | None:
        return self._predictions.get(item_id)
