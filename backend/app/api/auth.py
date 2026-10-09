from datetime import datetime, timedelta, timezone
import secrets
import httpx

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.authentication_session import AuthenticationSession
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/auth", tags=["authentication"])
auth_service = AuthService(settings)


@router.get("/login")
def login(request: Request):
    # Génère une valeur aléatoire pour sécuriser le retour OAuth.
    state = auth_service.generate_oauth_state()

    # Conserve le state dans la session pour pouvoir le vérifier au callback.
    request.session["oauth_state"] = state

    # Construit l'URL vers laquelle l'utilisateur sera redirigé.
    authorization_url = auth_service.build_authorization_url(state)

    # Redirige le navigateur vers Blizzard.
    return RedirectResponse(url=authorization_url)

@router.get("/callback")
def callback(request: Request, code: str, state: str):
    # Récupère le state généré avant la redirection vers Blizzard.
    expected_state = request.session.get("oauth_state")

    # Refuse le callback si aucune tentative OAuth n'est en cours.
    if expected_state is None:
        raise HTTPException(
            status_code=400,
            detail={"message": "Missing OAuth state"},
        )

    # Vérifie que le state reçu correspond à celui de la session.
    if not auth_service.validate_oauth_state(state, expected_state):
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid OAuth state"},
        )

    # Supprime le state temporaire après sa validation.
    request.session.pop("oauth_state", None)

    try:
        # Échange le code temporaire reçu de Blizzard contre un access token.
        token_data = auth_service.exchange_code_for_token(code)

        # Récupère le token et sa durée de validité, exprimée en secondes.
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in")

        # Vérifie que Blizzard a fourni les données nécessaires.
        if (
            not access_token
            or not isinstance(expires_in, (int, float))
            or isinstance(expires_in, bool)
            or expires_in <= 0
        ):
            raise HTTPException(
                status_code=502,
                detail={"message": "Invalid token response from Blizzard"},
            )

        # Interroge l'API Profile Blizzard pour identifier le compte connecté.
        profile = auth_service.get_account_profile(access_token)
        blizzard_account_id = profile.get("id")

        # L'identifiant Blizzard est nécessaire pour retrouver l'utilisateur.
        if blizzard_account_id is None:
            raise HTTPException(
                status_code=502,
                detail={"message": "Blizzard account ID is missing"},
            )

        # Ouvre une session SQLAlchemy pour effectuer les opérations en base.
        with SessionLocal() as db:
            # Recherche l'utilisateur à partir de son identifiant Blizzard.
            user = db.scalar(
                select(User).where(
                    User.blizzard_account_id == str(blizzard_account_id)
                )
            )

            # Utilise une date UTC pour les événements d'authentification.
            now = datetime.now(timezone.utc)

            if user is None:
                # Crée un utilisateur Warband HQ lors de sa première connexion.
                user = User(
                    blizzard_account_id=str(blizzard_account_id),
                    role="USER",
                    created_at=now,
                    last_login=now,
                )
                db.add(user)

                # Envoie l'insertion à PostgreSQL pour obtenir l'identifiant.
                db.flush()
            else:
                # Actualise la date de connexion de l'utilisateur existant.
                user.last_login = now

            # Génère un identifiant aléatoire distinct du token Blizzard.
            session_token = secrets.token_urlsafe(32)

            # Enregistre la session et l'expiration du token côté serveur.
            auth_session = AuthenticationSession(
                user_id=user.id,
                session_token=session_token,
                access_token=access_token,
                expires_at=now + timedelta(seconds=expires_in),
            )
            db.add(auth_session)

            # Valide les modifications en base de données.
            db.commit()

        # Efface les données OAuth temporaires du cookie.
        request.session.clear()

        # Le cookie signé conserve uniquement l'identifiant de session.
        request.session["session_token"] = session_token

    # Conserve les erreurs HTTP déjà prévues, notamment celles du callback.
    except HTTPException:
        raise

    # Blizzard a répondu avec un statut HTTP d'erreur.
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Blizzard returned an HTTP error"},
        )

    # Une erreur réseau empêche de contacter Blizzard.
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail={"message": "Unable to contact Blizzard"},
        )

    # Une erreur SQL empêche de créer ou d'enregistrer la session.
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to create authentication session"},
        )

    # Redirige le navigateur vers le frontend après la connexion.
    return RedirectResponse(
        url="http://127.0.0.1:5173/?auth=success",
        status_code=303,
    )

@router.post("/logout")
def logout(request: Request):
    # Récupère l'identifiant de session conservé dans le cookie.
    session_token = request.session.get("session_token")

    if session_token is not None:
        try:
            # Ouvre une session SQLAlchemy pour accéder à PostgreSQL.
            with SessionLocal() as db:
                # Recherche la session correspondant au cookie.
                auth_session = db.scalar(
                    select(AuthenticationSession).where(
                        AuthenticationSession.session_token == session_token
                    )
                )

                # Supprime la session côté serveur si elle existe.
                if auth_session is not None:
                    db.delete(auth_session)
                    db.commit()

        except SQLAlchemyError:
            # Signale une erreur si la session n'a pas pu être supprimée.
            raise HTTPException(
                status_code=500,
                detail={"message": "Unable to end authentication session"},
            )

    # Efface les données de session du cookie du navigateur.
    request.session.clear()

    return {"message": "Logout successful"}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Retourne les informations de l'utilisateur connecté."""

    return {
        "id": current_user.id,
        "blizzard_account_id": current_user.blizzard_account_id,
        "role": current_user.role,
    }
