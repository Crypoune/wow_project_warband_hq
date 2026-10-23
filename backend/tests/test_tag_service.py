
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import IntegrityError

from app.models.tag import Tag, CharacterTag
from app.services.tag_service import TagService


@pytest.fixture
def service():
    return TagService()


def test_create_tag_success(service):
    """Un utilisateur peut créer un tag personnel."""
    db = MagicMock()
    db.refresh.side_effect = lambda tag: setattr(tag, "id", 1)

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.create_tag(name="Raid")

    assert result == {"id": 1, "name": "Raid"}
    added_tag = db.add.call_args.args[0]

    assert isinstance(added_tag, Tag)
    assert added_tag.name == "Raid"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(added_tag)


@pytest.mark.parametrize("name", ["", "   "])
def test_create_tag_rejects_empty_name(service, name):
    """Un tag ne peut pas avoir un nom vide."""
    with pytest.raises(ValueError):
        service.create_tag(name=name)


def test_get_tags_returns_global_catalog(service):
    """Le catalogue contient les tags globaux."""
    db = MagicMock()
    db.scalars.return_value.all.return_value = [
        SimpleNamespace(id=1, name="Alt"),
        SimpleNamespace(id=2, name="Raid"),
    ]

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_tags()

    assert result == [
        {"id": 1, "name": "Alt"},
        {"id": 2, "name": "Raid"},
    ]

    db.scalars.assert_called_once()


def test_create_tag_trims_name(service):
    """Les espaces autour du nom sont supprimés."""
    db = MagicMock()
    db.refresh.side_effect = lambda tag: setattr(tag, "id", 1)

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.create_tag(name="  Raid  ")

    assert result["name"] == "Raid"
    assert db.add.call_args.args[0].name == "Raid"


def test_create_tag_rejects_name_over_50_characters(service):
    """Le nom d'un tag ne peut pas dépasser 50 caractères."""
    with pytest.raises(ValueError, match="50"):
        service.create_tag(name="R" * 51)


def test_create_tag_rejects_duplicate_name(service):
    """Un utilisateur ne peut pas créer deux tags du même nom."""
    db = MagicMock()
    db.commit.side_effect = IntegrityError(
        "INSERT INTO tags",
        {},
        Exception("duplicate key"),
    )

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(
            ValueError,
            match="Impossible de créer le tag",
        ):
            service.create_tag(name="Raid")

    db.rollback.assert_called_once()


def test_assign_tag_to_character_success(service):
    """Un utilisateur peut attribuer son tag à son personnage."""
    tag = SimpleNamespace(id=10, user_id=42)
    character = SimpleNamespace(id=5, user_id=42)

    db = MagicMock()
    db.scalar.side_effect = [tag, character]
    db.get.return_value = None

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.assign_tag(
            user_id=42,
            character_id=5,
            tag_id=10,
        )

    assert result is True
    db.add.assert_called_once()

    association = db.add.call_args.args[0]
    assert isinstance(association, CharacterTag)
    assert association.character_id == 5
    assert association.tag_id == 10

    db.commit.assert_called_once()


def test_assign_tag_rejects_tag_owned_by_another_user(service):
    """Un utilisateur ne peut pas utiliser le tag d'un autre utilisateur."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Tag introuvable"):
            service.assign_tag(
                user_id=42,
                character_id=5,
                tag_id=10,
            )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_assign_tag_rejects_character_owned_by_another_user(service):
    """Un utilisateur ne peut pas taguer le personnage d'un autre."""
    tag = SimpleNamespace(id=10, user_id=42)

    db = MagicMock()
    db.scalar.side_effect = [tag, None]

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Personnage introuvable"):
            service.assign_tag(
                user_id=42,
                character_id=5,
                tag_id=10,
            )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_assign_tag_rejects_duplicate_association(service):
    """Une association existante provoque une erreur explicite."""
    tag = SimpleNamespace(id=10, user_id=42)
    character = SimpleNamespace(id=5, user_id=42)
    association = SimpleNamespace(character_id=5, tag_id=10)

    db = MagicMock()
    db.scalar.side_effect = [tag, character]
    db.get.return_value = association

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="déjà attribué"):
            service.assign_tag(
                user_id=42,
                character_id=5,
                tag_id=10,
            )

    db.add.assert_not_called()
    db.commit.assert_not_called()

def test_remove_tag_success(service):
    """Un utilisateur peut retirer un tag de son personnage."""
    tag = SimpleNamespace(id=10, user_id=42)
    character = SimpleNamespace(id=5, user_id=42)
    association = SimpleNamespace(character_id=5, tag_id=10)

    db = MagicMock()
    db.scalar.side_effect = [character, tag]
    db.get.return_value = association

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.remove_tag(
            user_id=42,
            character_id=5,
            tag_id=10,
        )

    assert result is True
    db.delete.assert_called_once_with(association)
    db.commit.assert_called_once()


