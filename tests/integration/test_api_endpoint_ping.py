"""Integration Test API Endpoint /ping."""

from fastapi import status
from fastapi.testclient import TestClient

from italiclas.api.main import app
from italiclas.config import info

client = TestClient(app)


# ======================================================================
def test_endpoint_ping() -> None:
    """Predict Italian text as False."""
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": info.version}


# ======================================================================
def test_endpoint_ping_no_post() -> None:
    """Predict Italian text as False."""
    response = client.post("/ping")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
