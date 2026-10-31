from unittest.mock import MagicMock, patch

import pytest

from app.models.goal import Goal
from app.services.goal_service import GoalService


@pytest.fixture
def service():
    return GoalService()


def test_create_goal_success(service):
    """Un utilisateur peut créer un objectif."""
    db = MagicMock()
    db.refresh.side_effect = lambda goal: setattr(goal, "id", 1)

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.create_goal(
            user_id=42,
            title="  Monter mon personnage au niveau 90  ",
            description="Terminer la montée de niveau.",
            character_id=5,
        )

    assert result["id"] == 1
    assert result["title"] == "Monter mon personnage au niveau 90"
    assert result["description"] == "Terminer la montée de niveau."
    assert result["character_id"] == 5
    assert result["status"] == "IN_PROGRESS"

    added_goal = db.add.call_args.args[0]
    assert isinstance(added_goal, Goal)
    assert added_goal.user_id == 42
    assert added_goal.title == "Monter mon personnage au niveau 90"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(added_goal)


@pytest.mark.parametrize("title", ["", "   "])
def test_create_goal_rejects_empty_title(service, title):
    """Un objectif ne peut pas avoir un titre vide."""
    with pytest.raises(ValueError):
        service.create_goal(
            user_id=42,
            title=title,
        )


def test_create_goal_rejects_title_over_100_characters(service):
    """Le titre d'un objectif ne peut pas dépasser 100 caractères."""
    with pytest.raises(ValueError, match="100"):
        service.create_goal(
            user_id=42,
            title="A" * 101,
        )


def test_create_goal_rejects_character_owned_by_another_user(service):
    """Un utilisateur ne peut pas associer le personnage d'un autre."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="ne vous appartient pas"):
            service.create_goal(
                user_id=42,
                title="Mon objectif",
                character_id=5,
            )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_create_warband_goal_success(service):
    """Un objectif de Warband peut être créé sans personnage."""
    db = MagicMock()
    db.refresh.side_effect = lambda goal: setattr(goal, "id", 1)

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.create_goal(
            user_id=42,
            title="Préparer ma prochaine saison",
        )

    assert result["id"] == 1
    assert result["user_id"] == 42
    assert result["character_id"] is None
    assert result["title"] == "Préparer ma prochaine saison"
    assert result["description"] is None
    assert result["status"] == "IN_PROGRESS"

    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_create_goal_rejects_invalid_status(service):
    """Un objectif ne peut pas avoir un statut invalide."""
    with pytest.raises(ValueError, match="statut"):
        service.create_goal(
            user_id=42,
            title="Mon objectif",
            status="INVALID_STATUS",
        )


@pytest.mark.parametrize(
    "status",
    ["IN_PROGRESS", "ON_HOLD", "COMPLETED", "ABANDONED"],
)
def test_create_goal_accepts_valid_status(service, status):
    """Un objectif accepte chacun des statuts autorisés."""
    db = MagicMock()
    db.refresh.side_effect = lambda goal: setattr(goal, "id", 1)

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.create_goal(
            user_id=42,
            title="Mon objectif",
            status=status,
        )

    assert result["status"] == status
    db.commit.assert_called_once()


def test_get_goals_returns_user_goals(service):
    """Le service retourne les objectifs de l'utilisateur."""
    db = MagicMock()
    db.scalars.return_value.all.return_value = [
        MagicMock(
            id=1,
            user_id=42,
            character_id=5,
            title="Monter mon personnage",
            description="Atteindre le niveau 90.",
            status="IN_PROGRESS",
        ),
        MagicMock(
            id=2,
            user_id=42,
            character_id=None,
            title="Préparer ma Warband",
            description=None,
            status="ON_HOLD",
        ),
    ]

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_goals(user_id=42)

    assert len(result) == 2
    assert result[0]["user_id"] == 42
    assert result[0]["title"] == "Monter mon personnage"
    assert result[1]["user_id"] == 42
    assert result[1]["character_id"] is None
    assert result[1]["title"] == "Préparer ma Warband"

    db.scalars.assert_called_once()


def test_get_goals_returns_empty_list_when_no_goals(service):
    """Le service retourne une liste vide sans objectif."""
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.get_goals(user_id=42)

    assert result == []
    db.scalars.assert_called_once()


def test_get_goals_filters_by_user_id(service):
    """La requête de récupération filtre par utilisateur."""
    db = MagicMock()
    db.scalars.return_value.all.return_value = []

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        service.get_goals(user_id=42)

    query = db.scalars.call_args.args[0]

    where_clauses = query.whereclause

    assert where_clauses is not None
    assert "user_id" in str(where_clauses)


