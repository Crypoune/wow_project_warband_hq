import base64
import json
import httpx
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError
from itsdangerous import TimestampSigner
from app.core.config import settings
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse
from fastapi.testclient import TestClient
from app.models.user import User
from app.main import app

def test_login_redirects_to_blizzard():
    """Vérifie que la connexion redirige vers Blizzard."""

    with TestClient(app) as client:
        response = client.get("/api/auth/login", follow_redirects=False)

    assert response.status_code == 307

    redirect_url = urlparse(response.headers["location"])
    params = parse_qs(redirect_url.query)

    assert redirect_url.netloc == "oauth.battle.net"
    assert redirect_url.path == "/authorize"
    assert params["response_type"] == ["code"]
    assert params["scope"] == ["wow.profile"]
    assert "state" in params

def test_callback_without_state_returns_400():
    """Vérifie qu'un callback sans tentative OAuth est refusé."""

    with TestClient(app) as client:
        response = client.get(
            "/api/auth/callback",
            params={"code": "fake-code", "state": "fake-state"},
        )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Missing OAuth state"

def test_callback_with_invalid_state_returns_400():
    """Vérifie qu'un state incorrect est refusé."""

    with TestClient(app) as client:
        # Démarre une tentative OAuth pour enregistrer le state dans la session.
        client.get("/api/auth/login", follow_redirects=False)

        response = client.get(
            "/api/auth/callback",
            params={"code": "fake-code", "state": "invalid-state"},
        )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Invalid OAuth state"

def test_logout_without_session():
    """Vérifie que la déconnexion fonctionne sans session existante."""

    with TestClient(app) as client:
        response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}

def test_callback_success():
    """Vérifie qu'un callback valide crée une session."""

    fake_db = MagicMock()
    fake_db.scalar.return_value = None

    with (
        patch("app.api.auth.SessionLocal") as mock_session_local,
        patch("app.api.auth.select") as mock_select,
        patch(
            "app.api.auth.auth_service.validate_oauth_state",
            return_value=True,
        ),
        patch(
            "app.api.auth.auth_service.exchange_code_for_token",
            return_value={
                "access_token": "fake-access-token",
                "expires_in": 3600,
            },
        ),
        patch(
            "app.api.auth.auth_service.get_account_profile",
            return_value={"id": 12345},
        ),
        patch("app.api.auth.AuthenticationSession") as mock_auth_session,
        patch(
            "app.api.auth.secrets.token_urlsafe",
            return_value="fake-session-token",
        ),
    ):
        mock_session_local.return_value.__enter__.return_value = fake_db
        mock_select.return_value.where.return_value = MagicMock()

        with TestClient(app) as client:
            client.get("/api/auth/login", follow_redirects=False)

            response = client.get(
                "/api/auth/callback",
                params={"code": "fake-code", "state": "valid-state"},
                follow_redirects=False,
            )

            # Le callback doit conserver le token de session dans le cookie.
            assert client.cookies.get("session") is not None

    assert response.status_code == 303
    assert response.headers["location"] == "http://127.0.0.1:5173/?auth=success"

    fake_db.add.assert_called()
    fake_db.flush.assert_called_once()
    fake_db.commit.assert_called_once()
    mock_auth_session.assert_called_once()

def test_logout_deletes_existing_session():
    """Vérifie que la déconnexion supprime la session côté serveur."""

    fake_auth_session = MagicMock()
    fake_db = MagicMock()

    # Première requête : aucun utilisateur existant.
    # Deuxième requête : session trouvée lors de la déconnexion.
    fake_db.scalar.side_effect = [None, fake_auth_session]

    with (
        patch("app.api.auth.SessionLocal") as mock_session_local,
        patch("app.api.auth.select") as mock_select,
        patch(
            "app.api.auth.auth_service.validate_oauth_state",
            return_value=True,
        ),
        patch(
            "app.api.auth.auth_service.exchange_code_for_token",
            return_value={
                "access_token": "fake-access-token",
                "expires_in": 3600,
            },
        ),
        patch(
            "app.api.auth.auth_service.get_account_profile",
            return_value={"id": 12345},
        ),
        patch("app.api.auth.AuthenticationSession"),
        patch(
            "app.api.auth.secrets.token_urlsafe",
            return_value="fake-session-token",
        ),
    ):
        mock_session_local.return_value.__enter__.return_value = fake_db
        mock_select.return_value.where.return_value = MagicMock()

        with TestClient(app) as client:
            # Crée d'abord une session de connexion simulée.
            client.get("/api/auth/login", follow_redirects=False)

            login_response = client.get(
                "/api/auth/callback",
                params={"code": "fake-code", "state": "valid-state"},
                follow_redirects=False,
            )
            assert login_response.status_code == 303
            assert login_response.headers["location"] == "http://127.0.0.1:5173/?auth=success"

            # Vérifie ensuite la suppression de cette session.
            response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful"}
    fake_db.delete.assert_called_once_with(fake_auth_session)
    fake_db.commit.assert_any_call()

def _set_session_cookie(client, session_token):
    """Prépare une session de test signée par Starlette."""

    from starlette.routing import Route
    from starlette.responses import Response

    async def set_test_session(request):
        request.session["session_token"] = session_token
        return Response(status_code=204)

    # Ajoute temporairement une route qui écrit dans la session.
    test_route = Route("/__test_session__", set_test_session)
    app.router.routes.append(test_route)

    try:
        response = client.get("/__test_session__")
        assert response.status_code == 204
    finally:
        app.router.routes.remove(test_route)

def test_me_without_session_returns_401():
    """Refuse l'accès si aucun cookie de session n'est présent."""

    with TestClient(app) as client:
        response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"]["message"] == "Authentication required"

