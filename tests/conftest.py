import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def payload() -> dict:
    return {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 10,
        "name": "Велосипед",
        "description": "Городской велосипед в хорошем состоянии",
        "category": 2,
        "images_qty": 1,
    }


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
