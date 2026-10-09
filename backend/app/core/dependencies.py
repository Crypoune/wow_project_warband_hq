from datetime import datetime, timezone
from dataclasses import dataclass
from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.authentication_session import AuthenticationSession
from app.models.user import User


def get_current_user(request: Request) -> User:
    """Retourne l'utilisateur connecté à partir de sa session."""

    # Récupère le jeton de session conservé dans le cookie signé.
    session_token = request.session.get("session_token")

    # Refuse l'accès si aucun utilisateur n'est connecté.
    if not session_token:
        raise HTTPException(
            status_code=401,
            detail={"message": "Authentication required"},
        )

    try:
        with SessionLocal() as db:
            # Recherche la session correspondant au jeton du cookie.
            auth_session = db.scalar(
                select(AuthenticationSession).where(
                    AuthenticationSession.session_token == session_token
                )
            )

            # Refuse l'accès si la session n'existe plus en base.
            if auth_session is None:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Invalid session"},
                )

            # Vérifie que la session n'a pas expiré.
            now = datetime.now(timezone.utc)
            if auth_session.expires_at <= now:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Session expired"},
                )

            # Récupère l'utilisateur associé à cette session.
            user = db.get(User, auth_session.user_id)

            if user is None:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "User not found"},
                )

            return user

    except SQLAlchemyError:
        # Ne laisse pas une erreur de base devenir une erreur inattendue.
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to verify authentication"},
        )

@dataclass
class CurrentAuth:
    """Contient les informations nécessaires à une requête authentifiée."""

    user_id: int
    access_token: str


def get_current_auth(request: Request) -> CurrentAuth:
    """Retourne les identifiants de la session d'authentification active."""

    session_token = request.session.get("session_token")

    if not session_token:
        raise HTTPException(
            status_code=401,
            detail={"message": "Authentication required"},
        )

    try:
        with SessionLocal() as db:
            auth_session = db.scalar(
                select(AuthenticationSession).where(
                    AuthenticationSession.session_token == session_token
                )
            )

            if auth_session is None:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Invalid session"},
                )

            if auth_session.expires_at <= datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=401,
                    detail={"message": "Session expired"},
                )

            user = db.get(User, auth_session.user_id)

            if user is None:
                raise HTTPException(
                    status_code=401,
                    detail={"message": "User not found"},
                )

            return CurrentAuth(
                user_id=user.id,
                access_token=auth_session.access_token,
            )

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to verify authentication"},
        )
