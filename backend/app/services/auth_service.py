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
        profile = response.json()

        return profile


    def get_account_characters(self, access_token: str) -> list[dict]:
        """Récupère les personnages de tous les comptes WoW."""

        profile = self.get_account_profile(access_token)

        if not isinstance(profile, dict):
            raise ValueError("Invalid Blizzard profile structure")

        accounts = profile.get("wow_accounts", [])

        if not isinstance(accounts, list):
            raise ValueError("Invalid Blizzard profile structure")

        if not all(isinstance(account, dict) for account in accounts):
            raise ValueError("Invalid Blizzard profile structure")

        # Vérifie que chaque compte contient une liste de personnages valide.
        for account in accounts:
            account_characters = account.get("characters", [])

            if not isinstance(account_characters, list):
                raise ValueError("Invalid Blizzard profile structure")

            if not all(isinstance(entry, dict) for entry in account_characters):
                raise ValueError("Invalid Blizzard profile structure")

        characters = []

        # Parcourt les comptes WoW associés au compte Blizzard.
        for account in accounts:
            # Parcourt les personnages de chaque compte WoW.
            for entry in account.get("characters", []):
                # Les objets imbriqués sont facultatifs, mais doivent être des dictionnaires.
                nested_fields = (
                    "character",
                    "realm",
                    "playable_class",
                    "playable_race",
                    "faction",
                )

                for field in nested_fields:
                    value = entry.get(field, {})
                    if not isinstance(value, dict):
                        raise ValueError("Invalid Blizzard profile structure")

                character = entry.get("character", {})
                realm = entry.get("realm", {})
                playable_class = entry.get("playable_class", {})
                playable_race = entry.get("playable_race", {})
                faction = entry.get("faction", {})

                characters.append(
                    {
                        "id": entry.get("id"),
                        "name": entry.get("name"),
                        "level": entry.get("level"),
                        "realm": realm.get("name"),
                        "realm_slug": realm.get("slug"),
                        "class": playable_class.get("name"),
                        "class_id": playable_class.get("id"),
                        "race": playable_race.get("name"),
                        "race_id": playable_race.get("id"),
                        "faction": faction.get("name"),
                        "profile_url": character.get("href"),
                    }
                )

        return characters
