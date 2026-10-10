import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.services.auth_service import InvalidBlizzardProfileError
from app.core.dependencies import CurrentAuth, get_current_auth


client = TestClient(app)

AUTH = CurrentAuth(user_id=1, access_token="test-access-token")

CHARACTERS = [
    {
        "id": 123,
        "name": "Testwarrior",
        "level": 80,
        "realm": "Hyjal",
        "realm_slug": "hyjal",
        "class": "Warrior",
        "class_id": 1,
        "race": "Human",
        "race_id": 1,
        "faction": "Alliance",
        "profile_url": "https://example.com/character",
    }
]


def override_auth():
    return AUTH


def setup_function():
    app.dependency_overrides[get_current_auth] = override_auth


def teardown_function():
    app.dependency_overrides.clear()


def make_blizzard_http_error():
    request = httpx.Request(
        "GET",
        "https://eu.api.blizzard.com/profile/user/wow",
    )
    response = httpx.Response(500, request=request)

    return httpx.HTTPStatusError(
        "Blizzard API error",
        request=request,
        response=response,
    )


def make_blizzard_unauthorized_error():
    request = httpx.Request(
        "GET",
        "https://eu.api.blizzard.com/profile/user/wow",
    )
    response = httpx.Response(401, request=request)

    return httpx.HTTPStatusError(
        "Invalid or expired Blizzard token",
        request=request,
        response=response,
    )


def make_blizzard_connection_error():
    request = httpx.Request(
        "GET",
        "https://eu.api.blizzard.com/profile/user/wow",
    )
    return httpx.ConnectError("Connection failed", request=request)


# GET /api/characters/available


def test_get_available_characters_success():
    with patch(
        "app.api.characters.character_service.get_available_characters",
        return_value=CHARACTERS,
    ) as mock_service:
        response = client.get("/api/characters/available")

    assert response.status_code == 200
    assert response.json() == {"characters": CHARACTERS}
    mock_service.assert_called_once_with("test-access-token")


def test_get_available_characters_with_invalid_token():
    with patch(
        "app.api.characters.character_service.get_available_characters",
        side_effect=make_blizzard_unauthorized_error(),
    ):
        response = client.get("/api/characters/available")

    assert response.status_code == 401
    assert response.json()["message"] == (
        "Blizzard access token is invalid or expired"
    )


def test_import_characters_with_invalid_token():
    with patch(
        "app.api.characters.character_service.import_characters",
        side_effect=make_blizzard_unauthorized_error(),
    ):
        response = client.post(
            "/api/characters/import",
            json={"character_ids": [123]},
        )

    assert response.status_code == 401
    assert response.json()["message"] == (
        "Blizzard access token is invalid or expired"
    )


def test_get_characters_with_invalid_token():
    with patch(
        "app.api.characters.character_service.get_imported_characters",
        side_effect=make_blizzard_unauthorized_error(),
    ):
        response = client.get("/api/characters")

    assert response.status_code == 401
    assert response.json()["message"] == (
        "Blizzard access token is invalid or expired"
    )


def test_get_available_characters_empty():
    with patch(
        "app.api.characters.character_service.get_available_characters",
        return_value=[],
    ):
        response = client.get("/api/characters/available")

    assert response.status_code == 200
    assert response.json() == {"characters": []}


def test_get_available_characters_blizzard_http_error():
    with patch(
        "app.api.characters.character_service.get_available_characters",
        side_effect=make_blizzard_http_error(),
    ):
        response = client.get("/api/characters/available")

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Blizzard returned an HTTP error"
    )


def test_get_available_characters_connection_error():
    with patch(
        "app.api.characters.character_service.get_available_characters",
        side_effect=make_blizzard_connection_error(),
    ):
        response = client.get("/api/characters/available")

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Unable to contact Blizzard"
    )


# POST /api/characters/import


def test_import_characters_success():
    with patch(
        "app.api.characters.character_service.import_characters",
        return_value=CHARACTERS,
    ) as mock_service:
        response = client.post(
            "/api/characters/import",
            json={"character_ids": [123]},
        )

    assert response.status_code == 200
    assert response.json() == {"characters": CHARACTERS}
    mock_service.assert_called_once_with(
        user_id=1,
        access_token="test-access-token",
        character_ids=[123],
    )


def test_import_characters_invalid_id():
    with patch(
        "app.api.characters.character_service.import_characters",
        side_effect=ValueError(
            "One or more characters do not belong to the Blizzard account"
        ),
    ):
        response = client.post(
            "/api/characters/import",
            json={"character_ids": [999]},
        )

    assert response.status_code == 400
    assert response.json()["message"] == (
        "One or more characters do not belong to the Blizzard account"
    )


def test_import_characters_blizzard_http_error():
    with patch(
        "app.api.characters.character_service.import_characters",
        side_effect=make_blizzard_http_error(),
    ):
        response = client.post(
            "/api/characters/import",
            json={"character_ids": [123]},
        )

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Blizzard returned an HTTP error"
    )


