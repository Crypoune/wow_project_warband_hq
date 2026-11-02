from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import CurrentAuth, get_current_auth
from app.services.note_service import NoteService


# ============================================================
# 1. MODÈLES DE DONNÉES
# ============================================================

class CharacterNoteRequest(BaseModel):
    """Données nécessaires pour créer ou modifier une note."""

    model_config = ConfigDict(extra="forbid")

    content: str


# ============================================================
# 2. INITIALISATION
# ============================================================

router = APIRouter(tags=["character-notes"])

note_service = NoteService()


# ============================================================
# 3. RÉCUPÉRER LA NOTE D'UN PERSONNAGE
# ============================================================

@router.get("/api/characters/{character_id}/note")
def get_character_note(
    character_id: int,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Récupère la note d'un personnage appartenant à l'utilisateur."""

    try:
        note = note_service.get_character_note(
            character_id=character_id,
            user_id=current_auth.user_id,
        )

        return {"note": note}

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"message": str(exc)},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to retrieve character note"},
        ) from exc


# ============================================================
# 4. CRÉER OU MODIFIER LA NOTE D'UN PERSONNAGE
# ============================================================

@router.put("/api/characters/{character_id}/note")
def save_character_note(
    character_id: int,
    payload: CharacterNoteRequest,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Crée ou met à jour la note d'un personnage."""

    try:
        note = note_service.save_character_note(
            character_id=character_id,
            user_id=current_auth.user_id,
            content=payload.content,
        )

        return {"note": note}

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail={"message": str(exc)},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to save character note"},
        ) from exc
