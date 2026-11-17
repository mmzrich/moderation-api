from unittest.mock import Mock

import pytest

from main import app
from repositories.predictions import PredictionRepository
from routers.predict import get_moderation_service
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
def test_predict_returns_only_boolean(
    client, payload, is_verified_seller, images_qty, expected
):
    payload.update(
        is_verified_seller=is_verified_seller,
        images_qty=images_qty,
    )

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert type(response.json()) is bool
    assert response.json() is expected


@pytest.mark.parametrize(
    "field",
    [
        "seller_id",
        "is_verified_seller",
        "item_id",
        "name",
        "description",
        "category",
        "images_qty",
    ],
)
def test_all_fields_are_required(client, payload, field):
    del payload[field]

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert any(
        error["loc"] == ["body", field]
        for error in response.json()["detail"]
    )


@pytest.mark.parametrize(
    "field",
    [
        "seller_id",
        "is_verified_seller",
        "item_id",
        "name",
        "description",
        "category",
        "images_qty",
    ],
)
def test_fields_cannot_be_null(client, payload, field):
    payload[field] = None

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert any(
        error["loc"] == ["body", field]
        for error in response.json()["detail"]
    )


@pytest.mark.parametrize("field", ["seller_id", "item_id", "category", "images_qty"])
@pytest.mark.parametrize("value", [True, False, 1.0, "1", [], {}])
def test_integer_fields_reject_other_types(client, payload, field, value):
    payload[field] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize("value", [0, 1, "true", "false", [], {}])
def test_boolean_field_is_strict(client, payload, value):
    payload["is_verified_seller"] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("value", [1, 1.5, True, [], {}])
def test_text_fields_reject_other_types(client, payload, field, value):
    payload[field] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize("field", ["seller_id", "item_id", "category"])
@pytest.mark.parametrize("value", [0, -1])
def test_identifiers_must_be_positive(client, payload, field, value):
    payload[field] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400


def test_images_quantity_cannot_be_negative(client, payload):
    payload["images_qty"] = -1

    response = client.post("/predict", json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_text_fields_cannot_be_blank(client, payload, field, value):
    payload[field] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400


def test_unknown_fields_are_rejected(client, payload):
    payload["unexpected"] = "value"

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert any(
        error["loc"] == ["body", "unexpected"]
        for error in response.json()["detail"]
    )


@pytest.mark.parametrize("body", ["", "{", "null", "[]", "123", '"text"'])
def test_invalid_request_body_returns_bad_request(client, body):
    response = client.post(
        "/predict", content=body, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400
    assert isinstance(response.json()["detail"], list)


def test_business_error_returns_internal_server_error(client, payload, monkeypatch):
    def fail_prediction(self, item):
        raise RuntimeError("private business failure details")

    monkeypatch.setattr(ModerationService, "predict", fail_prediction)

    response = client.post("/predict", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "private business failure details" not in response.text


def test_repository_error_returns_internal_server_error(client, payload):
    repository = Mock(spec=PredictionRepository)
    repository.save.side_effect = RuntimeError("private storage failure details")
    app.dependency_overrides[get_moderation_service] = lambda: ModerationService(
        repository
    )

    response = client.post("/predict", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    repository.save.assert_called_once()
    assert "private storage failure details" not in response.text


def test_root_returns_greeting(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
