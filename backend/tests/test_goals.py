
"""Tests API des objectifs personnels de Warband HQ."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import CurrentAuth, get_current_auth


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


def test_create_goal_success():
    """Une requête valide doit renvoyer l'objectif créé."""
    goal = {
        "id": 1,
        "user_id": 1,
        "character_id": None,
        "title": "Finir un donjon mythique",
        "description": "Terminer le donjon cette semaine.",
        "status": "IN_PROGRESS",
    }

    with patch(
        "app.api.goals.goal_service.create_goal",
        return_value=goal,
    ) as service:
        response = client.post(
            "/api/goals",
            json={
                "title": "Finir un donjon mythique",
                "description": "Terminer le donjon cette semaine.",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"goal": goal}

    # Vérifie que le service reçoit l'identité authentifiée,
    # et non un user_id fourni par le client.
    service.assert_called_once_with(
        user_id=1,
        title="Finir un donjon mythique",
        description="Terminer le donjon cette semaine.",
        character_id=None,
        status="IN_PROGRESS",
    )


def test_create_goal_rejects_empty_title():
    """Le titre vide doit être rejeté par la validation de l'API."""
    response = client.post(
        "/api/goals",
        json={"title": ""},
    )

    assert response.status_code == 422


def test_create_goal_rejects_title_over_100_characters():
    """Un titre dépassant 100 caractères doit être rejeté."""
    response = client.post(
        "/api/goals",
        json={"title": "a" * 101},
    )

    assert response.status_code == 422


def test_get_goals_success():
    """La route doit renvoyer la liste des objectifs de l'utilisateur."""
    goals = [
        {
            "id": 1,
            "user_id": 1,
            "character_id": None,
            "title": "Finir un donjon mythique",
            "description": None,
            "status": "IN_PROGRESS",
        }
    ]

    with patch(
        "app.api.goals.goal_service.get_goals",
        return_value=goals,
    ) as service:
        response = client.get("/api/goals")

    assert response.status_code == 200
    assert response.json() == {"goals": goals}
    service.assert_called_once_with(user_id=1)


def test_update_goal_success():
    """La route doit transmettre uniquement le champ à modifier."""
    goal = {
        "id": 1,
        "user_id": 1,
        "character_id": None,
        "title": "Finir un donjon mythique",
        "description": None,
        "status": "COMPLETED",
    }

    with patch(
        "app.api.goals.goal_service.update_goal",
        return_value=goal,
    ) as service:
        response = client.patch(
            "/api/goals/1",
            json={"status": "COMPLETED"},
        )

    assert response.status_code == 200
    assert response.json() == {"goal": goal}
    service.assert_called_once_with(
        goal_id=1,
        user_id=1,
        status="COMPLETED",
    )


def test_update_goal_rejects_null_title():
    """Un titre explicitement envoyé à null doit être refusé."""
    response = client.patch(
        "/api/goals/1",
        json={"title": None},
    )

    assert response.status_code == 422


def test_update_goal_can_clear_description():
    """Une description peut être effacée en envoyant null."""
    goal = {
        "id": 1,
        "user_id": 1,
        "character_id": None,
        "title": "Finir un donjon mythique",
        "description": None,
        "status": "IN_PROGRESS",
    }

    with patch(
        "app.api.goals.goal_service.update_goal",
        return_value=goal,
    ) as service:
        response = client.patch(
            "/api/goals/1",
            json={"description": None},
        )

    assert response.status_code == 200
    service.assert_called_once_with(
        goal_id=1,
        user_id=1,
        description=None,
    )


def test_delete_goal_success():
    """La suppression doit renvoyer la réponse du service."""
    result = {
        "message": "Objectif supprimé avec succès.",
        "id": 1,
    }

    with patch(
        "app.api.goals.goal_service.delete_goal",
        return_value=result,
    ) as service:
        response = client.delete("/api/goals/1")

    assert response.status_code == 200
    assert response.json() == result
    service.assert_called_once_with(goal_id=1, user_id=1)


def test_delete_goal_not_found():
    """Un objectif inexistant ou inaccessible doit renvoyer 404."""
    with patch(
        "app.api.goals.goal_service.delete_goal",
        side_effect=ValueError("Objectif introuvable ou inaccessible."),
    ):
        response = client.delete("/api/goals/999")

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Objectif introuvable ou inaccessible."
    )


