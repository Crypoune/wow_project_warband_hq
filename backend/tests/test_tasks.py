"""Tests API des tâches de Warband HQ."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import CurrentAuth, get_current_auth


# ============================================================
# 1. INITIALISATION DU CLIENT DE TEST
# ============================================================

# Client de test : permet d'appeler l'API sans lancer un serveur.
client = TestClient(app)

# Simule un utilisateur authentifié avec l'identifiant 1.
AUTH = CurrentAuth(user_id=1, access_token="test-access-token")


def override_auth():
    """Remplace l'authentification réelle par notre utilisateur de test."""
    return AUTH


def setup_function():
    """Applique l'authentification simulée avant chaque test."""
    app.dependency_overrides[get_current_auth] = override_auth


def teardown_function():
    """Nettoie les remplacements de dépendances après chaque test."""
    app.dependency_overrides.clear()


# ============================================================
# 2. CRÉATION DES TÂCHES
# ============================================================

def test_create_task_success():
    """Une requête valide doit renvoyer la tâche créée."""

    task = {
        "id": 1,
        "goal_id": 10,
        "title": "Complete a dungeon",
        "description": "Finish a Mythic dungeon",
        "is_completed": False,
    }

    with patch(
        "app.api.tasks.task_service.create_task",
        return_value=task,
    ) as service:
        response = client.post(
            "/api/goals/10/tasks",
            json={
                "title": "Complete a dungeon",
                "description": "Finish a Mythic dungeon",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"task": task}

    service.assert_called_once_with(
        goal_id=10,
        user_id=1,
        title="Complete a dungeon",
        description="Finish a Mythic dungeon",
    )


def test_create_task_rejects_empty_title():
    """Un titre vide doit être rejeté par la validation de l'API."""

    response = client.post(
        "/api/goals/10/tasks",
        json={"title": ""},
    )

    assert response.status_code == 422


def test_create_task_rejects_title_over_100_characters():
    """Un titre dépassant 100 caractères doit être rejeté."""

    response = client.post(
        "/api/goals/10/tasks",
        json={"title": "A" * 101},
    )

    assert response.status_code == 422


def test_create_task_rejects_goal_not_owned():
    """Un objectif inexistant ou inaccessible doit renvoyer une erreur 404."""

    with patch(
        "app.api.tasks.task_service.create_task",
        side_effect=ValueError("Objectif introuvable ou inaccessible."),
    ) as service:
        response = client.post(
            "/api/goals/10/tasks",
            json={"title": "Complete a dungeon"},
        )

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Objectif introuvable ou inaccessible."
    )

    service.assert_called_once_with(
        goal_id=10,
        user_id=1,
        title="Complete a dungeon",
        description=None,
    )


# ============================================================
# 3. RÉCUPÉRATION DES TÂCHES
# ============================================================

def test_get_tasks_success():
    """La route doit renvoyer les tâches associées à un objectif."""

    tasks = [
        {
            "id": 1,
            "goal_id": 10,
            "title": "Complete a dungeon",
            "description": None,
            "is_completed": False,
        },
        {
            "id": 2,
            "goal_id": 10,
            "title": "Collect 100 resources",
            "description": None,
            "is_completed": True,
        },
    ]

    with patch(
        "app.api.tasks.task_service.get_tasks",
        return_value=tasks,
    ) as service:
        response = client.get("/api/goals/10/tasks")

    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}

    service.assert_called_once_with(
        goal_id=10,
        user_id=1,
    )


def test_get_tasks_returns_empty_list():
    """Un objectif sans tâche doit renvoyer une liste vide."""

    with patch(
        "app.api.tasks.task_service.get_tasks",
        return_value=[],
    ):
        response = client.get("/api/goals/10/tasks")

    assert response.status_code == 200
    assert response.json() == {"tasks": []}


def test_get_tasks_rejects_goal_not_owned():
    """Un objectif inaccessible doit renvoyer une erreur 404."""

    with patch(
        "app.api.tasks.task_service.get_tasks",
        side_effect=ValueError("Objectif introuvable ou inaccessible."),
    ):
        response = client.get("/api/goals/10/tasks")

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Objectif introuvable ou inaccessible."
    )


# ============================================================
# 4. MODIFICATION DES TÂCHES
# ============================================================

def test_update_task_success():
    """La route doit transmettre uniquement les champs à modifier."""

    task = {
        "id": 1,
        "goal_id": 10,
        "title": "Complete a dungeon",
        "description": "Updated description",
        "is_completed": True,
    }

    with patch(
        "app.api.tasks.task_service.update_task",
        return_value=task,
    ) as service:
        response = client.patch(
            "/api/tasks/1",
            json={
                "description": "Updated description",
                "is_completed": True,
            },
        )

    assert response.status_code == 200
    assert response.json() == {"task": task}

    service.assert_called_once_with(
        task_id=1,
        user_id=1,
        description="Updated description",
        is_completed=True,
    )


