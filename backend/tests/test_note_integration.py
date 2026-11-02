
"""Tests d'intégration de NoteService avec une vraie base MySQL."""

import os
from uuid import uuid4

import pytest

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.models import User, Character, CharacterNote
from app.services.note_service import NoteService
from app.core.database import SessionLocal


@pytest.fixture
def integration_context():
    """
    Prépare un environnement de test isolé dans warband_hq_test.
    """

    # Récupère l'adresse de connexion à la base depuis .env.test.
    url = make_url(os.environ["DATABASE_URL"])

    # SÉCURITÉ : interdit l'utilisation de la base principale.
    if url.database != "warband_hq_test":
        pytest.fail(
            "Sécurité : les tests doivent utiliser warband_hq_test."
        )

    # Crée un moteur SQLAlchemy dédié aux tests.
    engine = create_engine(url)

    # Fabrique des sessions pour effectuer les opérations SQL.
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    # Identifiants des données temporaires.
    ids = None

    try:
        # Préparation des données dans une transaction.
        with Session.begin() as db:

            # Création de deux utilisateurs indépendants.
            user = User(
                blizzard_account_id=f"i{uuid4().hex[:23]}"
            )
            other_user = User(
                blizzard_account_id=f"o{uuid4().hex[:23]}"
            )

            db.add_all([user, other_user])
            db.flush()

            # Création d'un personnage pour chaque utilisateur.
            character = Character(
                blizzard_character_id=900001,
                user_id=user.id,
            )
            other_character = Character(
                blizzard_character_id=900002,
                user_id=other_user.id,
            )

            db.add_all([character, other_character])
            db.flush()

            # Conservation des identifiants nécessaires aux tests.
            ids = {
                "user": user.id,
                "other_user": other_user.id,
                "character": character.id,
                "other_character": other_character.id,
            }

        yield ids

    finally:
        try:
            # Nettoyage uniquement si la préparation a réussi.
            if ids is not None:
                with Session.begin() as db:

                    # Supprime les notes temporaires.
                    db.query(CharacterNote).filter(
                        CharacterNote.character_id.in_(
                            [ids["character"], ids["other_character"]]
                        )
                    ).delete(synchronize_session=False)

                    # Supprime les personnages temporaires.
                    db.query(Character).filter(
                        Character.id.in_(
                            [ids["character"], ids["other_character"]]
                        )
                    ).delete(synchronize_session=False)

                    # Supprime les utilisateurs temporaires.
                    db.query(User).filter(
                        User.id.in_(
                            [ids["user"], ids["other_user"]]
                        )
                    ).delete(synchronize_session=False)

        finally:
            # Ferme toujours proprement le moteur SQLAlchemy.
            engine.dispose()


def test_note_creation_and_persistence(integration_context):
    """Vérifie la création et la persistance d'une note."""

    service = NoteService()

    character_id = integration_context["character"]
    user_id = integration_context["user"]

    content = "Main personnage\nSpécialisé en DPS\nÀ jouer en raid."

    note = service.save_character_note(
        character_id=character_id,
        user_id=user_id,
        content=content,
    )

    assert note["id"] is not None
    assert note["character_id"] == character_id
    assert note["content"] == content

    # Vérification directe dans la base de données.
    with SessionLocal() as db:
        persisted_note = db.get(CharacterNote, note["id"])

        assert persisted_note is not None
        assert persisted_note.content == content


def test_note_update_is_persisted(integration_context):
    """Vérifie que la modification d'une note est persistée."""

    service = NoteService()

    character_id = integration_context["character"]
    user_id = integration_context["user"]

    # Création initiale de la note.
    note = service.save_character_note(
        character_id=character_id,
        user_id=user_id,
        content="Ancienne description",
    )

    # Modification de la note.
    updated_note = service.save_character_note(
        character_id=character_id,
        user_id=user_id,
        content="Nouvelle description\nAvec plusieurs lignes.",
    )

    assert updated_note["id"] == note["id"]
    assert updated_note["content"] == (
        "Nouvelle description\nAvec plusieurs lignes."
    )

    # Vérifie que la note existante a été modifiée.
    with SessionLocal() as db:
        persisted_note = db.get(CharacterNote, note["id"])

        assert persisted_note is not None
        assert persisted_note.content == updated_note["content"]