# ============================================================
# 7. VALIDATION DES DONNÉES
# ============================================================

def test_create_goal_rejects_invalid_status():
    """Un statut qui ne fait pas partie des valeurs autorisées est refusé."""
    with patch(
        "app.api.goals.goal_service.create_goal",
        side_effect=ValueError("Statut invalide."),
    ):
        response = client.post(
            "/api/goals",
            json={
                "title": "Terminer un raid",
                "status": "INVALID_STATUS",
            },
        )

    assert response.status_code == 400
    assert response.json()["message"] == "Statut invalide."


def test_update_goal_rejects_null_status():
    """Un statut explicitement envoyé à null doit être refusé."""
    response = client.patch(
        "/api/goals/1",
        json={"status": None},
    )

    assert response.status_code == 422
    assert response.json()["message"] == "Le statut ne peut pas être null."


def test_update_goal_rejects_unknown_field():
    """La requête PATCH ne doit pas accepter de champs inconnus."""
    response = client.patch(
        "/api/goals/1",
        json={"user_id": 999},
    )

    assert response.status_code == 422


# ============================================================
# 8. SÉCURITÉ : ACCÈS AUX OBJECTIFS
# ============================================================

def test_update_goal_not_found():
    """Modifier un objectif inaccessible doit renvoyer 404."""
    with patch(
        "app.api.goals.goal_service.update_goal",
        side_effect=ValueError("Objectif introuvable ou inaccessible."),
    ):
        response = client.patch(
            "/api/goals/999",
            json={"title": "Nouvel objectif"},
        )

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Objectif introuvable ou inaccessible."
    )


def test_update_goal_rejects_character_owned_by_another_user():
    """
    Le service doit refuser un personnage qui n'appartient pas
    à l'utilisateur connecté.
    """
    with patch(
        "app.api.goals.goal_service.update_goal",
        side_effect=ValueError(
            "Ce personnage n'existe pas ou ne vous appartient pas."
        ),
    ) as service:
        response = client.patch(
            "/api/goals/1",
            json={"character_id": 99},
        )

    assert response.status_code == 404
    assert response.json()["message"] == (
        "Ce personnage n'existe pas ou ne vous appartient pas."
    )

    # Vérifie que l'identité transmise au service vient bien
    # de l'utilisateur authentifié, et non de la requête.
    service.assert_called_once_with(
        goal_id=1,
        user_id=1,
        character_id=99,
    )


def test_update_goal_can_detach_character():
    """Envoyer character_id à null doit permettre de détacher le personnage."""
    goal = {
        "id": 1,
        "user_id": 1,
        "character_id": None,
        "title": "Terminer un raid",
        "description": None,
        "status": "IN_PROGRESS",
    }

    with patch(
        "app.api.goals.goal_service.update_goal",
        return_value=goal,
    ) as service:
        response = client.patch(
            "/api/goals/1",
            json={"character_id": None},
        )

    assert response.status_code == 200
    assert response.json() == {"goal": goal}
    service.assert_called_once_with(
        goal_id=1,
        user_id=1,
        character_id=None,
    )


# ============================================================
# 9. GESTION DES ERREURS DE BASE DE DONNÉES
# ============================================================

def test_create_goal_handles_database_error():
    """Une erreur SQL pendant la création doit renvoyer une erreur 500."""
    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.goals.goal_service.create_goal",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.post(
            "/api/goals",
            json={"title": "Terminer un raid"},
        )

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to create goal"


def test_get_goals_handles_database_error():
    """Une erreur SQL pendant la lecture doit renvoyer une erreur 500."""
    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.goals.goal_service.get_goals",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.get("/api/goals")

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to retrieve goals"


def test_update_goal_handles_database_error():
    """Une erreur SQL pendant la modification doit renvoyer une erreur 500."""
    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.goals.goal_service.update_goal",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.patch(
            "/api/goals/1",
            json={"status": "COMPLETED"},
        )

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to update goal"


def test_delete_goal_handles_database_error():
    """Une erreur SQL pendant la suppression doit renvoyer une erreur 500."""
    from sqlalchemy.exc import SQLAlchemyError

    with patch(
        "app.api.goals.goal_service.delete_goal",
        side_effect=SQLAlchemyError("Database error"),
    ):
        response = client.delete("/api/goals/1")

    assert response.status_code == 500
    assert response.json()["message"] == "Unable to delete goal"
