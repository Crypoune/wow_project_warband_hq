from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

from app.main import app


client = TestClient(app, raise_server_exceptions=False)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "available",
    }

def test_health_check_database_unavailable():
    with patch(
        "app.api.health.engine.connect",
        side_effect=SQLAlchemyError("Database unavailable"),
    ):
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
		"detail": {
			"status": "error",
			"database": "unavailable",
		},
	}

def test_internal_server_error():
    with patch(
        "app.api.health.engine.connect",
        side_effect=Exception("Unexpected error"),
    ):
        response = client.get("/health")

    assert response.status_code == 500
    assert response.json() == {
        "message": "Internal server error",
    }
