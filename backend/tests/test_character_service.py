from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.models.character import Character
from app.services.character_service import CharacterService
from app.services.auth_service import InvalidBlizzardProfileError


# Personnages simulés renvoyés par l'API Blizzard pour les tests.
AVAILABLE_CHARACTERS = [
    {"id": 123, "name": "Testwarrior", "level": 80},
    {"id": 456, "name": "Testmage", "level": 70},
]


@pytest.fixture
def service():
    """Crée un CharacterService avec un AuthService simulé."""

    # On remplace AuthService pour éviter les vrais appels à Blizzard.
    with patch(
        "app.services.character_service.AuthService",
    ) as mock_auth_service:
        instance = CharacterService()
        instance.auth_service = mock_auth_service.return_value

        yield instance


def test_get_available_characters(service):
    """Vérifie que les personnages disponibles sont récupérés."""

    service.auth_service.get_account_characters.return_value = (
        AVAILABLE_CHARACTERS
    )

    result = service.get_available_characters("test-token")

    assert result == AVAILABLE_CHARACTERS
    service.auth_service.get_account_characters.assert_called_once_with(
        "test-token"
    )


def test_import_characters_rejects_unknown_character(service):
    """Vérifie qu'on ne peut pas importer un personnage inconnu."""

    service.auth_service.get_account_characters.return_value = (
        AVAILABLE_CHARACTERS
    )

    with pytest.raises(ValueError, match="do not belong"):
        service.import_characters(
            user_id=1,
            access_token="test-token",
            character_ids=[999],
        )


