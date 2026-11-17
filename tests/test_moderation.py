from unittest.mock import Mock

import pytest

from repositories.predictions import PredictionRecord, PredictionRepository
from schemas.prediction import PredictionRequest
from services.moderation import ModerationService


@pytest.mark.parametrize(
    ("is_verified_seller", "images_qty", "expected"),
    [
        (True, 0, False),
        (True, 1, False),
        (True, 10, False),
        (False, 0, True),
        (False, 1, False),
        (False, 10, False),
    ],
)
def test_service_predicts_and_saves_result(
    payload, is_verified_seller, images_qty, expected
):
    payload.update(
        is_verified_seller=is_verified_seller,
        images_qty=images_qty,
    )
    item = PredictionRequest(**payload)
    repository = Mock(spec=PredictionRepository)
    service = ModerationService(repository)

    result = service.predict(item)

    assert result is expected
    repository.save.assert_called_once_with(
        PredictionRecord(item_id=item.item_id, has_violations=expected)
    )


def test_service_propagates_repository_failure(payload):
    repository = Mock(spec=PredictionRepository)
    repository.save.side_effect = RuntimeError("storage is unavailable")
    service = ModerationService(repository)

    with pytest.raises(RuntimeError, match="storage is unavailable"):
        service.predict(PredictionRequest(**payload))

    repository.save.assert_called_once()
