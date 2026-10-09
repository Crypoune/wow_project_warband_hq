from urllib.parse import urlencode
import secrets

import httpx

from app.core.config import Settings


class AuthService:
    """Gère la logique d'authentification Blizzard."""

    TOKEN_URL = "https://oauth.battle.net/token"

    def __init__(self, settings: Settings):
        # Conserve la configuration nécessaire au service.
        self.settings = settings

    def generate_oauth_state(self) -> str:
        # Génère une valeur aléatoire utilisée pour sécuriser le retour OAuth.
        return secrets.token_urlsafe(32)

    def build_authorization_url(self, state: str) -> str:
        # Prépare les paramètres nécessaires à la demande d'autorisation Blizzard.
        params = {
            "client_id": self.settings.blizzard_client_id,
            "response_type": "code",
            "scope": "wow.profile",
            "redirect_uri": self.settings.blizzard_redirect_uri,
            "state": state,
        }

        # Encode correctement les paramètres pour construire l'URL finale.
        return f"https://oauth.battle.net/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> dict:
        """Échange le code OAuth contre un access token Blizzard."""

        # Prépare les données nécessaires à l'échange du code OAuth.
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.blizzard_redirect_uri,
        }

        # Envoie le code à Blizzard pour obtenir un access token.
        response = httpx.post(
            self.TOKEN_URL,
            data=data,
            auth=(
                self.settings.blizzard_client_id,
                self.settings.blizzard_client_secret,
            ),
            timeout=10.0,
        )

        # Déclenche une erreur si Blizzard renvoie un statut HTTP d'échec.
        response.raise_for_status()

        # Retourne la réponse JSON fournie par Blizzard.
        return response.json()

    def validate_oauth_state(
        self,
        received_state: str,
        expected_state: str,
    ) -> bool:
        # Vérifie que le state reçu correspond à celui généré avant la redirection.
        return secrets.compare_digest(received_state, expected_state)


    def get_account_profile(self, access_token: str) -> dict:
        """Récupère le profil du compte WoW connecté."""

        response = httpx.get(
            f"https://{self.settings.blizzard_region}.api.blizzard.com/profile/user/wow",
            params={
                "namespace": f"profile-{self.settings.blizzard_region}",
                "locale": "fr_FR",
            },
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10.0,
        )

        response.raise_for_status()
        return response.json()
