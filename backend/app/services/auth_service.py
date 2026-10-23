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

    # Cache partagé des icônes d'objets pour éviter les appels répétés.
    # L'URL de l'endpoint média Blizzard sert de clé.
    _item_icon_cache: dict[str, str | None] = {}

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


    def get_character_equipment(
        self,
        access_token: str,
        realm_slug: str,
        character_name: str,
    ) -> dict:
        """Récupère l'équipement actuellement porté par un personnage WoW."""

        # L'endpoint utilise le royaume et le nom normalisé du personnage.
        url = (
            f"https://{self.settings.blizzard_region}.api.blizzard.com"
            f"/profile/wow/character/{realm_slug}/{character_name.lower()}"
            "/equipment"
        )

        # On demande les données de profil, avec la région configurée
        # et la langue française, comme pour les autres appels Blizzard.
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

        # Une erreur HTTP est propagée à la couche appelante.
        response.raise_for_status()

        equipment = response.json()

        # On vérifie la structure avant de transmettre les données.
        # Une réponse inattendue ne doit pas être considérée comme valide.
        if (
            not isinstance(equipment, dict)
            or not isinstance(equipment.get("equipped_items"), list)
        ):
            raise InvalidBlizzardProfileError(
                "Invalid Blizzard equipment structure"
            )

        return equipment


    def _get_character_endpoint(
        self,
        access_token: str,
        realm_slug: str,
        character_name: str,
        endpoint: str,
    ) -> dict:
        """Récupère les données d'un endpoint de profil de personnage."""

        url = (
            f"https://{self.settings.blizzard_region}.api.blizzard.com"
            f"/profile/wow/character/{realm_slug}/{character_name.lower()}"
            f"/{endpoint}"
        )

        response = httpx.get(
            url,
            params={
                "namespace": f"profile-{self.settings.blizzard_region}",
                "locale": "fr_FR",
            },
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise InvalidBlizzardProfileError(
                f"Invalid Blizzard character {endpoint} structure"
            )

        return data


    def get_character_specializations(
        self,
        access_token: str,
        realm_slug: str,
        character_name: str,
    ) -> dict:
        """Récupère les spécialisations d'un personnage."""

        return self._get_character_endpoint(
            access_token, realm_slug, character_name, "specializations"
        )


    def get_character_statistics(
        self,
        access_token: str,
        realm_slug: str,
        character_name: str,
    ) -> dict:
        """Récupère les statistiques de combat d'un personnage."""

        return self._get_character_endpoint(
            access_token, realm_slug, character_name, "statistics"
        )


    def get_character_achievements(
        self,
        access_token: str,
        realm_slug: str,
        character_name: str,
    ) -> dict:
        """Récupère les hauts faits d'un personnage."""

        return self._get_character_endpoint(
            access_token, realm_slug, character_name, "achievements"
        )


    def get_item_icon_url(
        self,
        access_token: str,
        media_url: str,
    ) -> str | None:
        """Récupère l'URL de l'icône d'un objet WoW depuis son endpoint média Blizzard."""

        # On réutilise l'icône si elle a déjà été récupérée.
        if media_url in self._item_icon_cache:
            return self._item_icon_cache[media_url]

        response = httpx.get(
            media_url,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10.0,
        )
        response.raise_for_status()

        media = response.json()

        if not isinstance(media, dict):
            raise InvalidBlizzardProfileError(
                "Invalid Blizzard item media structure"
            )

        assets = media.get("assets", [])

        if not isinstance(assets, list):
            raise InvalidBlizzardProfileError(
                "Invalid Blizzard item media assets"
            )

        icon_url = next(
            (
                asset["value"]
                for asset in assets
                if (
                    isinstance(asset, dict)
                    and asset.get("key") == "icon"
                    and isinstance(asset.get("value"), str)
                )
            ),
            None,
        )

        # On mémorise aussi l'absence d'icône pour éviter les appels répétés.
        self._item_icon_cache[media_url] = icon_url

        return icon_url


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
                for key in ("main-raw", "main")
                for asset in assets
                if (
                    isinstance(asset, dict)
                    and asset.get("key") == key
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
