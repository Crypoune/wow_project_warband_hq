from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import (
    CurrentAuth,
    get_current_admin,
    get_current_auth,
)
from app.services.tag_service import TagService


router = APIRouter(prefix="/api/tags", tags=["tags"])
tag_service = TagService()


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class TagUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)

@router.get("")
def get_tags(
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    try:
        return {"tags": tag_service.get_tags()}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to retrieve tags"},
        )


@router.post("")
def create_tag(
    payload: TagCreateRequest,
    current_admin=Depends(get_current_admin),
):
    try:
        tag = tag_service.create_tag(name=payload.name)
        return {"tag": tag}
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc)},
        ) from exc
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to create tag"},
        )


@router.get("/{tag_id}")
def get_tag(
    tag_id: int,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    try:
        tags = tag_service.get_tags()
        tag = next(
            (item for item in tags if item["id"] == tag_id),
            None,
        )

        if tag is None:
            raise HTTPException(
                status_code=404,
                detail={"message": "Tag not found"},
            )

        return {"tag": tag}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to retrieve tag"},
        )


@router.patch("/{tag_id}")
def update_tag(
    tag_id: int,
    payload: TagUpdateRequest,
    current_admin=Depends(get_current_admin),
):
    try:
        tag = tag_service.update_tag(
            tag_id=tag_id,
            name=payload.name,
        )
        return {"tag": tag}
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if message == "Tag introuvable." else 400
        raise HTTPException(
            status_code=status_code,
            detail={"message": message},
        ) from exc
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to update tag"},
        )


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    current_admin=Depends(get_current_admin),
):
    try:
        tag_service.delete_tag(tag_id=tag_id)
        return {"message": "Tag deleted successfully"}
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if message == "Tag introuvable." else 400
        raise HTTPException(
            status_code=status_code,
            detail={"message": message},
        ) from exc
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to delete tag"},
        )
