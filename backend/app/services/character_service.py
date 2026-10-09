from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.character import Character
from app.services.auth_service import AuthService


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
                imported["blizzard_character_id"],
                {},
            )
            result.append({**blizzard_data, **imported})

        return result
