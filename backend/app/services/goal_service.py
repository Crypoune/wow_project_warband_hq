from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.character import Character
from app.models.goal import Goal


VALID_GOAL_STATUSES = {
    "IN_PROGRESS",
    "ON_HOLD",
    "COMPLETED",
    "ABANDONED",
}

UNSET = object()


class GoalService:
    """Gère les objectifs personnels de Warband HQ."""

    def create_goal(
        self,
        user_id: int,
        title: str,
        description: str | None = None,
        character_id: int | None = None,
        status: str = "IN_PROGRESS",
    ) -> dict:
        """Crée un objectif pour un utilisateur."""

        # Validation du titre
        title = title.strip()

        if not title:
            raise ValueError("Le titre de l'objectif ne peut pas être vide.")

        if len(title) > 100:
            raise ValueError(
                "Le titre de l'objectif ne peut pas dépasser 100 caractères."
            )

        if status not in VALID_GOAL_STATUSES:
            raise ValueError("Le statut de l'objectif est invalide.")

        with SessionLocal() as db:
            # Vérification que le personnage appartient à l'utilisateur
            if character_id is not None:
                character = db.scalar(
                    select(Character).where(
                        Character.id == character_id,
                        Character.user_id == user_id,
                    )
                )

                if character is None:
                    raise ValueError(
                        "Ce personnage n'existe pas ou ne vous appartient pas."
                    )

            goal = Goal(
                user_id=user_id,
                character_id=character_id,
                title=title,
                description=description,
                status=status,
            )

            db.add(goal)
            db.commit()
            db.refresh(goal)

            return {
                "id": goal.id,
                "user_id": goal.user_id,
                "character_id": goal.character_id,
                "title": goal.title,
                "description": goal.description,
                "status": goal.status,
            }


    def get_goals(self, user_id: int) -> list[dict]:
        """Récupère les objectifs d'un utilisateur."""

        with SessionLocal() as db:
            goals = db.scalars(
                select(Goal)
                .where(Goal.user_id == user_id)
                .order_by(Goal.created_at.desc())
            ).all()

            return [
                {
                    "id": goal.id,
                    "user_id": goal.user_id,
                    "character_id": goal.character_id,
                    "title": goal.title,
                    "description": goal.description,
                    "status": goal.status,
                }
                for goal in goals
            ]


    def update_goal(
        self,
        goal_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None | object = UNSET,
        character_id: int | None | object = UNSET,
        status: str | None = None,
    ) -> dict:
        """Modifie un objectif appartenant à l'utilisateur."""

        with SessionLocal() as db:
            goal = db.scalar(
                select(Goal).where(
                    Goal.id == goal_id,
                    Goal.user_id == user_id,
                )
            )

            if goal is None:
                raise ValueError(
                    "Objectif introuvable ou inaccessible."
                )

            if title is not None:
                title = title.strip()

                if not title:
                    raise ValueError(
                        "Le titre de l'objectif ne peut pas être vide."
                    )

                if len(title) > 100:
                    raise ValueError(
                        "Le titre de l'objectif ne peut pas dépasser 100 caractères."
                    )

                goal.title = title

            if description is not UNSET:
                goal.description = description


            if character_id is not UNSET:
                if character_id is None:
                    goal.character_id = None
                else:
                    character = db.scalar(
                        select(Character).where(
                            Character.id == character_id,
                            Character.user_id == user_id,
                        )
                    )

                    if character is None:
                        raise ValueError(
                            "Ce personnage n'existe pas ou ne vous appartient pas."
                        )

                    goal.character_id = character_id


            if status is not None:
                if status not in VALID_GOAL_STATUSES:
                    raise ValueError(
                        "Le statut de l'objectif est invalide."
                    )

                goal.status = status

            db.commit()
            db.refresh(goal)

            return {
                "id": goal.id,
                "user_id": goal.user_id,
                "character_id": goal.character_id,
                "title": goal.title,
                "description": goal.description,
                "status": goal.status,
            }


    def delete_goal(self, goal_id: int, user_id: int) -> dict:
        """Supprime un objectif appartenant à l'utilisateur."""

        with SessionLocal() as db:
            goal = db.scalar(
                select(Goal).where(
                    Goal.id == goal_id,
                    Goal.user_id == user_id,
                )
            )

            if goal is None:
                raise ValueError(
                    "Objectif introuvable ou inaccessible."
                )

            db.delete(goal)
            db.commit()

            return {
                "message": "Objectif supprimé avec succès.",
                "id": goal_id,
            }
