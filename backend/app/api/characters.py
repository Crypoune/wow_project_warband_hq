import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import CurrentAuth, get_current_auth
from app.services.auth_service import InvalidBlizzardProfileError
from app.services.character_service import CharacterService


router = APIRouter(prefix="/api/characters", tags=["characters"])
character_service = CharacterService()


class CharacterImportRequest(BaseModel):
    """Données nécessaires pour importer des personnages."""

    character_ids: list[int] = Field(min_length=1)

class CharacterFavoriteRequest(BaseModel):
    """Données nécessaires pour modifier le statut favori."""

    is_favorite: bool

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

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an unexpected response"},
        )

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": "Blizzard access token is invalid or expired"
                },
            ) from exc

        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an HTTP error"},
        ) from exc

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

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an unexpected response"},
        )

    except InvalidBlizzardProfileError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an unexpected response"},
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc)},
        )

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": "Blizzard access token is invalid or expired"
                },
            ) from exc

        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an HTTP error"},
        ) from exc

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

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an unexpected response"},
        )


    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail={
                    "message": "Blizzard access token is invalid or expired"
                },
            ) from exc

        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an HTTP error"},
        ) from exc


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

@router.patch("/{character_id}/favorite")
def update_character_favorite(
    character_id: int,
    payload: CharacterFavoriteRequest,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """Met à jour le statut favori d'un personnage importé."""

    try:
        character = character_service.update_favorite(
            user_id=current_auth.user_id,
            character_id=character_id,
            is_favorite=payload.is_favorite,
        )

        if character is None:
            raise HTTPException(
                status_code=404,
                detail={"message": "Character not found"},
            )

        return {"character": character}

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to update character favorite"},
        )
