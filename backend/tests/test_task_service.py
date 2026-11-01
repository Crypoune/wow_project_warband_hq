
from unittest.mock import MagicMock, patch

import pytest

from app.models.task import Task
from app.services.task_service import TaskService


@pytest.fixture
def service():
    return TaskService()


def test_create_task_success(service):
    """Un utilisateur peut créer une tâche pour son objectif."""
    goal = MagicMock(id=1, user_id=42)

    db = MagicMock()
    db.scalar.return_value = goal
    db.refresh.side_effect = lambda task: setattr(task, "id", 10)

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.create_task(
            goal_id=1,
            user_id=42,
            title="  Terminer le donjon  ",
            description="Vaincre le boss final.",
        )

    assert result["id"] == 10
    assert result["goal_id"] == 1
    assert result["title"] == "Terminer le donjon"
    assert result["description"] == "Vaincre le boss final."
    assert result["is_completed"] is False

    added_task = db.add.call_args.args[0]
    assert isinstance(added_task, Task)
    assert added_task.goal_id == 1

    db.commit.assert_called_once()


@pytest.mark.parametrize("title", ["", "   "])
def test_create_task_rejects_empty_title(service, title):
    """Une tâche ne peut pas avoir un titre vide."""
    with pytest.raises(ValueError, match="vide"):
        service.create_task(
            goal_id=1,
            user_id=42,
            title=title,
        )


def test_create_task_rejects_title_over_100_characters(service):
    """Le titre d'une tâche ne peut pas dépasser 100 caractères."""
    with pytest.raises(ValueError, match="100"):
        service.create_task(
            goal_id=1,
            user_id=42,
            title="A" * 101,
        )


def test_create_task_rejects_goal_not_owned_by_user(service):
    """Un utilisateur ne peut pas créer une tâche sur l'objectif d'un autre."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Objectif"):
            service.create_task(
                goal_id=1,
                user_id=42,
                title="Tâche interdite",
            )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_get_tasks_success(service):
    """Le service retourne les tâches d'un objectif."""
    goal = MagicMock(id=1, user_id=42)

    tasks = [
        MagicMock(
            id=10,
            goal_id=1,
            title="Terminer le donjon",
            description=None,
            is_completed=False,
        ),
        MagicMock(
            id=11,
            goal_id=1,
            title="Récupérer le butin",
            description="Ne pas oublier le coffre.",
            is_completed=True,
        ),
    ]

    db = MagicMock()
    db.scalar.return_value = goal
    db.scalars.return_value.all.return_value = tasks

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_tasks(goal_id=1, user_id=42)

    assert len(result) == 2
    assert result[0]["title"] == "Terminer le donjon"
    assert result[0]["is_completed"] is False
    assert result[1]["title"] == "Récupérer le butin"
    assert result[1]["is_completed"] is True


def test_get_tasks_rejects_goal_not_owned_by_user(service):
    """Un utilisateur ne peut pas consulter les tâches d'un autre."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Objectif"):
            service.get_tasks(goal_id=1, user_id=42)

    db.scalars.assert_not_called()


def test_get_tasks_returns_empty_list(service):
    """Un objectif sans tâche retourne une liste vide."""
    goal = MagicMock(id=1, user_id=42)

    db = MagicMock()
    db.scalar.return_value = goal
    db.scalars.return_value.all.return_value = []

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_tasks(goal_id=1, user_id=42)

    assert result == []


def test_update_task_success(service):
    """Un utilisateur peut modifier sa tâche."""
    task = MagicMock(
        id=10,
        goal_id=1,
        title="Ancien titre",
        description=None,
        is_completed=False,
    )

    db = MagicMock()
    db.scalar.return_value = task

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.update_task(
            task_id=10,
            user_id=42,
            title="Nouveau titre",
            is_completed=True,
        )

    assert result["title"] == "Nouveau titre"
    assert result["is_completed"] is True
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(task)


def test_update_task_can_clear_description(service):
    """Un utilisateur peut effacer la description d'une tâche."""
    task = MagicMock(
        id=10,
        goal_id=1,
        title="Ma tâche",
        description="Ancienne description",
        is_completed=False,
    )

    db = MagicMock()
    db.scalar.return_value = task

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.update_task(
            task_id=10,
            user_id=42,
            description=None,
        )

    assert result["description"] is None
    db.commit.assert_called_once()


def test_update_task_rejects_task_not_owned_by_user(service):
    """Un utilisateur ne peut pas modifier la tâche d'un autre."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Tâche"):
            service.update_task(
                task_id=10,
                user_id=42,
                title="Modification interdite",
            )

    db.commit.assert_not_called()


def test_update_task_rejects_empty_title(service):
    """Une tâche ne peut pas recevoir un titre vide."""
    task = MagicMock(
        id=10,
        goal_id=1,
        title="Ancien titre",
        description=None,
        is_completed=False,
    )

    db = MagicMock()
    db.scalar.return_value = task

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="vide"):
            service.update_task(
                task_id=10,
                user_id=42,
                title="   ",
            )

    db.commit.assert_not_called()


def test_delete_task_success(service):
    """Un utilisateur peut supprimer sa propre tâche."""
    task = MagicMock(id=10)

    db = MagicMock()
    db.scalar.return_value = task

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.delete_task(task_id=10, user_id=42)

    assert result == {
        "message": "Tâche supprimée avec succès.",
        "id": 10,
    }

    db.delete.assert_called_once_with(task)
    db.commit.assert_called_once()


def test_delete_task_rejects_task_not_owned_by_user(service):
    """Un utilisateur ne peut pas supprimer la tâche d'un autre."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.task_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="Tâche"):
            service.delete_task(task_id=10, user_id=42)

    db.delete.assert_not_called()
    db.commit.assert_not_called()