@patch("app.api.tasks.task_service.update_task")
def test_update_task_rejects_empty_title(mock_update_task):
    """Un titre vide doit être rejeté par le service."""

    mock_update_task.side_effect = ValueError(
        "Le titre de la tâche ne peut pas être vide."
    )

    response = client.patch(
        "/api/tasks/1",
        json={"title": ""},
    )

    assert response.status_code == 400
    assert response.json()["message"] == (
        "Le titre de la tâche ne peut pas être vide."
    )


def test_update_task_rejects_null_title():
    """Un titre explicitement envoyé à null doit être refusé."""

    response = client.patch(
        "/api/tasks/1",
        json={"title": None},
    )

    assert response.status_code == 422
    assert response.json()["message"] == (
        "Le titre ne peut pas être null."
    )


def test_update_task_rejects_null_completion_status():
    """Le statut de complétion ne peut pas être explicitement null."""

    response = client.patch(
        "/api/tasks/1",
        json={"is_completed": None},
    )

    assert response.status_code == 422
    assert response.json()["message"] == (
        "Le statut de complétion ne peut pas être null."
    )


def test_update_task_rejects_unknown_field():
    """La requête PATCH ne doit pas accepter de champs inconnus."""

    response = client.patch(
        "/api/tasks/1",
        json={"user_id": 999},
    )

    assert response.status_code == 422


def test_update_task_can_clear_description():
    """Une description peut être effacée en envoyant null."""

    task = {
        "id": 1,
        "goal_id": 10,
        "title": "Complete a dungeon",
        "description": None,
        "is_completed": False,
    }

    with patch(
        "app.api.tasks.task_service.update_task",
        return_value=task,
    ) as service:
        response = client.patch(
            "/api/tasks/1",
            json={"description": None},
        )

    assert response.status_code == 200
    assert response.json() == {"task": task}

    service.assert_called_once_with(
        task_id=1,
        user_id=1,
        description=None,
    )


def test_update_task_rejects_task_not_owned():
    """Une tâche inaccessible doit renvoyer une erreur 404."""

    with patch(
        "app.api.tasks.task_service.update_task",
        side_effect=ValueError("Tâche introuvable ou inaccessible."),
    ):
        response = client.patch(
            "/api/tasks/1",
            json={"is_completed": True},
        )

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Tâche introuvable ou inaccessible."
    )


# ============================================================
# 5. SUPPRESSION DES TÂCHES
# ============================================================

def test_delete_task_success():
    """La suppression doit renvoyer la réponse du service."""

    result = {
        "message": "Tâche supprimée avec succès.",
        "id": 1,
    }

    with patch(
        "app.api.tasks.task_service.delete_task",
        return_value=result,
    ) as service:
        response = client.delete("/api/tasks/1")

    assert response.status_code == 200
    assert response.json() == result

    service.assert_called_once_with(
        task_id=1,
        user_id=1,
    )


def test_delete_task_rejects_task_not_owned():
    """Une tâche inaccessible doit renvoyer une erreur 404."""

    with patch(
        "app.api.tasks.task_service.delete_task",
        side_effect=ValueError("Tâche introuvable ou inaccessible."),
    ):
        response = client.delete("/api/tasks/1")

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Tâche introuvable ou inaccessible."
    )


# ============================================================
# 6. GESTION DES ERREURS DE BASE DE DONNÉES
# ============================================================

def test_create_task_handles_database_error():
    """Une erreur SQL pendant la création doit renvoyer une erreur 500."""

    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.tasks.task_service.create_task",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.post(
            "/api/goals/10/tasks",
            json={"title": "Complete a dungeon"},
        )

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to create task"


def test_get_tasks_handles_database_error():
    """Une erreur SQL pendant la lecture doit renvoyer une erreur 500."""

    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.tasks.task_service.get_tasks",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.get("/api/goals/10/tasks")

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to retrieve tasks"


def test_update_task_handles_database_error():
    """Une erreur SQL pendant la modification doit renvoyer une erreur 500."""

    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.tasks.task_service.update_task",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.patch(
            "/api/tasks/1",
            json={"is_completed": True},
        )

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to update task"


def test_delete_task_handles_database_error():
    """Une erreur SQL pendant la suppression doit renvoyer une erreur 500."""

    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.tasks.task_service.delete_task",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.delete("/api/tasks/1")

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to delete task"
