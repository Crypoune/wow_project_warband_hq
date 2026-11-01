
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import CurrentAuth, get_current_auth
from app.services.task_service import TaskService


# ============================================================
# 1. MODÈLES DE DONNÉES
# ============================================================

class TaskCreateRequest(BaseModel):
    """Données nécessaires à la création d'une tâche."""

    title: str = Field(min_length=1, max_length=100)
    description: str | None = None


class TaskUpdateRequest(BaseModel):
    """Données acceptées pour modifier une tâche."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=100)
    description: str | None = None
    is_completed: bool | None = None


# ============================================================
# 2. INITIALISATION
# ============================================================

router = APIRouter(tags=["tasks"])

task_service = TaskService()


# ============================================================
# 3. CRÉER UNE TÂCHE
# ============================================================

@router.post("/api/goals/{goal_id}/tasks")
def create_task(
    goal_id: int,
    payload: TaskCreateRequest,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Crée une tâche pour un objectif de l'utilisateur connecté."""

    try:
        task = task_service.create_task(
            goal_id=goal_id,
            user_id=current_auth.user_id,
            title=payload.title,
            description=payload.description,
        )

        return {"task": task}

    except ValueError as exc:
        message = str(exc)

        status_code = (
            404
            if message == "Objectif introuvable ou inaccessible."
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail={"message": message},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to create task"},
        ) from exc


# ============================================================
# 4. RÉCUPÉRER LES TÂCHES D'UN OBJECTIF
# ============================================================

@router.get("/api/goals/{goal_id}/tasks")
def get_tasks(
    goal_id: int,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Récupère les tâches d'un objectif."""

    try:
        tasks = task_service.get_tasks(
            goal_id=goal_id,
            user_id=current_auth.user_id,
        )

        return {"tasks": tasks}

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"message": str(exc)},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to retrieve tasks"},
        ) from exc


# ============================================================
# 5. MODIFIER UNE TÂCHE
# ============================================================

@router.patch("/api/tasks/{task_id}")
def update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Modifie une tâche appartenant à l'utilisateur connecté."""

    fields_set = payload.model_fields_set

    if "title" in fields_set and payload.title is None:
        raise HTTPException(
            status_code=422,
            detail={"message": "Le titre ne peut pas être null."},
        )

    if "is_completed" in fields_set and payload.is_completed is None:
        raise HTTPException(
            status_code=422,
            detail={"message": "Le statut de complétion ne peut pas être null."},
        )

    update_data = {
        field: getattr(payload, field)
        for field in fields_set
    }

    try:
        task = task_service.update_task(
            task_id=task_id,
            user_id=current_auth.user_id,
            **update_data,
        )

        return {"task": task}

    except ValueError as exc:
        message = str(exc)

        status_code = (
            404
            if message == "Tâche introuvable ou inaccessible."
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail={"message": message},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to update task"},
        ) from exc


# ============================================================
# 6. SUPPRIMER UNE TÂCHE
# ============================================================

@router.delete("/api/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Supprime une tâche appartenant à l'utilisateur connecté."""

    try:
        return task_service.delete_task(
            task_id=task_id,
            user_id=current_auth.user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"message": str(exc)},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to delete task"},
        ) from exc
