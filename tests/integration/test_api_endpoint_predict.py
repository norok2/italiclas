"""Integration Test API Endpoint /predict."""

from fastapi import status
from fastapi.testclient import TestClient

from italiclas.api.main import app

client = TestClient(app)


def test_endpoint_predict_italian() -> None:
    """Predict Italian text as False."""
    response = client.post("/predict", json={"text": "ciao mondo"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"is_italian": True}


def test_endpoint_predict_not_italian() -> None:
    """Predict non-Italian text as False."""
    response = client.post("/predict", json={"text": "hello world"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"is_italian": False}


def test_endpoint_predict_no_get() -> None:
    """Fail on GET request."""
    response = client.get("/predict")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_endpoint_predict_empty_payload() -> None:
    """Fail on empty payload."""
    response = client.post("/predict", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_endpoint_predict_invalid_text_type() -> None:
    """Fail on invalid 'text' type."""
    response = client.post("/predict", json={"text": 123})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_endpoint_predict_payload_with_more_fields() -> None:
    """Predict even if payload contains unused fields."""
    response = client.post("/predict", json={"text": "ciao mondo", "a": "b"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"is_italian": True}


def test_endpoint_predict_payload_missing_required_fields() -> None:
    """Fail when payload misses required fields."""
    response = client.post("/predict", json={"a": "b"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
