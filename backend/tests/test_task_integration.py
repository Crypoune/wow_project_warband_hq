"""Tests d'intégration de TaskService avec une vraie base MySQL."""

import os
from uuid import uuid4

import pytest

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.models import User, Goal, Task
from app.services.task_service import TaskService
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

            # Création d'un objectif pour chaque utilisateur.
            goal = Goal(
                user_id=user.id,
                title="Objectif principal",
            )
            other_goal = Goal(
                user_id=other_user.id,
                title="Objectif secondaire",
            )

            db.add_all([goal, other_goal])
            db.flush()

            # Conservation des identifiants nécessaires aux tests.
            ids = {
                "user": user.id,
                "other_user": other_user.id,
                "goal": goal.id,
                "other_goal": other_goal.id,
            }

        # Transmet les identifiants au test.
        yield ids

    finally:
        try:
            # Nettoyage uniquement si la préparation a réussi.
            if ids is not None:
                with Session.begin() as db:

                    # Supprime les tâches temporaires.
                    db.query(Task).filter(
                        Task.goal_id.in_(
                            [ids["goal"], ids["other_goal"]]
                        )
                    ).delete(synchronize_session=False)

                    # Supprime les objectifs temporaires.
                    db.query(Goal).filter(
                        Goal.id.in_(
                            [ids["goal"], ids["other_goal"]]
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


def test_task_creation_and_user_isolation(integration_context):
    """
    Vérifie la création réelle de tâches dans MySQL
    et l'isolation des données entre deux utilisateurs.
    """

    service = TaskService()

    user_id = integration_context["user"]
    other_user_id = integration_context["other_user"]
    goal_id = integration_context["goal"]
    other_goal_id = integration_context["other_goal"]

    # Création d'une tâche pour chaque utilisateur.
    task = service.create_task(
        goal_id=goal_id,
        user_id=user_id,
        title="Terminer le donjon",
        description="Vaincre le boss final.",
    )

    other_task = service.create_task(
        goal_id=other_goal_id,
        user_id=other_user_id,
        title="Améliorer son équipement",
    )

    # Vérifie que les tâches ont bien été enregistrées.
    assert task["id"] is not None
    assert task["goal_id"] == goal_id
    assert task["title"] == "Terminer le donjon"
    assert task["is_completed"] is False

    assert other_task["id"] is not None

    # Vérifie que le premier utilisateur ne voit que ses tâches.
    user_tasks = service.get_tasks(goal_id, user_id)

    assert len(user_tasks) == 1
    assert user_tasks[0]["id"] == task["id"]

    # Vérifie que le deuxième utilisateur ne voit que les siennes.
    other_user_tasks = service.get_tasks(other_goal_id, other_user_id)

    assert len(other_user_tasks) == 1
    assert other_user_tasks[0]["id"] == other_task["id"]


def test_task_rejects_goal_from_another_user(integration_context):
    """
    Vérifie qu'un utilisateur ne peut pas créer une tâche
    dans l'objectif d'un autre utilisateur.
    """

    service = TaskService()

    with pytest.raises(
        ValueError,
        match="Objectif introuvable ou inaccessible.",
    ):
        service.create_task(
            goal_id=integration_context["other_goal"],
            user_id=integration_context["user"],
            title="Tâche interdite",
        )

    # Vérifie qu'aucune tâche n'a été créée.
    assert service.get_tasks(
        integration_context["goal"],
        integration_context["user"],
    ) == []


def test_task_update_is_persisted(integration_context):
    """
    Vérifie que les modifications d'une tâche
    sont réellement enregistrées dans MySQL.
    """

    service = TaskService()

    task = service.create_task(
        goal_id=integration_context["goal"],
        user_id=integration_context["user"],
        title="Ancien titre",
        description="Ancienne description",
    )

    # Modification de la tâche.
    updated_task = service.update_task(
        task_id=task["id"],
        user_id=integration_context["user"],
        title="Nouveau titre",
        description="Nouvelle description",
        is_completed=True,
    )

    assert updated_task["title"] == "Nouveau titre"
    assert updated_task["description"] == "Nouvelle description"
    assert updated_task["is_completed"] is True

    # Vérification directe dans la base de données.
    with SessionLocal() as db:
        persisted_task = db.get(Task, task["id"])

        assert persisted_task is not None
        assert persisted_task.title == "Nouveau titre"
        assert persisted_task.description == "Nouvelle description"
        assert persisted_task.is_completed is True


def test_task_deletion_is_persisted(integration_context):
    """
    Vérifie qu'une tâche supprimée disparaît réellement
    de la base de données.
    """

    service = TaskService()

    task = service.create_task(
        goal_id=integration_context["goal"],
        user_id=integration_context["user"],
        title="Tâche à supprimer",
    )

    # Suppression de la tâche.
    result = service.delete_task(
        task_id=task["id"],
        user_id=integration_context["user"],
    )

    assert result["id"] == task["id"]

    # Vérification directe dans la base de données.
    with SessionLocal() as db:
        assert db.get(Task, task["id"]) is None


def test_task_update_rejects_another_user(integration_context):
    """
    Vérifie qu'un utilisateur ne peut pas modifier
    une tâche appartenant à un autre utilisateur.
    """

    service = TaskService()

    task = service.create_task(
        goal_id=integration_context["goal"],
        user_id=integration_context["user"],
        title="Tâche privée",
    )

    with pytest.raises(
        ValueError,
        match="Tâche introuvable ou inaccessible.",
    ):
        service.update_task(
            task_id=task["id"],
            user_id=integration_context["other_user"],
            title="Modification interdite",
        )

    # Vérifie que le titre original est conservé.
    user_tasks = service.get_tasks(
        integration_context["goal"],
        integration_context["user"],
    )

    assert user_tasks[0]["title"] == "Tâche privée"


def test_task_deletion_rejects_another_user(integration_context):
    """
    Vérifie qu'un utilisateur ne peut pas supprimer
    une tâche appartenant à un autre utilisateur.
    """

    service = TaskService()

    task = service.create_task(
        goal_id=integration_context["goal"],
        user_id=integration_context["user"],
        title="Tâche à protéger",
    )

    with pytest.raises(
        ValueError,
        match="Tâche introuvable ou inaccessible.",
    ):
        service.delete_task(
            task_id=task["id"],
            user_id=integration_context["other_user"],
        )

    # Vérifie que la tâche existe toujours.
    with SessionLocal() as db:
        assert db.get(Task, task["id"]) is not None


def test_goal_deletion_cascades_to_tasks(integration_context):
    """
    Vérifie que la suppression d'un objectif
    entraîne la suppression de ses tâches.
    """

    service = TaskService()

    task = service.create_task(
        goal_id=integration_context["goal"],
        user_id=integration_context["user"],
        title="Tâche liée à l'objectif",
    )

    other_task = service.create_task(
        goal_id=integration_context["other_goal"],
        user_id=integration_context["other_user"],
        title="Tâche à conserver",
    )

    # Suppression réelle de l'objectif dans MySQL.
    with SessionLocal() as db:
        goal = db.get(Goal, integration_context["goal"])

        assert goal is not None

        db.delete(goal)
        db.commit()

    # Vérifie que la tâche liée à l'objectif a disparu.
    with SessionLocal() as db:
        assert db.get(Task, task["id"]) is None

        # Vérifie que la tâche de l'autre utilisateur existe toujours.
        assert db.get(Task, other_task["id"]) is not None


def test_user_deletion_cascades_to_tasks(integration_context):
    """
    Vérifie que la suppression d'un utilisateur
    entraîne la suppression de ses objectifs et de ses tâches.
    """

    service = TaskService()

    task = service.create_task(
        goal_id=integration_context["goal"],
        user_id=integration_context["user"],
        title="Tâche à supprimer avec son utilisateur",
    )

    other_task = service.create_task(
        goal_id=integration_context["other_goal"],
        user_id=integration_context["other_user"],
        title="Tâche à conserver",
    )

    # Suppression réelle de l'utilisateur dans MySQL.
    with SessionLocal() as db:
        user = db.get(User, integration_context["user"])

        assert user is not None

        db.delete(user)
        db.commit()

    # Vérification des suppressions en cascade.
    with SessionLocal() as db:
        assert db.get(Goal, integration_context["goal"]) is None
        assert db.get(Task, task["id"]) is None

        # Les données de l'autre utilisateur doivent rester intactes.
        assert db.get(Goal, integration_context["other_goal"]) is not None
        assert db.get(Task, other_task["id"]) is not None