def test_import_characters_skips_existing_and_duplicate_ids(service):
    """Vérifie que les personnages existants et les doublons sont ignorés."""

    service.auth_service.get_account_characters.return_value = (
        AVAILABLE_CHARACTERS
    )

    # Ce personnage existe déjà en base de données.
    existing_character = SimpleNamespace(
        blizzard_character_id=123,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = [existing_character]

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.import_characters(
            user_id=1,
            access_token="test-token",
            character_ids=[123, 456, 456],
        )

    # Seul Testmage doit être ajouté, une seule fois.
    assert result == [
        {"id": 456, "name": "Testmage", "level": 70}
    ]

    db.add.assert_called_once()
    added_character = db.add.call_args.args[0]

    assert isinstance(added_character, Character)
    assert added_character.user_id == 1
    assert added_character.blizzard_character_id == 456
    db.commit.assert_called_once()


def test_get_imported_characters_only_returns_current_users_characters(
    service,
):
    """Vérifie le comportement lorsqu'aucun personnage n'est importé."""

    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.get_imported_characters(
            user_id=1,
            access_token="test-token",
        )

    assert result == []
    db.scalars.assert_called_once()

    # Sans personnage importé, inutile d'interroger l'API Blizzard.
    service.auth_service.get_account_characters.assert_not_called()


def test_get_imported_characters_handles_missing_blizzard_character(
    service,
):
    """Vérifie qu'un personnage absent de Blizzard reste représenté."""

    imported_character = SimpleNamespace(
        id=1,
        blizzard_character_id=999,
        is_favorite=False,
        imported_at=None,
        last_synced_at=None,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = [imported_character]

    service.auth_service.get_account_characters.return_value = (
        AVAILABLE_CHARACTERS
    )

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.get_imported_characters(
            user_id=1,
            access_token="test-token",
        )

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["blizzard_character_id"] == 999
    assert result[0]["is_favorite"] is False


@pytest.mark.parametrize("favorite_state", [True, False])
def test_update_favorite_updates_character(service, favorite_state):
    """Vérifie qu'un personnage peut être marqué favori ou non."""

    character = SimpleNamespace(
        id=1,
        is_favorite=not favorite_state,
    )

    db = MagicMock()
    db.scalar.return_value = character

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.update_favorite(
            user_id=42,
            character_id=1,
            is_favorite=favorite_state,
        )

    assert result == {
        "id": 1,
        "is_favorite": favorite_state,
    }
    assert character.is_favorite is favorite_state
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(character)


def test_update_favorite_returns_none_when_character_not_found(service):
    """Vérifie qu'aucune mise à jour n'a lieu si le personnage est absent."""

    db = MagicMock()
    db.scalar.return_value = None

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.update_favorite(
            user_id=42,
            character_id=999,
            is_favorite=True,
        )

    assert result is None
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_get_imported_characters_keeps_character_when_portrait_fails(
    service,
):
    """Vérifie qu'un échec du portrait ne supprime pas le personnage."""

    imported_character = SimpleNamespace(
        id=1,
        blizzard_character_id=123,
        is_favorite=False,
        imported_at=None,
        last_synced_at=None,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = [imported_character]

    service.auth_service.get_account_characters.return_value = [
        {
            "id": 123,
            "name": "Testwarrior",
            "level": 80,
            "realm": "Hyjal",
            "realm_slug": "hyjal",
        }
    ]

    # On simule une erreur HTTP 404 lors de la récupération du portrait.
    # Le service doit tout de même renvoyer le personnage importé.
    media_url = (
        "https://eu.api.blizzard.com/profile/wow/character/"
        "hyjal/testwarrior/character-media"
    )
    request = httpx.Request("GET", media_url)
    response = httpx.Response(404, request=request)

    service.auth_service.get_character_media.side_effect = (
        httpx.HTTPStatusError(
            "Portrait unavailable",
            request=request,
            response=response,
        )
    )

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.get_imported_characters(
            user_id=1,
            access_token="test-token",
        )

    # Le personnage reste disponible, même sans URL de portrait.
    assert len(result) == 1
    assert result[0]["name"] == "Testwarrior"
    assert result[0]["portrait_url"] is None


def test_get_imported_characters_includes_item_levels(service):
    """Vérifie que les niveaux d'objet sont ajoutés au personnage."""

    imported_character = SimpleNamespace(
        id=1,
        blizzard_character_id=123,
        is_favorite=False,
        imported_at=None,
        last_synced_at=None,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = [imported_character]

    service.auth_service.get_account_characters.return_value = [
        {
            "id": 123,
            "name": "Testwarrior",
            "level": 80,
            "realm": "Hyjal",
            "realm_slug": "hyjal",
        }
    ]

    # On simule les données renvoyées par le profil Blizzard.
    service.auth_service.get_character_profile.return_value = {
        "average_item_level": 250,
        "equipped_item_level": 248,
    }

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.get_imported_characters(
            user_id=1,
            access_token="test-token",
        )

    assert len(result) == 1
    assert result[0]["average_item_level"] == 250
    assert result[0]["equipped_item_level"] == 248


def test_get_imported_characters_handles_item_level_failure(service):
    """Vérifie que le personnage reste disponible si le profil échoue."""

    imported_character = SimpleNamespace(
        id=1,
        blizzard_character_id=123,
        is_favorite=False,
        imported_at=None,
        last_synced_at=None,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = [imported_character]

    service.auth_service.get_account_characters.return_value = [
        {
            "id": 123,
            "name": "Testwarrior",
            "level": 80,
            "realm": "Hyjal",
            "realm_slug": "hyjal",
        }
    ]

    # On simule une erreur HTTP sur l'appel au profil détaillé.
    request = httpx.Request(
        "GET",
        "https://eu.api.blizzard.com/profile/wow/character/hyjal/testwarrior",
    )
    response = httpx.Response(404, request=request)

    service.auth_service.get_character_profile.side_effect = (
        httpx.HTTPStatusError(
            "Character profile unavailable",
            request=request,
            response=response,
        )
    )

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.get_imported_characters(
            user_id=1,
            access_token="test-token",
        )

    assert len(result) == 1
    assert result[0]["name"] == "Testwarrior"
    assert result[0]["average_item_level"] is None
    assert result[0]["equipped_item_level"] is None


def test_get_imported_characters_handles_invalid_profile(service):
    """Vérifie qu'un profil mal formé ne supprime pas le personnage."""

    imported_character = SimpleNamespace(
        id=1,
        blizzard_character_id=123,
        is_favorite=False,
        imported_at=None,
        last_synced_at=None,
    )

    db = MagicMock()
    db.scalars.return_value.all.return_value = [imported_character]

    service.auth_service.get_account_characters.return_value = [
        {
            "id": 123,
            "name": "Testwarrior",
            "level": 80,
            "realm": "Hyjal",
            "realm_slug": "hyjal",
        }
    ]

    service.auth_service.get_character_profile.side_effect = (
        InvalidBlizzardProfileError(
            "Invalid Blizzard profile structure"
        )
    )

    with patch(
        "app.services.character_service.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.get_imported_characters(
            user_id=1,
            access_token="test-token",
        )

    assert len(result) == 1
    assert result[0]["name"] == "Testwarrior"
    assert result[0]["average_item_level"] is None
    assert result[0]["equipped_item_level"] is None


def test_get_character_details_success(service, monkeypatch):
    """Vérifie la récupération des détails d'un personnage importé."""

    character = SimpleNamespace(
        id=17,
        blizzard_character_id=123,
        user_id=42,
        is_favorite=True,
        imported_at=None,
        last_synced_at=None,
    )

    mock_db = MagicMock()
    mock_db.scalar.return_value = character

    mock_session_local = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    monkeypatch.setattr(
        "app.services.character_service.SessionLocal",
        mock_session_local,
    )

    service.auth_service.get_account_characters.return_value = [
        {
            "id": 123,
            "name": "Testwarrior",
            "level": 80,
            "realm": "Hyjal",
            "realm_slug": "hyjal",
        }
    ]
    service.auth_service.get_character_media.return_value = (
        "https://example.com/portrait.jpg"
    )
    service.auth_service.get_character_profile.return_value = {
        "average_item_level": 250,
        "equipped_item_level": 248,
    }

    result = service.get_character_details(
        user_id=42,
        character_id=17,
        access_token="test-token",
    )

    assert result["id"] == 17
    assert result["blizzard_character_id"] == 123
    assert result["is_favorite"] is True
    assert result["name"] == "Testwarrior"
    assert result["portrait_url"] == "https://example.com/portrait.jpg"
    assert result["average_item_level"] == 250
    assert result["equipped_item_level"] == 248

    # La requête doit filtrer sur l'identifiant et le propriétaire.
    statement = str(mock_db.scalar.call_args.args[0])
    assert "characters.id" in statement
    assert "characters.user_id" in statement


def test_get_character_details_not_found(service, monkeypatch):
    """Vérifie qu'un personnage absent n'est pas renvoyé."""

    mock_db = MagicMock()
    mock_db.scalar.return_value = None

    mock_session_local = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    monkeypatch.setattr(
        "app.services.character_service.SessionLocal",
        mock_session_local,
    )

    result = service.get_character_details(
        user_id=42,
        character_id=999,
        access_token="test-token",
    )

    assert result is None

    # Aucun appel Blizzard n'est nécessaire si le personnage
    # n'existe pas, ou n'appartient pas à l'utilisateur.
    service.auth_service.get_account_characters.assert_not_called()
    service.auth_service.get_character_media.assert_not_called()
    service.auth_service.get_character_profile.assert_not_called()


def test_get_character_details_portrait_failure(service, monkeypatch):
    """Vérifie qu'un échec du portrait ne bloque pas les détails."""

    character = SimpleNamespace(
        id=17,
        blizzard_character_id=123,
        user_id=42,
        is_favorite=False,
        imported_at=None,
        last_synced_at=None,
    )

    mock_db = MagicMock()
    mock_db.scalar.return_value = character

    mock_session_local = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    monkeypatch.setattr(
        "app.services.character_service.SessionLocal",
        mock_session_local,
    )

    service.auth_service.get_account_characters.return_value = [
        {
            "id": 123,
            "name": "Testwarrior",
            "level": 80,
            "realm": "Hyjal",
            "realm_slug": "hyjal",
        }
    ]

    service.auth_service.get_character_media.side_effect = httpx.HTTPError(
        "Blizzard media unavailable"
    )

    service.auth_service.get_character_profile.return_value = {
        "average_item_level": 250,
        "equipped_item_level": 248,
    }

    result = service.get_character_details(
        user_id=42,
        character_id=17,
        access_token="test-token",
    )

    assert result["id"] == 17
    assert result["portrait_url"] is None
    assert result["average_item_level"] == 250
    assert result["equipped_item_level"] == 248
