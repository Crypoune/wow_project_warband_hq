from urllib.parse import urlencode
import secrets

import httpx

from app.core.config import Settings


class InvalidBlizzardProfileError(Exception):
    """Signale une réponse de profil Blizzard dont la structure est invalide."""


class AuthService:
    """Gère l'authentification OAuth et les appels de profil à l'API Blizzard."""

    TOKEN_URL = "https://oauth.battle.net/token"

    # Cache partagé entre les instances pour éviter de redemander les portraits.
    # La clé combine le royaume et le nom normalisé du personnage.
    _character_media_cache: dict[
    tuple[str, str],
    dict[str, str | None],
] = {}

    def __init__(self, settings: Settings):
        """Conserve la configuration nécessaire aux appels Blizzard."""

        self.settings = settings

    def generate_oauth_state(self) -> str:
        """Génère une valeur aléatoire pour sécuriser le retour OAuth."""

        # Le state permet de vérifier que le retour correspond à la demande
        # d'authentification initiée par notre application.
        return secrets.token_urlsafe(32)

    def build_authorization_url(self, state: str) -> str:
        """Construit l'URL de redirection vers l'autorisation Blizzard."""

        params = {
            "client_id": self.settings.blizzard_client_id,
            "response_type": "code",
            "scope": "wow.profile",
            "redirect_uri": self.settings.blizzard_redirect_uri,
            "state": state,
        }

        # urlencode encode les paramètres pour qu'ils soient correctement
        # transmis dans l'URL, notamment le redirect_uri et le state.
        return f"https://oauth.battle.net/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> dict:
        """Échange le code OAuth reçu contre un access token Blizzard."""

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.blizzard_redirect_uri,
        }

        # Les identifiants de l'application sont transmis en authentification
        # HTTP Basic. Le code OAuth est échangé côté serveur, pas côté frontend.
        response = httpx.post(
            self.TOKEN_URL,
            data=data,
            auth=(
                self.settings.blizzard_client_id,
                self.settings.blizzard_client_secret,
            ),
            timeout=10.0,
        )

        # Une réponse HTTP en erreur est propagée à la couche appelante.
        response.raise_for_status()

        return response.json()

    def validate_oauth_state(
        self,
        received_state: str,
        expected_state: str,
    ) -> bool:
        """Vérifie que le state reçu correspond à celui attendu."""

        # compare_digest compare les valeurs sans comparaison de chaînes
        # ordinaire, afin de limiter les risques d'attaques temporelles.
        return secrets.compare_digest(received_state, expected_state)

    def get_account_profile(self, access_token: str) -> dict:
        """Récupère les comptes WoW associés au compte Blizzard connecté."""

        response = httpx.get(
            (
                f"https://{self.settings.blizzard_region}.api.blizzard.com"
                "/profile/user/wow"
            ),
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

        # La validation de la structure est effectuée par la méthode qui
        # exploite le profil, afin de centraliser les règles de validation.
        return response.json()

    def get_character_profile(
        self,
        access_token: str,
        realm_slug: str,
        character_name: str,
    ) -> dict:
        """Récupère le profil détaillé d'un personnage WoW."""

        # Cet endpoint fournit les informations générales du personnage,
        # notamment average_item_level et equipped_item_level lorsqu'ils
        # sont présents dans la réponse de Blizzard.
        url = (
            f"https://{self.settings.blizzard_region}.api.blizzard.com"
            f"/profile/wow/character/{realm_slug}/{character_name.lower()}"
        )

        response = httpx.get(
            url,
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

        # On vérifie le type de la réponse avant que le service appelant
        # utilise .get(). Une réponse mal formée ne doit pas être traitée
        # comme un profil valide.
        if not isinstance(profile, dict):
            raise InvalidBlizzardProfileError(
                "Invalid Blizzard profile structure"
            )

        return profile

    def get_account_characters(self, access_token: str) -> list[dict]:
        """Récupère les personnages de tous les comptes WoW."""

        profile = self.get_account_profile(access_token)

        if not isinstance(profile, dict):
            raise InvalidBlizzardProfileError(
                "Invalid Blizzard profile structure"
            )

        accounts = profile.get("wow_accounts", [])

        if not isinstance(accounts, list):
            raise InvalidBlizzardProfileError(
                "Invalid Blizzard profile structure"
            )

        if not all(isinstance(account, dict) for account in accounts):
            raise InvalidBlizzardProfileError(
                "Invalid Blizzard profile structure"
            )

        # On valide les listes avant de parcourir les comptes. Cela évite
        # de traiter silencieusement une structure inattendue de Blizzard.
        for account in accounts:
            account_characters = account.get("characters", [])

            if not isinstance(account_characters, list):
                raise InvalidBlizzardProfileError(
                    "Invalid Blizzard profile structure"
                )

            if not all(
                isinstance(entry, dict) for entry in account_characters
            ):
                raise InvalidBlizzardProfileError(
                    "Invalid Blizzard profile structure"
                )

        characters = []

        # Un compte Blizzard peut contenir plusieurs comptes WoW.
        for account in accounts:
            for entry in account.get("characters", []):
                # Ces champs imbriqués sont facultatifs. Lorsqu'ils sont
                # présents, ils doivent toutefois être des dictionnaires.
                nested_fields = (
                    "character",
                    "realm",
                    "playable_class",
                    "playable_race",
                    "faction",
                    "gender",
                )

                for field in nested_fields:
                    value = entry.get(field, {})

                    if not isinstance(value, dict):
                        raise InvalidBlizzardProfileError(
                            "Invalid Blizzard profile structure"
                        )

                character = entry.get("character", {})
                realm = entry.get("realm", {})
                playable_class = entry.get("playable_class", {})
                playable_race = entry.get("playable_race", {})
                faction = entry.get("faction", {})
                gender = entry.get("gender", {})

                # On transforme la réponse Blizzard en dictionnaire stable
                # pour le reste de l'application, sans conserver tout le JSON.
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
                        "gender": gender.get("type"),
                        "faction": faction.get("name"),
                        "profile_url": character.get("href"),
                    }
                )

        return characters


    def get_character_media(
        self,
        access_token: str,
        realm_slug: str,
        character_name: str,
    ) -> dict[str, str | None]:
        """Récupère le portrait et le rendu principal d'un personnage WoW."""

        cache_key = (realm_slug, character_name.lower())

        if cache_key in self._character_media_cache:
            return self._character_media_cache[cache_key]

        url = (
            f"https://{self.settings.blizzard_region}.api.blizzard.com"
            f"/profile/wow/character/{realm_slug}/{character_name.lower()}"
            "/character-media"
        )

        response = httpx.get(
            url,
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
        media = response.json()
        assets = media.get("assets", [])

        # On privilégie inset pour le portrait, puis avatar.
        portrait_url = next(
            (
                asset.get("value")
                for key in ("inset", "avatar")
                for asset in assets
                if (
                    isinstance(asset, dict)
                    and asset.get("key") == key
                    and asset.get("value")
                )
            ),
            None,
        )

        main_art_url = next(
            (
                asset.get("value")
                for asset in assets
                if (
                    isinstance(asset, dict)
                    and asset.get("key") == "main"
                    and asset.get("value")
                )
            ),
            None,
        )

        result = {
            "portrait_url": portrait_url,
            "main_art_url": main_art_url,
        }

        self._character_media_cache[cache_key] = result

        return result
