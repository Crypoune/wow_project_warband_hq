from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.character import Character
from app.models.note import CharacterNote


class NoteService:
    """Gère les notes personnelles des personnages de Warband HQ."""

    def get_character_note(
        self,
        character_id: int,
        user_id: int,
    ) -> dict | None:
        """Récupère la note d'un personnage appartenant à l'utilisateur."""

        with SessionLocal() as db:
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                raise ValueError(
                    "Personnage introuvable ou inaccessible."
                )

            note = db.scalar(
                select(CharacterNote).where(
                    CharacterNote.character_id == character_id,
                )
            )

            if note is None:
                return None

            return {
                "id": note.id,
                "character_id": note.character_id,
                "content": note.content,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            }

    def save_character_note(
        self,
        character_id: int,
        user_id: int,
        content: str,
    ) -> dict:
        """Crée ou met à jour la note d'un personnage."""

        with SessionLocal() as db:
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                raise ValueError(
                    "Personnage introuvable ou inaccessible."
                )

            note = db.scalar(
                select(CharacterNote).where(
                    CharacterNote.character_id == character_id,
                )
            )

            if note is None:
                note = CharacterNote(
                    character_id=character_id,
                    content=content,
                )

                db.add(note)

            else:
                note.content = content

            db.commit()
            db.refresh(note)

            return {
                "id": note.id,
                "character_id": note.character_id,
                "content": note.content,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            }
