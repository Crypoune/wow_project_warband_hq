
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.core.dependencies import CurrentAuth, get_current_auth


client = TestClient(app)

AUTH = CurrentAuth(user_id=1, access_token="test-access-token")

NOTE = {
    "id": 10,
    "character_id": 12,
    "content": "Main DPS pour les raids.\nSpécialisé PvE HL.",
}


def override_auth():
    return AUTH


def setup_function():
    app.dependency_overrides[get_current_auth] = override_auth


def teardown_function():
    app.dependency_overrides.clear()


# ============================================================
# GET /api/characters/{character_id}/note
# ============================================================

def test_get_character_note_success():
    """Un utilisateur peut récupérer la note de son personnage."""

    with patch(
        "app.api.notes.note_service.get_character_note",
        return_value=NOTE,
    ) as mock_service:
        response = client.get("/api/characters/12/note")

    assert response.status_code == 200
    assert response.json() == {"note": NOTE}

    mock_service.assert_called_once_with(
        character_id=12,
        user_id=1,
    )


def test_get_character_note_returns_none():
    """Un personnage sans note retourne null."""

    with patch(
        "app.api.notes.note_service.get_character_note",
        return_value=None,
    ):
        response = client.get("/api/characters/12/note")

    assert response.status_code == 200
    assert response.json() == {"note": None}


def test_get_character_note_not_found():
    """Un utilisateur ne peut pas consulter la note d'un autre."""

    with patch(
        "app.api.notes.note_service.get_character_note",
        side_effect=ValueError(
            "Personnage introuvable ou inaccessible."
        ),
    ):
        response = client.get("/api/characters/12/note")

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Personnage introuvable ou inaccessible."
    )


def test_get_character_note_database_error():
    """Une erreur SQL renvoie une erreur 500."""

    with patch(
        "app.api.notes.note_service.get_character_note",
        side_effect=SQLAlchemyError("Database unavailable"),
    ):
        response = client.get("/api/characters/12/note")

    assert response.status_code == 500
    assert response.json()["message"] == (
        "Unable to retrieve character note"
    )


# ============================================================
# PUT /api/characters/{character_id}/note
# ============================================================

def test_save_character_note_success():
    """Un utilisateur peut sauvegarder la note de son personnage."""

    content = "Main DPS pour les raids.\nSpécialisé PvE HL."

    with patch(
        "app.api.notes.note_service.save_character_note",
        return_value=NOTE,
    ) as mock_service:
        response = client.put(
            "/api/characters/12/note",
            json={"content": content},
        )

    assert response.status_code == 200
    assert response.json() == {"note": NOTE}

    mock_service.assert_called_once_with(
        character_id=12,
        user_id=1,
        content=content,
    )


def test_save_character_note_not_found():
    """Un utilisateur ne peut pas modifier la note d'un autre."""

    with patch(
        "app.api.notes.note_service.save_character_note",
        side_effect=ValueError(
            "Personnage introuvable ou inaccessible."
        ),
    ):
        response = client.put(
            "/api/characters/12/note",
            json={"content": "Modification interdite."},
        )

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Personnage introuvable ou inaccessible."
    )


def test_save_character_note_database_error():
    """Une erreur SQL renvoie une erreur 500."""

    with patch(
        "app.api.notes.note_service.save_character_note",
        side_effect=SQLAlchemyError("Database unavailable"),
    ):
        response = client.put(
            "/api/characters/12/note",
            json={"content": "Une note."},
        )

    assert response.status_code == 500
    assert response.json()["message"] == (
        "Unable to save character note"
    )


# ============================================================
# VALIDATION DES DONNÉES
# ============================================================

def test_save_character_note_rejects_missing_content():
    """Le contenu doit être présent dans la requête."""

    response = client.put(
        "/api/characters/12/note",
        json={},
    )

    assert response.status_code == 422


def test_save_character_note_rejects_invalid_content_type():
    """Le contenu doit être une chaîne de caractères."""

    response = client.put(
        "/api/characters/12/note",
        json={"content": 123},
    )

    assert response.status_code == 422


def test_save_character_note_rejects_unknown_fields():
    """Les propriétés inconnues sont refusées."""

    response = client.put(
        "/api/characters/12/note",
        json={
            "content": "Une note.",
            "user_id": 999,
        },
    )

    assert response.status_code == 422


# ============================================================
# AUTHENTIFICATION
# ============================================================

@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/api/characters/12/note", None),
        ("PUT", "/api/characters/12/note", {"content": "Une note."}),
    ],
)
def test_character_note_routes_require_authentication(
    method,
    path,
    payload,
):
    """Les routes de notes nécessitent une authentification."""

    app.dependency_overrides.clear()

    response = client.request(
        method,
        path,
        json=payload,
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"
