import httpx

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import CurrentAuth, get_current_auth
from app.services.character_service import CharacterService


router = APIRouter(prefix="/api/characters", tags=["characters"])
character_service = CharacterService()


class CharacterImportRequest(BaseModel):
    """Données nécessaires pour importer des personnages."""

    character_ids: list[int] = Field(min_length=1)


@router.get("/available")
def get_available_characters(
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Retourne les personnages disponibles sur le compte Blizzard."""

    try:
        characters = character_service.get_available_characters(
            current_auth.access_token
        )
        return {"characters": characters}

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an HTTP error"},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Unable to contact Blizzard"},
        )


@router.post("/import")
def import_characters(
    payload: CharacterImportRequest,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Importe les personnages sélectionnés dans Warband HQ."""

    try:
        characters = character_service.import_characters(
            user_id=current_auth.user_id,
            access_token=current_auth.access_token,
            character_ids=payload.character_ids,
        )
        return {"characters": characters}

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc)},
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an HTTP error"},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Unable to contact Blizzard"},
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to import characters"},
        )


@router.get("")
def get_characters(
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Retourne les personnages importés dans Warband HQ."""

    try:
        characters = character_service.get_imported_characters(
            user_id=current_auth.user_id,
            access_token=current_auth.access_token,
        )
        return {"characters": characters}

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an HTTP error"},
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Unable to contact Blizzard"},
        )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to retrieve imported characters"},
        )
