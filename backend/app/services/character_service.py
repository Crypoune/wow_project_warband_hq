import httpx

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.character import Character
from app.services.auth_service import (
    AuthService,
    InvalidBlizzardProfileError,
)


class CharacterService:
    """Gère les personnages disponibles et importés dans Warband HQ."""

    def __init__(self):
        self.auth_service = AuthService(settings)

    def get_available_characters(self, access_token: str) -> list[dict]:
        """Récupère les personnages disponibles sur le compte Blizzard."""
        return self.auth_service.get_account_characters(access_token)

    def import_characters(
        self,
        user_id: int,
        access_token: str,
        character_ids: list[int],
    ) -> list[dict]:
        """Importe les personnages sélectionnés dans Warband HQ."""

        available_characters = self.get_available_characters(access_token)
        available_by_id = {
            character["id"]: character
            for character in available_characters
        }

        # Un utilisateur ne peut importer que ses propres personnages Blizzard.
        invalid_ids = set(character_ids) - set(available_by_id)

        if invalid_ids:
            raise ValueError(
                "One or more characters do not belong to the Blizzard account"
            )

        imported = []

        with SessionLocal() as db:
            existing_characters = db.scalars(
                select(Character).where(
                    Character.user_id == user_id,
                    Character.blizzard_character_id.in_(character_ids),
                )
            ).all()

            existing_ids = {
                character.blizzard_character_id
                for character in existing_characters
            }

            for character_id in dict.fromkeys(character_ids):
                if character_id in existing_ids:
                    continue

                character = Character(
                    user_id=user_id,
                    blizzard_character_id=character_id,
                )
                db.add(character)
                imported.append(character_id)

            db.commit()

        return [
            available_by_id[character_id]
            for character_id in imported
        ]

    def update_favorite(
        self,
        user_id: int,
        character_id: int,
        is_favorite: bool,
    ) -> dict | None:
        """Met à jour le statut favori d'un personnage appartenant à l'utilisateur."""

        with SessionLocal() as db:
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                return None

            character.is_favorite = is_favorite
            db.commit()
            db.refresh(character)

            return {
                "id": character.id,
                "is_favorite": character.is_favorite,
            }


    def get_imported_characters(
        self,
        user_id: int,
        access_token: str,
    ) -> list[dict]:
        """Retourne les personnages importés par l'utilisateur."""

        with SessionLocal() as db:
            imported_characters = db.scalars(
                select(Character).where(Character.user_id == user_id)
            ).all()

            # Copie des métadonnées avant la fermeture de la session.
            imported_data = [
                {
                    "id": character.id,
                    "blizzard_character_id": character.blizzard_character_id,
                    "is_favorite": character.is_favorite,
                    "imported_at": character.imported_at,
                    "last_synced_at": character.last_synced_at,
                }
                for character in imported_characters
            ]

        if not imported_data:
            return []

        # Blizzard reste la source de vérité pour les données du personnage.
        available_characters = self.get_available_characters(access_token)
        available_by_id = {
            character["id"]: character
            for character in available_characters
        }

        result = []

        for imported in imported_data:
            blizzard_data = available_by_id.get(
                imported["blizzard_character_id"], {}
            )

            character_data = {**blizzard_data, **imported}

            realm_slug = character_data.get("realm_slug")
            character_name = character_data.get("name")

            # Valeurs par défaut : un échec de récupération ne bloque pas
            # l'affichage du personnage.
            character_data["portrait_url"] = None
            character_data["average_item_level"] = None
            character_data["equipped_item_level"] = None

            if realm_slug and character_name:
                # Récupération du portrait.
                try:
                    character_data["portrait_url"] = (
                        self.auth_service.get_character_media(
                            access_token,
                            realm_slug,
                            character_name,
                        )
                    )
                except httpx.HTTPError:
                    # Le personnage reste disponible sans portrait.
                    pass

                # Récupération du profil détaillé et de son niveau d'objet.
                try:
                    profile = self.auth_service.get_character_profile(
                        access_token,
                        realm_slug,
                        character_name,
                    )

                    character_data["average_item_level"] = profile.get(
                        "average_item_level"
                    )
                    character_data["equipped_item_level"] = profile.get(
                        "equipped_item_level"
                    )

                except (httpx.HTTPError, InvalidBlizzardProfileError):
                    # Une erreur HTTP ou une réponse mal formée ne doit pas
                    # empêcher l'affichage du personnage.
                    # Les niveaux d'objet restent alors à None.
                    pass

            result.append(character_data)

        return result


    def get_character_details(
        self,
        user_id: int,
        character_id: int,
        access_token: str,
    ) -> dict | None:
        """Retourne les détails d'un personnage importé par l'utilisateur."""

        # Vérifie que le personnage appartient à l'utilisateur connecté.
        with SessionLocal() as db:
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                return None

            # Copie les métadonnées avant la fermeture de la session.
            imported_data = {
                "id": character.id,
                "blizzard_character_id": character.blizzard_character_id,
                "is_favorite": character.is_favorite,
                "imported_at": character.imported_at,
                "last_synced_at": character.last_synced_at,
            }

        # Récupère les informations du personnage depuis Blizzard.
        available_characters = self.get_available_characters(access_token)

        blizzard_data = next(
            (
                item
                for item in available_characters
                if item["id"] == imported_data["blizzard_character_id"]
            ),
            {},
        )

        character_data = {**blizzard_data, **imported_data}

        # Initialise les données détaillées.
        character_data["portrait_url"] = None
        character_data["average_item_level"] = None
        character_data["equipped_item_level"] = None

        realm_slug = character_data.get("realm_slug")
        character_name = character_data.get("name")

        if realm_slug and character_name:
            # Le portrait est facultatif : son indisponibilité
            # ne doit pas empêcher l'affichage des autres informations.
            try:
                character_data["portrait_url"] = (
                    self.auth_service.get_character_media(
                        access_token,
                        realm_slug,
                        character_name,
                    )
                )
            except httpx.HTTPError:
                pass

            # Le profil détaillé fournit notamment les niveaux d'objet.
            profile = self.auth_service.get_character_profile(
                access_token,
                realm_slug,
                character_name,
            )

            character_data["average_item_level"] = profile.get(
                "average_item_level"
            )
            character_data["equipped_item_level"] = profile.get(
                "equipped_item_level"
            )

        return character_data
