from repositories.predictions import InMemoryPredictionRepository, PredictionRecord


def test_repository_returns_none_for_unknown_item():
    repository = InMemoryPredictionRepository()

    assert repository.get(123) is None


def test_repository_saves_predictions_for_different_items():
    repository = InMemoryPredictionRepository()
    first = PredictionRecord(item_id=1, has_violations=True)
    second = PredictionRecord(item_id=2, has_violations=False)

    repository.save(first)
    repository.save(second)

    assert repository.get(1) == first
    assert repository.get(2) == second


def test_repeated_prediction_updates_same_item():
    repository = InMemoryPredictionRepository()
    repository.save(PredictionRecord(item_id=1, has_violations=True))
    latest = PredictionRecord(item_id=1, has_violations=False)

    repository.save(latest)

    assert repository.get(1) == latest


def test_repository_instances_have_independent_storage():
    first = InMemoryPredictionRepository()
    second = InMemoryPredictionRepository()

    first.save(PredictionRecord(item_id=1, has_violations=True))

    assert second.get(1) is None
