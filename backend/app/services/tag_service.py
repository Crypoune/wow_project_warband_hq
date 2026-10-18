from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.models.character import Character
from app.models.tag import Tag, CharacterTag


class TagService:
    """Gère le catalogue global de tags et leur attribution."""

    def create_tag(self, name: str) -> dict:
        """Crée un tag dans le catalogue global."""
        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("Le nom du tag ne peut pas être vide.")

        if len(normalized_name) > 50:
            raise ValueError(
                "Le nom du tag ne peut pas dépasser 50 caractères."
            )

        with SessionLocal() as db:
            tag = Tag(name=normalized_name)
            db.add(tag)

            try:
                db.commit()
                db.refresh(tag)
            except IntegrityError as exc:
                db.rollback()

                print(
                    "[TagService.create_tag] "
                    f"Erreur PostgreSQL : {exc.orig}"
                )

                raise ValueError(
                    "Impossible de créer le tag. "
                    "Consultez les logs du serveur."
                ) from exc

            return {"id": tag.id, "name": tag.name}

    def get_tags(self) -> list[dict]:
        """Récupère tous les tags du catalogue global."""
        with SessionLocal() as db:
            statement = select(Tag).order_by(Tag.name)
            tags = db.scalars(statement).all()

            return [
                {"id": tag.id, "name": tag.name}
                for tag in tags
            ]

    def update_tag(self, tag_id: int, name: str) -> dict:
        """Met à jour le nom d'un tag global."""
        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("Le nom du tag ne peut pas être vide.")

        if len(normalized_name) > 50:
            raise ValueError(
                "Le nom du tag ne peut pas dépasser 50 caractères."
            )

        with SessionLocal() as db:
            tag = db.get(Tag, tag_id)

            if tag is None:
                raise ValueError("Tag introuvable.")

            tag.name = normalized_name

            try:
                db.commit()
                db.refresh(tag)
            except IntegrityError as exc:
                db.rollback()
                raise ValueError(
                    "Un tag avec ce nom existe déjà."
                ) from exc

            return {"id": tag.id, "name": tag.name}

    def delete_tag(self, tag_id: int) -> bool:
        """Supprime un tag global et ses associations."""
        with SessionLocal() as db:
            tag = db.get(Tag, tag_id)

            if tag is None:
                raise ValueError("Tag introuvable.")

            try:
                db.query(CharacterTag).filter(
                    CharacterTag.tag_id == tag_id
                ).delete(synchronize_session=False)

                db.delete(tag)
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                raise ValueError(
                    "Impossible de supprimer ce tag."
                ) from exc

            return True

    def assign_tag(
        self,
        user_id: int,
        character_id: int,
        tag_id: int,
    ) -> bool:
        """Attribue un tag global à un personnage de l'utilisateur."""
        with SessionLocal() as db:
            tag = db.scalar(
                select(Tag).where(Tag.id == tag_id)
            )

            if tag is None:
                raise ValueError("Tag introuvable.")

            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                raise ValueError("Personnage introuvable.")

            association_key = (character_id, tag_id)

            if db.get(CharacterTag, association_key) is not None:
                raise ValueError(
                    "Ce tag est déjà attribué à ce personnage."
                )

            association = CharacterTag(
                character_id=character_id,
                tag_id=tag_id,
            )
            db.add(association)

            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                raise ValueError(
                    "Impossible d'attribuer ce tag."
                ) from exc

            return True

    def remove_tag(
        self,
        user_id: int,
        character_id: int,
        tag_id: int,
    ) -> bool:
        """Retire un tag d'un personnage de l'utilisateur."""
        with SessionLocal() as db:
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                raise ValueError("Personnage introuvable.")

            tag = db.scalar(
                select(Tag).where(Tag.id == tag_id)
            )

            if tag is None:
                raise ValueError("Tag introuvable.")

            association_key = (character_id, tag_id)
            association = db.get(CharacterTag, association_key)

            if association is None:
                raise ValueError(
                    "Ce tag n'est pas attribué à ce personnage."
                )

            try:
                db.delete(association)
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                raise ValueError(
                    "Impossible de retirer ce tag."
                ) from exc

            return True

    def get_character_tags(
        self,
        user_id: int,
        character_id: int,
    ) -> list[dict]:
        """Récupère les tags d'un personnage de l'utilisateur."""
        with SessionLocal() as db:
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                raise ValueError("Personnage introuvable.")

            statement = (
                select(Tag)
                .join(
                    CharacterTag,
                    CharacterTag.tag_id == Tag.id,
                )
                .where(CharacterTag.character_id == character_id)
                .order_by(Tag.name)
            )

            tags = db.scalars(statement).all()

            return [
                {"id": tag.id, "name": tag.name}
                for tag in tags
            ]