def test_update_goal_rejects_goal_not_owned_by_user(service):
    """Un utilisateur ne peut pas modifier l'objectif d'un autre."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="(?i)objectif"):
            service.update_goal(
                goal_id=1,
                user_id=42,
                title="Nouvelle version",
            )

    db.commit.assert_not_called()


def test_update_goal_success(service):
    """Un utilisateur peut modifier son propre objectif."""
    goal = MagicMock(
        id=1,
        user_id=42,
        character_id=None,
        title="Ancien titre",
        description="Ancienne description",
        status="IN_PROGRESS",
    )

    db = MagicMock()
    db.scalar.return_value = goal
    db.refresh.side_effect = lambda refreshed_goal: None

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.update_goal(
            goal_id=1,
            user_id=42,
            title="  Nouveau titre  ",
            status="COMPLETED",
        )

    assert result["title"] == "Nouveau titre"
    assert result["status"] == "COMPLETED"
    assert result["description"] == "Ancienne description"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(goal)


def test_update_goal_rejects_empty_title(service):
    """Un objectif ne peut pas recevoir un titre vide."""
    goal = MagicMock(
        id=1,
        user_id=42,
        character_id=None,
        title="Ancien titre",
        description=None,
        status="IN_PROGRESS",
    )

    db = MagicMock()
    db.scalar.return_value = goal

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="vide"):
            service.update_goal(
                goal_id=1,
                user_id=42,
                title="   ",
            )

    db.commit.assert_not_called()


def test_update_goal_rejects_title_over_100_characters(service):
    """Un titre modifié ne peut pas dépasser 100 caractères."""
    goal = MagicMock(
        id=1,
        user_id=42,
        character_id=None,
        title="Ancien titre",
        description=None,
        status="IN_PROGRESS",
    )

    db = MagicMock()
    db.scalar.return_value = goal

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="100"):
            service.update_goal(
                goal_id=1,
                user_id=42,
                title="A" * 101,
            )

    db.commit.assert_not_called()


def test_update_goal_rejects_invalid_status(service):
    """Un objectif ne peut pas recevoir un statut invalide."""
    goal = MagicMock(
        id=1,
        user_id=42,
        character_id=None,
        title="Mon objectif",
        description=None,
        status="IN_PROGRESS",
    )

    db = MagicMock()
    db.scalar.return_value = goal

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="statut"):
            service.update_goal(
                goal_id=1,
                user_id=42,
                status="INVALID_STATUS",
            )

    db.commit.assert_not_called()


def test_delete_goal_rejects_goal_not_owned_by_user(service):
    """Un utilisateur ne peut pas supprimer l'objectif d'un autre."""
    db = MagicMock()
    db.scalar.return_value = None

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="(?i)objectif"):
            service.delete_goal(
                goal_id=1,
                user_id=42,
            )

    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_delete_goal_success(service):
    """Un utilisateur peut supprimer son propre objectif."""
    goal = MagicMock(
        id=1,
        user_id=42,
        title="Objectif terminé",
    )

    db = MagicMock()
    db.scalar.return_value = goal

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.delete_goal(
            goal_id=1,
            user_id=42,
        )

    assert result == {
        "message": "Objectif supprimé avec succès.",
        "id": 1,
    }
    db.delete.assert_called_once_with(goal)
    db.commit.assert_called_once()


def test_update_goal_can_clear_description(service):
    """Un utilisateur peut effacer la description d'un objectif."""
    goal = MagicMock(
        id=1,
        user_id=42,
        character_id=None,
        title="Mon objectif",
        description="Description à supprimer",
        status="IN_PROGRESS",
    )

    db = MagicMock()
    db.scalar.return_value = goal

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.update_goal(
            goal_id=1,
            user_id=42,
            description=None,
        )

    assert result["description"] is None
    db.commit.assert_called_once()


def test_update_goal_can_detach_character(service):
    """Un objectif peut devenir un objectif de Warband."""
    goal = MagicMock(
        id=1,
        user_id=42,
        character_id=5,
        title="Mon objectif",
        description=None,
        status="IN_PROGRESS",
    )

    db = MagicMock()
    db.scalar.return_value = goal

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        result = service.update_goal(
            goal_id=1,
            user_id=42,
            character_id=None,
        )

    assert result["character_id"] is None
    db.commit.assert_called_once()


def test_update_goal_rejects_character_owned_by_another_user(service):
    """Un objectif ne peut pas être associé au personnage d'un autre."""
    goal = MagicMock(
        id=1,
        user_id=42,
        character_id=None,
        title="Mon objectif",
        description=None,
        status="IN_PROGRESS",
    )

    db = MagicMock()
    db.scalar.side_effect = [goal, None]

    with patch("app.services.goal_service.SessionLocal") as session_local:
        session_local.return_value.__enter__.return_value = db

        with pytest.raises(ValueError, match="ne vous appartient pas"):
            service.update_goal(
                goal_id=1,
                user_id=42,
                character_id=5,
            )

    db.commit.assert_not_called()
