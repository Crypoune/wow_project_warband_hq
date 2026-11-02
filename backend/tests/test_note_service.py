
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.models.note import CharacterNote
from app.services.note_service import NoteService


@pytest.fixture
def service():
    """Crée une instance de NoteService."""
    return NoteService()


def test_get_character_note_success(service):
    """Un utilisateur peut récupérer la note de son personnage."""

    character = MagicMock(id=1, user_id=42)

    note = MagicMock(
        id=10,
        character_id=1,
        content="Main DPS pour les raids.",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db = MagicMock()
    db.scalar.side_effect = [character, note]

    with patch("app.services.note_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_character_note(
            character_id=1,
            user_id=42,
        )

    assert result["id"] == 10
    assert result["character_id"] == 1
    assert result["content"] == "Main DPS pour les raids."


def test_get_character_note_returns_none_when_note_does_not_exist(service):
    """Un personnage sans note retourne None."""

    character = MagicMock(id=1, user_id=42)

    db = MagicMock()
    db.scalar.side_effect = [character, None]

    with patch("app.services.note_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_character_note(
            character_id=1,
            user_id=42,
        )

    assert result is None


def test_get_character_note_rejects_character_not_owned_by_user(service):
    """Un utilisateur ne peut pas consulter la note d'un autre."""

    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.note_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(
            ValueError,
            match="Personnage introuvable ou inaccessible.",
        ):
            service.get_character_note(
                character_id=1,
                user_id=42,
            )

    assert db.scalar.call_count == 1


def test_save_character_note_creates_note(service):
    """Un utilisateur peut créer une note pour son personnage."""

    character = MagicMock(id=1, user_id=42)

    content = "Main DPS pour les raids.\nSpécialisé PvE HL."

    db = MagicMock()
    db.scalar.side_effect = [character, None]

    def refresh_note(note):
        note.id = 10
        note.created_at = datetime.now(timezone.utc)
        note.updated_at = datetime.now(timezone.utc)

    db.refresh.side_effect = refresh_note

    with patch("app.services.note_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.save_character_note(
            character_id=1,
            user_id=42,
            content=content,
        )

    assert result["id"] == 10
    assert result["character_id"] == 1
    assert result["content"] == content
    assert "\n" in result["content"]

    added_note = db.add.call_args.args[0]

    assert isinstance(added_note, CharacterNote)
    assert added_note.character_id == 1
    assert added_note.content == content

    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_save_character_note_updates_existing_note(service):
    """Un utilisateur peut modifier sa note existante."""

    character = MagicMock(id=1, user_id=42)

    note = MagicMock(
        id=10,
        character_id=1,
        content="Ancienne note",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db = MagicMock()
    db.scalar.side_effect = [character, note]

    with patch("app.services.note_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.save_character_note(
            character_id=1,
            user_id=42,
            content="Nouvelle note\nAvec plusieurs lignes.",
        )

    assert result["id"] == 10
    assert result["content"] == "Nouvelle note\nAvec plusieurs lignes."

    db.add.assert_not_called()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(note)


def test_save_character_note_rejects_character_not_owned_by_user(service):
    """Un utilisateur ne peut pas modifier la note d'un autre."""

    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.note_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(
            ValueError,
            match="Personnage introuvable ou inaccessible.",
        ):
            service.save_character_note(
                character_id=1,
                user_id=42,
                content="Modification interdite.",
            )

    db.add.assert_not_called()
    db.commit.assert_not_called()
