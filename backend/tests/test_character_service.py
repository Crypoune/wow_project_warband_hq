
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.models.user import User
from app.models.character import Character
from app.services.character_service import CharacterService


AVAILABLE_CHARACTERS = [
    {"id": 123, "name": "Testwarrior", "level": 80},
    {"id": 456, "name": "Testmage", "level": 70},
]


@pytest.fixture
def service():
    with patch(
        "app.services.character_service.AuthService"
    ) as mock_auth_service:
        instance = CharacterService()
        instance.auth_service = mock_auth_service.return_value
        yield instance


def test_get_available_characters(service):
    service.auth_service.get_account_characters.return_value = (
        AVAILABLE_CHARACTERS
    )

    result = service.get_available_characters("test-token")

    assert result == AVAILABLE_CHARACTERS
    service.auth_service.get_account_characters.assert_called_once_with(
        "test-token"
    )


def test_import_characters_rejects_unknown_character(service):
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
    service.auth_service.get_account_characters.return_value = (
        AVAILABLE_CHARACTERS
    )

    existing_character = SimpleNamespace(
        blizzard_character_id=123,
    )
    db = MagicMock()
    db.scalars.return_value.all.return_value = [existing_character]

    with patch(
        "app.services.character_service.SessionLocal"
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.import_characters(
            user_id=1,
            access_token="test-token",
            character_ids=[123, 456, 456],
        )

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
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    with patch(
        "app.services.character_service.SessionLocal"
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = db

        result = service.get_imported_characters(
            user_id=1,
            access_token="test-token",
        )

    assert result == []
    db.scalars.assert_called_once()
    service.auth_service.get_account_characters.assert_not_called()


def test_get_imported_characters_handles_missing_blizzard_character(service):
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
        "app.services.character_service.SessionLocal"
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