def test_note_creation_and_user_isolation(integration_context):
    """
    Vérifie que chaque utilisateur possède sa propre note
    et ne peut pas accéder à celle d'un autre utilisateur.
    """

    service = NoteService()

    # Création d'une note pour chaque utilisateur.
    note = service.save_character_note(
        character_id=integration_context["character"],
        user_id=integration_context["user"],
        content="Note personnelle A",
    )

    other_note = service.save_character_note(
        character_id=integration_context["other_character"],
        user_id=integration_context["other_user"],
        content="Note personnelle B",
    )

    assert note["id"] != other_note["id"]

    # Chaque utilisateur récupère uniquement sa note.
    user_note = service.get_character_note(
        integration_context["character"],
        integration_context["user"],
    )

    other_user_note = service.get_character_note(
        integration_context["other_character"],
        integration_context["other_user"],
    )

    assert user_note["content"] == "Note personnelle A"
    assert other_user_note["content"] == "Note personnelle B"


def test_note_rejects_character_from_another_user(integration_context):
    """
    Vérifie qu'un utilisateur ne peut pas consulter
    la note du personnage d'un autre utilisateur.
    """

    service = NoteService()

    # Création d'une note appartenant au deuxième utilisateur.
    service.save_character_note(
        character_id=integration_context["other_character"],
        user_id=integration_context["other_user"],
        content="Note privée",
    )

    # Le premier utilisateur tente d'y accéder.
    with pytest.raises(
        ValueError,
        match="Personnage introuvable ou inaccessible.",
    ):
        service.get_character_note(
            character_id=integration_context["other_character"],
            user_id=integration_context["user"],
        )


def test_character_deletion_cascades_to_note(integration_context):
    """
    Vérifie que la suppression d'un personnage
    entraîne la suppression de sa note.
    """

    service = NoteService()

    # Création d'une note pour chaque utilisateur.
    note = service.save_character_note(
        character_id=integration_context["character"],
        user_id=integration_context["user"],
        content="Note à supprimer",
    )

    other_note = service.save_character_note(
        character_id=integration_context["other_character"],
        user_id=integration_context["other_user"],
        content="Note à conserver",
    )

    # Suppression réelle du personnage dans MySQL.
    with SessionLocal() as db:
        character = db.get(Character, integration_context["character"])

        assert character is not None

        db.delete(character)
        db.commit()

    # Vérification de la suppression en cascade.
    with SessionLocal() as db:
        assert db.get(CharacterNote, note["id"]) is None

        # La note de l'autre utilisateur doit être conservée.
        assert db.get(CharacterNote, other_note["id"]) is not None


def test_user_deletion_cascades_to_note(integration_context):
    """
    Vérifie que la suppression d'un utilisateur
    entraîne la suppression de ses personnages et de leurs notes.
    """

    service = NoteService()

    # Création d'une note pour chaque utilisateur.
    note = service.save_character_note(
        character_id=integration_context["character"],
        user_id=integration_context["user"],
        content="Note à supprimer avec son utilisateur",
    )

    other_note = service.save_character_note(
        character_id=integration_context["other_character"],
        user_id=integration_context["other_user"],
        content="Note à conserver",
    )

    # Suppression réelle de l'utilisateur dans MySQL.
    with SessionLocal() as db:
        user = db.get(User, integration_context["user"])

        assert user is not None

        db.delete(user)
        db.commit()

    # Vérification des suppressions en cascade.
    with SessionLocal() as db:
        assert db.get(Character, integration_context["character"]) is None
        assert db.get(CharacterNote, note["id"]) is None

        # Les données de l'autre utilisateur restent intactes.
        assert db.get(Character, integration_context["other_character"]) is not None
        assert db.get(CharacterNote, other_note["id"]) is not None