def test_me_with_unknown_session_returns_401():
    """Refuse l'accès si la session est absente de la base."""

    fake_db = MagicMock()
    fake_db.scalar.return_value = None

    with patch(
        "app.core.dependencies.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = fake_db

        with TestClient(app) as client:
            _set_session_cookie(client, "unknown-session-token")
            response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"]["message"] == "Invalid session"

def test_me_with_expired_session_returns_401():
    """Refuse l'accès si la session a expiré."""

    expired_session = MagicMock()
    expired_session.expires_at = datetime.now(timezone.utc) - timedelta(
        minutes=5
    )

    fake_db = MagicMock()
    fake_db.scalar.return_value = expired_session

    with patch(
        "app.core.dependencies.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = fake_db

        with TestClient(app) as client:
            _set_session_cookie(client, "expired-session-token")
            response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"]["message"] == "Session expired"

def test_me_with_valid_session_returns_user():
    """Retourne les informations de l'utilisateur connecté."""

    valid_session = MagicMock()
    valid_session.user_id = 42
    valid_session.expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )

    fake_user = MagicMock()
    fake_user.id = 42
    fake_user.blizzard_account_id = "12345"
    fake_user.role = "USER"

    fake_db = MagicMock()
    fake_db.scalar.return_value = valid_session
    fake_db.get.return_value = fake_user

    with patch(
        "app.core.dependencies.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = fake_db

        with TestClient(app) as client:
            _set_session_cookie(client, "valid-session-token")
            response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": 42,
        "blizzard_account_id": "12345",
        "role": "USER",
    }

    fake_db.get.assert_called_once_with(User, 42)

def test_callback_blizzard_http_error_returns_502():
    """Vérifie qu'une erreur HTTP Blizzard renvoie une erreur 502."""

    request = httpx.Request("POST", "https://oauth.battle.net/token")
    response = httpx.Response(401, request=request)
    error = httpx.HTTPStatusError(
        "Unauthorized",
        request=request,
        response=response,
    )

    with (
        patch(
            "app.api.auth.auth_service.validate_oauth_state",
            return_value=True,
        ),
        patch(
            "app.api.auth.auth_service.exchange_code_for_token",
            side_effect=error,
        ),
    ):
        with TestClient(app) as client:
            client.get("/api/auth/login", follow_redirects=False)
            response = client.get(
                "/api/auth/callback",
                params={"code": "fake-code", "state": "valid-state"},
            )

    assert response.status_code == 502
    assert response.json()["detail"]["message"] == (
        "Blizzard returned an HTTP error"
    )

def test_callback_blizzard_network_error_returns_502():
    """Vérifie qu'une erreur réseau Blizzard renvoie une erreur 502."""

    request = httpx.Request("POST", "https://oauth.battle.net/token")
    error = httpx.ConnectError("Connection failed", request=request)

    with (
        patch(
            "app.api.auth.auth_service.validate_oauth_state",
            return_value=True,
        ),
        patch(
            "app.api.auth.auth_service.exchange_code_for_token",
            side_effect=error,
        ),
    ):
        with TestClient(app) as client:
            client.get("/api/auth/login", follow_redirects=False)
            response = client.get(
                "/api/auth/callback",
                params={"code": "fake-code", "state": "valid-state"},
            )

    assert response.status_code == 502
    assert response.json()["detail"]["message"] == (
        "Unable to contact Blizzard"
    )

def test_callback_database_error_returns_500():
    """Vérifie qu'une erreur SQL renvoie une erreur 500."""

    fake_db = MagicMock()
    fake_db.scalar.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    with (
        patch(
            "app.api.auth.auth_service.validate_oauth_state",
            return_value=True,
        ),
        patch(
            "app.api.auth.auth_service.exchange_code_for_token",
            return_value={
                "access_token": "fake-access-token",
                "expires_in": 3600,
            },
        ),
        patch(
            "app.api.auth.auth_service.get_account_profile",
            return_value={"id": 12345},
        ),
        patch("app.api.auth.SessionLocal") as mock_session_local,
    ):
        mock_session_local.return_value.__enter__.return_value = fake_db

        with TestClient(app) as client:
            client.get("/api/auth/login", follow_redirects=False)
            response = client.get(
                "/api/auth/callback",
                params={"code": "fake-code", "state": "valid-state"},
            )

    assert response.status_code == 500
    assert response.json()["detail"]["message"] == (
        "Unable to create authentication session"
    )

def test_me_database_error_returns_500():
    """Vérifie qu'une erreur SQL renvoie une erreur 500."""

    fake_db = MagicMock()
    fake_db.scalar.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    with patch(
        "app.core.dependencies.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = fake_db

        with TestClient(app) as client:
            _set_session_cookie(client, "test-session-token")
            response = client.get("/api/auth/me")

    assert response.status_code == 500
    assert response.json()["detail"]["message"] == (
        "Unable to verify authentication"
    )

def test_current_auth_database_error_returns_500():
    """Vérifie qu'une erreur SQL bloque l'accès aux routes protégées."""

    app.dependency_overrides.clear()

    fake_db = MagicMock()
    fake_db.scalar.side_effect = SQLAlchemyError(
        "Database unavailable"
    )

    with patch(
        "app.core.dependencies.SessionLocal",
    ) as mock_session_local:
        mock_session_local.return_value.__enter__.return_value = fake_db

        with TestClient(app) as client:
            _set_session_cookie(client, "test-session-token")
            response = client.get("/api/characters/available")

    assert response.status_code == 500
    assert response.json()["detail"]["message"] == (
        "Unable to verify authentication"
    )
