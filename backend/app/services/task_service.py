from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.goal import Goal
from app.models.task import Task


UNSET = object()


class TaskService:
    """Gère les tâches associées aux objectifs de Warband HQ."""

    def create_task(
        self,
        goal_id: int,
        user_id: int,
        title: str,
        description: str | None = None,
    ) -> dict:
        """Crée une tâche pour un objectif appartenant à l'utilisateur."""

        title = title.strip()

        if not title:
            raise ValueError("Le titre de la tâche ne peut pas être vide.")

        if len(title) > 100:
            raise ValueError(
                "Le titre de la tâche ne peut pas dépasser 100 caractères."
            )

        with SessionLocal() as db:
            goal = db.scalar(
                select(Goal).where(
                    Goal.id == goal_id,
                    Goal.user_id == user_id,
                )
            )

            if goal is None:
                raise ValueError("Objectif introuvable ou inaccessible.")

            task = Task(
                goal_id=goal_id,
                title=title,
                description=description,
                is_completed=False,
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "id": task.id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
            }

    def get_tasks(self, goal_id: int, user_id: int) -> list[dict]:
        """Récupère les tâches d'un objectif appartenant à l'utilisateur."""

        with SessionLocal() as db:
            goal = db.scalar(
                select(Goal).where(
                    Goal.id == goal_id,
                    Goal.user_id == user_id,
                )
            )

            if goal is None:
                raise ValueError("Objectif introuvable ou inaccessible.")

            tasks = db.scalars(
                select(Task)
                .where(Task.goal_id == goal_id)
                .order_by(Task.created_at.asc())
            ).all()

            return [
                {
                    "id": task.id,
                    "goal_id": task.goal_id,
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                }
                for task in tasks
            ]

    def update_task(
        self,
        task_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None | object = UNSET,
        is_completed: bool | None = None,
    ) -> dict:
        """Modifie une tâche appartenant à l'utilisateur."""

        with SessionLocal() as db:
            task = db.scalar(
                select(Task)
                .join(Goal, Task.goal_id == Goal.id)
                .where(
                    Task.id == task_id,
                    Goal.user_id == user_id,
                )
            )

            if task is None:
                raise ValueError("Tâche introuvable ou inaccessible.")

            if title is not None:
                title = title.strip()

                if not title:
                    raise ValueError(
                        "Le titre de la tâche ne peut pas être vide."
                    )

                if len(title) > 100:
                    raise ValueError(
                        "Le titre de la tâche ne peut pas dépasser 100 caractères."
                    )

                task.title = title

            if description is not UNSET:
                task.description = description

            if is_completed is not None:
                task.is_completed = is_completed

            db.commit()
            db.refresh(task)

            return {
                "id": task.id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
            }

    def delete_task(self, task_id: int, user_id: int) -> dict:
        """Supprime une tâche appartenant à l'utilisateur."""

        with SessionLocal() as db:
            task = db.scalar(
                select(Task)
                .join(Goal, Task.goal_id == Goal.id)
                .where(
                    Task.id == task_id,
                    Goal.user_id == user_id,
                )
            )

            if task is None:
                raise ValueError("Tâche introuvable ou inaccessible.")

            db.delete(task)
            db.commit()

            return {
                "message": "Tâche supprimée avec succès.",
                "id": task_id,
            }
