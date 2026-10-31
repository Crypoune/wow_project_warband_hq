"""Tests d'intégration de GoalService avec une vraie base MySQL."""

import os
from uuid import uuid4

import pytest

from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.models import User, Character, Goal
from app.services.goal_service import GoalService
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
    # None signifie que la préparation n'a pas encore abouti.
    ids = None

    try:
        # Une seule transaction pour préparer toutes les données.
        # En cas d'erreur, SQLAlchemy annulera les insertions.
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

        # Transmet les identifiants au test.
        yield ids

    finally:
        try:
            # Nettoyage uniquement si la préparation a réussi.
            if ids is not None:
                with Session.begin() as db:

                    # Supprime les objectifs temporaires.
                    db.query(Goal).filter(
                        Goal.user_id.in_(
                            [ids["user"], ids["other_user"]]
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

def test_goal_creation_and_user_isolation(integration_context):
    """
    Vérifie la création réelle d'objectifs dans MySQL
    et l'isolation des données entre deux utilisateurs.
    """

    service = GoalService()

    # Récupération des identifiants fournis par la fixture.
    user_id = integration_context["user"]
    other_user_id = integration_context["other_user"]
    character_id = integration_context["character"]

    # Création d'un objectif associé à un personnage.
    character_goal = service.create_goal(
        user_id=user_id,
        title="Terminer le raid",
        description="Vaincre le boss final.",
        character_id=character_id,
    )

    # Création d'un objectif lié à la Warband.
    warband_goal = service.create_goal(
        user_id=user_id,
        title="Collectionner les montures",
    )

    # Création d'un objectif pour le deuxième utilisateur.
    other_goal = service.create_goal(
        user_id=other_user_id,
        title="Monter un nouveau personnage",
    )

    # Vérifie que les objectifs ont bien été enregistrés.
    assert character_goal["id"] is not None
    assert character_goal["character_id"] == character_id

    assert warband_goal["id"] is not None
    assert warband_goal["character_id"] is None

    assert other_goal["id"] is not None

    # Vérifie que le premier utilisateur ne voit que ses objectifs.
    user_goals = service.get_goals(user_id)

    assert len(user_goals) == 2
    assert {goal["id"] for goal in user_goals} == {
        character_goal["id"],
        warband_goal["id"],
    }

    # Vérifie que le deuxième utilisateur ne voit que le sien.
    other_user_goals = service.get_goals(other_user_id)

    assert len(other_user_goals) == 1
    assert other_user_goals[0]["id"] == other_goal["id"]

def test_goal_rejects_character_from_another_user(integration_context):
    """
    Vérifie qu'un utilisateur ne peut pas associer
    un objectif au personnage d'un autre utilisateur.
    """

    service = GoalService()

    # L'utilisateur A tente d'utiliser le personnage de l'utilisateur B.
    with pytest.raises(ValueError):
        service.create_goal(
            user_id=integration_context["user"],
            title="Objectif interdit",
            character_id=integration_context["other_character"],
        )

    # Vérifie qu'aucun objectif n'a été créé pour cet utilisateur.
    assert service.get_goals(integration_context["user"]) == []

def test_goal_survives_character_deletion(integration_context):
    """
    Vérifie qu'un objectif survit à la suppression
    du personnage auquel il était associé.
    """

    service = GoalService()

    user_id = integration_context["user"]
    character_id = integration_context["character"]

    # Création d'un objectif associé au personnage.
    goal = service.create_goal(
        user_id=user_id,
        title="Terminer une quête de classe",
        character_id=character_id,
    )

    goal_id = goal["id"]

    # Suppression réelle du personnage dans MySQL.
    with SessionLocal() as db:
        character = db.get(Character, character_id)
        db.delete(character)
        db.commit()

    # Récupération de l'objectif après suppression.
    goals = service.get_goals(user_id)

    assert len(goals) == 1
    assert goals[0]["id"] == goal_id
    assert goals[0]["character_id"] is None

def test_database_rejects_invalid_goal_status(integration_context):
    """
    Vérifie que MySQL refuse un statut invalide
    grâce à la contrainte ck_goals_status.
    """

    with SessionLocal() as db:
        goal = Goal(
            user_id=integration_context["user"],
            title="Objectif avec statut invalide",
            status="INVALID_STATUS",
        )

        db.add(goal)

        # MySQL doit refuser l'insertion.
        with pytest.raises(OperationalError):
            db.commit()

        # Annule la transaction après l'erreur SQL.
        db.rollback()

def test_goal_deletion_does_not_affect_other_users(integration_context):
    """Vérifie qu'un utilisateur ne peut supprimer que ses objectifs."""

    service = GoalService()

    user_id = integration_context["user"]
    other_user_id = integration_context["other_user"]

    # Création d'un objectif pour chaque utilisateur.
    goal = service.create_goal(
        user_id=user_id,
        title="Mon objectif",
    )

    other_goal = service.create_goal(
        user_id=other_user_id,
        title="Objectif de l'autre utilisateur",
    )

    # Suppression du premier objectif.
    service.delete_goal(goal["id"], user_id)

    # Vérifie que le premier objectif a disparu.
    assert service.get_goals(user_id) == []

    # Vérifie que l'objectif de l'autre utilisateur existe toujours.
    other_goals = service.get_goals(other_user_id)

    assert len(other_goals) == 1
    assert other_goals[0]["id"] == other_goal["id"]

def test_user_deletion_cascades_to_goals(integration_context):
    """Vérifie que la suppression d'un utilisateur supprime ses objectifs."""

    service = GoalService()

    user_id = integration_context["user"]
    other_user_id = integration_context["other_user"]

    # Création d'objectifs pour les deux utilisateurs.
    goal = service.create_goal(
        user_id=user_id,
        title="Objectif à supprimer avec son utilisateur",
    )

    other_goal = service.create_goal(
        user_id=other_user_id,
        title="Objectif à conserver",
    )

    # Suppression réelle de l'utilisateur dans MySQL.
    with SessionLocal() as db:
        user = db.get(User, user_id)

        assert user is not None

        db.delete(user)
        db.commit()

    # Vérifie que l'objectif du premier utilisateur a disparu.
    with SessionLocal() as db:
        assert db.get(Goal, goal["id"]) is None

    # Vérifie que l'objectif du second utilisateur existe toujours.
    other_goals = service.get_goals(other_user_id)

    assert len(other_goals) == 1
    assert other_goals[0]["id"] == other_goal["id"]