def test_remove_tag_rejects_character_owned_by_another_user(service):
    """Un utilisateur ne peut pas modifier les tags d'un autre personnage."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Personnage introuvable"):
            service.remove_tag(
                user_id=42,
                character_id=5,
                tag_id=10,
            )

    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_remove_tag_rejects_missing_association(service):
    """On ne peut pas retirer une association inexistante."""
    tag = SimpleNamespace(id=10, user_id=42)
    character = SimpleNamespace(id=5, user_id=42)

    db = MagicMock()
    db.scalar.side_effect = [character, tag]
    db.get.return_value = None

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(
            ValueError,
            match="n'est pas attribué",
        ):
            service.remove_tag(
                user_id=42,
                character_id=5,
                tag_id=10,
            )

    db.delete.assert_not_called()
    db.commit.assert_not_called()

def test_get_character_tags_success(service):
    """Récupère les tags associés au personnage."""
    character = SimpleNamespace(id=5, user_id=42)

    db = MagicMock()
    db.scalar.return_value = character
    db.scalars.return_value.all.return_value = [
        SimpleNamespace(id=10, name="Raid", user_id=42),
        SimpleNamespace(id=11, name="Main", user_id=42),
    ]

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_character_tags(
            user_id=42,
            character_id=5,
        )

    assert result == [
        {"id": 10, "name": "Raid"},
        {"id": 11, "name": "Main"},
    ]

    statement = db.scalars.call_args.args[0]
    compiled = statement.compile(dialect=mysql.dialect())

    assert "character_tags.character_id" in str(compiled)


def test_get_character_tags_returns_empty_list(service):
    """Un personnage sans tag renvoie une liste vide."""
    character = SimpleNamespace(id=5, user_id=42)

    db = MagicMock()
    db.scalar.return_value = character
    db.scalars.return_value.all.return_value = []

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_character_tags(
            user_id=42,
            character_id=5,
        )

    assert result == []


def test_get_character_tags_rejects_foreign_character(service):
    """Un utilisateur ne peut pas consulter les tags d'un autre personnage."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Personnage introuvable"):
            service.get_character_tags(
                user_id=42,
                character_id=5,
            )

    db.scalars.assert_not_called()


def test_update_tag_success(service):
    """Un administrateur peut modifier le nom d'un tag via le service."""
    tag = Tag(id=1, name="Raid")

    db = MagicMock()
    db.get.return_value = tag

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.update_tag(tag_id=1, name="  Mythique  ")

    assert result == {"id": 1, "name": "Mythique"}
    assert tag.name == "Mythique"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(tag)


def test_update_tag_rejects_missing_tag(service):
    """La modification d'un tag inexistant est refusée."""
    db = MagicMock()
    db.get.return_value = None

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Tag introuvable"):
            service.update_tag(tag_id=999, name="Mythique")

    db.commit.assert_not_called()


@pytest.mark.parametrize("name", ["", "   "])
def test_update_tag_rejects_empty_name(service, name):
    """Un nom vide ou composé d'espaces est refusé."""
    with pytest.raises(ValueError, match="vide"):
        service.update_tag(tag_id=1, name=name)


def test_update_tag_rejects_name_over_50_characters(service):
    """Un nom de tag ne peut pas dépasser 50 caractères."""
    with pytest.raises(ValueError, match="50"):
        service.update_tag(tag_id=1, name="R" * 51)


def test_update_tag_rejects_duplicate_name(service):
    """Deux tags ne peuvent pas avoir le même nom."""
    db = MagicMock()
    db.get.return_value = Tag(id=1, name="Raid")
    db.commit.side_effect = IntegrityError(
        "UPDATE tags",
        {},
        Exception("duplicate key"),
    )

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="existe déjà"):
            service.update_tag(tag_id=1, name="Mythique")

    db.rollback.assert_called_once()


def test_delete_tag_success(service):
    """Un tag existant peut être supprimé."""
    tag = Tag(id=1, name="Raid")

    db = MagicMock()
    db.get.return_value = tag

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.delete_tag(tag_id=1)

    assert result is True
    db.delete.assert_called_once_with(tag)
    db.commit.assert_called_once()


def test_delete_tag_removes_character_associations(service):
    """La suppression d'un tag nettoie ses associations."""
    tag = Tag(id=1, name="Raid")

    db = MagicMock()
    db.get.return_value = tag

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        service.delete_tag(tag_id=1)

    db.query.assert_called_once_with(CharacterTag)
    db.query.return_value.filter.assert_called_once()
    db.query.return_value.filter.return_value.delete.assert_called_once_with(
        synchronize_session=False
    )
    db.delete.assert_called_once_with(tag)
    db.commit.assert_called_once()


def test_delete_tag_rejects_missing_tag(service):
    """La suppression d'un tag inexistant est refusée."""
    db = MagicMock()
    db.get.return_value = None

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Tag introuvable"):
            service.delete_tag(tag_id=999)

    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_get_tags_for_characters_groups_tags_by_character(service):
    """Récupère les tags de plusieurs personnages en une requête."""
    db = MagicMock()
    db.execute.return_value.all.return_value = [
        (1, 10, "Main"),
        (1, 11, "Raid"),
        (2, 10, "Main"),
    ]

    with patch("app.services.tag_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_tags_for_characters(
            user_id=42,
            character_ids=[1, 2, 3],
        )

    assert result == {
        1: [
            {"id": 10, "name": "Main"},
            {"id": 11, "name": "Raid"},
        ],
        2: [{"id": 10, "name": "Main"}],
        3: [],
    }

    db.execute.assert_called_once()


def test_get_tags_for_characters_returns_empty_dict_without_ids(service):
    """Aucune requête SQL n'est exécutée sans identifiant."""
    with patch("app.services.tag_service.SessionLocal") as session_local:
        result = service.get_tags_for_characters(
            user_id=42,
            character_ids=[],
        )

    assert result == {}
    session_local.assert_not_called()