def test_import_characters_connection_error():
    with patch(
        "app.api.characters.character_service.import_characters",
        side_effect=make_blizzard_connection_error(),
    ):
        response = client.post(
            "/api/characters/import",
            json={"character_ids": [123]},
        )

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Unable to contact Blizzard"
    )


def test_import_characters_empty_ids():
    response = client.post(
        "/api/characters/import",
        json={"character_ids": []},
    )

    assert response.status_code == 422


# GET /api/characters


def test_get_imported_characters_success():
    with patch(
        "app.api.characters.character_service.get_imported_characters",
        return_value=CHARACTERS,
    ) as mock_service:
        response = client.get("/api/characters")

    assert response.status_code == 200
    assert response.json() == {"characters": CHARACTERS}
    mock_service.assert_called_once_with(
        user_id=1,
        access_token="test-access-token",
    )


def test_get_imported_characters_empty():
    with patch(
        "app.api.characters.character_service.get_imported_characters",
        return_value=[],
    ):
        response = client.get("/api/characters")

    assert response.status_code == 200
    assert response.json() == {"characters": []}


def test_get_imported_characters_blizzard_http_error():
    with patch(
        "app.api.characters.character_service.get_imported_characters",
        side_effect=make_blizzard_http_error(),
    ):
        response = client.get("/api/characters")

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Blizzard returned an HTTP error"
    )


def test_get_imported_characters_connection_error():
    with patch(
        "app.api.characters.character_service.get_imported_characters",
        side_effect=make_blizzard_connection_error(),
    ):
        response = client.get("/api/characters")

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Unable to contact Blizzard"
    )


def test_get_imported_characters_database_error_returns_500():
    with patch(
        "app.api.characters.character_service.get_imported_characters",
        side_effect=SQLAlchemyError("Database unavailable"),
    ):
        response = client.get("/api/characters")

    assert response.status_code == 500
    assert response.json()["message"] == (
        "Unable to retrieve imported characters"
    )


# Authentication


def test_available_characters_requires_authentication():
    app.dependency_overrides.clear()

    response = client.get("/api/characters/available")

    assert response.status_code == 401
    assert response.json()["message"] == (
        "Authentication required"
    )


def test_import_characters_requires_authentication():
    app.dependency_overrides.clear()

    response = client.post(
        "/api/characters/import",
        json={"character_ids": [123]},
    )

    assert response.status_code == 401
    assert response.json()["message"] == (
        "Authentication required"
    )


def test_imported_characters_requires_authentication():
    app.dependency_overrides.clear()

    response = client.get("/api/characters")

    assert response.status_code == 401
    assert response.json()["message"] == (
        "Authentication required"
    )

def test_get_current_auth_database_error_returns_500():
    """Vérifie qu'une erreur SQL renvoie une erreur 500."""

    request = MagicMock()
    request.session = {"session_token": "test-session-token"}

    fake_db = MagicMock()
    fake_db.scalar.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    with patch(
        "app.core.dependencies.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = fake_db

        try:
            get_current_auth(request)
            assert False, "Une HTTPException était attendue"
        except HTTPException as exc:
            assert exc.status_code == 500
            assert exc.detail["message"] == (
                "Unable to verify authentication"
            )

def make_blizzard_invalid_json_error():
    """Simule une réponse Blizzard dont le JSON est invalide."""
    return json.JSONDecodeError(
        "Expecting value",
        "<html>Unexpected response</html>",
        0,
    )


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/api/characters/available", None),
        ("POST", "/api/characters/import", {"character_ids": [123]}),
        ("GET", "/api/characters", None),
    ],
)


def test_character_routes_handle_invalid_blizzard_json(
    method,
    path,
    payload,
):
    """Vérifie qu'une réponse Blizzard invalide produit une erreur 502."""

    with patch(
        "app.api.characters.character_service.get_available_characters",
        side_effect=make_blizzard_invalid_json_error(),
    ), patch(
        "app.api.characters.character_service.import_characters",
        side_effect=make_blizzard_invalid_json_error(),
    ), patch(
        "app.api.characters.character_service.get_imported_characters",
        side_effect=make_blizzard_invalid_json_error(),
    ):
        response = client.request(method, path, json=payload)

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Blizzard returned an unexpected response"
    )


def test_import_characters_invalid_blizzard_profile_returns_502():
    with patch(
        "app.api.characters.character_service.import_characters",
        side_effect=InvalidBlizzardProfileError(
            "Invalid Blizzard profile structure"
        ),
    ):
        response = client.post(
            "/api/characters/import",
            json={"character_ids": [123]},
        )

    assert response.status_code == 502
    assert response.json()["message"] == (
        "Blizzard returned an unexpected response"
    )
