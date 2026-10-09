
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
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
    assert response.json()["detail"]["message"] == (
        "Blizzard returned an HTTP error"
    )


def test_get_available_characters_connection_error():
    with patch(
        "app.api.characters.character_service.get_available_characters",
        side_effect=make_blizzard_connection_error(),
    ):
        response = client.get("/api/characters/available")

    assert response.status_code == 502
    assert response.json()["detail"]["message"] == (
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
    assert response.json()["detail"]["message"] == (
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
    assert response.json()["detail"]["message"] == (
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
    assert response.json()["detail"]["message"] == (
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
    assert response.json()["detail"]["message"] == (
        "Blizzard returned an HTTP error"
    )


def test_get_imported_characters_connection_error():
    with patch(
        "app.api.characters.character_service.get_imported_characters",
        side_effect=make_blizzard_connection_error(),
    ):
        response = client.get("/api/characters")

    assert response.status_code == 502
    assert response.json()["detail"]["message"] == (
        "Unable to contact Blizzard"
    )


# Authentication


def test_available_characters_requires_authentication():
    app.dependency_overrides.clear()

    response = client.get("/api/characters/available")

    assert response.status_code == 401
    assert response.json()["detail"]["message"] == (
        "Authentication required"
    )


def test_import_characters_requires_authentication():
    app.dependency_overrides.clear()

    response = client.post(
        "/api/characters/import",
        json={"character_ids": [123]},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["message"] == (
        "Authentication required"
    )


def test_imported_characters_requires_authentication():
    app.dependency_overrides.clear()

    response = client.get("/api/characters")

    assert response.status_code == 401
    assert response.json()["detail"]["message"] == (
        "Authentication required"
    )
